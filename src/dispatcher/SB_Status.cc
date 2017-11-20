/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Status 
*
*/

#include <iostream>
#include <sstream>

#include "SB_Dispatcher_Utils.h"
#include "SB_Status.h"

string SB_Status::renderPair(string name,string text)
{
  string outstr="<pair name=\"" + name + "\" value=\"" + text + "\" />";
  return outstr;
}


#define RENDERPAIR(name,value) "<pair name=\"" << name << "\" value=\"" << value << "\" />"
string SB_Status::toXml(string transactionId)
{
  ostringstream message;
  
  message << "<status transactionId=\"" << transactionId << "\">";
  message << RENDERPAIR("Tasking", m_action);
  message << "</status>";
  return message.str();
}

void SB_Status::populate()
{
  int foo;
}

SB_Status::SB_Status(string action)
{
  m_action=action;
//  populate();
}
