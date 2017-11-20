/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*
*/
#include <fstream>
#include <vector>
#include <syslog.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include "SB_Tasks.h"
#include "SB_time_code.h"
#include "SB_Dispatcher_Utils.h"

extern DISPATCHER_OPTS disp_opts;


ostream & operator << (ostream &out,const SB_Task &task)
{
  out <<"notificationAddress "<< task.m_notificationAddress<<endl;
  out <<"verificationAddress "<< task.m_verificationAddress<<endl;
  // whofrom may or may not be valid - if empty, don't say anything
  if (!task.m_whofrom.empty()) out <<"whofrom "<< task.m_whofrom<<endl;
  out <<"actions "<< task.m_actions<<endl;
  out <<"hour "<< task.m_hour<<endl;
  out <<"minute "<<task.m_minute<<endl;
  out <<"loggingLevel "<<task.m_loggingLevel<<endl;
  out <<"periodIncrement "<< task.m_periodIncrement<<endl;
  out <<"periodType "<< task.m_periodType<<endl;
  return out;
}

void SB_Task::clear()
{
  m_actions="";
  m_hour=0;
  m_minute=0;
  m_loggingLevel=LOG_INFO;
  m_periodIncrement=0;
  m_periodType=0;
  m_id="";
  m_notificationAddress="";
  m_start_time=0;
}

SB_Task::SB_Task()
{
  clear();
}

SB_Task::SB_Task(string &dirname, string &filename)
{
  clear();
  m_id=filename;
  string fullname=dirname+filename;  // dirname *should* end with a '/'
  try
  {  
    ifstream taskfile(fullname.c_str());
    string taskvalue,tasktag;
    size_t equalsign;
    do
    {
      taskfile >> tasktag;
      if (taskfile.good())
      {
        if      (tasktag=="notificationAddress")    taskfile>>m_notificationAddress;	
        else if (tasktag=="verificationAddress")    taskfile>>m_verificationAddress;	
        else if (tasktag=="whofrom")                taskfile>>m_whofrom;	
        else if (tasktag=="actions")                taskfile>>m_actions;
        else if (tasktag=="hour")                   taskfile>>m_hour;
        else if (tasktag=="minute")                 taskfile>>m_minute;
        else if (tasktag=="loggingLevel")           taskfile>>m_loggingLevel;
        else if (tasktag=="periodIncrement")        taskfile>>m_periodIncrement;
        else if (tasktag=="periodType")            {  taskfile>>m_periodType; break; }  // This should be the *LAST* element
        else {
          ostringstream message;
          message << "Invalid field found in task file (" << tasktag << ")";
          throw (message.str());
        }
      } else {
        throw ("Unexpected end of file");
      }
    } while (taskfile.good());

    taskfile.close();
  }
  catch (exception &exc)
  {
    throw (exc.what());
  }
}

void 
SB_Task::update(SB_Task* newtask, string taskdir)
{
  if ((m_actions!=newtask->m_actions)                 ||
      (m_hour!=newtask->m_hour)                       ||
      (m_minute!=newtask->m_minute)                   ||
      (m_loggingLevel!=newtask->m_loggingLevel)       ||
      (m_periodIncrement!=newtask->m_periodIncrement) ||
      (m_periodType != newtask->m_periodType)         ||
      (m_notificationAddress != newtask->m_notificationAddress) ||
      (m_verificationAddress != newtask->m_verificationAddress) ||
      (m_whofrom != newtask->m_whofrom) 
     )
  {
    m_actions=newtask->m_actions;  	      
    m_hour=newtask->m_hour;		      
    m_minute=newtask->m_minute;		      
    m_loggingLevel=newtask->m_loggingLevel;      
    m_periodIncrement=newtask->m_periodIncrement;
    m_periodType = newtask->m_periodType; 
    m_whofrom = newtask->m_whofrom;
    m_notificationAddress = newtask->m_notificationAddress;
    m_verificationAddress = newtask->m_verificationAddress;       
    write_log(LOG_INFO,"Task %s details changed",m_id.c_str());
    write_task_file(taskdir);
    schedule();
  }
}

