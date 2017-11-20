/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher utilities
*
*/

#include <cstdlib>
#include <string.h>
#include <fstream>
#include <cerrno>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdarg.h>
#include <openssl/crypto.h>
#include "SB_Dispatcher_Utils.h"
#include "version.h"    // *should* be from top-level OSLockdown includes...
#include "sbprops.h"


extern DISPATCHER_OPTS disp_opts;

bool isValidClientType(int clientType)
{
  bool retval = false;
  switch (clientType)
  {
    case CLIENT_STANDALONE:
    case CLIENT_ENTERPRISE:
    case CLIENT_BULK:
    case CLIENT_ZSERIES:
    case CLIENT_AIX:
        retval = true;
    default:
        retval = false;
  }
  return retval;
}

#define CHECKENUM(x) if (prodEnum==x) return #x; 

string
prodTypeToString(SB_CLIENT_ENUM prodEnum)
{
//    cout <<" PRODUCT ENUMERATION IS "<< prodEnum << endl;
    CHECKENUM(CLIENT_STANDALONE)
    CHECKENUM(CLIENT_ENTERPRISE)
    CHECKENUM(CLIENT_BULK)
    CHECKENUM(CLIENT_ZSERIES)
    CHECKENUM(CLIENT_AIX)
    return "Unknown product enumeration";
}

/*
  The Verify* routines will thrown an exception (SBDispatcher_Except) if they fail.
  The intent is that the catcher is the invoked SOAP server routine, and the error
  code and message will be returned to the SOAP remote caller process.
 */
void Verify_Am_Root()
{
  uid_t my_uid,my_euid;
  my_uid=getuid();
  my_euid=geteuid();
  if ((my_uid!=0) && (my_euid!=0))
  {
    ostringstream message;
    message<<"Must run as root, instead of : UID="<<my_uid<<"  EUID="<<my_euid;
    throw (SBDispatcher_Except(500,message.str()));
  }
}

extern string MY_APPLICATION_DISPATCHER_LOG;
bool
string_ends_with(const string &str, const string &suffix)
{
  if (suffix.length()>str.length()) return false;
  size_t start_check=str.length()-suffix.length();
  size_t end_find=str.find(suffix,start_check);
  if (start_check==end_find) return true;
  return false;
}

void
search_replace(string& bigstr, string& target, string& repstr)
{
  size_t pos;
  pos=bigstr.find(target);
  if (pos!=string::npos)
  {
    size_t targetlen= target.length();
    size_t replen=repstr.length();
    bigstr.replace(pos,targetlen,repstr);
  }
}

int
SB_Daemonize(void)
{
  char buffer[11];
  int fd;
  long int pid;

/* Redirect stdin/stdout/stderr to /dev/null */
  freopen("/dev/null", "w", stdout);
  freopen("/dev/null", "w", stderr);
  freopen("/dev/null", "r", stdin);
//  close(STDIN_FILENO);
//  close(STDOUT_FILENO);
//  close(STDERR_FILENO);
  
/* Follow preprocess in place to allow for debugging, so we're not constantly adding/removing it */
  if ((pid = fork ()) < 0)
    return (-1);
  else if (pid != 0)
    exit (0);

              /** Parent goes bye-bye **/

  /* Become session leader and change directory * */
  setsid ();

  chdir (APPLICATION_HOME);

  /** Write to PID file **/
  memset (buffer, '\0', sizeof (buffer));
  pid = getpid ();
  snprintf (buffer, sizeof (buffer) - 1, "%ld", pid);
  fd = open (APPLICATION_PID_FILE, O_CREAT | O_TRUNC | O_WRONLY, 0644);
  if (fd < 0)
  {
    throw (SBDispatcher_Except(500,"Unable to create pid file"));
  }
  else
  {
    write (fd, buffer, sizeof (buffer));
    close (fd);
    
    write_log(LOG_INFO,"Create pid file %s with pid %d",APPLICATION_PID_FILE, pid);
  }
  umask (0);
  return (0);
}


void
SB_ACTION::set_thread()
{
  m_thread=pthread_self();
}

void SB_ACTION::kill()
{
  pthread_mutex_lock(&m_mutex);
  m_kill_flag=true;
  pthread_mutex_unlock(&m_mutex);
}

