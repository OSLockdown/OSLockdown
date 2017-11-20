/**
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown State Handler Class (Header File)
*
* Simple class to retrieve information such as last action from
* the OSLockdown state file.
*
*
* Test Build:
*   g++ -o test -I../include -I/usr/include/libxml2 -DGLIBCXX_FORCE_NEW -lxml2 StateHandler.cc
*
*
*/
#ifndef __STATE_HANDLER_H
#define __STATE_HANDLER_H

#include "sbprops.h"

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>

#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <assert.h>
#include <stdlib.h>

#include <string>
#include <iostream>
#include <sstream>


class StateHandler {
 private:
  std::string filename_;
  std::string last_action_;
  std::string last_action_time_;
  bool stateFileExists();
  void load();

 public:
    StateHandler();
  void reload();
    std::string getLastAction();
    std::string getLastActionTime();
};

#endif // __STATE_HANDLER_H
