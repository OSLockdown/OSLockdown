/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*/
#ifndef __SB_TASKS_H
#define __SB_TASKS_H

#include <iostream>
#include <vector>
#include <fstream>
#include <pthread.h>

using namespace std;
#include "soapStub.h"
#include "SB_Dispatcher_Utils.h"

// we duplicate many of the structures from the actual wsdl here, just to insulate us from changes between a potentially older saved
// structure and a newer wsdl definition

class SB_TaskList;

class SB_Task
{
  friend class SB_TaskList;
  private:
    string m_actions;
    int m_hour, m_minute, m_loggingLevel,m_periodIncrement,m_periodType;
    string m_id;
    string m_notificationAddress;
    string m_verificationAddress;
    string m_whofrom;
    void clear();
    time_t m_start_time;
  public:
    void schedule();
    void write_task_file(string &dirname);
    void remove_task_file(string &dirname);
    SB_Task();
    SB_Task(string &dirname, string &filename);
    SB_Task(ns1__dispatcherTask*,char *notifyAddr=NULL,char *verifyAddr=NULL, string whofrom="");
    ~SB_Task();
    string id();
    void update(SB_Task* newtask,string taskdir);
    friend ostream & operator << (ostream &out,const SB_Task &task);
};

class SB_TaskList
{
  private:
    pthread_mutex_t m_mutex;
    vector<SB_Task*> m_tasks;
    string m_autoupdate_id;    
    string m_taskdir;
    void add_task(SB_Task *taskptr,bool write_file);
    void remove_task(SB_Task *taskptr);
  public:
    SB_TaskList(string & taskdir);
    ~SB_TaskList();
    void add_task(ns1__dispatcherTask*,char *notifyAddr=NULL,char *verifyAddr=NULL, string whofrom="");
    void add_task(string& filename);
    void remove_task(string &id);
    void cleanup(bool delete_files=false);
    string get_taskdir();
    SB_ACTION * GetScheduledTaskToDo();
    void ReSubmitTask(string transid);
    bool update_task(ns1__dispatcherTask*, char * notifyAddr=NULL,char * verifyAddr=NULL, string whofrom="");
    void ReSortTaskList();
    void dumpTaskList();
};

extern void ReadTaskFiles();
extern SB_TaskList *TaskList;
extern void TaskListInit(string &dirname);
extern void TaskListCleanUp();
extern void TaskListRemoveAllTasks();
extern void Task_format_time(time_t tasktime,char *buffer,size_t bufsize);

#endif // __SB_TASKS_H
