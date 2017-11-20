/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Retrieve Linux Specific Info
*
*/

#include <sys/utsname.h>
#include <sys/sysinfo.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstring>
#include <sys/statvfs.h>
#include <stdlib.h>
#include "SB_Dispatcher_Utils.h"
#include "SB_Info.h"

extern string MY_APPLICATION_ASSESSMENTS;

/*
    string m_ClientVersion;
    string m_Nodename;
    string m_Kernel;

    string m_Distro;
    string m_Uptime;
    string m_Arch;
    string m_ProcCount;
    string m_Loadavg;
    string m_Memory;
*/

bool SB_Info::get_release(const char *relfilename)
{
  bool got_release=false;
  int retval=0;
  retval=access(relfilename, R_OK);
  if (retval==0)
  {
    ifstream relfile(relfilename);
    if (relfile.is_open())
    {
      string dist="",filler,version="",codename="",patch="";
      
      // SUSE/openSUSE does it a bit differently, so look explicitly for it here...
      if (strcmp(relfilename,"/etc/SuSE-release")==0)
      {
        string linetext,subline;
        istringstream thisline;
        size_t equals;

        getline(relfile,linetext);
        thisline.str(linetext);
        thisline >> dist;

        getline (relfile , linetext);
        equals=linetext.find("=");
        if (equals!=string::npos)
        {        
          version=linetext.substr(equals+2);
        }
        
        getline (relfile , linetext);
        equals=linetext.find("=");
        if (equals!=string::npos)
        {        
          patch=linetext.substr(equals+2);
        }
        
        m_Distro = dist + " " +version ;
        if (!patch.empty())
        {
          m_Distro = m_Distro + "."+ patch;
        }

      }
      else
      {
        // *EVERYONE* else seems to have 'release' in there somewhere, so split on it.
        // So basically we have <OS NAME OR NAMES> release <VERSION> <CODENAME>
        
        string word;
        vector<string> words;
        
        // get entire line into our word vector
        while (relfile)
        {
          relfile >> word;
          words.push_back(word);
        }
   
        ssize_t relIdx=-1;
        try
        {
          // *EVERYTHING* in front of 'release' is the actual distro name
          ssize_t idx=0;
          for (; idx<words.size() && words[idx] != "release"; idx++)
          {
            dist += (dist.size()==0?"":" ") + words[idx];
          }  
   
          version = words[++idx];
          codename = words[++idx];
          
        }
        catch (exception &exc)
        {
          // any problems, grab the first two words which is what we *use* to do anyway
          dist = words[0];
          version = words[1];
        } 


        relfile >> dist >> filler >>  version >> codename;
        m_Distro= dist + string(" ")+version;
        relfile.close();
      }
      got_release=true;
    }
  }
  return got_release;
}

/* populates:
  m_ClientVersion
  m_Nodename
  m_Kernel
  m_Arch
  m_LoadAvg
  m_Uptime
  m_Memory
  m_Distro
 */
void SB_Info::populate()
{                

  // use uname to get sysname,nodenmae,release, version, and machine
  struct utsname utsname;
  struct sysinfo s_info;
  double loadavgs[3];
  
  m_ClientVersion="TBD";
  if (uname(&utsname) || sysinfo(&s_info) || (getloadavg(loadavgs,3)!=3))
  {
    throw (SBDispatcher_Except(500,"Unable to obtain system information"));
  }
  
  m_Nodename=utsname.nodename;
  m_Kernel=string(utsname.sysname)+string(utsname.release);
  m_Arch= utsname.machine;

  ostringstream message;
  for (int i=0;i!=3;i++) loadavgs[i]=((int)(loadavgs[i]*100))/100.0;
  message.precision(2);
  message << "(1, 5, 15 min) "<<loadavgs[0]<<", "<<loadavgs[1]<<", "<<loadavgs[2];
  m_LoadAvg=message.str();
  message.str("");

  m_Uptime=s_info.uptime;

  message.str("");
  s_info.totalram = s_info.totalram/ (1024*1024);
  s_info.freeram  = s_info.freeram / (1024*1024);
  message << (s_info.totalram-s_info.freeram) << " MB used / " << s_info.totalram << " MB total";
  m_Memory = message.str();

  // start with redhat-release, and then code for some known variants.  First one returning true wins
  if ( !get_release("/etc/redhat-release") && 
       !get_release("/etc/SuSE-release") && 
       !get_release("/etc/fedora-release") )
  {
    m_Distro="Unknown Linux release";
  }

/*
  message<<"
                "uptime=%ld\ntotalram=%lu\nfreeram=%lu\nprocs=%d\n",
                s_info.uptime, s_info.totalram, s_info.freeram, s_info.procs);
*/  
}

