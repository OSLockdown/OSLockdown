/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*
*/

#include <iostream>
#include <pthread.h>
#include <sstream>
#include <fstream>
#include <vector>
#include <cstdio>
#include <cstring>

#include <sys/types.h>
#include <sys/stat.h>

#include <unistd.h>
#include <getopt.h>
#include <signal.h>
#include <sys/wait.h>
#include <openssl/engine.h>

#ifdef SOLARIS
#include <sys/loadavg.h>

// Solaris requires the 'KERNEL' preprocessor to pick this up, so we're just
// going to define it here.
#define s6_addr32 _S6_un._S6_u32
#endif

#include "version.h"
#include "sbprops.h"
#include "SB_Dispatcher_Utils.h"
#include "SB_Info.h"
#include "SB_Status.h"
#include "SB_Tasks.h"
#include "SB_Update.h"
#include "sub_proc.h"

#include "soapAgentServiceImplPortBindingService.h"
#include "soapAgentServiceImplPortBindingProxy.h"
#include "AgentServiceImplPortBinding.nsmap"

#define IF_NOT_NULL(x) (x!=NULL)?x:"(nil)"

using namespace std;

static bool have_scheduler=true;

static bool force_exit=false;
static SB_ACTION *SB_current_action=NULL;
static SB_ACTION_ENUM SB_current_action_enum;
static SB_ACTION *SB_pending_action=NULL;
static SB_ACTION *SB_pending_autoupdate=NULL;
static bool AgentUpdateRequested = false; 
static pthread_mutex_t SB_mutex=PTHREAD_MUTEX_INITIALIZER;

// some forward defs
static bool SB_try_tasking(SB_ACTION* action);
static void SB_finished();
static void *SB_task_manager(void*);
static bool must_exit();
static void trigger_shutdown();
static void *SB_inbound_comms_thread(void *);
static void tweak_sigmask(int sig, int how);

extern bool SB_Integrity(bool integrity_check);
extern void get_file_sha1(const char *filename, char charbuffer[145]);
extern char *get_buffer_sha1(char *, size_t);

// forward def
char * get_full_file(struct soap*,const string, const string,string &, int maxsizeMB);
static int have_pid=-1;
// We can modify the following, so make our own copies on startup


string MY_APPLICATION_ASSESSMENTS       = APPLICATION_ASSESSMENTS"/";       //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_APPLY_REPORTS     = APPLICATION_APPLY_REPORTS"/";     //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_UNDO_REPORTS      = APPLICATION_UNDO_REPORTS"/";      //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_BASELINES         = APPLICATION_BASELINES"/";         //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_ASSESSMENT_COMPS  = APPLICATION_ASSESSMENT_COMPS"/";  //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_BASELINE_COMPS    = APPLICATION_BASELINE_COMPS"/";    //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_SSL_CERTS         = APPLICATION_SSL_CERTS;
string MY_APPLICATION_TASKS             = APPLICATION_TASKS"/";      //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_ENTERPRISE_HIDDEN = APPLICATION_DATA"/profiles/.enterprise/";      //append a trailing '/' for the SB_make_full_path command
string MY_APPLICATION_DISPATCHER_LOG    = APPLICATION_DISPATCHER_LOG; 

DISPATCHER_OPTS disp_opts;


#define Default_200 "Ok"
#define Default_409 "Busy, try again later please"
#define Default_500 "Internal error"

int ssl_server_flags=0; 
int ssl_client_flags=0;
char *ssl_server_my_cert=NULL;
char *ssl_server_ca_cert=NULL;
char *ssl_client_my_cert=NULL;
char *ssl_my_pass=NULL;
char *ssl_ca_path=NULL;
char *ssl_dh_file=NULL;
char *ssl_random_file=NULL;
char *ssl_cachename=NULL;
string conn_ip_addr;

/* 
   only say something as commentary (msg starts with ::) if we're
   running as a shim - so the shimGUI can show it succinctly
 */
void
SB_shim_commentary(int level, string message)
{
  if (!disp_opts.shim_name.empty())
  {
    ostringstream msg;
    msg <<  ":::" << level << ":::"<< message.c_str() <<endl;
    cout<<msg.str().c_str()<<endl;
  }
}
void
SB_remove_pid_file()
{
  unlink(APPLICATION_PID_FILE);
}

string
GetActionText(SB_ACTION_ENUM action_enum)
{
  if (action_enum>=0 && action_enum<SB_TASK_LAST_ACTION)
  {
    return SB_ACTION_TEXT[action_enum];
  }
  else
  {
    return SB_ACTION_TEXT[SB_TASK_COMPLETED];
  }
}

SB_ACTION_ENUM
GetActionEnum(char action_char)
{
  SB_ACTION_ENUM action_enum=SB_TASK_COMPLETED;

  switch (action_char)
  {
    case 'S': action_enum=SB_SCAN; break;
    case 'Q': action_enum=SB_QSCAN; break;
    case 'A': action_enum=SB_APPLY; break;
    case 'U': action_enum=SB_UNDO; break;
    case 'B': action_enum=SB_BASELINE; break;
    case 's': action_enum=SB_SCHEDULED_SCAN; break;
    case 'q': action_enum=SB_SCHEDULED_QSCAN; break;
    case 'a': action_enum=SB_SCHEDULED_APPLY; break;
    case 'b': action_enum=SB_SCHEDULED_BASELINE; break;
    case '*': action_enum=SB_AUTOUPDATE_CLIENT ; break;
    default: throw (SBDispatcher_Except(500,"Unable to recognize requested action - aborting"));
        break;
  }
  return action_enum;
}


void 
get_connection_address(struct soap *soap,string &conn_str)
{
  ostringstream message;
  ostringstream ip_stream;

  socklen_t len;
  struct sockaddr_storage addr;
  char ipstr[INET6_ADDRSTRLEN+1];
  int port;
  string prefix="";
  string postfix="";
  int ret;
  
  len = sizeof addr;
  ret = getpeername(soap->socket, (struct sockaddr*)&addr, &len);
  // deal with both IPv4 and IPv6:
  
  if (addr.ss_family == AF_INET) {
      struct sockaddr_in *s4 = (struct sockaddr_in *)&addr;
      port = ntohs(s4->sin_port);
      if (!inet_ntop(AF_INET, &s4->sin_addr, ipstr, INET_ADDRSTRLEN))
      {
//        cout << "inet_ntop = " << errno << endl;
      }
  } else { // AF_INET6
      struct sockaddr_in6 *s6 = (struct sockaddr_in6 *)&addr;
      if (IN6_IS_ADDR_V4MAPPED(&s6->sin6_addr))
      {
        struct sockaddr_in s4;
        memset(&s4,0,sizeof(s4));
        s4.sin_family = AF_INET;
        s4.sin_port = s6->sin6_port;
        s4.sin_addr.s_addr = s6->sin6_addr.s6_addr32[3];
        port = ntohs(s6->sin6_port);
        if (!inet_ntop(AF_INET, &s4.sin_addr, ipstr, INET6_ADDRSTRLEN))
        {
//            cout << "inet_ntop = " << errno << endl;
        }
        
      } else {
        prefix="[";
        postfix="]";
        port = ntohs(s6->sin6_port);
        if (! inet_ntop(AF_INET6, &s6->sin6_addr, ipstr, INET6_ADDRSTRLEN)) 
        {
//            cout << "inet_ntop = " << errno << endl;
        }
      }
  }

  
  conn_str = prefix+ipstr+postfix;  

  message << "connection from IP " << conn_str << " port "<< port;
  write_log(LOG_INFO,"%s",message.str().c_str());
  
}
  
static void
SB_finished(string transactionid)
{
  pthread_mutex_lock(&SB_mutex);
  if (SB_current_action && (SB_current_action->m_transid==transactionid))
  {
    delete SB_current_action;
    SB_current_action=NULL;
    SB_current_action_enum=SB_TASK_COMPLETED;
    TaskList->ReSubmitTask(transactionid);
  }

  pthread_mutex_unlock(&SB_mutex);
}

// returns true if OSLockdown is NOT busy (ie - not scan/apply/undo/baseline) and sets the busy flag
// False otherwise

static bool
SB_try_tasking(SB_ACTION *action)
{
  bool retval=false;
  pthread_mutex_lock(&SB_mutex);
  if (SB_current_action==NULL) 
  {
    if (action)
    {
      SB_current_action=action;
    }
  }
  pthread_mutex_unlock(&SB_mutex);
  return retval;  
}  

static bool must_exit()
{
  bool retval;
  pthread_mutex_lock(&SB_mutex);
  retval=force_exit;
  pthread_mutex_unlock(&SB_mutex);
  return retval;  
}

static void trigger_shutdown()
{
  pthread_mutex_lock(&SB_mutex);
  force_exit=true;
  pthread_mutex_unlock(&SB_mutex);
  write_log(LOG_INFO,"Shutdown commencing..");
}

static void reset_shutdown_trigger()
{
  pthread_mutex_lock(&SB_mutex);
  force_exit=false;
  pthread_mutex_unlock(&SB_mutex);
}


static void tweak_sigmask(int sig, int how)
{
  sigset_t signal_set;
  
  sigemptyset(&signal_set);
  sigaddset(&signal_set,sig);
  pthread_sigmask(how,&signal_set,NULL);
}

string nowInCoreHours(bool is_from_console)
{
  string retStr = "";
  if ((disp_opts.start_time>=0) && (disp_opts.end_time>=0))
  {
    struct timeval tv;
    struct tm tm, *tmptr;
    bool is_allowed = true; 
    gettimeofday(&tv,NULL);
    tmptr = localtime_r(&tv.tv_sec,&tm);

    if (tmptr) 
    {
      int localHour = tm.tm_hour;
      is_allowed = insideCoreHours(localHour);
      if (!is_allowed)
      {
        ostringstream msg;
        msg <<"Currently inside core business hours ";
        msg << "(hours are between "<<ShowAsTwelveHourClock(disp_opts.start_time) << " and "<< ShowAsTwelveHourClock(disp_opts.end_time) <<").  " ;
        if (is_from_console)
        {
          msg << "Please try again later.";
        }
        else
        {
          msg << "Task being resubmitted to try again at next schedule time.";
        }
        retStr = msg.str();
      }
    }
  }
  return retStr;
}

string machineTooBusy(bool is_from_console)
{
  string retStr = "";
  
  // Check if loading it too high
  if (disp_opts.max_load!=0)
  {
    double loadavgs[3];
    if (getloadavg(loadavgs,3)!=3)
    {
      write_log(LOG_WARNING,"Unable to get current load average, operation will be allowed");
      loadavgs[1]=disp_opts.max_load;
    }
//    cout <<"loadavgs[1]="<<loadavgs[1]<<"   disp_opts.max_load="<< disp_opts.max_load <<endl;
    if (loadavgs[1]>disp_opts.max_load)
    {
      int tval;
      double tval2;
      tval=int(loadavgs[2]*100.0);
      tval2=tval/100.0;
      ostringstream msg;
      msg <<"Machine 5 minute load average ("<<tval2<<") is above maximum load of "<<disp_opts.max_load<<".  ";
      if (is_from_console)
      {
        msg << "Please try again later.";
      }
      else
      {
        msg << "Task being resubmitted to try again at next schedule time.";
      }
      retStr = msg.str();
    }
  }
  return retStr;
}