SB_ACTION::SB_ACTION(string transid,string replyto, bool from_console)
{
  m_actionIdx=-1;
  m_from_console=from_console;
  m_transid=transid;
  m_replyto=replyto;
  pthread_mutex_init(&m_mutex,NULL);  
}

SB_ACTION::~SB_ACTION()
{
//  cout <<"Deleting task context for "<<m_action<<"("<<m_transid<<")"<<endl;
  // clean up anything we need to
  pthread_mutex_destroy(&m_mutex); 
}

void SB_DirList::populate()
{
  DIR *dirp;
  struct dirent *dp;
  struct stat info;
  if ((dirp = opendir(m_dirname.c_str()))==NULL)
  {
    m_reason="Unable to read";
    m_valid=false;
    return;
  }
  while ((dp=readdir(dirp))!=NULL)
  {
    // check for some filenames we know we don't want */
    if ((strcmp(dp->d_name,".")==0) || (strcmp(dp->d_name,"..")==0)) continue;

    /* now see if the filename ends with the designated suffix, (if suffix is empty then skip this */
    if (!m_suffix.empty())
    {
      if (!string_ends_with(dp->d_name,m_suffix)) continue;
    }
    size_t filesize;
    time_t timestamp;
    string path(m_dirname+"/"+dp->d_name);
//    cout <<"\t"<<path<<endl;
    if ((stat (path.c_str(),&info))==0)
    {
      if (S_ISREG (info.st_mode))
      {
        m_files.push_back(SB_DirEntry(dp->d_name,info.st_size,info.st_mtime));
      }
    }
    
  }
  closedir(dirp);
}

SB_DirList::SB_DirList(string dirname,string suffix,string kind)
{
  m_valid=true;
  m_dirname=dirname;
  m_suffix=suffix;
  m_kind=kind;
  populate();
}

string SB_DirList::toXml()
{
  ostringstream message;
  
  message << "<reportList dirname=\"" << m_dirname<< "\" type=\"" << m_kind << "\" >";
  for (size_t i=0;i!=m_files.size();i++)
  {
    message << "<file ";
    message << " name=\"" << m_files[i].m_filename << "\"" ;
    message << " timestamp=\"" << m_files[i].m_timestamp << "\"";
    message << " size=\"" << m_files[i].m_filesize << "\"";
    message << "/>";
  }
  message << "</reportList>";
  return message.str();

}

bool log_to_stderr=false;

/**
 * Write to log (syslog and dedicated log)
 * @param level   Logleve
 * @param fmt     Message format (like snprintf())
 * @param ...     variables for fmt
 *
 */
void
write_log (int level, const char *fmt, ...)
{
  FILE *sblog = NULL;
  const struct tm *tm = NULL;
  struct tm tmObj;
  time_t now = 0;
  int mask = 0;
  static char time_buffer[40];
  char message[1024];

  const char *logprefix[] = {
    "Emergency: ",
    "Alert:     ",
    "Critical:  ",
    "Error:     ",
    "Warning:   ",
    "Notice:    ",
    "Info:      ",
    "DEBUG:     "
  };

  if (level < 0 && level > 7)
    level = 5;
  memset (&message, '\0', sizeof (message));
  memset (&time_buffer, '\0', sizeof (time_buffer));
  va_list arglist;
  va_start (arglist, fmt);
  vsnprintf (message, sizeof (message) - 1, fmt, arglist);
  va_end (arglist);

  /* Determine current log mask */
  mask = setlogmask (0);

  umask (027);
  if (log_to_stderr)
    {
      now = time (NULL);
      tm = localtime_r (&now, &tmObj);
      if (tm != NULL) 
      {
      	(void) strftime (time_buffer, 40, "%F %T", tm);
      }
      else 
      {
      	strcpy(time_buffer, "<TIME_ERROR>");
      }
      fprintf (stderr, "%s %s %s\n", time_buffer, logprefix[level], message);
    }
  else
    {
      if ((sblog = fopen (MY_APPLICATION_DISPATCHER_LOG.c_str(), "a")) != NULL)
        {
          now = time (NULL);
          tm = localtime_r (&now, &tmObj);
      	  if (tm != NULL) 
      	  {
      	    (void) strftime (time_buffer, 40, "%F %T", tm);
      	  }
      	  else 
      	  {
      	    strcpy(time_buffer, "<TIME_ERROR>");
      	  }
          fprintf (sblog, "%s %s %s\n", time_buffer, logprefix[level], message);
          fclose (sblog);
        }

      /* Only log messages < LOG_DEBUG to syslog to avoid cluttering it */
      if (mask < 255)
        {
          openlog ("SB_Dispatcher", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_DAEMON);
          (void) syslog (level, message);
          closelog ();
        }
    }
  return;
}