SB_Task::SB_Task(ns1__dispatcherTask* task,char *notifyAddr, char *verifyAddr, string whofrom)
{

  clear();
  m_actions=task->actions;
  m_hour=task->hour;
  m_minute=task->minute;
  m_loggingLevel=task->loggingLevel;
  m_periodIncrement=task->periodIncrement;
  m_periodType=task->periodType;
  m_id=task->id;
  if (notifyAddr) m_notificationAddress=notifyAddr;
  if (verifyAddr) m_verificationAddress=verifyAddr;
  m_whofrom = whofrom;
}


void SB_Task::schedule()
{
  char timebuf[50];  

  m_start_time=CalculateStartTime(m_hour, m_minute, m_periodType, m_periodIncrement);
//  ctime_r(&m_start_time,timebuf);
  Task_format_time(m_start_time,timebuf,sizeof(timebuf));
  write_log(LOG_INFO,"Task %s scheduled for %s",m_id.c_str(),timebuf);
}

// Blind overwrite
void SB_Task::write_task_file(string &dirname)
{
  try 
  {
    string filename=dirname+m_id;
    ofstream taskfile(filename.c_str());
    if (taskfile.fail()) throw (SBDispatcher_Except(500,"Unable to open Task file"));
    taskfile << *this;
    taskfile.close();
  }
  catch(exception &exc)
  {
    write_log(LOG_ERR,"Unable to write task file -> %s",exc.what());
  }
}

void SB_Task::remove_task_file(string &dirname)
{
  string filename=dirname+m_id;
  struct stat statbuf;
  
  if ((stat(filename.c_str(),&statbuf)==0) && (S_ISREG(statbuf.st_mode)))
  {
    if (unlink(filename.c_str()))
    {
      ostringstream message;
      message <<"Unable to delete Taskfile -> "<<strerror(errno);
      throw (SBDispatcher_Except(500,message.str().c_str()));
    }
  }
  else
  {
    ostringstream message;
    message <<"Unable to delete Taskfile -> "<<strerror(errno);
    write_log(LOG_WARNING, message.str().c_str());
//    throw (SBDispatcher_Except(500,message.str().c_str()));
  }
}

string SB_Task::id()
{
  return m_id;
}

SB_Task::~SB_Task()
{
}

// None of the SB_Task methods need mutex protection, but *almost all* of the SB_TaskList methods should
SB_TaskList::SB_TaskList(string& taskdir)
{ 
  write_log(LOG_DEBUG,"Initializing tasklist.");
  pthread_mutex_init(&m_mutex,NULL);
  m_taskdir=taskdir;
}

SB_TaskList::~SB_TaskList()
{
  cout <<" DELETING TASKLIST !"<<endl;
}

void SB_TaskList::add_task(SB_Task *taskptr,bool write_file)
{
  taskptr->schedule();
  remove_task(taskptr->m_id);
  pthread_mutex_lock(&m_mutex);
  try 
  { 
    m_tasks.push_back(taskptr);
  }
  catch (exception & exc)
  {
    taskptr->remove_task_file(m_taskdir);
    write_log(LOG_ERR,"Unable to add taskfile %s",taskptr->id().c_str());
  }
  pthread_mutex_unlock(&m_mutex);
  if (write_file) taskptr->write_task_file(m_taskdir);
}

void SB_TaskList::remove_task(SB_Task *taskptr)
{
}

void SB_TaskList::add_task(ns1__dispatcherTask* task,char *notifyAddr, char *verifyAddr, string whofrom)
{

  if ((task->actions[0] != '*') && (!insideCoreHours(task->hour)))
  {
    ostringstream msg;
    write_log(LOG_WARNING, "Unable to add task %s - would execute inside of core hours." , task->id);
    msg <<"Task would execute inside core business hours ";
    msg << "(hours are between "<<ShowAsTwelveHourClock(disp_opts.start_time) << " and "<< ShowAsTwelveHourClock(disp_opts.end_time) <<").  " ;
    msg << "Please schedule for a different time.  Task dropped on client.";
    throw (SBDispatcher_Except(409,msg.str().c_str()));
  }

  SB_Task *taskptr= new SB_Task(task,notifyAddr,verifyAddr, whofrom);
  add_task(taskptr,true);  // new task, write task file
}