static void process_profile(char *rawprofilestring, string&profile_path, string profile_name)
{
  size_t shortlength;
  
  shortlength=min(size_t(30),strlen(rawprofilestring));
  
  string substring (rawprofilestring,shortlength);
  write_log(LOG_DEBUG,"profilepath(%d) : %s",(int)shortlength,substring.c_str());
  
  if ((strncasecmp(rawprofilestring,"<profile "        ,9 )!=0) && 
      (strncasecmp(rawprofilestring,"<baselineprofile ",17)!=0) &&
      (strncmp(rawprofilestring,    "<?xml "           ,6 )!=0))
  {
    // assume we've been given the name of the profile
    profile_path=rawprofilestring;
    if (access(profile_path.c_str(),R_OK)!=0)
    {
      // no such file, perhaps we got the contents instead, so limit our output if needed
      if (profile_path.length()>100) profile_path=profile_path.substr(0,100)+"...";
      throw (SBDispatcher_Except(500,"No such profile name found : "+profile_path));
    }
  }
  else
  {    
    ostringstream tpath;

    // use a hidden name so standalone GUI won't see it, unless we're a shim, then write to the shim directory
    tpath<<"/var/lib/oslockdown";
    if (disp_opts.shim_name.empty())  tpath<<"/profiles/.enterprise"; 
    else                    tpath<<"/reports/shim/" << disp_opts.shim_name ;
    
    tpath << profile_name;
    profile_path = tpath.str();
    SB_make_full_path(profile_path);
    ofstream profilestream;
    profilestream.open(profile_path.c_str(),(ios_base::trunc|ios_base::out));
    if (profilestream.is_open())
    {
      profilestream<<rawprofilestring;
      profilestream.close();
      if (profilestream.fail())
      {
        throw (SBDispatcher_Except(500,"Unable to save profile data to disk"));
      }
    }
    else
    {
      throw (SBDispatcher_Except(500,"Unable to save profile data to disk"));
    }
  }
  write_log(LOG_DEBUG,"profilepath : %s",profile_path.c_str());
}


void SB_process_cmd_line_args(int argc, char *argv[])
{
  int c;
  int intarg;
  int longIndex;
  double dval;
  static const struct option longOpts[] = {
    {"recv_timeout", required_argument, NULL, 0},
    {"send_timeout", required_argument, NULL, 0},
    {"accept_timeout", required_argument, NULL, 0},
  };  
  // Note the following are for development only
  // -z <name>
  // -o 
  // -H 
//  while ((c = getopt (argc, argv, "Sv:A:ia:l:p:T:s:e:oz:HL:")) != -1)
  
  write_log(LOG_NOTICE, "Processing command line arguments");
   
  while ((c = getopt_long (argc, argv, "SvA:ia:l:p:T:s:e:oz:HL:", longOpts, &longIndex)) != -1)
  {
    switch (c)
    {
      case 'L':
        intarg=atoi(optarg);
          if ((intarg>=0) && (intarg<512) && (intarg != disp_opts.max_log_MB))
        {
          write_log(LOG_NOTICE, "Redefining maximum allowed log transfer size (in MB)  from %d  to %d",disp_opts.max_log_MB, intarg);
          disp_opts.max_log_MB = intarg;
        }
        break;
      case 'H':
        disp_opts.skip_host=false;
        break;
      case 'z':
        disp_opts.shim_name=optarg;
        break;
      case 'S':
        disp_opts.use_https=false;
        break;
      case 'o':
        disp_opts.daemonize=false;
        log_to_stderr=true;
        break;
      case 'p': 
        intarg=atoi(optarg);
        write_log(LOG_NOTICE, "Redefining port from %d  to %d",disp_opts.port, intarg);
        disp_opts.port=intarg;
        break;
      case 'v':
        disp_opts.verbose=true;
        break;
      case 'l':
        intarg=atoi(optarg);
        if ((intarg>=LOG_EMERG) && (intarg<=LOG_DEBUG))
        {
          disp_opts.loglevel=intarg;
        }
        break;
      case 'i':
        disp_opts.integrity_check=false;
        break;
      case 'T':
        dval=atof(optarg);
        if (dval>0.0) 
        {
          disp_opts.max_load=dval;
        }
        break;
      case 's':
        intarg=atoi(optarg);
        if ( (intarg>=0) && (intarg<24) )
        {
          disp_opts.start_time=intarg;
        }
        break;
      case 'e':
        intarg=atoi(optarg);
        if ( (intarg>=0) && (intarg<24) )
        {
          disp_opts.end_time=intarg;
        }
        break;
      case 'A':
        disp_opts.address=optarg;
        break;
      case 'a':
        disp_opts.ciphers=optarg;
        break;
      case 'C':
        disp_opts.commonname=optarg;
        break;
      case 0:  /* long option - so strncmp required - note we're assuming that arguments *are* valid strings (NULL terminated) */
        if (strcmp("accept_timeout", longOpts[longIndex].name) == 0 )
        {
          intarg=atoi(optarg);
          if ((intarg >2) && (intarg < 60))
          {
            write_log(LOG_NOTICE, "Redefining 'accept_timeout' from %d seconds to %d seconds",disp_opts.accept_timeout, intarg);
            disp_opts.accept_timeout = intarg;
          }
        }
        else if (strcmp("recv_timeout", longOpts[longIndex].name) == 0 )
        {
          intarg=atoi(optarg);
          if ((intarg >2) && (intarg < 60))
          {
            write_log(LOG_NOTICE, "Redefining 'recv_timeout' from %d seconds to %d seconds",disp_opts.recv_timeout, intarg);
            disp_opts.recv_timeout = intarg;
          }
        }
        else if (strcmp("send_timeout", longOpts[longIndex].name) == 0 )
        {
          intarg=atoi(optarg);
          if ((intarg >2) && (intarg < 60))
          {
            write_log(LOG_NOTICE, "Redefining 'send_timeout' from %d seconds to %d seconds",disp_opts.send_timeout, intarg);
            disp_opts.send_timeout = intarg;
          }
        }
        else
        {
            write_log(LOG_WARNING,"Option BUMPLYBURG");
            break;
        }
	break;
      default:
        write_log(LOG_WARNING,"Option '%c' not implemented.",(char)c);
        break;
    }
  }
}


void * SB_inbound_comms_thread(void *arg)
{
  int c;
  int backlog=100;
  ostringstream message;
  SOAP_SOCKET in_sock;

  write_log(LOG_INFO,"Inbound Communication manager startup...");
  SB_shim_commentary(LOG_INFO,"Startup...");
#ifdef DEBUG
  soap_set_recv_logfile(&Agent,"SERVER_RECV.LOG");
  soap_set_sent_logfile(&Agent,"SERVER_SENT.LOG");
  soap_set_test_logfile(&Agent,"SERVER_TEST.LOG");
#endif

  AgentServiceImplPortBindingService Agent;
  
  soap_set_imode(&Agent, SOAP_C_UTFSTRING);
  soap_set_omode(&Agent, SOAP_C_UTFSTRING);
  Agent.bind_flags |= SO_REUSEADDR;
  Agent.accept_timeout=disp_opts.accept_timeout;
  Agent.recv_timeout=disp_opts.recv_timeout;
  Agent.send_timeout=disp_opts.send_timeout;

  if (disp_opts.use_https)
  {
    // Note that we set both server and client flags here, all flags are global 
    ssl_server_my_cert = strdup(string(MY_APPLICATION_SSL_CERTS+"/Disp.pem").c_str());
    ssl_server_ca_cert = strdup(string(MY_APPLICATION_SSL_CERTS+"/cacert.pem").c_str());
    ssl_ca_path = NULL;
//    ssl_dh_file = "dh2048.pem";
    ssl_dh_file = NULL;
    ssl_random_file = NULL;
    ssl_cachename = (char *)arg;
    
    ssl_server_flags = (SOAP_SSL_REQUIRE_SERVER_AUTHENTICATION | SOAP_TLSv1 | SOAP_SSL_REQUIRE_CLIENT_AUTHENTICATION);
    ssl_client_flags = (SOAP_SSL_REQUIRE_SERVER_AUTHENTICATION | SOAP_TLSv1 );
    if (disp_opts.skip_host)
    {
      ssl_server_flags |= SOAP_SSL_SKIP_HOST_CHECK;
      ssl_client_flags |= SOAP_SSL_SKIP_HOST_CHECK;
    }
    ssl_client_my_cert = NULL;

/*
    printf("ssl_server_flags   = %d\n" ,ssl_server_flags);
    printf("ssl_server_my_cert = %s\n" ,IF_NOT_NULL(ssl_server_my_cert));
    printf("ssl_my_pass        = %s\n" ,IF_NOT_NULL(ssl_my_pass));
    printf("ssl_server_ca_cert = %s\n" ,IF_NOT_NULL(ssl_server_ca_cert));
    printf("ssl_ca_path        = %s\n" ,IF_NOT_NULL(ssl_ca_path));
    printf("ssl_dh_file        = %s\n" ,IF_NOT_NULL(ssl_dh_file));
    printf("ssl_random_file    = %s\n" ,IF_NOT_NULL(ssl_random_file));
    printf("ssl_cachename      = %s\n" ,IF_NOT_NULL(ssl_cachename));
*/
    if (soap_ssl_server_context(&Agent,ssl_server_flags,ssl_server_my_cert,ssl_my_pass,ssl_server_ca_cert,ssl_ca_path,
                                 ssl_dh_file,ssl_random_file,ssl_cachename))
    {
      Agent.soap_stream_fault(message);
      write_log(LOG_ERR,"%s",message.str().c_str());
      exit(1);
    }
  }
  
  if (disp_opts.address.empty())
  {
    write_log(LOG_INFO,"Attempting to bind to all address at port %d",disp_opts.port);
    in_sock=Agent.bind(NULL,disp_opts.port, backlog);
  }
  else
  {
    write_log(LOG_INFO,"Attempting to bind to address %s at port %d",disp_opts.address.c_str(),disp_opts.port);
    in_sock=Agent.bind(disp_opts.address.c_str(),disp_opts.port, backlog);
  }
  write_log(LOG_DEBUG,"Inbound socket address is %d",in_sock);
  if (!soap_valid_socket(in_sock))
  {
    Agent.soap_stream_fault(message);
    write_log(LOG_ERR,"SB_Dispatcher SOAP socket failure: %s",message.str().c_str());
    exit(1);
  } 
  // Mark this socket to be closed on execs....
  fcntl(in_sock,F_SETFD, FD_CLOEXEC);
  write_log(LOG_INFO,"SB_Dispatcher listening to port %d",disp_opts.port);

  SB_shim_commentary(LOG_INFO,"Waiting...");
  while (!must_exit())
  {
    SOAP_SOCKET s= Agent.accept();
    if (!soap_valid_socket(s))
    { 
      if (Agent.errnum)
      {
        message.str("");
        Agent.soap_stream_fault(message);
        write_log(LOG_ERR,"SOAP Accept failure: %s",message.str().c_str());
        SB_shim_commentary(LOG_ERR,"Connect Failure");
        break;
      }
      else
      {
        continue;
      }
    }
    else
    { 
      fcntl(s,F_SETFD, FD_CLOEXEC);
      write_log(LOG_DEBUG,"Accepting inbound request...");
      
      if (disp_opts.use_https)
      {
        if (soap_ssl_accept(&Agent))
        {
          message.str("");
          Agent.soap_stream_fault(message);
          write_log(LOG_ERR,"SSL Accept failure: %s",message.str().c_str());
          SB_shim_commentary(LOG_ERR,"Accept Failed");
          continue;
        }
        else
        {
          write_log(LOG_INFO,"SSL Accept succeeded");
        }
      }
      Agent.serve();  // Serve the request, if it is 'long term' then the service routine will deal with
                     // keeping track of things...
      write_log(LOG_DEBUG,"Request dispatched, waiting for next request...");
    }
  } 
  Agent.destroy();
  write_log(LOG_INFO,"Inbound Communication manager exiting...");
  pthread_detach(pthread_self());
  return 0;    

}

