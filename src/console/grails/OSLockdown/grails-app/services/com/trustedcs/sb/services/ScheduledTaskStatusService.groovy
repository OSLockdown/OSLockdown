/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import com.trustedcs.sb.scheduler.ScheduledTask;
import com.trustedcs.sb.scheduler.ScheduledTaskStatus;
import com.trustedcs.sb.scheduler.ClientTaskStatus;
import com.trustedcs.sb.notification.OSLockdownNotificationEvent;
import com.trustedcs.sb.web.notifications.NotificationTypeEnum;
import com.trustedcs.sb.util.SyslogAppenderLevel;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.web.pojo.Client

class ScheduledTaskStatusService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ScheduledTaskService");

    // transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def auditLogService;
    def upstreamNotificationService
    
    // Once a task should have 'fired', how long should we wait for *any* CLient to send an update before 
    // calling this task overdue.  We keep track of the more recent received from any Client for this task
    // and apply that to the task as a whole.  Note that a RHEL6 SITG box can take 6-7 minutes to complete
    // the standard 'STIG', so this time needs to exceed that.  We're hardcoding this to 15 minutes for now.
    
    static int TASK_COMPLETION_TIMEOUT = -15
    
    def initScheduledTaskStatus()
    {
      ScheduledTask.list().each { taskData ->
        def newStatus = new ScheduledTaskStatus(taskId:taskData.id, expectedFireTime:taskData.getNextFireTime(), clientStatus: [:])
        m_log.info("Initializing task status for ${taskData}")
        newStatus.save(failOnError:true)
      }

    }


    /**
     *  Save a new/updated scheduledTaskStatus record by ID
     */
     
    def save(long taskId)
    {
      def statusInstance = ScheduledTaskStatus.findByTaskId(taskId)
      
      return save(ScheduledTask.get(taskId))
        
    }
    
    /** 
     *  Save a new/updated scheduledTaskStatus record by taskInstance
     *  
     */
    def save(ScheduledTask taskInstance)
    {
      def statusInstance = ScheduledTaskStatus.findByTaskId(taskInstance.id)
      
//      println "Asked to save id ${taskInstance.id}"
      if (!statusInstance)
      {
//        println  "Did not find taskId - creating new entry"
        statusInstance = new ScheduledTaskStatus()
        statusInstance.taskId = taskInstance.id
      }
//      statusInstance.clientStatus.each { k,v ->
//        println "---> ${k} ${v}"
//      }

      statusInstance.clientStatus.clear()
//      println "Cleared client status for ${taskInstance.id}"
      statusInstance.expectedFireTime = taskInstance.getNextFireTime()
      statusInstance.save()
      return true
    }
    
    /**
     *  Delete a status record (and the clientstatus mapping)
     */
    
    def delete(def taskId)
    {
      def statusInstance = ScheduledTaskStatus.findByTaskId(taskId)
      if (statusInstance)
      {
        statusInstance.delete();
      }
      return true
    
    }
    
    /**
     *  Register the last step that a particular Client did on a particular task
     *  Extra work, but everything we need is in the 'event' structure, so (re)parse
     *  some fields.  
     */
    def updateStatusForClient(OSLockdownNotificationEvent event)
    {
      def updateTime = new Date()
      String[] splits = event.getTransactionId().split(":");
      
      // splits should have at least 3 fields (task/group/client)  If we have a 4th field is the the index
      // of the 'action' being reported on for this schedule task (remember that a scheduled task can have multiple
      // actions [ scan/apply/scan/baseline for example]).  We will still get the 
      
      def taskIdStr = splits[0]
      def clientIdStr = splits[1]
      def subaction = -1
      if (splits.size()==4)
      {
        // if we have a subaction (SB4.1.4 or later) and only seen for a subaction notification, fill in the subaction id
        subaction = splits[3]
      }
      
      def statusInstance = ScheduledTaskStatus.findByTaskId(taskIdStr)
      if (statusInstance)
      {
//        println "Looking for ${clientIdStr}"
        def clientStatus = statusInstance.clientStatus[clientIdStr]
        if (!clientStatus) 
        {
//          println "creating new instance for ${clientIdStr}"
          statusInstance.clientStatus[clientIdStr] = new ClientTaskStatus()
        }
        statusInstance.clientStatus[clientIdStr].lastUpdateTime = updateTime
        statusInstance.clientStatus[clientIdStr].lastStatus = event.getActionType()
        
        statusInstance.save()
      }
//      println "Updating Client ${statusInstance.clientStatus[clientIdStr]}"
      return true
    }
    
    /**
     *  Return a map of the Client statuses for a particular task.  Remember that the mapping stores things
     *  as a map with strings as the keys/values, to convert back to integers
     */
     
    def getStatusForTask(def taskId)
    {
      statusMap = [:]
      def statusInstance = ScheduledTaskStatus.findByTaskId(taskId)
      if (statusInstance)
      {
        statusInstance.clientStatus { k,v ->
          statusMap[k as Integer] = v as Integer
        }
      }
      return statusMap 
    }
    
    /**
     * Return two lists of tasks, those triggering in the next 30 minutex, and those that *should* have triggered or are in progress
     * If a task has fully completed then it should not show up
     */ 
     
     def dumpIt(def text, def thislist)
     {
       println "Tasks for ${text}"
       thislist.each { foooo ->
         println "   ${foooo}"
       }
     }
     
     
     /**
      *  Go through our tasks and check the status.  Don't care about ones
      *  that are 'future', but we do need to see which ones have 'completed',
      *  are 'in progress', or 'overdue'.  To do this we look at the scheduled 
      *  fire time and subtract that from 'now'.  
      *
      *  - If positive then a future task so ignore.
      *  - We also ignore any task with no Clients in that assigned Group.
      *  - If the delta is negative then we should have fired.  
      *    - if we have a 'completion' from everyone we're done. Reschedule task.
      *    - if we haven't gotten an update from *someone* w/in a certain period of
      *    -    time, we're overdue.  Yowl and reschedule task. 
      *    - if task is even longer overdue, then also yowl and reset.   
      *  
      */

     def checkTaskStatus(Boolean rescheduleIt)
     { 
       def statusMap = [:]
       statusMap.pending = []   // anything triggering 'in the future'
       statusMap.completed = [] // anything where all tasks have completed
       statusMap.overdue = []   // anything that started more than 30 minutes ago *and* has no status within the past 15 minutes
       statusMap.active  = []   // anything else
       
       def now = new Date().getTime()
       
        ScheduledTaskStatus.list().each { task ->
            def isCompleted = true
            def atLeastOneStatus = false
            def mostRecentStatus = new Date(0)
            def extensionsList = []
            
            // we need to know how many Clients in the Group that this task is slated for
            
            def clientArray = ScheduledTask.get(task.id)?.group.clients
            def groupName = ScheduledTask.get(task.id)?.group.name
            def clientList = clientArray.collect { it ->
                it.name
            }
            def clientCount = clientList.size()

            // delta is the time difference bewteen now and when the task should have initiated, in minutes
            // delta > 0 == future task
            // dalta < 0 == task should have fired
            
            def delta = (task.expectedFireTime.getTime() - now)/60000   // remember 1000ms/sec, 60 sec/min = 60000ms/min , delta is in MINUTES
//            println "Task ${task.id} delta=${delta} clientCount=${clientCount}"
            
            if (clientCount <=0 ) 
            {
              // no clients, ignore any processing on this task
            }
            else if (delta> 0)  // task has not yet hit the trigger time
            {
               statusMap.pending << task
            }
            else  // Should have fired. Did we get every status?
            {
               // first things first, see if we got a completion from *everyone*
               task.clientStatus.each { k,v ->
                  def clientName = Client.get(k).name
                  
                  if (v.lastStatus == NotificationTypeEnum.SCHEDULED_TASK_COMPLETE.ordinal())
                  {
                    clientList = clientList - clientName 
                  }
                  if (mostRecentStatus < v.lastUpdateTime)
                  { 
                     mostRecentStatus = v.lastUpdateTime
                  }
//                  println "Checking status for ${clientName} == ${v.lastStatus} ${isCompleted} ${NotificationTypeEnum.SCHEDULED_TASK_COMPLETE.ordinal()}"
               }

               def updateDelta = (now - mostRecentStatus.getTime())/60000
               
//               println "Most recent update for task is ${mostRecentStatus} which is a delta of ${updateDelta} minutes "

               // which list should we drop this into?  These lists are returned to the caller 
               
               // a task is "complete" when all clients have reported 'done'
               // so see if 'isComplete' is true and the status count matches

               extensionsList << "cs3Label=Group"
               extensionsList << "cs3=${groupName}"
               extensionsList << "cs4Label=TaskId"
               extensionsList << "cs4=${task.id}"
               extensionsList << "cs5Label=Result"
               extensionsList << "cs5=Client task status"
               if (!clientList) 
               {
                 extensionsList << "msg=Task completed on all Clients"
                 upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.TASK_COMPLETION, "Scheduled Task Status", extensionsList)
                 statusMap.completed << task
                 if (rescheduleIt) save(task.id)
               }
               else if (delta < TASK_COMPLETION_TIMEOUT) 
               {
                 clientList.each { thisClient ->
                   def clientExtrasList = []
                   clientExtrasList << "cs2Label=Client"
                   clientExtrasList << "cs2=${thisClient}"
                   clientExtrasList << "msg=Scheduled Task did not complete on Client"
                   upstreamNotificationService.log(SyslogAppenderLevel.WARN, UpstreamNotificationTypeEnum.TASK_COMPLETION, "Scheduled Task Status", extensionsList + clientExtrasList)
                 }
                 statusMap.overdue << task
                 if (rescheduleIt) save(task.id)
               }
               else
               {
                 // task is still running, so *DO NOT* reschedule yet
                 statusMap.active << task
               }
               
            } 
        }
//        dumpIt("PENDING", statusMap.pending)
//        dumpIt("ACTIVE" , statusMap.active)
//        dumpIt("COMPLETED", statusMap.completed)
//        dumpIt("OVERDUE", statusMap.overdue)
//        dumpIt("REARM", statusMap.rearm)
        
//        return statusMap
     }
}    
