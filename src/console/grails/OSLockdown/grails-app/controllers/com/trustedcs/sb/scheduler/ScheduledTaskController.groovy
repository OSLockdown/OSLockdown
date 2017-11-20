/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.scheduler;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.ws.client.SchedulerCommunicator;
import com.trustedcs.sb.services.client.scheduler.DispatcherTask;
import com.trustedcs.sb.scheduler.ScheduledTaskStatus;
import grails.util.Environment;

import com.trustedcs.sb.exceptions.SbScheduledTaskException;
import com.trustedcs.sb.exceptions.SbGroupException;
import com.trustedcs.sb.exceptions.SchedulerCommunicationException;
import org.quartz.CronExpression
import org.quartz.CronScheduleBuilder
import org.quartz.TriggerBuilder
import com.trustedcs.sb.web.notifications.NotificationTypeEnum;


import java.text.MessageFormat;

class ScheduledTaskController {

    // injected services
    def messageSource;
    def scheduledTaskService;
    def schedulerCommunicationService;
    def auditLogService;
    def periodicService
    def scheduledTaskStatusService;
    
    //  logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.scheduler.ScheduledTaskController");

    static def taskActions = ["s":"Scan",
                              "a":"Apply",
                              "b":"Baseline"];

    // Hours range starts with 12 and then proceeds with 1 through 11, as that is the asc order for the hours
    // (ie. 12:15 am is before 1:15 am and so on)
    static final HOURS_RANGE = [12,1,2,3,4,5,6,7,8,9,10,11]

    /**
     * Shows the list of tasks
     */
    def index = {
    	redirect(action:'list')
    }

    /**
     * Shows the list of tasks
     */
    def list = {
        params.max = Math.min( params.max ? params.max.toInteger() : 25,  100);
        def taskList =  ScheduledTask.createCriteria().list() {
            order('group','desc')
            order('periodType','asc')
            order('periodIncrement','asc')
            order('hour','asc')
            order('minute','asc')
            maxResults(params.max)
            if ( params.offset ) {
            	firstResult(params.offset.toInteger())
            }
        }
    
        // Testing only
        def taskStatusMap = []
        
        ScheduledTaskStatus.list().each { taskStatus ->
            taskStatusMap << determineIndividualTaskStatus(taskStatus)
        }
//    	println "taskStatusMap = ${taskStatusMap}"
        [taskList:taskList,
            taskInstanceTotal:ScheduledTask.count(),
            taskStatusMap:taskStatusMap];
    }

    def determineIndividualTaskStatus(def taskStatus)
    {
        def detail = [:]
        def taskData = ScheduledTask.get(taskStatus.taskId as Integer)
        def statusString = "Unknown"
        def allClientsReportDone = true
        def now = new Date()
        
        // what Clients are supposed to be in the group for this task
        def clients = taskData.group.clients

        // ok, get some data and start prepping our 'status'
        detail.group = taskData.group.name
        detail.expectedFireTime = taskStatus.expectedFireTime
        detail.status = "Unknown"
        detail.allClientsReportDone = true  // assume true, mark any failures
        detail.lastUpdate = null 

        // what is the relative time difference between now and the 'expected' time?
        
        def deltaTimeSecs = (now.getTime() - detail.expectedFireTime.getTime())/1000
        
        // start with blank client details
        detail.clientDetails = []
        
        // Only check for the Clients we *expect* to see because they are in the group
        // we could wind up with a 'race' if someone mods a Group right as a trigger time hits 
        // race here would be Group is modified but the firetime has already passed on the Client, so it
        // schedules the task for the 'next' trigger time.
        
        def expectedClients = taskData.group.clients
        
        // what Clients are in (i.e. - have reported) status for this job
        def sts = ScheduledTaskStatus.findByTaskId(taskStatus.taskId)
        expectedClients.each { clientInfo ->
          def clientStr = clientInfo.id as String 
          def cdata = sts.clientStatus[clientStr]
          def clientStatus = cdata?.lastStatus
          def clientUpdate = cdata?.lastUpdateTime
          
          detail.clientDetails << [name:clientInfo.name, status:clientStatus, update:clientUpdate] 
          
        }
        return detail
    }



    /**
     * Create a new task
     */
    def create = {
        [groupList:Group.withCriteria { order('name','asc') },
            taskActions:taskActions, hoursRange:HOURS_RANGE];
    }