int main(int argc,char *argv[])
{
  pthread_t soap_thread;
  pthread_t inbound_comms_thread, task_manager_thread;
  int c;
  ostringstream message;
  bool soft_restart = false;
  struct timespec waittime={1,0}; // a one-second wait
  int signum;
  sigset_t signal_set;
  
  // Top level try block to catch anything that is thrown.  We'll catch SB_Exceptions, then any other Exception...

  try
  {
    tzset();
    init_disp_opts(disp_opts);
    // quickly zip through cmd line to see if we're daemonizing ourselves.  If *NOT* then ensure that messages are displayed to stdout also
    for (size_t i=1; i<argc ; i++)
    {
      if (strncmp (argv[i],"-o",2)==0)
      {
        log_to_stderr=true;
      }
    } 
    read_dispatcher_properties(disp_opts);
    SB_process_cmd_line_args(argc,argv);

    if (disp_opts.use_https)
    {
      CRYPTO_thread_setup();
      soap_ssl_init();
      write_log(LOG_INFO,"Dispatcher deployed to expect HTTPS connections on port %d",disp_opts.port);
      ssl_my_pass = password_cb("Dispatcher PEM private passphrase:");
    }
    else
    {
      write_log(LOG_INFO,"Dispatcher deployed to expect HTTP connections on port %d",disp_opts.port);
    }
    OpenSSL_add_all_algorithms();
    if (!disp_opts.shim_name.empty())
    {  
      write_log(LOG_INFO," SHIM MODE - shim target is %s",disp_opts.shim_name.c_str());
      write_log(LOG_INFO,"   Creating directories for shim reports...");
      string shimstr=string("shim/")+disp_opts.shim_name;
      string target="standalone";

      search_replace(MY_APPLICATION_ASSESSMENTS,target,shimstr);
      search_replace(MY_APPLICATION_APPLY_REPORTS,target,shimstr);
      search_replace(MY_APPLICATION_UNDO_REPORTS,target,shimstr);
      search_replace(MY_APPLICATION_BASELINES,target,shimstr);
      search_replace(MY_APPLICATION_ASSESSMENT_COMPS,target,shimstr);
      search_replace(MY_APPLICATION_BASELINE_COMPS,target,shimstr);
      search_replace(MY_APPLICATION_TASKS,target,shimstr);
      shimstr=string("dispatcher_")+disp_opts.shim_name;
      target="dispatcher";
      search_replace(MY_APPLICATION_DISPATCHER_LOG,target,shimstr);
//      cout <<"DISPATCHER LOG FILES GOING TO "<<MY_APPLICATION_DISPATCHER_LOG<<endl;
    }

// These *should* all exists, but just in case....
    SB_make_full_path(MY_APPLICATION_ASSESSMENTS);
    SB_make_full_path(MY_APPLICATION_APPLY_REPORTS);
    SB_make_full_path(MY_APPLICATION_UNDO_REPORTS);
    SB_make_full_path(MY_APPLICATION_BASELINES);
    SB_make_full_path(MY_APPLICATION_ASSESSMENT_COMPS);
    SB_make_full_path(MY_APPLICATION_BASELINE_COMPS);
    SB_make_full_path(MY_APPLICATION_TASKS);
    write_log(LOG_INFO,  "Task files stored in       : %s",MY_APPLICATION_ASSESSMENTS.c_str());

    write_log(LOG_INFO,"Assessment reports in      : %s",MY_APPLICATION_ASSESSMENTS.c_str());
    write_log(LOG_INFO,"Apply reports in           : %s",MY_APPLICATION_APPLY_REPORTS.c_str());
    write_log(LOG_INFO,"Undo reports in            : %s",MY_APPLICATION_UNDO_REPORTS.c_str());
    write_log(LOG_INFO,"Baseline reports in        : %s",MY_APPLICATION_BASELINES.c_str());
    write_log(LOG_INFO,"Assessment comp reports in : %s",MY_APPLICATION_ASSESSMENT_COMPS.c_str());
    write_log(LOG_INFO,"Baseline comp reports in   : %s",MY_APPLICATION_BASELINE_COMPS.c_str());
    setlogmask(LOG_UPTO(disp_opts.loglevel));
    write_log(LOG_INFO,"SB_Dispatcher process start, loglevel set to %d",disp_opts.loglevel);
  
//   block the async signals we might need , sigint, sigusr1, sigusr2
    tweak_sigmask(SIGINT,SIG_BLOCK);  
    tweak_sigmask(SIGTERM,SIG_BLOCK);
    tweak_sigmask(SIGUSR1,SIG_BLOCK);  
    tweak_sigmask(SIGUSR2,SIG_BLOCK);  
    tweak_sigmask(SIGPIPE,SIG_BLOCK);  


    if (disp_opts.shim_name.empty() && SB_Integrity(disp_opts.integrity_check) && disp_opts.daemonize  )
    {
      have_pid=SB_Daemonize();
    }
    atexit(SB_remove_pid_file);

    TaskListInit(MY_APPLICATION_TASKS);
    if (have_scheduler)
    {
      SB_make_full_path(MY_APPLICATION_TASKS);
      ReadTaskFiles();
    }

  
    sigemptyset(&signal_set);
    sigaddset(&signal_set,SIGINT);
    sigaddset(&signal_set,SIGTERM);
    sigaddset(&signal_set,SIGUSR1);
    sigaddset(&signal_set,SIGUSR2);
    sigaddset(&signal_set,SIGPIPE);

    do 
    {
      reset_shutdown_trigger();
      if (soft_restart) 
      {
        write_log(LOG_INFO,"Soft restart of Dispatcher commencing");
        soft_restart = false;
      }
      if (pthread_create(&task_manager_thread,NULL,SB_task_manager,NULL))
      {
        throw (SBDispatcher_Except(500,"Unable to spawn task manager thread"));
      }
      if (pthread_create(&inbound_comms_thread,NULL,SB_inbound_comms_thread,argv[0]))
      {
        throw (SBDispatcher_Except(500,"Unable to spawn inbound comms thread"));
      }

      do  
      {
        if ((signum=sigtimedwait(&signal_set,NULL,&waittime))>0)
        {
          switch (signum)
          {
            case SIGINT:
              write_log(LOG_INFO,"SIGINT detected.");
              trigger_shutdown();
              write_log(LOG_INFO,"Shutdown initiated...");
              break;
            case SIGTERM:
              write_log(LOG_INFO,"SIGTERM detected.");
              trigger_shutdown();
              write_log(LOG_INFO,"Shutdown initiated...");
              break;
            case SIGUSR1:
              write_log(LOG_INFO,"Ignoring SIGUSR1...");
              break;
            case SIGUSR2:
              write_log(LOG_INFO,"Treating SIGUSR2 as soft reset trigger..");
              trigger_shutdown();
              soft_restart = true;
              break;
            case SIGPIPE:
              write_log(LOG_INFO,"Ignoring SIGPIPE...");
              break;
            default:
              write_log(LOG_INFO,"Ignoring signal %d...",signum);
              break;
          }
        }
      } while (!must_exit());

      write_log(LOG_INFO,"Thread shutdown delay for 3 seconds");

      sleep(3);
    } while (  soft_restart );
    
    write_log(LOG_INFO,"Continuing with full process shutdown.");
    
    TaskListCleanUp();
    if (disp_opts.use_https)
    {
      CRYPTO_thread_cleanup();
    }

    if (ssl_server_my_cert) free(ssl_server_my_cert);
    if (ssl_server_ca_cert) free(ssl_server_ca_cert);
    if (ssl_my_pass!=NULL) free(ssl_my_pass);

//   Engine cleanup
    ENGINE_cleanup();
    CONF_modules_unload(1);
    CRYPTO_cleanup_all_ex_data();
    ERR_free_strings();
    ERR_remove_state(0);
    EVP_cleanup();
  }

  catch (SBDispatcher_Except & exc)
  {
    cerr << "SB_Dispatcher exception: "<<exc.what()<<endl;
    write_log(LOG_ERR,"SB_Dispatcher exception: %s",exc.what());
    exit(1);
  }
  catch (exception &exc)
  {
    cerr <<"SB_Disspatcher general exception: "<<exc.what()<<endl;
    write_log(LOG_ERR,"SB_Dispatcher general exception: %s",exc.what());
    exit(1);
  }
  return 0;    

}

/* return true/false to execute task */
bool
VerifyTaskWithConsole(string &id, string &verifyaddr, char *security_fingerprint, string &security_newprofpath,
                            char *baseline_fingerprint, string &baseline_newprofpath,
                            string reply_to, string whofrom)
{
  AgentServiceImplPortBindingProxy Console;
  ns1__verifyTask vt;
  ns1__taskVerificationQuery query;
  ns1__verifyTaskResponse  response;
  ns1__taskVerificationResponse *vt_reply;
  int retval=SB_TASK_VALID;
  bool execute_task=true;  // assume task is valid unless determined otherwise
  ostringstream message;
  
  write_log(LOG_DEBUG,"Verifying task %s with console at %s",id.c_str(),verifyaddr.c_str());
  
  if (baseline_fingerprint) write_log(LOG_DEBUG,"Task profile baseline fingerprint is -> %s", baseline_fingerprint);
  else             write_log(LOG_DEBUG,"No baseline fingerprint file found");

  if (security_fingerprint) write_log(LOG_DEBUG,"Task profile security fingerprint is -> %s", security_fingerprint);
  else             write_log(LOG_DEBUG,"No security fingerprint file found");
  
  vt.query=&query;
  Console.soap_endpoint=verifyaddr.c_str();
  query.id=(char*)id.c_str();
  query.baselineProfileFingerprint=baseline_fingerprint;
  query.securityProfileFingerprint=security_fingerprint;
  if (disp_opts.use_https)
  {   
    if (soap_ssl_client_context(&Console,ssl_client_flags,ssl_client_my_cert,ssl_my_pass,ssl_server_ca_cert,ssl_ca_path,ssl_random_file))
    {
      Console.soap_stream_fault(message);
      throw (SBDispatcher_Except(500, message.str()));
//      write_log(LOG_ERR,"%s",message.str().c_str());
//      exit(1);
    }
  }
  if (Console.verifyTask(&vt,&response)==SOAP_OK)
  {
    vt_reply=response.return_;
    if (vt_reply->queryResultCode==SB_TASK_INVALID)
    {
      write_log(LOG_INFO, "Console does not recognize task %s, removing task",id.c_str());
      TaskList->remove_task(id);
      execute_task=false;
    }
    else
    {
      TaskList->update_task(vt_reply->task, (char*)reply_to.c_str(), (char*)verifyaddr.c_str(), whofrom );
      switch(vt_reply->queryResultCode)
      {
        case (SB_TASK_NOPROFILE):
          write_log(LOG_INFO, "Console does not have a profile associated with task %s, rescheduling",id.c_str());
          execute_task=false;
          break;
        case (SB_TASK_NEWPROFILE):
          write_log(LOG_INFO, "Console reports updated profile for task %s, saving new profile and executing task",id.c_str());
          if (vt_reply->task->baselineProfile)
          {
            process_profile(vt_reply->task->baselineProfile,baseline_newprofpath,"/default_baseline.xml");
          }
          if (vt_reply->task->securityProfile)
          {
            process_profile(vt_reply->task->securityProfile,security_newprofpath,"/default_security.xml");
          }

        case (SB_TASK_VALID):  // NOTE FALL THROUGH FROM ABOVE
          break;
        default:
          write_log(LOG_ERR,"Task Verify returned code %d ('%s') for %s, not executing.",
              vt_reply->queryResultCode,vt_reply->queryResultInfo,id.c_str());
          break;
      }
    }    
  }
  else
  {
    ostringstream message;
    Console.soap_stream_fault(message);
    write_log(LOG_ERR,"%s -> Unable to contact Console to verify, assuming valid: error -> %s",id.c_str(),message.str().c_str());
  }
  return execute_task;
}




static void *SB_invoke(void*);

// This section will need to be changed eventually - standalone will get an absolute path (as will scheduled tasks probably)
// Enterprise will be given the text of the profile, and will need to save this to a scratch file first.  If we hit a problem
// throw an exception with ns1__agentResponse

