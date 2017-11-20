/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*
*
*/
#include <iostream>
#include <sstream>
#include <cstdio>
#include <cerrno>
#include <cstring>
#include <stdlib.h>
#include <unistd.h>
#include <poll.h>
#include <sys/types.h>
#include <signal.h>
#include <sys/wait.h>

#include "sub_proc.h"


enum { FROM_CHILD=0,TO_PARENT};


using namespace std;


void SUB_PROC::init()
{
  m_child_failstr.clear();
  m_num_args=0;
  m_cmdpath.clear();
  m_cmdname.clear();
  m_term_str.clear();
  m_raw_args.clear();
  m_stdoutbuffer.clear();
  m_stderrbuffer.clear();
  m_stdout[0]=m_stdout[1]=m_stderr[0]=m_stderr[1]=-1;
  m_term_type=SUB_PROC_TERM_NORMAL;
  m_term_code=0;
}

SUB_PROC::SUB_PROC()
{
  init();
}

SUB_PROC::~SUB_PROC()
{
}

void SUB_PROC::set_path(string cmdpath)
{
  m_cmdpath=cmdpath;
}

void SUB_PROC::set_execname(string cmdname)
{
  m_cmdname=cmdname;
}

void SUB_PROC::add_arg(string arg)
{
  if ((m_num_args+1)>=SUB_PROC_MAX_ARGS) 
  {
    m_child_failstr="Too many arguments to command - not executed";
  }
  else
  {
    m_cmdargs[m_num_args++]=strdup(arg.c_str());
  }
}

void SUB_PROC::dispatch(string args)
{
  size_t start,end;
  start=0;
  m_raw_args=args;
  while (start!=string::npos)
  {
    string token;
    end=args.find(' ',start);
    if (end!=string::npos)
    {
      token=args.substr(start,end-start);
      add_arg(token);
      end++;
    }
    else
    {
      token=args.substr(start);
      add_arg(token);
    }
    start=end;
  }
  m_cmdargs[m_num_args++]='\0';
  fork_and_build_fds();
}


void SUB_PROC::parent_path()
{
  close(m_stdout[TO_PARENT]);
  close(m_stderr[TO_PARENT]);
  m_pfds[0].fd=m_stdout[FROM_CHILD];
  m_pfds[1].fd=m_stderr[FROM_CHILD];  
}

void SUB_PROC::fork_and_build_fds()
{
  errno=0;
  if (pipe(m_stdout)<0 || pipe(m_stderr)<0)
  {
    m_child_failstr=strerror(errno);
  }
  else if ( (m_pid=fork())<0) 
  {
    m_child_failstr=strerror(errno);
  }
  else if (m_pid==0)
  {
    child_path();
  }
  else
  {
    parent_path();
    // free the command string.  Remember that the last argument is *NOT*
    // malloc-ed, but explicitly set to Null
    for (int i = 0; i< m_num_args;i++)
    {
      if (m_cmdargs[i] != '\0') free(m_cmdargs[i]);
      m_cmdargs[i] = '\0';
    }
  }
}

const char UNABLE_TO_DUP_STDOUT[]="Unable to call dup2 on stdout";
const char UNABLE_TO_DUP_STDERR[]="Unable to call dup2 on stderr";

const char STDOUT_MSG[]="should be on stdout";
const char STDERR_MSG[]="should be on stderr";


void SUB_PROC::child_path()
{
  close(m_stdout[FROM_CHILD]);
  close(m_stderr[FROM_CHILD]);

  if ( m_stdout[TO_PARENT]!=STDOUT_FILENO)
  {
    if (dup2(m_stdout[TO_PARENT],STDOUT_FILENO)!=STDOUT_FILENO)
    {
      m_child_failstr=UNABLE_TO_DUP_STDOUT;
      goto child_failure;
    }
    close(m_stdout[TO_PARENT]);
  }
  if (m_stderr[TO_PARENT]!=STDERR_FILENO)
  {
    if (dup2(m_stderr[TO_PARENT],STDERR_FILENO)!=STDERR_FILENO)
    {
      m_child_failstr=UNABLE_TO_DUP_STDOUT;
      goto child_failure;
    }
    close(m_stderr[TO_PARENT]);
  }
  errno=0;

  // We need to *explicitly* clear the mask of blocked signals here, so this mask propogates down through
  // the execv, so ultimately we can send a SIGUSR1 to the python core engine to indicate an abort...
  
  sigset_t newmask;
  sigemptyset(&newmask);  
  sigprocmask(SIG_SETMASK,&newmask,NULL);

  execv((char*)m_cmdpath.c_str(),m_cmdargs);
  // We should *only* get here if there was some sort of failure, either on setup *or* the execlp failed...
  m_child_failstr="FATAL: Unable to spawn command -> ";
  m_child_failstr+= m_cmdpath.c_str();
  m_child_failstr+= " ";
  m_child_failstr+= strerror(errno);
  m_child_failstr+= "\n";

child_failure:
  write(STDERR_FILENO,m_child_failstr.c_str(),m_child_failstr.length());
//  cout <<"ERROR: CHILD FAILED  - "<<m_child_failstr<<endl;
  exit(-1);
}