    /**
     * Save the created task
     */
    def save = {
        m_log.info("Save Task ${params}");
    	clearFlash();

    	// task
    	ScheduledTask taskInstance = new ScheduledTask(params);

        // model that contains all required objects for redisplay of the create
        // page
        def errorModel = [
            groupList:Group.withCriteria { order('name','asc') },
            taskActions:taskActions, hoursRange:HOURS_RANGE];

        // actions
        def actions = request.getParameterValues('taskAction');

        try {
//            println taskInstance
//            println params
//            println actions as List <String>
            scheduledTaskService.save(taskInstance,params,actions as List<String>);
            auditLogService.logTask("add",taskInstance.taskIdentifier);
            // create the dispatcher task for the web service
            DispatcherTask dispatcherTask = schedulerCommunicationService.schedulerToDispatcherTask(taskInstance);
            // send each client a dispatcher task via web services
            taskInstance.group.clients?.each { client ->
                // set the dispatcher task's id
                dispatcherTask.id = "${taskInstance.id}:${client.id}:${taskInstance.group.id}";
                try {
                    schedulerCommunicationService.updateTask(client,dispatcherTask);
                }
                catch ( SchedulerCommunicationException communicationException ) {
                    m_log.error("Client ${client.name} was unable to add task ${dispatcherTask.id} : ${communicationException.message}");
                    flash.error += "Client ${client.name} was unable to add the task [${communicationException.message}]<br>";
                }
            }
        }
        catch( SbScheduledTaskException e ) {
            flash.error += g.renderErrors(bean:e.scheduledTaskInstance,as:"list");
            errorModel['task'] = e.scheduledTaskInstance;
            render(view:'create',model:errorModel);
            return;
        }
        catch( SbGroupException e ) {
            flash.error += g.renderErrors(bean:e.groupInstance,as:"list");
            errorModel['task'] = taskInstance;
            render(view:'create',model:errorModel);
            return;
        }

    	// return to the task list
    	redirect(action:'list');
    }