/*
  The Verify* routines will thrown an exception (SBDispatcher_Except) if they fail.
  The intent is that the catcher is the invoked SOAP server routine, and the error
  code and message will be returned to the SOAP remote caller process.
 */

void Verify_Task_Can_Be_Accepted(char action_char, vector<string> procinfo)
{
  bool is_idle=false;
  SB_ACTION_ENUM action_enum=SB_TASK_COMPLETED;
  string errStr;


  pthread_mutex_lock(&SB_mutex);

  if (SB_current_action!=NULL) 
  {
    action_enum=SB_current_action_enum;
  }
  else if (SB_pending_action!=NULL)
  {
    action_enum=GetActionEnum(SB_pending_action->m_action_chars[0]);
  }
  else
  {
    is_idle=true;
  }
  pthread_mutex_unlock(&SB_mutex);
//  cout <<"Idle status is "<<is_idle<<endl;
  if (!is_idle)
  {
    string reason=string("OSLockdown is already processing a Console ")+string(GetActionText(action_enum))+string(" request, please try again later...");
    throw (SBDispatcher_Except(409,reason));
  }
  
  // Check for possible incursion into forbidden time slots - if a non-empty string is returned then the string holds the text of the reason why we can't execute.
  errStr = nowInCoreHours(true);
  if (errStr != "")
  {
    throw (SBDispatcher_Except(409,errStr.c_str()));
  }

  // Check if loading it too high - if a non-empty string is returned then the string holds the text of the reason why we can't execute.
  errStr = machineTooBusy(true);
  if (errStr != "")
  {
    throw (SBDispatcher_Except(409,errStr.c_str()));
  }
}

void SB_submit_action(SB_ACTION *action, int &code, string &reason)
{
  code=200;
  reason=Default_200;
  
  pthread_mutex_lock(&SB_mutex);

  if (action -> m_action_chars == "*") 
  {
    if (SB_pending_autoupdate==NULL)
    {
      SB_pending_autoupdate=action;
    }
    else
    {
      code=409;
      reason=string("OSLockdown is already has a pending AutoUpdate request from Console ")+string(", please try again later...");
      delete action;
    }
  }
  else
  {
    if (SB_pending_action==NULL)
    {
      SB_pending_action=action;
    }
    else
    {
      code=409;
      reason=string("OSLockdown is already processing a Console ")+string(GetActionText(SB_current_action_enum))+string(" request, please try again later...");
      delete action;
    }
  }
  pthread_mutex_unlock(&SB_mutex);
}

bool TimeSyncCloseEnough(string transactionId)
{
  // a transactionID is a colon separated string with
  //     clientId
  //     Console response IP/DNS address
  //     Console response 
  //     Time (assuming UTC, and in milliseconds)  command initiated on Console 
  //  We need to pull this last field, convert back to seconds, and see if we are 'close enough'
  // in time to accept the command.  We need to allow for machines that are not in NTP sync.
  // For now - hardcode a one hour (60 second/minute * 60 minutes/hour = 3600 seconds/hour) window  
  

    size_t lastColon = transactionId.rfind(':');
    if (lastColon != string::npos)
    {
      // start one character after the colon and read an integer
      istringstream stringin(transactionId.substr(lastColon+1));
      
      int64_t milliTime;
      stringin >> milliTime;

      int64_t cmdTime = milliTime/1000;

      struct timeval tv;
      gettimeofday(&tv,NULL);
      int64_t nowTime = tv.tv_sec;
      int64_t deltaTime = nowTime - cmdTime;
      
      ostringstream message;
      string deltaType;
      if (deltaTime > 0) 
      {
        deltaType = "Console behind";
      }
      else
      {
        deltaType = "Console ahead";
        deltaTime = -deltaTime;
      }

      if (deltaTime > 3600)
      {
        message << "Command rejected, time synch between Console and Client exceeds 1 hour - " << deltaType << " by " << deltaTime << " seconds";
        throw (SBDispatcher_Except(500, message.str().c_str()));
      } 
      else
      {
      
        message <<"Command accepted, Command sent from Console @ " << cmdTime << "  rec'd @ " << nowTime << "    :: " << deltaType << " by " << deltaTime << " seconds";
        write_log(LOG_INFO, "%s", message.str().c_str() );
      }
    } 
    return true;
}
    
    

void Process_Console_Command(struct soap *soap,char action_char, char *transactionId, char *notificationAddress, int productType, 
                             char * profile, vector<string> procinfo, int loggingLevel, int&code, string&reason)
{
  try 
  {
    if (!disp_opts.shim_name.empty())
    {
      write_log(LOG_INFO,"Dispatcher is operating in SHIM mode - root not required");
    }
    else
    {
      Verify_Am_Root();
    }
    TimeSyncCloseEnough(transactionId);
    Verify_Task_Can_Be_Accepted(action_char, procinfo);
    SB_ACTION *action = new SB_ACTION;
    
    action->m_loggingLevel=loggingLevel;
    action->m_security_profilepath="";
    action->m_baseline_profilepath="";
    
    switch(action_char)
    {
      case 'S':                 
      case 'Q': 
      case 'A': 
      case 'U': // Note combined action
        action->m_action_chars+=action_char;
        process_profile(profile,action->m_security_profilepath, "/default_security.xml");
        break;
      case 'B': action->m_action_chars="B";
        if (profile!=NULL)
        {
          process_profile(profile,action->m_baseline_profilepath, "/default_baseline.xml");
        }
        break;
    }
    
    write_log(LOG_INFO,"processing '%s'...",GetActionText(GetActionEnum(action_char)).c_str());
    get_connection_address(soap,action->m_whofrom);
    action->m_transid=transactionId;
    action->m_replyto=notificationAddress;
    action->m_prodtype=(SB_CLIENT_ENUM)productType;
    action->m_procinfo = procinfo;
    SB_submit_action(action,code,reason);
     
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  } 
}

#define CONVERT_LIST_TO_VECTOR(x,y) vector<string>(x->y, x->__size##y + x->y)
int AgentServiceImplPortBindingService::apply(ns1__apply *ns1__apply_, ns1__applyResponse *ns1__applyResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__applyResponse_->soap,-1);
  string reason;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate apply reply")); 

  
  write_log(LOG_INFO,"Apply command received from console");
  Process_Console_Command(ns1__apply_->soap,
                          'A',
                          ns1__apply_->transactionId,
                          ns1__apply_->notificationAddress,
                          ns1__apply_->productType,
                          ns1__apply_->profile,
                          CONVERT_LIST_TO_VECTOR(ns1__apply_, procinfo),
                          ns1__apply_->loggingLevel,
                          code,
                          reason);
  resp->code=code;
  resp->reasonPhrase=soap_strdup(ns1__applyResponse_->soap,reason.c_str());
  ns1__applyResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::undo(ns1__undo *ns1__undo_, ns1__undoResponse *ns1__undoResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__undoResponse_->soap,-1);
  string profile_path;
  string reason;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate undo reply")); 


  write_log(LOG_INFO,"Undo command received from console");
  Process_Console_Command(ns1__undo_->soap,
                          'U',
                          ns1__undo_->transactionId,
                          ns1__undo_->notificationAddress,
                          ns1__undo_->productType,
                          ns1__undo_->profile,
                          CONVERT_LIST_TO_VECTOR(ns1__undo_, procinfo),
                          ns1__undo_->loggingLevel,
                          code,
                          reason);
  resp->code=code;
  resp->reasonPhrase=soap_strdup(ns1__undoResponse_->soap,reason.c_str());
  ns1__undoResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}


int AgentServiceImplPortBindingService::baseline(ns1__baseline *ns1__baseline_, ns1__baselineResponse *ns1__baselineResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__baselineResponse_->soap,-1);
  string profile_path;
  string reason;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate baseline reply")); 


  write_log(LOG_INFO,"Baseline command received from console");
  Process_Console_Command(ns1__baseline_->soap,
                          'B',
                          ns1__baseline_->transactionId,
                          ns1__baseline_->notificationAddress,
                          ns1__baseline_->productType,
                          NULL,
                          CONVERT_LIST_TO_VECTOR(ns1__baseline_, procinfo),
                          ns1__baseline_->loggingLevel,
                          code,
                          reason);
  resp->code=code;
  resp->reasonPhrase=soap_strdup(ns1__baselineResponse_->soap,reason.c_str());
  ns1__baselineResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

#define dumpName(name, value) \
    if (value) cout << name << value << endl; \
    else       cout << name << "-- no value passed -- "<<endl; \
    
void 
dumpScan(ns1__scan *scan)
{
    dumpName("transactionId       ",scan->transactionId)
    dumpName("notificationAddress ",scan->notificationAddress)
    dumpName("productType         ",scan->productType)
    cout <<  "productTypeStr      " << prodTypeToString((SB_CLIENT_ENUM)scan->productType)<<endl;
    dumpName("profile             ",scan->profile)
    dumpName("scanLevel           ",scan->scanLevel)
    dumpName("loggingLevel        ",scan->loggingLevel )
    for (int i=0;i<scan->__sizeprocinfo;i++)
      dumpName("  procinfo            ",scan->procinfo[i] )
    
}

int AgentServiceImplPortBindingService::scan(ns1__scan *ns1__scan_, ns1__scanResponse *ns1__scanResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__scanResponse_->soap,-1);
  string profile_path;
  string reason;
  int code;
  char action_char='S';
  
//  dumpScan(ns1__scan_);

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate scan reply")); 

  write_log(LOG_INFO,"Scan command received from console");
  if (ns1__scan_->scanLevel<=5) action_char='Q';
  
  Process_Console_Command(ns1__scan_->soap,
                          action_char,
                          ns1__scan_->transactionId,
                          ns1__scan_->notificationAddress,
                          ns1__scan_->productType,
                          ns1__scan_->profile,
                          CONVERT_LIST_TO_VECTOR(ns1__scan_, procinfo),
                          ns1__scan_->loggingLevel,
                          code,
                          reason);

  resp->code=code;
  resp->reasonPhrase=soap_strdup(ns1__scanResponse_->soap,reason.c_str());
  ns1__scanResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request queued");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::baselineWithProfile(ns1__baselineWithProfile *ns1__baselineWithProfile_, ns1__baselineWithProfileResponse *ns1__baselineWithProfileResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__baselineWithProfileResponse_->soap,-1);
  string profile_path;
  string reason;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate baselineWithProfile reply")); 


  
  write_log(LOG_INFO,"Baseline command received from console (with profile)");
  
  Process_Console_Command(ns1__baselineWithProfile_->soap,
                          'B',
                          ns1__baselineWithProfile_->transactionId,
                          ns1__baselineWithProfile_->notificationAddress,
                          ns1__baselineWithProfile_->productType,
                          ns1__baselineWithProfile_->baselineProfile,
                          CONVERT_LIST_TO_VECTOR(ns1__baselineWithProfile_, procinfo),
                          ns1__baselineWithProfile_->loggingLevel,
                          code,
                          reason);

  resp->code=code;
  resp->reasonPhrase=soap_strdup(ns1__baselineWithProfileResponse_->soap,reason.c_str());
  ns1__baselineWithProfileResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request queued");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}


int
SB_send_notification_core(string where_to, SB_ACTION *action, ns1__notify & console_notify)
{
  AgentServiceImplPortBindingProxy Console;
  ns1__notifyResponse console_reply;
  int retval=SOAP_ERR;
  ostringstream message;
  
  Console.soap_endpoint=where_to.c_str();
  if (disp_opts.use_https)
  {   
    if (soap_ssl_client_context(&Console,ssl_client_flags,ssl_client_my_cert,ssl_my_pass,ssl_server_ca_cert,ssl_ca_path,ssl_random_file))
    {
      Console.soap_stream_fault(message);
      throw (SBDispatcher_Except(500,message.str()));
//      write_log(LOG_ERR,"%s",message.str().c_str());
//      exit(1);
    }
  }

  if (Console.notify(&console_notify,&console_reply)!=SOAP_OK)
  {
    ostringstream message;
    Console.soap_stream_fault(message);
    string actiontext=GetActionText((SB_ACTION_ENUM)console_notify.notification->type);
    write_log(LOG_ERR,"%s -> Completion notification unable to send to %s : %s",actiontext.c_str(),message.str().c_str(),Console.soap_endpoint);
  }
  else
  {
    retval=SOAP_OK;
  }
  return retval;
}

