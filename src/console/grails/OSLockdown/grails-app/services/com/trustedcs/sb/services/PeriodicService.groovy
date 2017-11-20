/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import com.trustedcs.sb.preferences.UpstreamNotificationFlag
import org.apache.log4j.Logger;
import groovy.time.TimeCategory

import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.util.ConsoleTaskPeriodicity
import com.trustedcs.sb.util.SyslogAppenderLevel;
import com.trustedcs.sb.scheduler.ScheduledTask;
import com.trustedcs.sb.scheduler.ScheduledTaskStatus;
import com.trustedcs.sb.scheduler.ClientCommStatus;
import com.trustedcs.sb.web.pojo.Client;

// Quartz imports
import org.quartz.JobBuilder;
import org.quartz.JobDetail;   
import org.quartz.TriggerBuilder;   
import org.quartz.SimpleScheduleBuilder;   
import org.quartz.CronScheduleBuilder;   
import org.quartz.CronTrigger
import org.quartz.Scheduler;
import org.quartz.CalendarIntervalScheduleBuilder;   
import org.quartz.JobKey;   
import org.quartz.TriggerKey;   
import org.quartz.DateBuilder;   
import org.quartz.impl.matchers.KeyMatcher;   
import org.quartz.impl.matchers.GroupMatcher;   
import org.quartz.impl.matchers.AndMatcher;   
import org.quartz.impl.matchers.OrMatcher;   
import org.quartz.impl.matchers.EverythingMatcher;
import org.quartz.impl.StdSchedulerFactory;


// gpars for worker group
import  grails.async.*
//import groovyx.gpars.scheduler.DefaultPool

