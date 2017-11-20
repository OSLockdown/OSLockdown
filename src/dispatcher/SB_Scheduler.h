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
#ifndef __SB_SCHEDULER_H
#define __SB_SCHEDULER_H

#include "SB_Tasks.h"


extern void ReadTaskFiles();
extern SB_TaskList *TaskList;
extern void TaskListInit(string &dirname);
extern void TaskListCleanUp();
#endif // __SB_SCHEDULER_H