/****************************************************************************
 *                     Password Callback to Decrypt PEM File                *
 ****************************************************************************/
/**
  * Password callback
  */

char * 
password_cb (const char * prompt)
{
  int ret_val = 0;
  char *temp_pass = NULL;
  string passphrase;
  
  ifstream passfile;
  passfile.open("/var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat");
  passfile >> passphrase;
  passfile.close();
  if (passphrase.empty())
  {
    write_log (LOG_DEBUG, "Startup: encrypted passphrase file not found.");
    write_log (LOG_INFO, "Startup: Prompting for passhprase");
    temp_pass = simple_prompt (prompt, 128, 0);    
  }
  else
  {
    temp_pass=strdup(passphrase.c_str());
  }
  return temp_pass;
}

static struct CRYPTO_dynlock_value **my_locks;
static int num_locks;

/* public functions */
void CRYPTO_thread_setup();
void CRYPTO_thread_cleanup();

static struct CRYPTO_dynlock_value * my_lock_create(struct CRYPTO_dynlock_value *ptr,const char *file, int line)
{
  int retval;
  if (!ptr) ptr=(struct CRYPTO_dynlock_value*)calloc(1,sizeof(struct CRYPTO_dynlock_value));
  if (!ptr)
  {
//    perror("Unable to allocate mutex");
    throw (SBDispatcher_Except(500,"Unable to allocate mutex "));
// exit(1);
  }
  retval=pthread_mutex_init(&(ptr->mutex),NULL);
  return ptr;
}


static void my_lock_core(int mode, CRYPTO_dynlock_value *ptr, const char *file, int line)
{
  if (mode &CRYPTO_LOCK)     pthread_mutex_lock(&(ptr->mutex));
  else                       pthread_mutex_unlock(&(ptr->mutex));
}
static void my_lock(int mode, int n, const char *file, int line)
{
  my_lock_core(mode,my_locks[n],file,line);
}

long unsigned int my_id()
{
  return (long unsigned int)pthread_self();
}

static void my_dyn_lock(int mode, struct CRYPTO_dynlock_value *ptr, const char *file, int line)
{
  my_lock_core(mode,ptr,file,line);
}

static struct CRYPTO_dynlock_value * my_dyn_create(const char *file, int line)
{
  return my_lock_create(NULL,file,line);
}

static void my_dyn_destroy(struct CRYPTO_dynlock_value *ptr, const char *file, int line)
{
  if (ptr) free(ptr);  
}

void CRYPTO_thread_setup()
{
  int i;
  
  if (my_locks) return;
  num_locks=CRYPTO_num_locks();
  my_locks=(struct CRYPTO_dynlock_value**)calloc(num_locks,sizeof(struct CRYPTO_dynlock_value*));
  if (!my_locks)
  { 
    throw (SBDispatcher_Except(500,"Unable to allocate lock structures"));
//    write_log(LOG_ERR,"Unable to allocate lock structures");
//    exit(1);
  }
  for (i = 0;i!=num_locks;i++)
  {
    my_locks[i]=my_lock_create(NULL,__FILE__,__LINE__);
  }
  CRYPTO_set_id_callback(my_id);
  CRYPTO_set_locking_callback(my_lock);
  CRYPTO_set_dynlock_create_callback(my_dyn_create);
  CRYPTO_set_dynlock_lock_callback(my_dyn_lock);
  CRYPTO_set_dynlock_destroy_callback(my_dyn_destroy);
}

