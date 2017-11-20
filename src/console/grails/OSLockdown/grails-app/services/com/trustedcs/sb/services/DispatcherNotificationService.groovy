/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

// web service notification listener classes
import com.trustedcs.sb.notification.OSLockdownNotificationListener;
import com.trustedcs.sb.notification.OSLockdownNotificationEvent;

// domain object
import com.trustedcs.sb.web.notifications.Notification;
import com.trustedcs.sb.web.notifications.NotificationException;
import com.trustedcs.sb.web.notifications.NotificationTypeEnum;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.scheduler.ScheduledTask;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;

// service exception
import com.trustedcs.sb.exceptions.DispatcherNotificationException;
import com.trustedcs.sb.util.SyslogAppenderLevel;

class DispatcherNotificationService implements OSLockdownNotificationListener {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.DispatcherNotificationService");

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def reportsService;
    def scheduledTaskStatusService;
    def upstreamNotificationService;     
    /**
     * Saves the notification
     *
     * @param notificationInstance
     */
    def save(Notification notificationInstance) {
        // save Notification to the database
        if (!notificationInstance.hasErrors() && notificationInstance.save()) {
            m_log.info("Notification Saved");
        }
        else {
            m_log.error("Unable to save Notification");
            notificationInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new DispatcherNotificationException(notificationInstance:notificationInstance);
        }
    }

    /**
     *  Deletes the given notification
     *
     *  @param notificationInstance
     */
    def delete(Notification notificationInstance) {
        // delete from db
        notificationInstance.delete();
        // iterate errors
        if ( notificationInstance.hasErrors() ) {
            notificationInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new DispatcherNotificationException(notificationInstance:notificationInstance);
        }
    }

    /**
     * NotificationListener method that is called by the web service when a notification
     * is recieved from a client.  This method is responsible for peristing the
     * notification to the database after parsing its notification body.
     *
     * @param event
     */
    public void notificationReceived(OSLockdownNotificationEvent event) {
        // persist the event
    	try {
            // create the time stamp
            Calendar calendar = Calendar.getInstance();
            Date date = calendar.getTime();

            // get the source id
            String sourceId;
            String taskId;
            // get the transaction id to parse
            String transactionId = event.getTransactionId();
            def extensionsList = []
            
//            println "EVENT -> ${transactionId} ${event.getActionType()}"
            
            // if there is a transaction id split it and find out the source id
            if ( transactionId ) {
                String[] splits = transactionId.split(":");
                if ( splits ) {
                    taskId = splits[0];
                    switch ( event.getActionType() ) {
                        case NotificationTypeEnum.SCHEDULED_SCAN.ordinal() :
                        case NotificationTypeEnum.SCHEDULED_QUICK_SCAN.ordinal() :
                        case NotificationTypeEnum.SCHEDULED_APPLY.ordinal() :
                        case NotificationTypeEnum.SCHEDULED_BASELINE.ordinal() :
                        case NotificationTypeEnum.SCHEDULED_TASK_COMPLETE.ordinal() :
                        // client
                        sourceId = splits[1];
                        break;
                        case NotificationTypeEnum.GROUP_ASSESSMENT.ordinal() :
                        // group
                        sourceId = splits[0];
                        break;
                        default:
                        // client
                        sourceId = splits[0];
                        break;
                    }
                }
            }

            // get the datamap
            def dataMap = event.getDataMap();
            if ( !dataMap ) {
                dataMap = [:];
            }

            // set the source id on the datamap
            if ( sourceId ) {
                dataMap['sourceId'] = sourceId;
            }

            // create the notification
            Notification notification = new Notification(timeStamp:date,
                transactionId:transactionId,
                type:event.getActionType(),
                successful:event.wasSuccessful(),
                aborted:event.wasAborted(),
                info:event.getInfo(),
                sourceId:sourceId,
                client:Client.get(sourceId),
                dataMap:dataMap);
            notification.hasFileName = 'fileName' in notification.dataMap.keySet()

            // get the exception list
            Map<String,List<String>> exceptionMap = event.getExceptionMap();
            exceptionMap.each { level, messages ->
                messages.each { message ->
                    notification.addToExceptions(new NotificationException(level:level,message:message));
                }
            }

            // save the notification domain class
            try {
                save(notification);
                
                // Ok, if this task has the genDelta flag set, then 
                // go ahead and try and generate a delta report of the most recent *two* reports.
                // note we're checking scan only right now looking for 'new' problems.  Haven't figured
                // out exactly how to check for Dispatcher.
                
		if (taskId)
		{
		    def taskInst = ScheduledTask.get(taskId)
                    def genDelta = taskInst?.genDelta
                    def groupName = taskInst?.group?.name
//                    println "GenDelta for task ${taskId}  is ${genDelta} - event data = ${event.wasSuccessful()} "
                
                
                    scheduledTaskStatusService.updateStatusForClient(event) 
                    extensionsList << "cs2Label=Client"
                    extensionsList << "cs2=${Client.get(sourceId)?.name}"
                    extensionsList << "cs3Label=Group"
                    extensionsList << "cs3=${groupName}"
                    extensionsList << "cs4Label=TaskId"
                    extensionsList << "cs4=${taskId}"
                
                    switch ( event.getActionType() ) {
                    	case NotificationTypeEnum.SCHEDULED_SCAN.ordinal() :
                    	    if (event.wasSuccessful() && ( genDelta == true)) {
                    		reportsService.generateComparisonFromScheduledTask(event)
                    	    }
                    	    // Explicit fall through....
                       case NotificationTypeEnum.SCHEDULED_BASELINE.ordinal() : 	       
                       case NotificationTypeEnum.SCHEDULED_APPLY.ordinal() :
                    	    extensionsList << "reason=Client completed ${NotificationTypeEnum.getDisplayString(event.getActionType())} action"
                    	    upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.TASK_RPT_STATUS,"Scheduled Task Status", extensionsList);   
                    	    break
                       case NotificationTypeEnum.SCHEDULED_TASK_COMPLETE.ordinal() :
                    	    extensionsList << "reason=Client completed all actions"
                    	    upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.TASK_RPT_STATUS,"Scheduled Task Status", extensionsList);   
                    	    break
                    																					     	 							 
                    }
		}
            }
            catch ( DispatcherNotificationException dispatcherNotificationException ) {
                m_log.error("Unable to persist notification : ${dispatcherNotificationException.message}");
            }
    	}
    	catch ( Exception e ) {
            m_log.error("Unable to persist notification : ${event}",e);
    	}
    }

    /**
     * Method not implemented
     *
     * @param notificationEvent
     */
    public void infoReceived(OSLockdownNotificationEvent notificationEvent) {
        m_log.info(notificationEvent.toString());
    }

    /**
     * Method not implemented
     *
     * @param notificationEvent
     */
    public void statusReceived(OSLockdownNotificationEvent notificationEvent) {
        m_log.info(notificationEvent.toString());
    }
}