// return false only if pipe closed *and* all data has been read...
bool SUB_PROC::read_from_pfd(struct pollfd *pfd,string *databuffer,string *nextstr, bool all_done)
{
  bool retval=true;
  int numread=0;
  
  m_buffer[0]='\0';
  if (nextstr) nextstr->clear();
  if (pfd->revents & POLLIN)
  {
    numread=read(pfd->fd,m_buffer,RD_BUFFERSIZE-1);
    if (numread>0)					    
    { 
      m_buffer[numread]='\0';
      databuffer->append(m_buffer);
//      cout <<"--> pipe "<<pfd->fd<<" read "<<numread<<" -> "<<m_buffer;
    }
    retval=numread;
  }
  if (!databuffer->empty() && nextstr)
  {
    size_t eol=databuffer->find_first_of("\n\r");
    if (eol!=string::npos) 
    {
      nextstr->append(databuffer->substr(0,eol+1));
      databuffer->erase(0,eol+1);
//      cout <<"PFD "<<pfd->fd<<" string returns "<<(*nextstr)<<" with "<<databuffer->length()<<" to go"<<endl;
    }
    else if (all_done)
    {
      nextstr->append(databuffer->substr(0));
//      cout <<"PFD "<<pfd->fd<<" string flusheded "<<(*nextstr)<<endl;
      databuffer->clear();
    }
  }
  else if (pfd->revents & POLLHUP)
  {
    retval=false;
//    cout <<" --> pipe "<<pfd->fd<<" hangup"<<endl;
  }
//  cout <<"PFD "<<pfd->fd<<" return "<<retval<<endl;
  return retval;
  
}

// returns true if EOF detected on either stdout or stderr

bool SUB_PROC::read_output(string *stdout_str,string *stderr_str)
{
  int numread_stdout=0,numread_stderr=0;
  int poll_res;
  size_t eol;
  bool good_read=true;
  
  if (!m_child_failstr.empty()) 
  {
    m_stderrbuffer=m_child_failstr;
    good_read=false;
  }
  else
  {
    errno=0;
    m_pfds[0].events=POLLIN;
    m_pfds[1].events=POLLIN;

    if (stdout_str) stdout_str->clear();
    if (stderr_str) stderr_str->clear();
    poll_res=poll(m_pfds,2,100);  // wait at most 100 ms for something to arrive 
    if (poll_res>0) 
    {
    // check stderr and stdout.  Only if *both* return closed pipes (false) trigger a shutdown
      int closed=0;
      if (!read_from_pfd(&m_pfds[1],&m_stderrbuffer,stderr_str,false)) closed++;
      if (!read_from_pfd(&m_pfds[0],&m_stdoutbuffer,stdout_str,false)) closed++;
      if (closed==2)
      {
    	good_read=false;
	// process any characters left in the buffers
        read_from_pfd(&m_pfds[1],&m_stderrbuffer,stderr_str,true);
        read_from_pfd(&m_pfds[0],&m_stdoutbuffer,stdout_str,true);
      }
    }
  }
#if 0
  printf("good_read=%d poll_res=%d  out=%x/%d  err=%x/%d\n", good_read,poll_res,
           m_pfds[0].revents,numread_stdout,
	   m_pfds[1].revents,numread_stderr);
#endif
  return good_read;
}

void SUB_PROC::shutdown(string *term_str,SUB_PROC_TERMINATION *term_type, int *term_code)
{
  int waitstat,status,signum;
  ostringstream msg("Normal completion");
  pid_t ret_stat;
  int thissig;
  
//  cout <<"Waiting for "<<m_pid<<endl;
  // close the descriptors from the child
  close(m_pfds[0].fd);
  close(m_pfds[1].fd);
  
  ret_stat=0;
  // do we have an exit code already?
  for (int i=0; i!= 5 && ret_stat==0; i++ )
  {
    ret_stat=waitpid(m_pid,&waitstat,WNOHANG);
    if (ret_stat==0)
    {
//      cout <<"..."<<endl;
      sleep(1);
    }
  }
//  cout <<"RET_STAT is "<<ret_stat<<" and waitstat is "<<waitstat <<endl;
  if (ret_stat<0)
  {
    m_term_code=errno;
    msg.str("");
    msg<<"Got '"<<strerror(errno)<<"' from waitpid -returning -1"<<endl;
  }
  else if (ret_stat==m_pid)
  {
    if (WIFSIGNALED(waitstat))
    {
      m_term_code=WTERMSIG(waitstat);
      msg.str("");
      msg<<"Process died with signal "<<m_term_code;
    }
    else
    {    
      m_term_code=WEXITSTATUS(waitstat);
      msg.str("");
      msg<<"Process returned with exitcode "<<m_term_code;
      if (m_term_code != 0 ) 
      {
        m_term_type = SUB_PROC_TERM_STARTUP;
      }
    }
  }
  else
  {
    
  // Nope - terminate with prejudice
    thissig=SIGTERM;
    msg.str("Process not terminated, sending SIGTERM");
    kill(m_pid,SIGTERM);
    ret_stat=waitpid(m_pid,&status,5);  // give it 5 seconds to die... 
    if (ret_stat==0) 
    {
      thissig=SIGKILL;
      msg.str("Process not terminated, sending SIGKILL");
      kill(m_pid,SIGKILL); // if it didn't die after 5 seconds, terminate with prejudice
    }
  }
/*
  cout <<"TERM_STR  "<<msg.str()<<endl;
  cout <<"TERM_TYPE "<<m_term_type<<endl;
  cout <<"TERM_code "<<m_term_code<<endl;
*/
  
  if (term_str) (*term_str)=msg.str();
  if (term_type) (*term_type)=m_term_type;
  if (term_code) (*term_code)=m_term_code;
}