void CRYPTO_thread_cleanup()
{
  int i;
  CRYPTO_set_id_callback(NULL);
  CRYPTO_set_locking_callback(NULL);
  CRYPTO_set_dynlock_create_callback(NULL);
  CRYPTO_set_dynlock_lock_callback(NULL);
  CRYPTO_set_dynlock_destroy_callback(NULL);
  for (i=0;i!=num_locks;i++)
  {
    my_dyn_destroy(my_locks[i],__FILE__,__LINE__);
  }
  free(my_locks);
}


string action_text(SB_ACTION_ENUM me)
{
  switch (me)
  {
    case (SB_SCAN):                     return "Scan"; break;
    case (SB_QSCAN):                    return "Quick-Scan"; break;
    case (SB_APPLY):                    return "Apply"; break;
    case (SB_UNDO):                     return "Undo"; break;
    case (SB_BASELINE):            return "Baseline"; break;
    case (SB_GROUP_ASSESSMENT):    return "Group Assessment"; break;
    case (SB_BASELINE_COMPARISON): return "Baseline Comparison"; break;
    default:                       return "UNKNOWN"; break;
  }
}

void init_disp_opts(DISPATCHER_OPTS& opts)
{
  opts.port=6443;
  opts.skip_host=true;
  opts.use_https=true;
  opts.daemonize=true;
  opts.verbose=false;
  opts.loglevel=7;
  opts.shim_name="";
  opts.integrity_check=true;
  opts.start_time=-1;
  opts.end_time=-1;
  opts.max_load=0.0;
  opts.address="";
  opts.interface="";
  opts.ciphers="";
  opts.commonname="";
  opts.send_timeout=2;
  opts.recv_timeout=2;
  opts.accept_timeout=1;
  opts.max_log_MB = APPLICATION_LOG_FILE_MAX_MB;  // initially 4Meg max log size
}

static void
lowercase(string &textphrase)
{
  for (size_t j=0;j<textphrase.length();j++)
  {
    textphrase[j]=tolower(textphrase[j]);
  }
}