bool SB_TaskList::update_task(ns1__dispatcherTask* task, char * notifyAddr, char * verifyAddr, string whofrom)
{

//  dumpTaskList();

  if ((task->actions[0] != '*') && (!insideCoreHours(task->hour)))
  {
    string tempId = task->id;
    remove_task(tempId);
    ostringstream msg;
    write_log(LOG_WARNING, "Unable to add/update task %s - would execute inside of core hours - dropping task." , task->id);
    msg <<"Updated tasking would execute inside core business hours ";
    msg << "(hours are between "<<ShowAsTwelveHourClock(disp_opts.start_time) << " and "<< ShowAsTwelveHourClock(disp_opts.end_time) <<").  " ;
    msg << "Please schedule for a different time.  Task dropped on client.";
    throw (SBDispatcher_Except(409,msg.str().c_str()));
  }

  SB_Task temptask(task,notifyAddr, verifyAddr, whofrom);
  bool updated_task=false;

  pthread_mutex_lock(&m_mutex);
  for (size_t i=0;i!=m_tasks.size();i++)
  {
    if (task->id==m_tasks[i]->m_id)
    {
      m_tasks[i]->update(&temptask,m_taskdir);
      updated_task=true;
      break;
    }
  }
  pthread_mutex_unlock(&m_mutex);
  return updated_task;
}

void SB_TaskList::add_task(string& filename)
{
  SB_Task *taskptr= new SB_Task(m_taskdir, filename);

  add_task(taskptr,false);  // getting task from file, don't re-write
}

string SB_TaskList::get_taskdir()
{
  string taskdir;

  pthread_mutex_lock(&m_mutex);
  taskdir=m_taskdir;
  pthread_mutex_unlock(&m_mutex);
  return taskdir;
}

void SB_TaskList::remove_task(string &id)
{
  pthread_mutex_lock(&m_mutex);
  
  
  SB_Task *taskptr=NULL;
  
  for (vector<SB_Task*>::iterator taskiter= m_tasks.begin() ; taskiter!= m_tasks.end() ; taskiter++)
  {
    if ((*taskiter)->id()==id)
    {
      taskptr=*taskiter;
      m_tasks.erase(taskiter);
      break;
    }
  }
  pthread_mutex_unlock(&m_mutex);
  if (taskptr) taskptr->remove_task_file(m_taskdir);
  delete taskptr;
}

void SB_TaskList::dumpTaskList()
{
  pthread_mutex_lock(&m_mutex);
  
  
  cout <<" Currently have " << m_tasks.size() << " tasks" << endl;
  SB_Task *taskptr=NULL;
  
  for (vector<SB_Task*>::iterator taskiter= m_tasks.begin() ; taskiter!= m_tasks.end() ; taskiter++)
  {
    cout << " Task  <" << (*taskiter)->id() << "> " <<endl; //RMS
  }
  pthread_mutex_unlock(&m_mutex);
}

void SB_TaskList::cleanup(bool delete_files)
{
  pthread_mutex_lock(&m_mutex);
  SB_Task *taskptr=NULL;
  for (vector<SB_Task*>::iterator taskiter= m_tasks.begin() ; taskiter!= m_tasks.end() ; taskiter++)
  {
    taskptr=*taskiter;
    if (delete_files) taskptr->remove_task_file(m_taskdir);
    delete taskptr;
  }
  m_tasks.clear();
  pthread_mutex_unlock(&m_mutex);
}

void SB_TaskList::ReSortTaskList()
{
  
}

