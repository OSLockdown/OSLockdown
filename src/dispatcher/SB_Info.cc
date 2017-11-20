/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Information Module
*
*
*/

#include <iostream>
#include <sstream>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/unistd.h>
#include <errno.h>
#include <string.h>
#include "SB_Dispatcher_Utils.h"
#include "SB_Info.h"
#include "version.h"


extern string MY_APPLICATION_ASSESSMENTS;
extern string MY_APPLICATION_APPLY_REPORTS;
extern string MY_APPLICATION_UNDO_REPORTS;
extern string MY_APPLICATION_BASELINES;
extern string MY_APPLICATION_ASSESSMENT_COMPS;
extern string MY_APPLICATION_BASELINE_COMPS;
extern DISPATCHER_OPTS disp_opts;

// count the number of files in a given directory with a given suffix, such as .xml

void SB_Info::countFilesInDir(string dname, string suffix, string label, string& results)
{
   DIR *dptr=NULL;
   struct dirent *dent=NULL;
   int numfiles=0;
   size_t lastdot;
   string filename;
   double totalsize=0;
   int errors=0;
   string averagesize;
   
   dptr=opendir(dname.c_str());
   if (dptr!=NULL)
   {
     string fullpath;
     struct stat statbuf;
     while ((dent=readdir(dptr)))
     {
       filename=dent->d_name;
       lastdot=filename.rfind('.');
       if (lastdot!=string::npos)
       {
         if (filename.substr(lastdot)==suffix)
	 {
	   fullpath=dname+"/"+filename;
	   if (stat(fullpath.c_str(),&statbuf)==0)
	   {
	     totalsize+=statbuf.st_size;
	   }
	   else
	   {
	     errors++;
	   }
	   numfiles++;	   
	 }
       }
     }
     closedir(dptr);
   }
   else
   {
     write_log(LOG_WARNING, "Unable to open %s", dname.c_str());
     numfiles=-1;
   }
   
   ostringstream ostr;
   if (numfiles<0)
   {
     ostr<<"Unable to count "<<label<<" reports";
   }
   else if (numfiles==0)
   {
     ostr<<"No "<<label<<" reports found";
   }
   else
   {
     ostr<<"Found "<<numfiles<<" "<<label << " report";
     if (numfiles>1)
     {
       ostr<<"s";
     }
   }
   if (numfiles>0) 
   {
     string sizerange;
     totalsize/=numfiles;
     if (totalsize>(1024*1024)) 
     {
       totalsize/=(1024*1024);
       sizerange=" MB";
     }
     else if (totalsize>1024)
     {
       totalsize/=1024;
       sizerange=" KB";
     }
     ostr<<"(avgsize="<<(long)(totalsize+0.5)<<sizerange<<")";
     averagesize=ostr.str();
     
   }
   results=ostr.str();
}

string SB_Info::renderPair(string name,string text)
{
  string outstr="<pair name=\"" + name + "\" value=\"" + text + "\" />";
  return outstr;
}

// use m_Uptime as as seconds of uptime, so tell us how many days, hours, and minutes we've been up
string SB_Info::MakeTimeLengthString()
{
  ostringstream message;
  string timestring;
  int count,days, hours, minutes, seconds;
  
  long int elapsed=m_Uptime;
  days = elapsed/86400; elapsed=elapsed%86400;
  hours = elapsed/3600; elapsed=elapsed%3600;
  minutes = elapsed/60; elapsed=elapsed%60;
  seconds = elapsed;
//  cout << "uptime="<<m_Uptime<< " d="<< days <<" h="<< hours << " m="<<minutes << " s="<<seconds<<endl;
  count=0;
  if ((days>0) && (count<2))  
  {
    message<<", "<<days<<" day";
    if (days>1) message<<"s";
    count++;
  }
  if ((hours>0) && (count<2)) 
  {
    message<<", "<<hours<<" hour";
    if (hours>1) message<<"s";
    count++;
  }
  if ((minutes>0) && (count<2))
  {
    message<<", "<<minutes<<" minute";
    if (minutes>1) message<<"s";
    count++;
  }
  if ((seconds>0) && (count<2))  
  {
    message<<", "<<seconds<<" second";
    if (seconds>1) message<<"s";
    count++;
  }
  timestring=message.str();
  return timestring.substr(2);
}


