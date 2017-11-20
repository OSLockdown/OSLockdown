/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services.communication;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;

import com.trustedcs.sb.ws.client.SchedulerCommunicator;
import com.trustedcs.sb.services.client.scheduler.SchedulerResponse;

import com.trustedcs.sb.exceptions.SbScheduledTaskException;
import com.trustedcs.sb.exceptions.SchedulerCommunicationException;

import com.trustedcs.sb.services.client.scheduler.DispatcherTask;

import com.trustedcs.sb.scheduler.ScheduledTask;

class SchedulerCommunicationService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.communication.SchedulerCommunicationService");

    // transactional service
    boolean transactional = true;

    // injected services
    def messageSource;
    def grailsApplication;
    def securityProfileService;
    def baselineProfileService;

    /**
     * Update the task to the given client
     *
     * @param clientInstance
     * @param dispatcherTask
     */
    def updateTask(Client clientInstance, DispatcherTask dispatcherTask) throws SchedulerCommunicationException {
        // response from the web service
        SchedulerResponse schedulerResponse;
        try {
            // create the web service client
            SchedulerCommunicator scheduler = createSchedulerCommunicator(clientInstance);
            // make the call
            schedulerResponse = scheduler.updateTask(dispatcherTask);
        }
        catch (Exception e) {
            m_log.error("Unable to connect to and update task ${dispatcherTask.id} for client ${clientInstance.name}");
            throw new SchedulerCommunicationException(message:e.message);
        }

        // check to see if the response is an error response
        if ( !(schedulerResponse) || schedulerResponse.code >= 400 ) {
            def message;
            if ( schedulerResponse ) {
                message = schedulerResponse.reasonPhrase;
            }
            else {
                message = messageSource.getMessage("client.update.task.error",[clientInstance.name, dispatcherTask.id] as Object[], null);
            }
            throw new SchedulerCommunicationException(message:message);
        }
    }

    /**
     * Remove the task to the given client
     *
     * @param clientInstance
     * @param dispatcherTask
     */
    def removeTask(Client clientInstance, DispatcherTask dispatcherTask) throws SchedulerCommunicationException {
        // response from the web service
        SchedulerResponse schedulerResponse;
        try {
            // create the web service client
            SchedulerCommunicator scheduler = createSchedulerCommunicator(clientInstance);
            // make the call
            schedulerResponse = scheduler.removeTask(dispatcherTask);
        }
        catch (Exception e) {
            m_log.error("Unable to connect to and remove task ${dispatcherTask.id} for client ${clientInstance.name}");
            throw new SchedulerCommunicationException(message:e.message);
        }

        // check to see if the response is an error response
        if ( !(schedulerResponse) || schedulerResponse.code >= 400 ) {
            def message;
            if ( schedulerResponse ) {
                message = schedulerResponse.reasonPhrase;
            }
            else {
                message = messageSource.getMessage("client.remove.task.error",[clientInstance.name, dispatcherTask.id] as Object[], null);
            }
            throw new SchedulerCommunicationException(message:message);
        }
    }

    /**
     * Update the list of tasks given to the client
     *
     * @param clientInstance
     * @param dispatcherTaskList
     */
    def updateTaskList(Client clientInstance, List<DispatcherTask> dispatcherTaskList) throws SchedulerCommunicationException {
        // response from the web service
        SchedulerResponse schedulerResponse;
        try {
            // create the web service client
            SchedulerCommunicator scheduler = createSchedulerCommunicator(clientInstance);
            // make the call
            schedulerResponse = scheduler.updateTaskList(dispatcherTaskList);
        }
        catch (Exception e) {
            m_log.error("Unable to connect to and update task list for ${clientInstance.name}");
            throw new SchedulerCommunicationException(message:e.message);
        }

        // check to see if the response is an error response
        if ( !(schedulerResponse) || schedulerResponse.code >= 400 ) {
            def message;
            if ( schedulerResponse ) {
                message = schedulerResponse.reasonPhrase;
            }
            else {
                message = messageSource.getMessage("client.update.tasks.error",[clientInstance.name] as Object[], null);
            }
            throw new SchedulerCommunicationException(message:message);
        }
    }

    /**
     * Removes all tasks from the client
     *
     * @param clientInstance
     */
    def clearTasks(Client clientInstance) throws SchedulerCommunicationException {

        // response from the web service
        SchedulerResponse schedulerResponse;
        try {
            // create the web service client
            SchedulerCommunicator scheduler = createSchedulerCommunicator(clientInstance);
            // make the call
            schedulerResponse = scheduler.clearTasks();
        }
        catch (Exception e) {
            m_log.error("Unable to connect to and clear tasks for client ${clientInstance.name}");
            throw new SchedulerCommunicationException(message:e.message);
        }

        // check to see if the response is an error response
        if ( !(schedulerResponse) || schedulerResponse.code >= 400 ) {
            def message;
            if ( schedulerResponse ) {
                message = schedulerResponse.reasonPhrase;
            }
            else {
                message = messageSource.getMessage("client.clear.tasks.error",[clientInstance.name] as Object[], null);
            }            
            throw new SchedulerCommunicationException(message:message);
        }
    }

    /**
     * Verifies a list of tasks on the client
     *
     * @param clientInstance
     * @param dispatcherTaskList
     */
    def verifyTaskList(Client clientInstance, List<DispatcherTask> dispatcherTaskList) throws SchedulerCommunicationException {

        // response from the web service
        SchedulerResponse schedulerResponse;
        try {
            // create the web service client
            SchedulerCommunicator scheduler = createSchedulerCommunicator(clientInstance);
            // make the call
            schedulerResponse = scheduler.verifyTaskList(dispatcherTaskList);
        }
        catch (Exception e) {
            m_log.error("Unable to connect to and verify tasks for client ${clientInstance.name}");
            throw new SchedulerCommunicationException(message:e.message);
        }

        // check to see if the response is an error response
        if ( !(schedulerResponse) || schedulerResponse.code >= 400 ) {
            def message;
            if ( schedulerResponse ) {
                message = schedulerResponse.reasonPhrase;
            }
            else {
                message = messageSource.getMessage("client.verify.tasks.error",[clientInstance.name] as Object[], null);
            }
            throw new SchedulerCommunicationException(message:message);
        }
    }

    /**
     * Creates a dispatcher task with the attributes of the domain object
     * @param groupTask
     * @return a DispatcherTask that represents the group task
     */
    public DispatcherTask schedulerToDispatcherTask(ScheduledTask groupTask) {
        // create the dispatcher task
        DispatcherTask dispatcherTask = new DispatcherTask();
        // set the properties on the dispatcher task from the domain class
        dispatcherTask.actions = groupTask.actions;
        dispatcherTask.loggingLevel = groupTask.loggingLevel;
        dispatcherTask.periodType = groupTask.periodType;
        dispatcherTask.periodIncrement = groupTask.periodIncrement;
        dispatcherTask.hour = groupTask.hour;
        dispatcherTask.minute = groupTask.minute;
        // set the security profile on the dispatcher task
        if ( groupTask.group.profile ) {
            dispatcherTask.securityProfile = securityProfileService.toXmlString(groupTask.group.profile,true);
        }
        // set the baseline profile on the dispatcher task
        if ( groupTask.group.baselineProfile) {
            dispatcherTask.baselineProfile = baselineProfileService.toXmlString(groupTask.group.baselineProfile,true);
        }

        // return the created dispatcher task
        return dispatcherTask;
    }

    /**
     * Creates a web services client proxy object for a given client
     * The proxy is for the scheduler service
     *
     * @param client
     * @return schedule communicator instance
     */
    SchedulerCommunicator createSchedulerCommunicator(Client client) {

        // http(s)
    	boolean useHttps = grailsApplication.config.tcs.sb.console.secure.toBoolean();

        // create the communication client
        SchedulerCommunicator communicator = new SchedulerCommunicator(client.id,
            client.hostAddress,
            client.port,
            useHttps );

        // notification address for the response
        def notificationAddress = "${grailsApplication.config.tcs.sb.console.ip}:${grailsApplication.config.tcs.sb.console.port}"
        communicator.setNotificationAddress( grailsApplication.config.tcs.sb.console.ip, grailsApplication.config.tcs.sb.console.port);

        // return the communicator
        return communicator;
    }
}
