/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown - Test Shims
*
*/
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <fstream>
#include <vector>
#include <cstdio>

#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

using namespace std;
bool use_https=true;

static void tweak_sigmask(int sig, int how)
{
  sigset_t signal_set;
  
  sigemptyset(&signal_set);
  sigaddset(&signal_set,sig);
  pthread_sigmask(how,&signal_set,NULL);
}

void
spawnit(string cmd)
{
  if (fork()==0)
  {
    system(cmd.c_str());
  }
  else
  {
    return;
  }
}

void
spawn_kids(string exec_name,string shimname,int port, int num_shims)
{
  int idx=1;  
  while (num_shims>0)
  {
    ostringstream cmd;
    
    cmd.str("");
    cmd<<exec_name<<" -o -p "<<port<<" -z "<<shimname<<"_"<<idx;
    if (!use_https) cmd << " -S ";
    spawnit(cmd.str());
    port++; idx++; num_shims--;
  }
}

void
usage(char *execcmd)
{
  cout <<"Usage : "<<execcmd<<" -e <execname> -z <shimbasename> -p <startport> -n <num> "<<endl;
  cout <<"\t\texecname     = full path to OSL_Dispatcher"<<endl;
  cout <<"\t\tshimbasename = leading part of name used for shim clients"<<endl;
  cout <<"\t\tstartport    = what port number to start shims listening at"<<endl;
  cout <<"\t\tnum          = how many shims to start"<<endl;
  cout <<endl;
  cout <<"Example: "<<execcmd<<" -e /sbin/OSL_Dispatcher -z foo -p 9000 -n 5"<<endl;
  cout << "is equivalent to one shell starting the following:"<<endl;
  cout << "\tOSL_Dispatcher -o -p 9000 -z foo_1"<<endl;
  cout << "\tOSL_Dispatcher -o -p 9001 -z foo_2"<<endl;
  cout << "\tOSL_Dispatcher -o -p 9002 -z foo_3"<<endl;
  cout << "\tOSL_Dispatcher -o -p 9003 -z foo_4"<<endl;
  cout << "\tOSL_Dispatcher -o -p 9004 -z foo_5"<<endl;
}

int main(int argc,char *argv[])
{
  string shim_name,exec_name;
  int intarg;
  int port;
  int num_shims;
  int c,signum;
  bool have_e,have_p,have_z,have_n;
  struct timespec waittime={1,0}; // a one-second wait
  
  have_e=have_p=have_z=have_n=false;
  while ((c = getopt (argc, argv, "e:p:z:n:S")) != -1)
  {
    switch (c)
    {
      case 'S':
         use_https=false;
	 break;
      case 'h': 
         usage(argv[0]); 
         exit (0); 
         break;
      case 'e':
         have_e=true;
         exec_name=optarg;
         break;
      case 'z':
        have_z=true;
        shim_name=optarg;
	break;
      case 'p': 
        intarg=atoi(optarg);
        port=intarg;
        have_p=true;
//        if (intarg>8080) port=intarg;
        break;
      case 'n':
        num_shims=atoi(optarg);
        have_n=true;
        break;
      default:
        usage(argv[0]); 
        exit(1);
        break;
    }
    
  }
  if (!(have_e&have_p&have_z&have_n)) 
  { 
    usage(argv[0]);
     exit (1);
  }
  setsid ();
  pid_t pgrp=getpgrp();
  
  tweak_sigmask(SIGINT,SIG_BLOCK);  
  spawn_kids(exec_name,shim_name,port,num_shims);
  
  sigset_t signal_set;
  sigemptyset(&signal_set);
  sigaddset(&signal_set,SIGINT);
  while(1)
  {
    if ((signum=sigtimedwait(&signal_set,NULL,&waittime))>0)
    if (signum==SIGINT)
    {
      cout <<"KILLING!"<<endl;
      killpg(0,9);
      break;
    }
  }  
}