// Assumption is that the properties files are valid.  If not they are quietly ignored.
void read_dispatcher_properties(DISPATCHER_OPTS& opts)
{
  static char prop_file[]="/usr/share/oslockdown/cfg/osl-dispatcher.properties";
  
  ifstream properties(prop_file);
  
  if (properties.is_open())
  {
    write_log(LOG_INFO, "Reading persistent properties file %s .", prop_file);
    string thisline,tag,value;
    istringstream valstr;
    size_t equalsign;
    
    while (properties.good())
    {
      valstr.clear();
      getline(properties,thisline);
      if (thisline[0]=='#') continue ; // ignore anything starting with a '#'
    // find the first 'equal' sign and turn it into a space
      equalsign=thisline.find('=');
      if (equalsign!=string::npos)
      {
        tag=thisline.substr(0,equalsign);
        value=thisline.substr(equalsign+1);
        valstr.str(value);

        if (tag=="port") 
        {
          valstr >> opts.port;
        }
        else if (tag=="address") 
        {
          valstr >> opts.address;
        }
        else if (tag=="skip_host") 
        {
          lowercase(value);
          if (value=="false") opts.skip_host=false;          
        }
        else if (tag=="use_https") 
        {
          lowercase(value);
          if (value=="false") opts.use_https=false;          
        }
        else if (tag=="daemonize")
        {
          lowercase(value);
          if (value=="false") opts.daemonize=false;          
        }
        else if (tag=="verbose") 
        {
          lowercase(value);
          if (value=="false") opts.verbose=false;          
        }
        else if (tag=="loglevel") 
        {
          int intval;
          valstr >> intval;
          if ((intval>=LOG_EMERG) && (intval<=LOG_DEBUG))
          {
            opts.loglevel=intval;
          }
          else
          {
            write_log(LOG_WARNING, "Invalid value for loglevel - should be between %d and %d instead of %d - will use %d", LOG_EMERG, LOG_DEBUG, intval, opts.loglevel);
          }
        }
        else if (tag=="shim_name") 
        {
          opts.shim_name=value;
        }
        else if (tag=="integrity_check") 
        {
          lowercase(value);
          if (value=="false") opts.integrity_check=false;          
        }
        else if (tag=="logmax")
        {
          int logmaxsize;
          string logmaxunits;
          valstr >> logmaxsize>>logmaxunits;
        
          if ( !logmaxunits.empty() && (logmaxunits[0] == 'M') && (logmaxsize > 0) && (logmaxsize < 512) && logmaxsize != opts.max_log_MB) 
          {
            write_log(LOG_INFO, "Redefining maximum allowed log transfer size (in MB) from %d to %d",opts.max_log_MB, logmaxsize);
            opts.max_log_MB = logmaxsize;        
          }
          else
          {
            write_log(LOG_WARNING, "Invalid value for logmax - trying to process : %s  - will use %d M", value.c_str(), opts.max_log_MB);
          }
        }
        else if (tag == "recv_timeout")
        {
          int intval;
          valstr >> intval;
          if ((intval >= 2) && (intval <= 60))
          {
            write_log(LOG_INFO, "Resetting recv_timeout from %d seconds to %d seconds.", opts.recv_timeout, intval);
            opts.recv_timeout=intval;
          }
          else
          {
            write_log(LOG_WARNING, "Invalid value for recv_timeout - should be between 2 and 60 instead of %d - will use %d", intval, opts.recv_timeout);
          }
        }
        else if (tag == "send_timeout")
        {
          int intval;
          valstr >> intval;
          if ((intval >= 2) && (intval <= 60))
          {
            write_log(LOG_INFO, "Resetting send_timeout from %d seconds to %d seconds.", opts.send_timeout, intval);
            opts.send_timeout=intval;
          }
          else
          {
            write_log(LOG_WARNING, "Invalid value for send_timeout - should be between 2 and 60 instead of %d - will use %d", intval, opts.send_timeout);
          }
        }
        else if (tag == "accept_timeout")
        {
          int intval;
          valstr >> intval;
          if ((intval >= 1) && (intval <= 60))
          {
            write_log(LOG_INFO, "Resetting accept_timeout from %d seconds to %d seconds.", opts.accept_timeout, intval);
            opts.accept_timeout=intval;
          }
          else
          {
            write_log(LOG_WARNING, "Invalid value for accept_timeout - should be between 1 and 60 instead of %d - will use %d", intval, opts.accept_timeout);
          }
        }

      }
    }
  }
  else
  {
    write_log(LOG_INFO, "Persistent properties file %s not read.", prop_file);
  }
}







// See if this pathame is already exists.  If it is *not* a directory, punt.  If it doesn't
// exist, try and create it.
void mkdirComponent(char *pathname)
{
  struct stat statbuf;
  int statret;

  // sanity check - if stat returns 0 it *exists* in some fashion - only throw an error if 
  // a piece is of the component is *not* a directory
  
  statret=stat(pathname,&statbuf);
  if ((statret == 0))
  {
    if (!S_ISDIR(statbuf.st_mode))
    {
     throw(SBDispatcher_Except(500,"Pathname component is not a directory."));
    }
    else
    {
      write_log(LOG_DEBUG,"Directory %s exists", pathname);
    }
  }
  else
  {
    // Ok, we don't exist.  Try and make it.
    write_log(LOG_INFO, "Attempting to create %s", pathname);
    if (mkdir(pathname,S_IRWXU))
    {
      {
        char errorstring_buffer[1024];
        ostringstream msg;
        msg << "Unable to create directory " << pathname << ":  " << strerror_r(errno, errorstring_buffer,sizeof(errorstring_buffer));
        throw(SBDispatcher_Except(500,msg.str().c_str()));
      }
    }
  }
}

