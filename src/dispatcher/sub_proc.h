/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*/
#ifndef __SUB_PROC_H
#define __SUB_PROC_H

#include <poll.h>
#include <sys/types.h>

const int RD_BUFFERSIZE=1024;  // one KB should be enought for any single line...
const int SUB_PROC_MAX_ARGS=100;

enum SUB_PROC_TERMINATION { SUB_PROC_TERM_NORMAL=0,SUB_PROC_TERM_SIGNAL, SUB_PROC_TERM_STARTUP};

using namespace std;

class SUB_PROC
{
  private:
    string m_stdoutbuffer;
    string m_stderrbuffer;
    string m_term_str;
    string m_raw_args;
    int m_num_args;
    int m_term_code;
    enum SUB_PROC_TERMINATION m_term_type;
    int m_stdout[2];
    int m_stderr[2];
    pid_t m_pid;
    string m_child_failstr;
    char m_buffer[RD_BUFFERSIZE] ; 
    string m_cmdpath,m_cmdname;
    char *m_cmdargs[SUB_PROC_MAX_ARGS] ;  // hopefully we'll never have more than 100 arsg...
    struct pollfd m_pfds[2];
    void child_path();
    void parent_path();
    void fork_and_build_fds();
    bool read_from_pfd(struct pollfd *pfd,string *buffer,string *nextstr,bool all_done=false);
    bool check_descriptors(struct pollfd *pfds,int timeout,string &stdout_str,string &stderr_str);
    void add_arg(string arg);
  public:
    SUB_PROC();
    void init();
    ~SUB_PROC();
    void set_path(string cmdpath);
    void set_execname(string cmdname);
    void dispatch(string args);
    void shutdown(string *term_str,SUB_PROC_TERMINATION *term_type,int *term_code);
    bool read_output(string *stdout_str=NULL,string *stderr_str=NULL);    
};

#endif