// Return the next scheduled action - note that autoupdate requests take precedent over *EVERYTHING* else here
SB_ACTION* SB_TaskList::GetScheduledTaskToDo()
{
  SB_ACTION *action=NULL;
  SB_Task *taskptr=NULL;
  
  pthread_mutex_lock(&m_mutex);
  if (m_tasks.size()>0)
  {   
    char timebuf[50];
    struct timeval tv;
    gettimeofday(&tv,NULL);
    const time_t nowtime=tv.tv_sec;
//    char *timestr=ctime_r(&nowtime,timebuf);
      Task_format_time(nowtime,timebuf,sizeof(timebuf));
//    cout <<"Nowtime is "<<nowtime<< "   "<<timebuf << endl;
    for (size_t i=0;i!=m_tasks.size();i++)
    { 
      if ( m_tasks[i]->m_actions == "*" ) 
      {
        taskptr = m_tasks[i];
        break;
      }
      Task_format_time(m_tasks[i]->m_start_time,timebuf,sizeof(timebuf));
//      cout <<"Task "<<m_tasks[i]->m_id<<" scheduled for "<<m_tasks[i]->m_start_time<<"  "<<timebuf << endl;  //ctime puts a \n char on 
      if ((m_tasks[i]->m_start_time==0) || (m_tasks[i]->m_start_time>nowtime) )continue;  // unscheduled or 'not yet' ignore
      if ( (taskptr==NULL) || 
           (taskptr->m_start_time> m_tasks[i]->m_start_time))
      {
/**/        cout <<"  Using "<<m_tasks[i]->m_id<<endl;
        taskptr=m_tasks[i];
      }
    }
    if (taskptr)
    {
      try
      {
        action=new SB_ACTION(taskptr->m_id, taskptr->m_notificationAddress,false);
        action->m_action_chars=taskptr->m_actions;
        action->m_loggingLevel=taskptr->m_loggingLevel;
        action->m_baseline_profilepath="";  // profile path will be set later...
        action->m_security_profilepath="";  // profile path will be set later...
        action->m_from_console=false;
        action->m_verifyaddr=taskptr->m_verificationAddress;
        action->m_whofrom = taskptr->m_whofrom;
        taskptr->m_start_time=0;
        // Note that shcheduled tasks are Enterprise *ONLY*, so mark it as such to generate transient key
        action->m_prodtype = CLIENT_ENTERPRISE;
      }
      catch (...)
      {
        write_log(LOG_ERR,"Unable to invoke scheduled action %s, rescheduling...",taskptr->m_actions.c_str());
        taskptr->schedule();
      }
    }
  }
  pthread_mutex_unlock(&m_mutex);
  return action;
}

void SB_TaskList::ReSubmitTask(string transid)
{
  pthread_mutex_lock(&m_mutex);
  for (size_t i=0;i!=m_tasks.size();i++)
  {
    if (m_tasks[i]->m_id==transid)
    {
      m_tasks[i]->schedule();
      break;
    }
  }
  pthread_mutex_unlock(&m_mutex);
}


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
      try {
        TaskList->add_task(filename);
      }
      catch (string exc) {
        write_log(LOG_ERR, "%s : %s", namelist[n]->d_name, exc.c_str());
      }
      catch (const char *exc) {
        write_log(LOG_ERR, "%s : %s", namelist[n]->d_name, exc);
      }
      catch (char *exc) {
        write_log(LOG_ERR, "%s : %s", namelist[n]->d_name, exc);
      }
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
TaskListRemoveAllTasks()
{
  struct dirent **namelist;
  int n;
  SB_Task *task;

  write_log(LOG_INFO,"Removing all in memory tasks for Client");
  TaskList->cleanup(true);

  write_log(LOG_INFO, "Removing all on disk task files for Client");  
  string taskdir=TaskList->get_taskdir();
  n = scandir(taskdir.c_str(), &namelist, validtaskfile, alphasort);

   
  if (n < 0)
    perror("scandir");
  else {
    while(n--) {
      string filename=taskdir + namelist[n]->d_name;
      write_log(LOG_INFO,"Removing Taskfile %s",filename.c_str());
      unlink(filename.c_str());
      free(namelist[n]);
    }
    free(namelist);
  }  
}

void
TaskListCleanUp()
{
  TaskList->cleanup(false);
  delete TaskList;
}

void
Task_format_time(time_t tasktime,char *buffer,size_t bufsize)
{
  struct tm time_fields;
  localtime_r(&tasktime,&time_fields);
  strftime(buffer,bufsize,"%A %B %d, %Y at %T",&time_fields);
}