void SB_make_full_path(const string targetpath)
{
  // some boilerplate against empty input
  //cout <<"Targetpath is <"<< targetpath << ">" <<endl;

  if (targetpath.empty()) throw(SBDispatcher_Except(500,"No directory name given to create"));
  if (targetpath[0]!='/') throw(SBDispatcher_Except(500,"Directory creation requires absolute pathname"));

    
  size_t lastSlash = targetpath.find_last_of('/');

  
  if (lastSlash == 0) 
  {
    throw(SBDispatcher_Except(500,"File system root is only directory component - assuming it exists"));  
  }
  // first things first, is it *already* a directory?  If so, we're done
  // yes, we're doing a c_str() twice, but we hit this code very infrequently
  
  struct stat statbuf;  
  char *dupStr = NULL;
  char *ptr = dupStr;
  char ptrOrig;
  int statret;
  string dirsOnly = targetpath.substr(0,lastSlash);
  

  // See if it is *already* a directory.  If so, we're done and do not need 
  // process the string any further.  Otherwise explicitly  duplicate the
  // string and process

  statret=stat(dirsOnly.c_str(),&statbuf);
  if ((statret == 0 ) && (S_ISDIR(statbuf.st_mode))) 
  {
    write_log(LOG_INFO,"Directory path %s already exists", dirsOnly.c_str());
    dupStr = NULL;
  } 
  else
  {
    dupStr = strdup(dirsOnly.c_str());
    if (!dupStr) 
    {
      throw(SBDispatcher_Except(500,"Unable to process pathstring to ensure directories exist."));
    }
  }
  ptr = dupStr;
  while (ptr && *ptr)
  {
    // keep going until we find a '/'
    while (*ptr && *ptr != '/') ptr++; 
    // swallow *repeated* slashed
    while (*ptr && *ptr == '/') ptr++;

    // ok, we're at either end-of-string or a slash.  So remember which and 
    // set this character to null so we have a null-terminated string
    ptrOrig = *ptr;
    *ptr = '\0';
    
    // Check status and create if needed, or toss an exception    
    mkdirComponent(dupStr);
    // return the character to the original state so we can continue
    *ptr = ptrOrig;
    
  }  
  // clean up if we need to
  if (dupStr) free(dupStr);

}


#if 0

/* Given a pathname, try to create a full path to said file.  From the last '/' to the end of the string is
   assumed to be a filename, and is ignored 
   *ALL* created directories are assumed to have */
void SB_make_full_path(const string targetpath)
{
  char *working;
  char *ptr,*ptr_next;
  
  try
  { 
    write_log(LOG_INFO,"Verifying full path exists to %s",targetpath.c_str());

    /* do some preliminary checks ... */
    if (targetpath.empty()) throw(SBDispatcher_Except(500,"No directory name given to create"));
    if (targetpath[0]!='/') throw(SBDispatcher_Except(500,"Directory creation requires absolute pathname"));
    working=strdup(targetpath.c_str());
    if (working==NULL) throw(SBDispatcher_Except(500,"Unable to allocate memory for directory duplication"));
    ptr=strrchr(working,'/');
    
    // Find the last '/', and terminate the string right after that - *UNLESS* that slash
    // is the first character.
    if ( (ptr != NULL) && (ptr!=working) && (*(ptr+1)!='\0')) *ptr='\0';
    struct stat statbuf;
    int statret;
    statret=stat(working,&statbuf);
    if ( (statret==0) && (S_ISDIR(statbuf.st_mode))) goto done;
    string errorstring=strerror(errno);
    if ((errno != ENOENT) && (errno!=ENOTDIR))  throw(SBDispatcher_Except(500,"Unable to create directory "+targetpath+": "+errorstring));
    /* ok, start walking the string from the back to see if we can make it ... */
    
    ptr=working+1; 
    ptr_next=ptr+1;
//    cout <<"Working to create the following path  : <"<<ptr<<">"<<endl;
    while (*ptr!='\0')
    {
      char save;
      if ( ((*ptr=='/') && (*ptr_next!='/')) || 
           (*(ptr+1)=='\0') ) 
      {
        save=*ptr;
        if (*ptr=='/')
        {
             *ptr='\0';
           }
//        cout <<"Working= "<<working<<endl;
           errno-0;

           if (mkdir(working,S_IRWXU))
           {
//             cout<<"  errno="<<errno<<" "<<strerror(errno)<<endl;
             if (errno==EEXIST) 
             {
               int statret=stat(working,&statbuf);
               if ((statret==0) && (!S_ISDIR(statbuf.st_mode)))
               {
                 throw(SBDispatcher_Except(500,"Unable to create directory "+targetpath+", "+working+" exists and is not a directory"));
               }
             }           
             else 
             {
               errorstring=strerror(errno);
               throw(SBDispatcher_Except(500,"Unable to create directory "+targetpath+":  "+errorstring));
             }
           }
           *ptr=save;
      }
      ptr++; 
      ptr_next++;
    }
  }
  catch (SBDispatcher_Except & exc)
  {
    if (working) free(working);  // gotta cleanup our scratch space...
    throw;
  }
done:
  if (working) free(working); 
}

