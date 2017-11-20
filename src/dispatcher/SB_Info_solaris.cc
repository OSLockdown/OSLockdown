/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Retrieve Solaris specific info
*
*/

#include <iostream>
#include <sstream>

#include <sys/utsname.h>
#include <sys/loadavg.h>
#include <sys/systeminfo.h>
#include <sys/time.h>
#include <kstat.h>
#include <errno.h>

#include "SB_Dispatcher_Utils.h"
#include "SB_Info.h"


static void
check_sysinfo(int cmd, char *buffer, int buflen)
{
  long retval=sysinfo(cmd,buffer,buflen);
  
  if (retval<0)
  {
    snprintf(buffer,buflen,"Unable to obtain");
  }
}

static long int 
check_uptime()
{
  struct timeval tp;
  long int uptime_delta;
  kstat_ctl_t *kc = 0;
  kstat_t *ksp = 0;
  kstat_named_t *kn = 0;
  
  gettimeofday(&tp,NULL);
  kc = kstat_open ();
  if (kc != 0)
  {
    ksp = kstat_lookup (kc, "unix", 0, "system_misc");
    if (ksp != 0)
    {
      if (kstat_read (kc, ksp, 0) != -1)
      {
        kn = (kstat_named_t*)kstat_data_lookup (ksp, "boot_time");
      }
    }
  }
  
  uptime_delta=tp.tv_sec -  kn->value.ul;
  return uptime_delta;
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

#define ONE_MB (1024 * 1024)

void SB_Info::populate()
{	
  struct utsname uts;	
  double loadavgs[3];
  ostringstream message;
  struct timeval tp;
  long page_size;
  long num_pages;
  long free_pages;
  longlong_t mem;
  longlong_t free_mem;
  
  gettimeofday(&tp,NULL);
  if (uname(&uts)<0 )
  {
    throw (SBDispatcher_Except(500,"Unable to obtain system information - uname"));
  }
  if (getloadavg(loadavgs,3)!=3)
  {
    throw (SBDispatcher_Except(500,"Unable to obtain system information - getloadavgs"));
  }
  m_Nodename=uts.nodename;
  m_Kernel = uts.version;
  m_Distro = string("Solaris ") + string(uts.release+2);  // strip the first two chars from the release, otherwise we'd get 5.xxx
  for (int i=0;i!=3;i++) loadavgs[i]=((int)(loadavgs[i]*100))/100.0;
  message.precision(2);
  message << "(1, 5, 15 min) "<<loadavgs[0]<<", "<<loadavgs[1]<<", "<<loadavgs[2];
  m_LoadAvg = message.str();
  message.str(""); 
  char buffer[256];
  
  check_sysinfo( SI_PLATFORM,buffer,sizeof(buffer));
  m_Arch = buffer;

  m_Uptime= check_uptime();
  
  page_size = sysconf (_SC_PAGESIZE);
  num_pages = sysconf (_SC_PHYS_PAGES);
  free_pages = sysconf (_SC_AVPHYS_PAGES);

  mem = (longlong_t) ((longlong_t) num_pages * (longlong_t) page_size);
  mem /= ONE_MB;

  free_mem = (longlong_t) free_pages *(longlong_t) page_size;
  free_mem /= ONE_MB;
  
  message.str("");
  message << (mem- free_mem) << " MB used / " << mem << " MB total";
  m_Memory=message.str();

}