// Try to send first to the indicated notification address, if that fails try to send to the address we *think* the message
// came from

void
SB_send_notification(SB_ACTION *action, string & info, string &body,SB_ACTION_ENUM action_enum)
{
  string send_to,alternate_addr;
  bool sent=false;
  size_t slashes,colon;
  ostringstream message;
   
  write_log(LOG_DEBUG,"%s -> notification id=%s info=%s body=%s action_enum=%d\n",
                      GetActionText(action_enum).c_str(),
                      action->m_transid.c_str(),
                      info.c_str(),
                      body.c_str(),
                      action_enum);
  send_to=action->m_replyto;


// Ok, we need to grab the hostname.  We know the the hostname starts after the '//', and the *last*
// colon separates that from the port number.  So grab what is between.

// *IF* action->m_whofrom is not empty, then assume that is the IP address we received the task from
// Note - for scheduled tasks from previous versions this *WILL* be empty until such time as tasks
// are synchronized - we probably should  quietly sync tasks on each host as they finish an autoupdate....

  if (!action->m_whofrom.empty()) 
  {
    // The '://' indicates the start of the hostname, and the 
    // colon separates the hostname from port and remainder of URL
    slashes=send_to.find("://");
    colon = send_to.find_last_of(":");
//    cout << "slashes = "<< slashes << "   colon = "<< colon << endl;
    // if we found both, then try and replace the text between with the
    // altername (that is - what IP (ipv4 or ipv6) did the command come from)
    if (( slashes != string::npos) && (colon != string::npos) )
    {
      if (colon != string::npos)
      {
        alternate_addr = send_to;
        alternate_addr.replace(slashes+2, colon-slashes-2, action ->m_whofrom); 
      }
    }
  }
  
//  cout <<"NOTIF ADDRESS IS "<< send_to << endl;
//  cout <<"ALTERNATE ADDR   "<< alternate_addr << endl;
  
  ns1__notify console_notify;
  ns1__consoleNotification notice_data;

  // append whatever the subAction index is to the actual transaction ID so that
  // the Console knows *which* action is getting the notification, but only if idx >=0
  ostringstream transIdOStr;
  transIdOStr << action->m_transid.c_str() ;
  if (action->m_actionIdx >= 0)
  {
    transIdOStr << ':' << action->m_actionIdx;
  }
  string transId = transIdOStr.str();


  cout << '<' << transIdOStr.str().c_str() << '>' << endl;

  notice_data.info=         (char*)info.c_str();
//  notice_data.transactionId= (char*)action->m_transid.c_str();
  notice_data.transactionId= (char*)transId.c_str();
  notice_data.body=         (char*)body.c_str();
  notice_data.type=          action_enum;
  console_notify.notification=&notice_data;

  sent=SB_send_notification_core(send_to, action, console_notify);
  if (sent!=SOAP_OK)
  {
    if (!alternate_addr.empty())
    {
      send_to=alternate_addr;
      sent=SB_send_notification_core(send_to, action, console_notify);
    }
    else
    {
      write_log(LOG_WARNING,"No IP address recorded as an origination address - unable to attempt fallback notification");
    }
  }
  if (sent==SOAP_OK)
  {
    write_log(LOG_INFO,"%s -> Completion notification sent to %s",GetActionText(action_enum).c_str(),send_to.c_str());
    SB_shim_commentary(LOG_INFO, "Notification Sent");
  }
  else
  {
    write_log(LOG_INFO,"%s -> Completion notification unable to be sent",GetActionText(action_enum).c_str());
    SB_shim_commentary(LOG_ERR, "Notification Failure");
  }
}

void
process_profile_line(char *bigline,ostringstream &data_text)
{
  istringstream stringin(bigline);
  string key,value;
  // PROFILE: name
  stringin>>key>>value;
  cout <<bigline<<endl;
  cout <<key<<" --- "<<value<<endl;
  data_text<< "<entry name=\"profileName\" value=\""<<value<<"\" />";
}

void
process_error_line(char *bigline,ostringstream &exc_text)
{
  istringstream stringin(bigline);
  string key,tag,value;
  // strip the first two tags off and use the remainder for value
  stringin>>key;
  getline(stringin,value);
  exc_text << value;
//  exc_text<< "<exception level=\"error\" message=\""<<value<<"\" />";
//  cout << "<exception level=\"error\" message=\""<<value<<"\" />"<<endl;;
}

// this line will NOT have a STDERR prefix, so just read until EOL

void
process_stderr_line(char *bigline,ostringstream &exc_text,string &traceback_text)
{
  static bool is_traceback=false;
  istringstream stringin(bigline);
  string key,tag,value;

  getline(stringin,value);
  // if the line to stderr starts with 'Traceback (most recent call last):"
  // then we only keep the *last* line we've seen.  A traceback should abort
  // the entire opteration, and the terminal line should say what kind of
  // exception we saw.
  if (is_traceback || (strncmp(bigline,"Traceback (most recent call last):",34 )==0))
  {
    if ((strlen(bigline)>0) && (bigline[0]!='\n'))traceback_text=bigline;
    is_traceback=true;
  }
  else
  { 
    exc_text<<value<<endl;  // concatentate *all* stderr lines together...
  }
//  exc_text<< "<exception level=\"error\" message=\""<<value<<"\" />";
//  cout << "<exception level=\"error\" message=\""<<bigline<<"\" />"<<endl;;
}
void
process_stats_line(char *bigline,ostringstream &data_text)
{
  istringstream stringin(bigline);
  string key,tag,value;
  stringin>>key>>tag>>value;
  if (tag=="MODULES") 
  {
    data_text<< "<entry name=\"totalModules\" value=\""<<value<<"\" />";
  }
  else if (tag=="TIME")
  {
    data_text<< "<entry name=\"totalTime\" value=\""<<value<<"\" />";
  }
  else if (tag=="PASS")
  {
    data_text<< "<entry name=\"totalPass\" value=\""<<value<<"\" />";
  }
  else if (tag=="APPLY")
  {
    data_text<< "<entry name=\"totalApply\" value=\""<<value<<"\" />";
  }
  else if (tag=="Undone")
  {
    data_text<< "<entry name=\"totalUndone\" value=\""<<value<<"\" />";
  }
  else if (tag=="NotReqd")
  {
    data_text<< "<entry name=\"totalNotReqd\" value=\""<<value<<"\" />";
  }
  else if (tag=="FAIL")
  {
    data_text<< "<entry name=\"totalFail\" value=\""<<value<<"\" />";
  }
  else if (tag=="N/A")
  {
    data_text<< "<entry name=\"totalNA\" value=\""<<value<<"\" />";
  }
  else if (tag=="ERROR")
  {
    data_text<< "<entry name=\"totalError\" value=\""<<value<<"\" />";
  }
  else if (tag=="MANUAL")
  {
    data_text<< "<entry name=\"totalManual\" value=\""<<value<<"\" />";
  }
  else if (tag=="OTHER")
  {
    data_text<< "<entry name=\"totalOther\" value=\""<<value<<"\" />";
  }
}

void
process_module_line(char *bigline,ostringstream &data_text)
{
}

void
process_step_line(char *bigline,ostringstream &data_text)
{
}

void
process_created_line(char *bigline,ostringstream &data_text)
{
  istringstream stringin(bigline);
  string key,tag,value;
  stringin>>key>>value;
  // find the last '/' and keep from then on...
  size_t lastslash=value.rfind('/');
  if (lastslash!=string::npos) value=value.substr(lastslash+1);
  data_text<< "<entry name=\"fileName\" value=\""<<value<<"\" />";

}


void*
SB_task_manager(void *arg)
{
  SB_ACTION *action;
  pthread_t action_thread;
  int retval;
  bool execute ;
  
  write_log(LOG_INFO,"Task manager startup...");
  do
  {
    retval = 0;
    action=NULL;
    execute = true;
    pthread_mutex_lock(&SB_mutex);
    if (!SB_current_action)
    {
//      cout <<"Check pending..."<<endl;
      if (SB_pending_autoupdate)
      {
        action  = SB_pending_autoupdate;
        SB_pending_autoupdate = NULL;
        SB_current_action = action;
      }
      else if (SB_pending_action)
      {
        action=SB_pending_action;
        SB_pending_action=NULL;
        SB_current_action=action;
      }
      else
      {
//        cout <<"Check task queue..."<<endl;
        action=TaskList->GetScheduledTaskToDo();
        if (action) action->m_from_console=false;
      }
    }
    else
    {
//      cout <<"Task executing..."<<endl;
    }
    if (action) SB_current_action=action;
    pthread_mutex_unlock(&SB_mutex);
    
    // Verify that current conditions allow the task to execute - immediate tasks were already checked when sent from the Console.
    // These checks are more for scheduled tasks
    
    // If in core hours, or the machine is too busy, notify the Console and do not execute the action. 
    

    if (action)
    {
      string coreErrStr = "";
      string loadErrStr = "";
      
      if ( !( (coreErrStr = nowInCoreHours(action->m_from_console)) != "") )
      {
        if ( ! ( (loadErrStr = machineTooBusy(action->m_from_console)) != "") )
        {
          retval=pthread_create(&action_thread,NULL,SB_invoke,(void*)action);
        }
      }
    
      if (( retval!=0) || (coreErrStr != "") || (loadErrStr != "") )
      {
        ostringstream info_stream,body_stream;
        if (coreErrStr != "")
        {
          write_log(LOG_WARNING,"Unable to spawn task %s: %s", action->m_transid.c_str(), coreErrStr.c_str());
          body_stream << "<details success=\"false\"><data><entry name=\"info\" value=\"errortext=" << coreErrStr << "\"/>";
        }
        else if (loadErrStr != "")
        {
          write_log(LOG_WARNING,"Unable to spawn task %s: %s", action->m_transid.c_str(), coreErrStr.c_str());
          body_stream << "<details success=\"false\"><data><entry name=\"info\" value=\"errortext=" << coreErrStr << "\"/>";
        }
        else
        {
          write_log(LOG_WARNING,"Unable to spawn task %s: pthread spawn errcode=%d", action->m_transid.c_str(), retval);
          body_stream << "<details success=\"false\"><data><entry name=\"info\" value=\"errorcode=" << retval << "\"/>";
        }

        info_stream << "Unable to spawn task(s) " <<action->m_action_chars.c_str() ;

        // initial body_stream text from above statements
        body_stream << "<entry name=\"task\" value=\"" << action->m_transid << "\"/>";

        body_stream<<"<entry name=\"actionSequence\" value=\"";
        for (size_t i=0;i<action->m_action_chars.size();i++)
        {
          if (i!=0) body_stream<<", "<<endl;
          body_stream<<GetActionText(GetActionEnum(action->m_action_chars[i])); 
        }
        body_stream << "\"/>";
        body_stream << "</data></details>";

        string info=info_stream.str();
        string body=body_stream.str();
        SB_ACTION_ENUM action_enum;
        if (action->m_from_console)
        {
          action_enum=GetActionEnum(action->m_action_chars[0]);
        }
        else
        {
          action_enum=SB_TASK_COMPLETED;
        }
        SB_send_notification(action,info,body,action_enum);
        SB_finished(action->m_transid);
      } 
    }   
    sleep(1);
  } while (!must_exit());
  write_log(LOG_INFO,"Task manager exiting...");
  pthread_detach(pthread_self());
  return NULL;
}