class PeriodicService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.");

    // Transactional
    static transactional = false
    static String lastSynopsis = ""
    
    def upstreamNotificationService
    // Reference to Grails application.
    def grailsApplication
    
    def quartzScheduler
    def dispatcherCommunicationService
    def scheduledTaskService
    def scheduledTaskStatusService

    private void checkLicense () {
        
        try {
            def logLevel = SyslogAppenderLevel.INFO
            def logIt = false
            def reason
            
            String licSynopsis = SbLicense.instance.licenseSynopsis()
            if (lastSynopsis != licSynopsis) {
//                println "LAST SYNOPSYS = ${lastSynopsis}"
//                println "THIS SYNOPSYS = ${licSynopsis}"
            }
            reason = "License valid"
            if (licSynopsis.contains("invalid")) {
                logLevel = SyslogAppenderLevel.ERROR
                logIt = true
                reason = "License invalid"
            }
            else if (licSynopsis.contains("expires")) {
                logLevel = SyslogAppenderLevel.WARN
                logIt = true   
                reason = "License expiring"
            }
            else if (lastSynopsis != licSynopsis){
                logIt = true
                lastSynopsis = licSynopsis
                reason = "License change"
            }
            
            lastSynopsis = licSynopsis
            
            if (logIt) {
                def extensionsList = []
                extensionsList << "cs5Label=Result"
                extensionsList << "cs5License check"
                extensionsList <<  "msg=${licSynopsis}"
                upstreamNotificationService.log(logLevel, UpstreamNotificationTypeEnum.APP_LICENSE, "App Status", extensionsList );
            
            }
        } catch (Throwable t) {
            println "${t}"
        }
    }

    void initializeAllJobs()
    {
       
       scheduledTaskStatusService.initScheduledTaskStatus()
       UpstreamNotificationFlag.list().each { flag ->
         def taskName = flag.upstreamNotificationType.quartzJobName
         if (flag.periodicity.valid)
         {
           updateTasking(taskName, flag.periodicity.cronexpr, flag.enabled)
         }
       }
    }

    
    void updateTasking(String taskName, String cronexpr, Boolean enabled)
    {
      String triggerName = "com.trustedcs.sb.timers.${taskName}Trigger"     
      TriggerKey triggerKey = TriggerKey.triggerKey(triggerName, "SBTimers")
      String jobName = "com.trustedcs.sb.timers.${taskName}Job"
      JobKey jobKey = JobKey.jobKey(jobName, "SBTimers")
      
      // Do we have a valid trigger already?
      if (quartzScheduler.getTrigger(triggerKey))
      {
        m_log.info("Removing existing task for ${taskName}")
        quartzScheduler.unscheduleJob(triggerKey)
      }

      if (enabled)
      {
        JobDetail jobDetail = quartzScheduler.getJobDetail(jobKey)
        CronTrigger trigger = TriggerBuilder.newTrigger()
           .withIdentity("com.trustedcs.sb.timers.${taskName}Trigger", "SBTimers")
           .withSchedule(CronScheduleBuilder.cronSchedule(cronexpr))
           .forJob(jobName, "SBTimers")
           .build();
     
        quartzScheduler.scheduleJob(trigger)
        m_log.info("Scheduled new execution time for for ${taskName} at ${trigger.getNextFireTime()}")
      } 
    }
    
    void rescheduleAllJobs()
    {
      // First things first, go delete *all* triggers
      // We know one trigger per job, so build the individual triggerkeys and pop 'em before rescheduling a new job
       UpstreamNotificationFlag.list().each { flag ->
         if (flag.valid)
         {
           String taskName = flag.upstreamNotificationType.quartzJobName
           String jobName = "com.trustedcs.sb.timers.${taskName}Job"
           JobKey jobKey = JobKey.jobKey(jobName, "SBTimers")
           String triggerName = "com.trustedcs.sb.timers.${taskName}Trigger"     
           TriggerKey triggerKey = TriggerKey.triggerKey(triggerName, "SBTimers")
           quartzScheduler.unscheduleJob(triggerKey)
           
           // reschedule
           def trigger = TriggerBuilder.newTrigger()
              .withIdentity(triggerName, "SBTimers")
              .withSchedule(CronScheduleBuilder.cronScheduler(flag.periodicity.cronexpr))
              .build();
         } 
       }
    }
    
    // debug routine if required
    void listSchedulerDetails()
    {
      quartzScheduler.getJobGroupNames().each { group ->

        quartzScheduler.getJobKeys(GroupMatcher.jobGroupEquals(group)).each { jobKey ->
            def jobName = jobKey.getName()

            println "  Job -> ${jobName} ->"
            println "    jobClass -> ${quartzScheduler.getJobDetail(jobKey).jobClass} ::::"
            println "    Durable -> ${quartzScheduler.getJobDetail(jobKey).isDurable()} ::::"
            quartzScheduler.getTriggersOfJob(jobKey).each { trigger ->
                println "    Trigger -> ${trigger.getNextFireTime()} "
            }
        }
      }
    }

    void initScheduledTaskStatus()
    {
      taskList.each { taskData ->
        if (!ScheduledTaskStatus.findByTaskId(taskData.id))
        {
          def newStatus = new ScheduledTaskStatus(taskId:taskData.id, expectedFireTime:taskData.expectedFireTime, clientStatus: [:])
          newStatus.save()
        }
      }
    }

    // Here's the guts of the checkTask job
    void checkTasksCore()
    {
      scheduledTaskStatusService.checkTaskStatus(true)

//      def now = new Date()
//      println "Got here check task ${now}"
    }


    // Here's the guts of the checkTask job


    void checkClientsCore()
    {
      // only check if the notification is actually enabled...
      
      if (UpstreamNotificationFlag.findByUpstreamNotificationType(notif).enabled)    
      {
        def map = new PromiseMap()
        def results = [:]
        def now = new Date()      
      
        Client.list().each { client ->
          map[client.name] = { dispatcherCommunicationService.pingDispatcher(client) }
        }
        results = map.get()
           
        // iterate over the results, we've kept the last known ping status in the in-memory DB
        // so the only time we don't repeat a status is if the box is in a reachable state.
              
        results.each {box,state ->
          def extensionsList = []
          def boxHistory
          def logLevel = SyslogAppenderLevel.INFO
          boxHistory = ClientCommStatus.findByClientName(box)
          if (!boxHistory) {
            boxHistory = new ClientCommStatus()
            boxHistory.clientName = box
          }
          extensionsList << "dhost=${box}"
          extensionsList << "msg=${state.trim()}"
          extensionsList << "cs5Label=Result"
          extensionsList << "cs5=Check client"
          if (state == "Ok")
          {
//            println "BOX ${box} is good"
            if (boxHistory.lastState != state)
            {
//              println "   -> was ${boxHistory.lastState}"
            }
          }
          else
          {
              logLevel = SyslogAppenderLevel.WARN
//            println "BOX ${box} is bad -> ${boxHistory.lastState} : ${state}"
          }
          upstreamNotificationService.log(logLevel, UpstreamNotificationTypeEnum.CLIENT_STATUS, "App Status",  extensionsList)
          boxHistory.lastState = state
          boxHistory.lastCheck = now
          boxHistory.save()
        }
      }
    }
}