#define RENDERPAIR(name,value) "<pair name=\"" << name << "\" value=\"" << value << "\" />"
string SB_Info::toXml(string transactionId)
{
  ostringstream message,version_id;
  version_id << APPLICATION_NAME <<" " << APPLICATION_VERS << "-" << SB_RELEASE;
  message << "<info transactionId=\"" << transactionId << "\">";
  message << RENDERPAIR("ClientVersion"     ,version_id.str());
  message << RENDERPAIR("Nodename"          ,m_Nodename);
  message << RENDERPAIR("Distro"            ,m_Distro);
  message << RENDERPAIR("Kernel"            ,m_Kernel);
  message << RENDERPAIR("Uptime"            ,MakeTimeLengthString());
  message << RENDERPAIR("Arch"              ,m_Arch);
//  message << RENDERPAIR("ProcCount"        ,m_ProcCount);
  message << RENDERPAIR("Loadavg"           ,m_LoadAvg);
  message << RENDERPAIR("Memory"            ,m_Memory);
  message << RENDERPAIR("Assessments"       ,m_assessments);
  message << RENDERPAIR("Assessments-Comps" ,m_assessment_comps);
  message << RENDERPAIR("Apply-rpts"        ,m_apply_rpts);
  message << RENDERPAIR("Undo-rpts"         ,m_undo_rpts);
  message << RENDERPAIR("CoreHours"         ,m_corehours);
  message << RENDERPAIR("MaxLoad"           ,m_maxload);
  message << RENDERPAIR("Baselines"         ,m_baselines);
  message << RENDERPAIR("Baseline-Comps"    ,m_baseline_comps);
  message << RENDERPAIR("ReportDirStats"    ,m_reportDirStats);
  message << "</info>";
  cout <<message.str()<<endl;
  return message.str();
}


void SB_Info::getLoadTimeRestrictions()
{
  ostringstream message;

  if ((disp_opts.start_time < 0) || (disp_opts.end_time<0) )
  {
    m_corehours = "None";
  }
  else
  {
    ostringstream message;
    message << ShowAsTwelveHourClock(disp_opts.start_time) << " - " << ShowAsTwelveHourClock(disp_opts.end_time);
    m_corehours = message.str();
  }

  message.str("");

  if (disp_opts.max_load != 0)
  {
    message << disp_opts.max_load;
    m_maxload = message.str();
  }
  else
  {
    m_maxload = "None";
  }
}


SB_Info::SB_Info()
{
  getLoadTimeRestrictions();
  populate();  // os dependent, look in SB_Info_linux.cc or SB_Info_solaris.cc
  ReportDirStats();
  countFilesInDir(MY_APPLICATION_ASSESSMENTS,      ".xml", "assessment",      m_assessments);
  countFilesInDir(MY_APPLICATION_APPLY_REPORTS,    ".xml", "apply",   m_apply_rpts);
  countFilesInDir(MY_APPLICATION_UNDO_REPORTS,     ".xml", "undo",    m_undo_rpts);
  countFilesInDir(MY_APPLICATION_BASELINES,        ".xml", "baseline",        m_baselines);
  countFilesInDir(MY_APPLICATION_ASSESSMENT_COMPS, ".xml", "assessment-comp", m_assessment_comps);
  countFilesInDir(MY_APPLICATION_BASELINE_COMPS,   ".xml", "baseline-comp",   m_baseline_comps);
}

void SB_Info::ReportDirStats()
{
  struct statvfs mystatvfs;
  
  errno=0;
  if (statvfs(MY_APPLICATION_ASSESSMENTS.c_str(),&mystatvfs))
  {
    m_reportDirStats=strerror(errno);
  }
  else if (mystatvfs.f_blocks<1)
  {
    m_reportDirStats="No space left on device";
  }
  else
  {
#if 0
    cout <<"f_blocks "<<mystatvfs.f_blocks<<endl;
    cout <<"f_bavail "<<mystatvfs.f_bavail<<endl;
    cout <<"f_bsize  "<<mystatvfs.f_bsize<<endl;
    cout <<"f_frsize "<<mystatvfs.f_frsize<<endl;
#endif
    double scaling=(mystatvfs.f_frsize)/(1024.0*1024.0);  // start with a scaling factor to return the results in MB free.
    long perc_free=((mystatvfs.f_bavail*100)/mystatvfs.f_blocks);
    long free_size=(long)(mystatvfs.f_bavail*scaling);
    string sizerange;
    
    sizerange=" MB";
    if (free_size>1024) 
    {
      free_size/=1024;
      sizerange=" GB";
    }
    
    ostringstream ostr;
    ostr<<perc_free<<" % free, ("<<free_size<<sizerange<<" avail)";
    m_reportDirStats=ostr.str();
  }
}