void
SB_invoke_core(SB_ACTION *action,char action_character,SB_ACTION_ENUM action_enum)
{
  bool is_ok=false;
  bool aborted=false;  
  bool have_errors=false;
  action->set_thread();
  int retstatus;
  string status_str;
  ostringstream info_text,body_text,data_text,exc_text;
  string sb_cmd;
  ostringstream sb_args;
  string sb_path,sb_name,traceback_text;
  string term_str;
  SUB_PROC_TERMINATION term_type;
  int term_code;
  string stdout_str,stderr_str;
  string commentary;
  
  sb_path=APPLICATION_CMD_PATH;
  sb_name=APPLICATION_EXECNAME;
  SUB_PROC sub_proc;

  sub_proc.set_path(sb_path.c_str());
  sub_proc.set_execname(sb_name.c_str());
  
  sb_args << " -v -l "<<action->m_loggingLevel;
  data_text<< "<entry name=\"action\" value=\""<<GetActionText(action_enum)<<"\" />";
  
  switch (toupper(action_character))
  {
    case '*': sb_args << " -U ";
              sb_args << " -n " << action->m_replyto ;
              sb_args << " -t " << action->m_transid;
              commentary = "Update";
              if (action->m_forceFlag) 
              {
                sb_args << " -f";
              }
              break;
    case 'S': sb_args << " -f -s "    << action->m_security_profilepath  ; commentary = "Scan"; break;
    case 'Q': sb_args << " -f -q -s " << action->m_security_profilepath  ; commentary = "Quickscan"; break;
    case 'A': sb_args << " -f -a "    << action->m_security_profilepath  ; commentary = "Apply"; break;
    case 'U': sb_args << " -f -u "    << action->m_security_profilepath  ; commentary = "Undo"; break;
    case 'B': commentary = "Baseline"; 
              if (action->m_baseline_profilepath.empty())
              {
                sb_args << " -f -b "                            ; break;
              }
              else
              {
                sb_args << " -f -b " << action->m_baseline_profilepath   ; break;
              }
  }

  errno=0;
  if (!disp_opts.shim_name.empty()) sb_args << " -z "<< disp_opts.shim_name;
//  sb_args << " 2>&1 ";
  sb_cmd=sb_args.str();
  write_log(LOG_DEBUG,"Executing command : %s %s",sb_path.c_str(),sb_cmd.c_str());

  if (!disp_opts.shim_name.empty() and !islower(action_character)) 
  {
    SB_shim_commentary(LOG_INFO, "Preinvoke delay");
    for (int cdown = 0; cdown !=0; cdown --)
    {
        sleep(1);
        ostringstream msg;
        msg <<  "TMinus "<< cdown;
        SB_shim_commentary(LOG_INFO, msg.str());
    }
  }
  SB_shim_commentary(LOG_INFO, "Invoking "+commentary);
  sub_proc.dispatch(sb_cmd);

  while (sub_proc.read_output(&stdout_str,&stderr_str))
  {
    if (!stdout_str.empty()) 
    {
//      cout <<"STDOUT -> "<<stdout_str;
/*
    Line coming back that we're interested in start with 'INFO:', 'ERROR:', 'STATS:', 'MODULE:'
    We'll tag these and keep track of them to report back upstream
 */
      char *bigline=(char*)stdout_str.c_str();
        /* remember that bigline is a char array from C, not C++ -- FIXME */
      if (strncmp(bigline,"PROFILE:",8)==0)       
      {
        process_profile_line(bigline,data_text);
      }
      else if (strncmp(bigline,"ERROR:",6)==0) 
      {
        process_error_line(bigline,exc_text);
        have_errors=true;
      }
      else if (strncmp(bigline,"STATS:",6)==0) 
      {
        process_stats_line(bigline,data_text);
      }
      else if (strncmp(bigline,"MODULE:",7)==0) 
      {
        process_module_line(bigline,data_text);
      }
      else if (strncmp(bigline,"CREATED:",8)==0) 
      {
        process_created_line(bigline,data_text);
        is_ok=true;
      }
      else if (strncmp(bigline,"STEP:",8)==0) 
      {
        process_step_line(bigline,data_text);
      }
    }    
    
    if (!stderr_str.empty()) 
    {
//      cout <<"STDERR -> "<<stderr_str;     
      char *bigline=(char*)stderr_str.c_str();
      process_stderr_line(bigline,exc_text,traceback_text);
      have_errors=true;
    }
  }
  sub_proc.shutdown(&term_str,&term_type,&term_code);
//  cout <<"Term_type = "<<term_type<<endl;
  if ((term_type==SUB_PROC_TERM_NORMAL) )
  {
    if ((term_code==0) && !have_errors)
    {
      status_str="Command completed";
      data_text << "<entry name=\"info\" value=\"No errors reported.\" />";
      write_log(LOG_INFO,"%s -> OSLockdown returned normally after processing command",GetActionText(action_enum).c_str());
    }
    else if (term_code == SIGUSR1 )
    { 
      aborted=true;
      if (!have_errors)
      {
        status_str="Command aborted by request";
        data_text << "<entry name=\"info\" value=\"No errors reported.\" />";
        write_log(LOG_INFO,"%s -> OSLockdown command aborted during processing",GetActionText(action_enum).c_str());
      }
      else
      {
         status_str="Command aborted, with error(s)";
         data_text << "<entry name=\"info\" value=\"errorcode="<<term_code<<"\" />";
         write_log(LOG_INFO,"%s -> OSLockdown command aborted, returning errorcode %d",GetActionText(action_enum).c_str(),term_code);
      }
    }
    else
    {
       status_str="Command executed with error(s)";
       data_text << "<entry name=\"info\" value=\"errorcode="<<term_code<<"\" />";
       write_log(LOG_INFO,"%s -> OSLockdown returned errorcode %d",GetActionText(action_enum).c_str(),term_code);
    }
  }
  else if (term_type==SUB_PROC_TERM_SIGNAL)
  {
    is_ok=false;
    status_str="Command failed to complete";
    data_text <<"<entry name=\"info\" value=\"Terminated by signal "<<term_code<<"\" />";
    write_log(LOG_ERR,"%s -> OSLockdown process terminated by signal %d ",GetActionText(action_enum).c_str(),term_code);
  }
  else if (term_type=SUB_PROC_TERM_STARTUP)
  {
    is_ok=false;
    status_str="Command failed to execute";
    data_text << "<entry name=\"info\" value=\"Unable to execute command : "<<term_str<<"\" />";
    write_log(LOG_INFO,"%s -> OSLockdown failed to execute : %s",GetActionText(action_enum).c_str(),term_str.c_str());
  }

pipe_done:  

  body_text<<"<details";
  body_text<<" success=";
  if (is_ok)  body_text<<"\"true\"";
  else        body_text<<"\"false\"";

  body_text<<" aborted=";

  if (aborted)  body_text<<"\"true\"";
  else          body_text<<"\"false\"";
 
  body_text<<" >";

  body_text<<"<data>";
  body_text<<data_text.str()<<"</data>";
  if (!exc_text.str().empty() || !traceback_text.empty()) 
  {
    body_text<< "<exceptions>" ;
    if (!exc_text.str().empty()) body_text<< "<exception level=\"error\" message=\""<<exc_text.str()<<"\" />";
    if (!traceback_text.empty()) body_text<< "<exception level=\"fatal\" message=\""<<traceback_text<<"\" />";
    body_text<< "</exceptions>";
  }
  body_text<<"</details>";

  string body_str=body_text.str();
  string info_str=status_str.c_str();

  // send a notification if the action was *NOT* an autoupdate, or if an autoupdate reported an error

  if (action_character != '*' || is_ok == false)
  {
    SB_send_notification(action, info_str, body_str,action_enum);
  }
}


void*
SB_invoke(void *arg)
{
  SB_ACTION *action=(SB_ACTION*)arg;
  bool execute_task=true; 
  SB_ACTION_ENUM action_enum;
  
  // If we're *not* immediately tasked from the console then try and verify that we are still a valid task...
  if (action->m_from_console==false)
  {
    char security_fingerprint_ptr[145];
    char baseline_fingerprint_ptr[145];
    
    // if we need a profile then we first need to get the fingerprint of the *current* enterprise profile
    // remember for the actions, saub = scan/apply/undo/baseline, and SAB = scheduled scan/apply/baseline
    // we're using '*' for Autoupdate to prevent confusion on what 'U' means here, even though the actual
    // command passed to oslockdown is '-U' for autoUpdate.
    
    if (action->m_action_chars.find_first_of("saubSAB")!=string::npos)
    {
      string security_profile;
      string baseline_profile;
      if (disp_opts.shim_name.empty() ) 
      {
        security_profile = string(APPLICATION_DATA)+string("/profiles/.enterprise/default_security.xml");
        baseline_profile = string(APPLICATION_DATA)+string("/profiles/.enterprise/default_baseline.xml");
      }
      else
      { 
        security_profile = string(APPLICATION_DATA)+string("/reports/shim/" + disp_opts.shim_name + "/default_security.xml");
        baseline_profile = string(APPLICATION_DATA)+string("/reports/shim/" + disp_opts.shim_name + "/default_baseline.xml");
      }
      
      get_file_sha1(security_profile.c_str(),security_fingerprint_ptr);
      action->m_security_profilepath=security_profile;

      get_file_sha1(baseline_profile.c_str(),baseline_fingerprint_ptr);
      action->m_baseline_profilepath=baseline_profile;

      execute_task=VerifyTaskWithConsole(action->m_transid,action->m_verifyaddr, 
                                       security_fingerprint_ptr,action->m_security_profilepath,
                                       baseline_fingerprint_ptr,action->m_baseline_profilepath,
                                       action->m_replyto, action->m_whofrom);
    }
  }
  if (execute_task)
  {
    for (size_t idx=0;idx<action->m_action_chars.length();idx++)
    {
      char action_character=action->m_action_chars[idx];
      SB_ACTION_ENUM action_enum=GetActionEnum(action_character);
      pthread_mutex_lock(&SB_mutex);
      SB_current_action_enum=action_enum;
      pthread_mutex_unlock(&SB_mutex);
      // set actionIdx to indicate the actual subaction index being done
      action->m_actionIdx = idx;
      SB_invoke_core(action,action_character,action_enum);
    }
  }
  // reset action to -1 since we're not actually *doing* something
  action->m_actionIdx = -1;
  
  if (!action->m_from_console)
  {
    ostringstream info_stream,body_stream;

    info_stream << "Task completed" ;
    body_stream<<"<details success=\"true\"><data>";
    body_stream<<"<entry name=\"task\" value=\""<<action->m_transid<<"\"/>";
    body_stream<<"<entry name=\"actionSequence\" value=\"";
    for (size_t i=0;i<action->m_action_chars.size();i++)
    {
      if (i!=0) body_stream<<", "<<endl;
      body_stream<<GetActionText(GetActionEnum(action->m_action_chars[i])); 
    }
    body_stream<<"\"/>";
    body_stream<<"</data></details>";

    string info=info_stream.str();
    string body=body_stream.str();
    SB_send_notification(action,info,body,SB_TASK_COMPLETED);
  }
  SB_finished(action->m_transid);
  pthread_detach(pthread_self());
  return NULL;
}


