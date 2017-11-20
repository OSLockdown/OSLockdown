/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Information Module
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
#include "SB_Update.h"
#include "version.h"


// count the number of files in a given directory with a given suffix, such as .xml


#define RENDERPAIR(name,value) "<pair name=\"" << name << "\" value=\"" << value << "\" />"
string SB_Update::toXml(string transactionId)
{
  ostringstream message,version_id;
  string pending;
  if (m_updateRequired)
  {
    pending = "yes";
  }
  else
  {
    pending = "no";
  }
  message << "<info transactionId=\"" << transactionId << "\">";
  message << RENDERPAIR("AppVersion"     ,APPLICATION_VERS);
  message << RENDERPAIR("RelVersion"     ,SB_RELEASE);
  message << RENDERPAIR("updatePending"  ,pending);
  message << "</info>";
//  cout <<message.str()<<endl;
  return message.str();
}

bool SB_Update::updateRequired()
{ 
  return m_updateRequired;
}

string SB_Update::logText()
{
  return m_logText;
}

SB_Update::SB_Update(string version)
{
   string myVersion = string(APPLICATION_VERS);
   
   m_updateRequired = false;

   if (version != myVersion)
   {
     m_updateRequired = true;
     m_logText = "Update Required - Console version is "+ version + ", Client version is "+myVersion;
   }
   else
   {
     m_logText = "Update not required - Console and Client are version "+myVersion;
   }
}

