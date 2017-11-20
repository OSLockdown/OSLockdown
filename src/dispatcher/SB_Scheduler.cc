/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Scheduler
*
*/
#include <vector>
#include <syslog.h>
#include <dirent.h>
#include "SB_Tasks.h"
#include "SB_Scheduler.h"
#include "SB_Dispatcher_Utils.h"

SB_TaskList *TaskList=NULL;

// quick and dirty, do we have two colons...
static int validtaskfile(const struct dirent *dirent)
{
  int colons=0;
  int retval=0;
  
  char *ptr=(char*)dirent->d_name;
  do 
  {
    ptr=strchr(ptr,':');
    if (ptr) 
    {
      colons++;
      ptr++;
    }
  } while (ptr!=NULL);
  if (colons==2) retval=1;
  return retval;
}

void ReadTaskFiles()
{
  struct dirent **namelist;
  int n;
  SB_Task *task;
  string taskdir=TaskList->get_taskdir();
  n = scandir(taskdir.c_str(), &namelist, validtaskfile, alphasort);
  if (n < 0)
    perror("scandir");
  else {
    while(n--) {
      string filename=namelist[n]->d_name;
      write_log(LOG_INFO,"Reading Taskfile %s",namelist[n]->d_name);
      TaskList->add_task(filename);
      free(namelist[n]);
    }
    free(namelist);
  }  
}

void
TaskListInit(string &dirname)
{
  TaskList=new SB_TaskList(dirname);
}

void
TaskListCleanUp()
{
  TaskList->cleanup();
}