int AgentServiceImplPortBindingService::info(ns1__info *ns1__info_, ns1__infoResponse *ns1__infoResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__infoResponse_->soap,-1);
  string reason,body;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate info reply")); 

  write_log(LOG_INFO,"Info command received from console");

  try 
  {
    SB_Info sbinfo;
    body=sbinfo.toXml(ns1__info_->transactionId);
    code=200;
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__infoResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__infoResponse_->soap,body.c_str());

  ns1__infoResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::status(ns1__status *ns1__status_, ns1__statusResponse *ns1__statusResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__statusResponse_->soap,-1);
  string reason,body;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate status reply")); 

  write_log(LOG_INFO,"Status command received from console");
  string whofrom;
  get_connection_address(ns1__status_->soap, whofrom);
  try 
  {
    string action="Idle";
    pthread_mutex_lock(&SB_mutex);
    if (SB_current_action)  action=GetActionText(SB_current_action_enum);
    pthread_mutex_unlock(&SB_mutex);
    SB_Status sbstatus(action);
    body=sbstatus.toXml(ns1__status_->transactionId);
    code=200;
    reason=Default_200;
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__statusResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__statusResponse_->soap,body.c_str());
  ns1__statusResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::getSbAppLog(ns1__getSbAppLog *ns1__getSbAppLog_, ns1__getSbAppLogResponse *ns1__getSbAppLogResponse_)
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getSbAppLogResponse_->soap,-1);
  string reason,report_meta;
  char *content=NULL;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate getSbAppLog reply")); 

  write_log(LOG_INFO,"Request Application Log command received from console");
  try
  {
    code=200;
    reason=Default_200;
    content=get_full_file(ns1__getSbAppLogResponse_->soap,APPLICATION_DATA,string("/logs/oslockdown.log"),report_meta, disp_opts.max_log_MB);
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getSbAppLogResponse_->soap,reason.c_str());
  resp->body=                    soap_strdup(ns1__getSbAppLogResponse_->soap,report_meta.c_str());
  resp->content=content;
  ns1__getSbAppLogResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::getBaselineList(ns1__getBaselineList *ns1__getBaselineList_, ns1__getBaselineListResponse *ns1__getBaselineListResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getBaselineListResponse_->soap,-1);
  string reason,body;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate getBaselineList reply")); 


  write_log(LOG_INFO,"List Baseline Reports command received from console");
  try
  {
    code=200;
    reason=Default_200;
    SB_DirList dirlist(MY_APPLICATION_BASELINES,".xml","baselines");
    body=dirlist.toXml();
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getBaselineListResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__getBaselineListResponse_->soap,body.c_str());
  ns1__getBaselineListResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;

}

int AgentServiceImplPortBindingService::getBaseline(ns1__getBaseline *ns1__getBaseline_, ns1__getBaselineResponse *ns1__getBaselineResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getBaselineResponse_->soap,-1);
  string reason,report_meta;
  char *content=NULL;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate getBaseline reply")); 

  write_log(LOG_INFO,"Get Baseline Report command received from console");
  try
  {
    code=200;
    reason=Default_200;    
    /* we know the file is ascii, so go get the total file size and pre-allocate space for it.  If the allocation fails, then
       we punt throwing an error, otherwise open the file and read in the data...*/
    content=get_full_file(ns1__getBaselineResponse_->soap,MY_APPLICATION_BASELINES,ns1__getBaseline_->fileName,report_meta,-1);
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getBaselineResponse_->soap,reason.c_str());
  resp->body=                    soap_strdup(ns1__getBaselineResponse_->soap,report_meta.c_str());
  resp->content=content;
  ns1__getBaselineResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;

}

/* Assessment files live in /var/lib/oslockdown/reports/standalone/assessments */
int AgentServiceImplPortBindingService::getAssessmentList(ns1__getAssessmentList *ns1__getAssessmentList_, ns1__getAssessmentListResponse *ns1__getAssessmentListResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getAssessmentListResponse_->soap,-1);
  string reason,body;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate getAssessmentLlist reply")); 

  write_log(LOG_INFO,"List Assessment Reports command received from console");
  try
  {
    code=200;
    reason=Default_200;
    SB_DirList dirlist(MY_APPLICATION_ASSESSMENTS,".xml","assessments");
    body=dirlist.toXml();
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getAssessmentListResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__getAssessmentListResponse_->soap,body.c_str());
  ns1__getAssessmentListResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

/* Assessment files live in /var/lib/oslockdown/reports/standalone/assessments */
int AgentServiceImplPortBindingService::getAssessment(ns1__getAssessment *ns1__getAssessment_, ns1__getAssessmentResponse *ns1__getAssessmentResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getAssessmentResponse_->soap,-1);
  string reason,report_meta;
  char *content;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate getAssessment reply")); 

  write_log(LOG_INFO,"Get Assessment Report command received from console");
  try
  {
    code=200;
    reason=Default_200;
    /* go read the report */
    content=get_full_file(ns1__getAssessmentResponse_->soap,MY_APPLICATION_ASSESSMENTS,ns1__getAssessment_->fileName,report_meta,-1);
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getAssessmentResponse_->soap,reason.c_str());
  resp->body=                    soap_strdup(ns1__getAssessmentResponse_->soap,report_meta.c_str());
  resp->content=content;
  ns1__getAssessmentResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

/* Apply files live in /var/lib/oslockdown/reports/standalone/apply_reports */
int AgentServiceImplPortBindingService::getApplyList(ns1__getApplyList *ns1__getApplyList_, ns1__getApplyListResponse *ns1__getApplyListResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getApplyListResponse_->soap,-1);
  string reason,body;
  int code;


  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate getApplyList reply")); 

  write_log(LOG_INFO,"List Apply Reports command received from console");
  try
  {
    code=200;
    reason=Default_200;
    SB_DirList dirlist(MY_APPLICATION_APPLY_REPORTS,".xml","apply_reports");
    body=dirlist.toXml();
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getApplyListResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__getApplyListResponse_->soap,body.c_str());
  ns1__getApplyListResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

/* Apply files live in /var/lib/oslockdown/reports/standalone/apply_reports */
int AgentServiceImplPortBindingService::getApply(ns1__getApply *ns1__getApply_, ns1__getApplyResponse *ns1__getApplyResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getApplyResponse_->soap,-1);
  string reason,report_meta;
  char *content;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to process getApply command")); 

  write_log(LOG_INFO,"Get Apply Report command received from console");
  try
  {
    code=200;
    reason=Default_200;
    /* go read the report */
    content=get_full_file(ns1__getApplyResponse_->soap,MY_APPLICATION_APPLY_REPORTS,ns1__getApply_->fileName,report_meta,-1);
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getApplyResponse_->soap,reason.c_str());
  resp->body=                    soap_strdup(ns1__getApplyResponse_->soap,report_meta.c_str());
  resp->content=content;
  ns1__getApplyResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}


/* Undo files live in /var/lib/oslockdown/reports/standalone/undo_reports */
int AgentServiceImplPortBindingService::getUndoList(ns1__getUndoList *ns1__getUndoList_, ns1__getUndoListResponse *ns1__getUndoListResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getUndoListResponse_->soap,-1);
  string reason,body;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to process getUndoList command")); 

  write_log(LOG_INFO,"List Undo Reports command received from console");
  try
  {
    code=200;
    reason=Default_200;
    SB_DirList dirlist(MY_APPLICATION_UNDO_REPORTS,".xml","undo_reports");
    body=dirlist.toXml();
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getUndoListResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__getUndoListResponse_->soap,body.c_str());
  ns1__getUndoListResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}

/* Undo files live in /var/lib/oslockdown/reports/standalone/undo_reports */
int AgentServiceImplPortBindingService::getUndo(ns1__getUndo *ns1__getUndo_, ns1__getUndoResponse *ns1__getUndoResponse_) 
{
  ns1__reportsResponse *resp = soap_new_ns1__reportsResponse(ns1__getUndoResponse_->soap,-1);
  string reason,report_meta;
  char *content;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to process getUndo command")); 

  write_log(LOG_INFO,"Get Undo Report command received from console");
  try
  {
    code=200;
    reason=Default_200;
    /* go read the report */
    content=get_full_file(ns1__getUndoResponse_->soap,MY_APPLICATION_UNDO_REPORTS,ns1__getUndo_->fileName,report_meta,-1);
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__getUndoResponse_->soap,reason.c_str());
  resp->body=                    soap_strdup(ns1__getUndoResponse_->soap,report_meta.c_str());
  resp->content=content;
  ns1__getUndoResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  return SOAP_OK;
}