#endif
string ShowAsTwelveHourClock(int hour)
{
  ostringstream hourstr;
  if (hour > 12)
  {
    hourstr << (hour-12) << "PM" ;
  }
  else
  {
    hourstr << hour << "AM";
  }  
  return hourstr.str();
}


/* If start_time and end_time are greater than zero, they represent the start/end of core business
 * hours, where no 'costly' actions (scan/apply/undo/baseline/ClientUpdate) should be performed.
 * So return True is we're inside core hours.  Note two cases - one where start is before end, and
 * one where end is before start.
*/
bool insideCoreHours(int hour)
{
  bool is_allowed = true;

  if ((disp_opts.start_time >=0 ) && (disp_opts.end_time >=0 ))
  {
    if (disp_opts.start_time<disp_opts.end_time)    // IE start=8 and end = 16  for 8am to 4pm (core is during day)
    { 
      if ((disp_opts.start_time < hour) && (disp_opts.end_time > hour))    
      {
        is_allowed=false;
      }
    }
    else                                           // IE start=16 and end = 8  for 4pm to 8am (core is at night)
    { 
      if ((disp_opts.start_time > hour) && (disp_opts.end_time < hour))    
      {
        is_allowed=false;
      }
    }
  }
  
//  cout <<"S:" << disp_opts.start_time <<" E:"<<disp_opts.end_time<< " NOW:" << hour<< " ---> is_allowed: "<<is_allowed<<endl;

  return is_allowed;
}




/*
 * Functions to Encrypt & Decrypt a passphrase in AES 256 CBC to/from
 * a dedicated file (KEYSTORE_FILE)
 *
 * Function to retrieve a default key to decrypt/encrypted only
 * known to the vendor. get_key().
 *
 * simple_prompt
 *
 * Generalized function especially intended for reading in passwords
 * Reads from /dev/tty or stdin/stderr.
 *
 * prompt:             The prompt to print
 * maxlen:             How many characters to accept
 * echo:               Set to 0 if you want to hide what is entered (for passwords)
 *
 * Returns a malloc()'ed string with the input (w/o trailing newline).
 */

#include <termios.h>

char *
simple_prompt (const char *prompt, int maxlen, int echo)
{
  int length;
  char *destination;
  FILE *termin, *termout;

  struct termios t_orig, t;

  destination = (char *) malloc (maxlen + 2);
  if (!destination)
    return NULL;

  termin = fopen ("/dev/tty", "r");
  if (!termin)
    {
      termin = stdin;
    }

  termout = fopen ("/dev/tty", "w");
  if (!termout)
    {
      termout = stderr;
    }

  if (!echo)
    {
      tcgetattr (fileno (termin), &t);
      t_orig = t;
      t.c_lflag &= ~ECHO;
      tcsetattr (fileno (termin), TCSAFLUSH, &t);
    }

  if (prompt)
    {
      fputs ("\n", termout);
      fputs (prompt, termout);
      fflush (termout);
    }

  if (fgets (destination, maxlen, termin) == NULL)
    destination[0] = '\0';

  length = strlen (destination);
  if (length > 0 && destination[length - 1] != '\n')
    {
      /* eat rest of the line */
      char buf[128];
      int buflen;

      do
        {
          if (fgets (buf, sizeof (buf), termin) == NULL)
            break;
          buflen = strlen (buf);
        }
      while (buflen > 0 && buf[buflen - 1] != '\n');
    }

  if (length > 0 && destination[length - 1] == '\n')
    /* remove trailing newline */
    destination[length - 1] = '\0';

  if (!echo)
    {
      tcsetattr (fileno (termin), TCSAFLUSH, &t_orig);
      fputs ("\n", termout);
      fflush (termout);
    }

  if (termin != stdin)
    {
      fclose (termin);
      termin = NULL;
    }
  if (termout != stdout)
    {
      fclose (termout);
      termout = NULL;
    }

  return destination;
}