    /**
     * Edits a task for the given id in the parameters
     */
    def edit = {
        // find the task
    	ScheduledTask task = ScheduledTask.get(params.id);

        // if the task doesn't exist return the list
        if ( !task ) {
            flash.error = messageSource.getMessage("scheduledTask.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }

        // return the model
    	[task:task,
            groupList:Group.withCriteria { order('name','asc') },
            taskActions:taskActions, hoursRange:HOURS_RANGE];
    }

    /**
     * Save the modified task
     */
    def update = {
        m_log.info("Update Task ${params}");
    	clearFlash();

    	// task
    	ScheduledTask taskInstance = ScheduledTask.get(params.id);

        // the old group
        Group oldGroup = taskInstance.group;

        // model that contains all required objects for redisplay of the create
        // page
        def errorModel = [
            groupList:Group.withCriteria { order('name','asc') },
            taskActions:taskActions, hoursRange:HOURS_RANGE];

        // actions
        def actions = request.getParameterValues('taskAction');

        try {
            // update the task with service
            scheduledTaskService.update(taskInstance,params,actions as List<String>);
            // audit logs
            auditLogService.logTask("modify",taskInstance.taskIdentifier);

            // create the dispatcher task for the web service
            DispatcherTask dispatcherTask = schedulerCommunicationService.schedulerToDispatcherTask(taskInstance);

            // did the group change?
            if ( oldGroup != taskInstance.group ) {
                m_log.info("Group changed for the task");
                // remove the task from the old group's clients
                oldGroup.clients?.each { client ->
                    // set the dispatcher task's id
                    dispatcherTask.id = "${taskInstance.id}:${client.id}:${taskInstance.group.id}";
                    try {
                        schedulerCommunicationService.removeTask(client,dispatcherTask);
                    }
                    catch ( SchedulerCommunicationException communicationException ) {
                        m_log.error("Client ${client.name} was unable to remove task ${dispatcherTask.id} : ${communicationException.message}");
                        flash.error += "Client ${client.name} was unable to remove the task [${communicationException.message}]<br>";
                    }
                }
            }

            // update the client's with the modified tasks
            taskInstance.group.clients?.each { client ->
                // set the dispatcher task's id
                dispatcherTask.id = "${taskInstance.id}:${client.id}:${taskInstance.group.id}";
                try {
                    schedulerCommunicationService.updateTask(client,dispatcherTask);
                }
                catch ( SchedulerCommunicationException communicationException ) {
                    m_log.error("Client ${client.name} was unable to update task ${dispatcherTask.id} : ${communicationException.message}");
                    flash.error += "Client ${client.name} was unable to update the task [${communicationException.message}]<br>";
                }
            }
        }
        catch( SbScheduledTaskException e ) {
            flash.error += g.renderErrors(bean:e.scheduledTaskInstance,as:"list");
            errorModel['task'] = e.scheduledTaskInstance;
            render(view:'create',model:errorModel);
            return;
        }
        catch( SbGroupException e ) {
            flash.error += g.renderErrors(bean:e.groupInstance,as:"list");
            errorModel['task'] = taskInstance;
            render(view:'create',model:errorModel);
            return;
        }

    	// return to the task list
    	redirect(action:'list');
    }

    /**
     * Delete a list of tasks
     */
    def deleteMulti = {
    	clearFlash();
        // clear flash
        flash.error = "";

        // get the ids of baseline profile
        def ids = request.getParameterValues('taskList')?.collect { id ->
            id.toLong();
        }

        // delete each group in the list
        m_log.info("delete task ids" + ids);
        String taskIdentifier;
        def taskInstance;
        ids.each { id ->
            taskInstance = ScheduledTask.get(id);
            if ( taskInstance ) {
                try {
                    taskIdentifier = taskInstance.taskIdentifier;

                    // update the client's with the modified tasks
                    taskInstance.group.clients?.each { client ->
                        // set the dispatcher task's id
                        DispatcherTask dispatcherTask = schedulerCommunicationService.schedulerToDispatcherTask(taskInstance);

                        dispatcherTask.id = "${taskInstance.id}:${client.id}:${taskInstance.group.id}";
                        try {
                            schedulerCommunicationService.removeTask(client,dispatcherTask);
                        }
                        catch ( SchedulerCommunicationException communicationException ) {
                            m_log.error("Client ${client.name} was unable to remove task ${dispatcherTask.id} : ${communicationException.message}");
                            flash.error += "Client ${client.name} was unable to remove task ${dispatcherTask.id} : [${communicationException.message}]<br>";
                        }
                    }

                    scheduledTaskService.delete(taskInstance,true);                    
                    auditLogService.logTask("delete",taskIdentifier);
                }
                catch ( SbScheduledTaskException e ) {
                    flash.error += g.renderErrors(bean:e.scheduledTaskInstance);
                }
            }
            else {
                flash.error += messageSource.getMessage("task.not.found",[id] as Object[],null);
            }
        }
    	flash.message = "$ids.size Tasks attempted to be deleted";
    	redirect(action:'list');
    }

    /**
     * Verifies that the given task has been successfully registered
     * on all the clients
     */
    def verifyTask = {
    	// ??? NEED IMPLEMENTATION ???
    	flash.warning = "Needs Implementation"
        redirect(action:"list");
    }

    /**
     * Verifies multiple tasks
     */
    def verifyMulti = {
        clearFlash();

        // get the list of task ids
        def taskIds = request.getParameterValues('taskList').collect { id ->
            id.toLong();
        }

        // scheduled task
        ScheduledTask scheduledTask;
        // Map< groupId , List< taskId > >
        def groupsMap = [:];
        taskIds.each { id ->
            scheduledTask = ScheduledTask.get(id);
            if ( !groupsMap[scheduledTask.group.id] ) {
            	groupsMap[scheduledTask.group.id] = [];
            }
            groupsMap[scheduledTask.group.id] << id;
        }

        m_log.info("Groups Map: ${groupsMap}");

        // dispatcher communcation objects
        def dispatcherTask;
        def dispatcherTaskList;
        def group;
        MessageFormat dispatcherTaskIdFormat;

        // iterater over the group ids so that we can verify task lists on the client
        groupsMap.each { groupId, taskIdList ->

            // find the correct group
            group = Group.get(groupId);

            // create the dispatcher task list for the given ids
            taskIdList.each { taskId ->
                dispatcherTaskList = [];
                scheduledTask = ScheduledTask.get(taskId);
                dispatcherTask = schedulerCommunicationService.schedulerToDispatcherTask(scheduledTask);
                // template for the dispatcher task id
                dispatcherTaskIdFormat = new MessageFormat("${scheduledTask.id}:{0}:${group.id}");
                dispatcherTaskList << dispatcherTask;


                // invoke the dispatcher task verification on each client in the group
                group.clients?.each { client ->
                    // set id on the task for the individual client "${taskId}:${clientId}:${groupId}"
                    // using the created message format ( dispatcherTaskIdFormat )
                    dispatcherTaskList.each { task ->
                        task.id = dispatcherTaskIdFormat.format([client.id] as Object[]);
                        m_log.info ( "modified task id = ${task.id}" );
                    }
                    // communication service invocation
                    try {
                        schedulerCommunicationService.verifyTaskList(client,dispatcherTaskList);
                    }
                    catch ( SchedulerCommunicationException communicationException ) {
                        m_log.error("Client ${client.name} was unable to verify task list : ${communicationException.message}");
                        flash.error += "Client ${client.name} was unable to verify task list [${communicationException.message}]<br>";
                    }
                }
            }
        }

    	redirect(action:'list');
    }

    // AJAX METHODS
    def addTaskAction = {
    	[taskActions:taskActions]
    }

    def removeTaskAction = {

    }

    /**
     * Clear flash scope of messages
     */
    private clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }
    def foobar () {     
	      scheduledTaskStatusService.checkTaskStatus(false)
          periodicService.listSchedulerDetails()      
	      redirect (action:"list");     
	    }
}