int AgentServiceImplPortBindingService::updateTask(ns1__updateTask *ns1__updateTask_, ns1__updateTaskResponse *ns1__updateTaskResponse_)
{
  ns1__schedulerResponse *resp = soap_new_ns1__schedulerResponse(ns1__updateTaskResponse_->soap,-1);
  string reason=Default_200;
  char *content;
  int code=200;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate updateTask reply")); 

  if (!have_scheduler) return SOAP_NO_METHOD;
  write_log(LOG_INFO,"Update Task command received from console");

  string whofrom;
  get_connection_address(ns1__updateTask_->soap, whofrom);
  
  try 
  {
    if (!TaskList->update_task(ns1__updateTask_->task, ns1__updateTask_->notificationAddress, ns1__updateTask_->verificationAddress, whofrom))
    {
      TaskList->add_task(ns1__updateTask_->task, ns1__updateTask_->notificationAddress, ns1__updateTask_->verificationAddress, whofrom);
    }
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__updateTaskResponse_->soap,reason.c_str());
  ns1__updateTaskResponse_->return_=resp;
  
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::removeTask(ns1__removeTask *ns1__removeTask_, ns1__removeTaskResponse *ns1__removeTaskResponse_) 
{
  ns1__schedulerResponse *resp = soap_new_ns1__schedulerResponse(ns1__removeTaskResponse_->soap,-1);
  string reason=Default_200;
  char *content;
  int code=200;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate removeTask reply")); 


  write_log(LOG_INFO,"Remove Task command received from console");
  if (!have_scheduler) return SOAP_NO_METHOD;
  try 
  {
    string id=ns1__removeTask_->task->id;
    TaskList->remove_task(id);
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__removeTaskResponse_->soap,reason.c_str());
  ns1__removeTaskResponse_->return_=resp;
  
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::updateTaskList(ns1__updateTaskList *ns1__updateTaskList_, ns1__updateTaskListResponse *ns1__updateTaskListResponse_) 
{
  ns1__schedulerResponse *resp = soap_new_ns1__schedulerResponse(ns1__updateTaskListResponse_->soap,-1);
  string reason=Default_200;
  char *content;
  int code=200;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate updateTaskList reply")); 


  if (!have_scheduler) return SOAP_NO_METHOD;
  write_log(LOG_INFO,"Update Task command received from console");
  
  // Ok, we're getting a list of all *current* tasks, so delete anything we have already

  string whofrom;
  get_connection_address(ns1__updateTaskList_->soap, whofrom);
  
  write_log(LOG_INFO,"Clear All Tasks command received from console");
  TaskListRemoveAllTasks();
  write_log(LOG_INFO,"Updating list of %d task(s)", ns1__updateTaskList_->__sizetaskList);
  try 
  {
    for (int i = 0; i< ns1__updateTaskList_->__sizetaskList; i++) {
      if (!TaskList->update_task(ns1__updateTaskList_->taskList[i], ns1__updateTaskList_->notificationAddress, ns1__updateTaskList_->verificationAddress,
      whofrom))
      {
        TaskList->add_task(ns1__updateTaskList_->taskList[i], ns1__updateTaskList_->notificationAddress, ns1__updateTaskList_->verificationAddress, whofrom);
      }
    }
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__updateTaskListResponse_->soap,reason.c_str());
  ns1__updateTaskListResponse_->return_=resp;
  
  return SOAP_OK;

}

int AgentServiceImplPortBindingService::clearTasks(ns1__clearTasks *ns1__clearTasks_, ns1__clearTasksResponse *ns1__clearTasksResponse_) 
{
  string reason=Default_200;
  ns1__schedulerResponse *resp = soap_new_ns1__schedulerResponse(ns1__clearTasksResponse_->soap,-1);
  int code=200;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate clearTasks reply")); 


  write_log(LOG_INFO,"Clear All Tasks command received from console");
  TaskListRemoveAllTasks();

  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__clearTasksResponse_->soap,reason.c_str());
  ns1__clearTasksResponse_->return_=resp;
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::verifyTaskList(ns1__verifyTaskList *ns1__verifyTaskList_, ns1__verifyTaskListResponse *ns1__verifyTaskListResponse_) 
{
  ns1__schedulerResponse *resp = soap_new_ns1__schedulerResponse(ns1__verifyTaskListResponse_->soap,-1);
  string reason=Default_200;
  char *content;
  int code=200;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate updateTaskList reply")); 


  if (!have_scheduler) return SOAP_NO_METHOD;
  write_log(LOG_INFO,"Verify Task List command received from console");
  string whofrom;
  get_connection_address(ns1__verifyTaskList_->soap, whofrom);
  try 
  {
//    cout <<"verifytasklist"<<endl;
//    cout <<"TaskCount: "<<ns1__verifyTaskList_->__sizetaskList<<endl;
    for (size_t a=0;a<ns1__verifyTaskList_->__sizetaskList;a++)
    {
      ns1__dispatcherTask *taskptr=ns1__verifyTaskList_->taskList[a];
      
      TaskList->add_task(taskptr,ns1__verifyTaskList_->notificationAddress,ns1__verifyTaskList_->verificationAddress, whofrom);
    }
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__verifyTaskListResponse_->soap,reason.c_str());
  ns1__verifyTaskListResponse_->return_=resp;
  
  return SOAP_OK;
}


char *
get_full_file(struct soap *soapptr,const string dirname,const string filename,string &report_meta, int maxsizeMB)
{
  char *content=NULL;
  struct stat info;
  string path=(string)dirname+"/"+(string)filename;
  
  write_log(LOG_INFO,"Asked to obtain %s",path.c_str());
  if ((stat (path.c_str(),&info))==0)
  {
    int sizeMB = info.st_size/(1024*1024)+(info.st_size%(1024*1024)!=0?1:0) ; 
    write_log(LOG_INFO, "max is %d, allowed is %d (actual is %ld)",maxsizeMB, sizeMB, (long)info.st_size);
    if ((maxsizeMB>=0) && (sizeMB > maxsizeMB)) 
    {
      ostringstream msg;
      msg << " : File " << path << " is " <<info.st_size<< " bytes, which is larger than the maximum allowed transfer size of " << maxsizeMB << " MB";
      throw (SBDispatcher_Except(500,msg.str().c_str()));
    }
    content=(char*)soap_malloc(soapptr,info.st_size+1);
    if (!content)
    {
      throw (SBDispatcher_Except(500,"Unable to allocate memory to read full file: "+path));
    }
    /* use 'C' read routines for simplicity */
    int fd;
    
    if ((fd=open(path.c_str(),O_RDONLY))==-1)
    {
      throw (SBDispatcher_Except(500,"Unable to open file for reading: "+path));
    }
    int buffer_read, data_read, data_left;
    data_left=info.st_size;
    data_read=0;
    buffer_read=-1;
    while (data_left)
    {
      errno=0;
      buffer_read=read(fd,content+data_read,data_left);
      if (buffer_read<0)
      {
        if (errno!=EINTR)
        {
          close(fd);
          throw(SBDispatcher_Except(500,"Unable to read data:"+path));
        }
      }
      else
      {
        data_read+=buffer_read;
        data_left-=buffer_read;
      }
    }
    content[data_read]='\0';
    close(fd);
  }
  else
  {
    throw (SBDispatcher_Except(500,"Unable to obtain information on file"));
  } 

  char *sha1=get_buffer_sha1(content,info.st_size);
  ostringstream message;
  message << "<report_meta name=\"" << filename << "\" sha1=\"" << sha1 << "\" />";
  report_meta=message.str(); 
  free(sha1);
  return content;
}


int AgentServiceImplPortBindingService::abort(ns1__abort *ns1__abort_, ns1__abortResponse *ns1__abortResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__abortResponse_->soap,-1);
  string reason,body;
  string killmsg;
  int code;
  body="No action currently in progress - nothing to abort";
  code=200;
  reason=Default_200;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate abort reply")); 


  write_log(LOG_INFO,"Abort command received from console");

  try 
  {
    string action="Idle";

    // get the action and pid into thread safe variables...
    pthread_mutex_lock(&SB_mutex);
    if (SB_current_action) 
    {
      action=GetActionText(SB_current_action_enum);
    }
    pthread_mutex_unlock(&SB_mutex);
    if (action == "Idle")
    {
      write_log(LOG_INFO,body.c_str());
    }
    else
    {
      ostringstream msg;
      if (killpg(getpgrp(),SIGUSR1)!=0)
      {
        SB_Status sbstatus(action);
        body="Aborting"+ sbstatus.toXml(ns1__abort_->transactionId)+ " -> unable to send SIGUSR1";
        code=200;
        reason=Default_200;
        msg << "Unable to send SIGUSR1 : " << strerror(errno);
        write_log(LOG_ERR,"%s",msg.str().c_str());

      }
      else
      {  
        SB_Status sbstatus(action);
        body="Aborting "+ sbstatus.toXml(ns1__abort_->transactionId);
        code=200;
        reason=Default_200;
        msg << "Sent SIGUSR1 to Process Group  "<< getpgrp();
        write_log(LOG_INFO,"%s",msg.str().c_str());
      }      
    }
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__abortResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__abortResponse_->soap,body.c_str());
  ns1__abortResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }
  cerr <<endl<<"ABORT -> "<<body<<endl;
  return SOAP_OK;
}

int AgentServiceImplPortBindingService::updateAgent(ns1__updateAgent *ns1__updateAgent_, ns1__updateAgentResponse *ns1__updateAgentResponse_)
{
  ns1__agentResponse *resp = soap_new_ns1__agentResponse(ns1__updateAgentResponse_->soap,-1);
  string reason,body;
  int code;

  if (resp == NULL) throw (SBDispatcher_Except(500,"Unable to generate updateAgent reply")); 


  write_log(LOG_INFO,"updateAgent command received from console");

  try 
  {
// All autoupdates require a transaction id - if that doesn't exist then punt
   if (!ns1__updateAgent_->transactionId) 
   {
     throw (SBDispatcher_Except(500,"No transaction ID present - autoupdate aborting.")); 
   }
   
// we'll need to indicate that the update was requested *IF* 'updateFlag' is True.
    string action="Idle";
    pthread_mutex_lock(&SB_mutex);
    if (SB_current_action)  action=GetActionText(SB_current_action_enum);
    pthread_mutex_unlock(&SB_mutex);
    
//    if (ns1__updateAgent_->updater != NULL)
//    {
//        cout <<"Updater   = "<<ns1__updateAgent_->updater->__size<<" characters"<<endl;
//    }
//    else
//    {
//        cout <<"Updater   = null pointer"<<endl;
//    }
    // Ok, determine if we *need* to update - couple of possible outcomes:
    
    // if update != "" then it is a zipped tarball with our update, pass it *and* forceFlag down to the lockdown engine and 
    //     it decide if an update is required by looking at the individual packages
    // if updater == "" 
    //     compare 'build' version numbers - update only if they are different, indicate to the Console that we *need* an update
    //     and return that info, then we're done
    
    SB_Update sbupdate(ns1__updateAgent_->version);

    body=sbupdate.toXml(ns1__updateAgent_->transactionId);
    code=200;
//    cout <<"forceFlag = "<<ns1__updateAgent_->forceFlag<<endl;
//    cout <<"from      = "<<ns1__updateAgent_->notificationAddress<<endl;
//    cout <<"transId   = "<<ns1__updateAgent_->transactionId << endl;

    string whofrom;
    get_connection_address(ns1__updateAgent_->soap, whofrom);

    if (ns1__updateAgent_->updater && ns1__updateAgent_->updater->__size > 0 ) 
    {
     
      // Try and save the passed updater
      ofstream updaterstream;
      
      string updaterFile=MY_APPLICATION_ENTERPRISE_HIDDEN+string("autoupdate.tgz");
      SB_make_full_path(MY_APPLICATION_ENTERPRISE_HIDDEN);

      updaterstream.open(updaterFile.c_str(),(ios_base::trunc|ios_base::out));   
      if (updaterstream.is_open())                                                
      {                                                                           
        updaterstream.write((const char*)ns1__updateAgent_->updater->__ptr, ns1__updateAgent_->updater->__size);                                          
        updaterstream.close();                                                    
        if (updaterstream.fail())                                                 
        {                                                                         
//          cout <<"Unable to save autoUpdater instructions to "<<updaterFile<<endl;
          throw (SBDispatcher_Except(500,"Unable to save autoUpdater instructions to disk -")); 
        }                                                                         
      }                                                                           
      else                                                                        
      {                                                                           
//        cout <<"Unable to save autoUpdater instructions to "<<updaterFile<<endl;
        throw (SBDispatcher_Except(500,"Unable to save autoUpdater instructions data to disk"));   
      }                                                                           

      SB_ACTION *action = new SB_ACTION;
      action->m_forceFlag = ns1__updateAgent_->forceFlag;
      action->m_action_chars += "*";
      get_connection_address(ns1__updateAgent_->soap,action->m_whofrom);
      action->m_loggingLevel = 7;
      action->m_transid=ns1__updateAgent_->transactionId;
      action->m_replyto=ns1__updateAgent_->notificationAddress;
      action->m_whofrom = whofrom;
      SB_submit_action(action, code, reason); 
      reason = "Processing AutoUpdate request";
      write_log(LOG_INFO, "AutoUpdate request being handed off to Core processing...");
    }
    else
    {
      SB_ACTION action;
      action.m_forceFlag = ns1__updateAgent_->forceFlag;
      action.m_action_chars += "*";
      action.m_loggingLevel = 7;
      action.m_transid=ns1__updateAgent_->transactionId;
      action.m_replyto=ns1__updateAgent_->notificationAddress;
      action.m_whofrom = whofrom;
      reason = sbupdate.logText();

      write_log(LOG_INFO, reason.c_str() );

      // Either way, send a notification with our results....

      ostringstream info_stream, body_stream, data_text;
      info_stream << reason;
      data_text<< "<entry name=\"action\" value=\"AutoUpdate\" />";

      body_stream <<"<details success=\"true\"><data>";
      body_stream << data_text.str() << "</data>";
      
      body_stream << "<entry name=\"task\" value=\"" ;
      body_stream << ns1__updateAgent_->transactionId ;
      body_stream << "\"/>";
      body_stream << "</details>";      
      string body_str = body_stream.str();
      string info_str = info_stream.str().c_str();
//      cout << endl << "BODY"<< endl << body_str << endl;
//      cout << endl << "INFO"<< endl << info_str << endl;
      SB_send_notification(&action,info_str,body_str,SB_AUTOUPDATE_CLIENT);
    } 
  }
  catch (SBDispatcher_Except & exc)
  {
    code=exc.m_code; 
    reason=exc.m_text.c_str();
  }
  catch (exception &exc)
  {
    code=500;
    reason=(char*)exc.what();
  }
  resp->code=code;
  resp->reasonPhrase=            soap_strdup(ns1__updateAgentResponse_->soap,reason.c_str());
  if (!body.empty()) resp->body= soap_strdup(ns1__updateAgentResponse_->soap,body.c_str());
  ns1__updateAgentResponse_->return_=resp;
  if (code==200)
  {
    write_log(LOG_DEBUG,"Request done, successful processing");
  }
  else
  {
    write_log(LOG_DEBUG,"Request failed, returning code %d -> %s",code,reason.c_str());
  }

  return SOAP_OK;
}



#define GenStub(x) \
int AgentServiceImplPortBindingService::x(ns1__##x *ns1__##x##_, ns1__##x##Response *ns1__##x##Response_) { cout <<"GENSTUB for "<<#x<<endl; return SOAP_NO_METHOD ; }


GenStub(verifyTask)
GenStub(reportStatus)
GenStub(reportInfo)
GenStub(notify)
GenStub(registerClient)
GenStub(listPackages)

