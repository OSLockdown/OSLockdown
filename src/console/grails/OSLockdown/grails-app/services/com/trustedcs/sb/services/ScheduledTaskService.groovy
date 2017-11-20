/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import com.trustedcs.sb.scheduler.ScheduledTask;
import com.trustedcs.sb.exceptions.SbScheduledTaskException;

import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.exceptions.SbGroupException;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

class ScheduledTaskService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ScheduledTaskService");

    // transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def auditLogService;
    def scheduledTaskStatusService
    
    /**
     * Saves the specified task to the database
     *
     * @param taskInstance
     */
    def save(ScheduledTask taskInstance) {
        // save group to the database
        if (!taskInstance.hasErrors() && taskInstance.save()) {
            m_log.info("Task Saved");
            scheduledTaskStatusService.save(taskInstance)
        }
        else {
            m_log.error("Unable to save Task");
            taskInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbScheduledTaskException(scheduledTaskInstance:taskInstance);
        }
    }

    /**
     * Saves the specified group to the database for task association chaining
     *
     * This method is replicated from the groupService due to the fact that we
     * would get a bidirection dependency issue if groupService was attempted
     * to be included in this service.
     *
     * @param groupInstance
     */
    def saveGroup(Group groupInstance) {
        // save group to the database
        if (!groupInstance.hasErrors() && groupInstance.save()) {
            m_log.info("Saved group");
        }
        else {
            m_log.error("Unable to save Group");
            groupInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbGroupException(groupInstance:groupInstance);
        }
    }

    /**
     * Saves the specified task to the database based on 12 hour am/pm clock params passed from the UI
     * which are being adjusted for the 24 hour clock for persistence by this method.
     *
     * @param taskInstance
     * @param params
     * @param actions
     */
    def save(ScheduledTask taskInstance, Map params, List<String> actions) {

        // find out the sequence of actions for the task. The actions are combined
        // into a single string without a delimiter using the first letter of the action
        // as its value.
        def actionString = "";
        actions.each {
            actionString += it;
        }
        taskInstance.actions = actionString;

        // group assignment
        Group group = Group.get(params.groupId);
        taskInstance.group = group;

        // compute hours based on am/pm
        computeHoursForSavingBasedOnAmPm( taskInstance )

        m_log.info(taskInstance);

        // save the task instance
        save(taskInstance);

        // add the task to the group
        group.addToTasks(taskInstance);
        saveGroup(group);

    }

    /**
     * Updates the task in the database based on 12 hour am/pm clock params passed from the UI
     * which are being adjusted for the 24 hour clock for persistence by this method.
     *
     * @param taskInstance
     */
    def update(ScheduledTask taskInstance, Map params, List<String> actions) {
        // update the instance with the params map
        taskInstance.properties = params;

        // find out the sequence of actions for the task. The actions are combined
        // into a single string without a delimiter using the first letter of the action
        // as its value.
        def actionString = "";
        actions.each {
            actionString += it;
        }
        taskInstance.actions = actionString;

        // group assignment
        Group group = Group.get(params.groupId);
        if ( group != taskInstance.group ) {
            // TODO : remove task from old group
            def oldGroup = taskInstance.group;
            oldGroup.removeFromTasks(taskInstance);
            // add task to new group
            group.addToTasks(taskInstance);
            // set new group on task
            taskInstance.group = group;
            // save old group
            saveGroup(oldGroup);
        }

        // compute hours based on am/pm
        computeHoursForSavingBasedOnAmPm( taskInstance )

        m_log.info(taskInstance);

        // save the task instance
        save(taskInstance);

        // add the task to the group
        saveGroup(group);
    }

    // Adjusts the 12 hour am/pm clock params passed from the UI to the 24 hour clock for persistence.
    private void computeHoursForSavingBasedOnAmPm( ScheduledTask taskInstance ){
        // compute hours based on am/pm

        if ( taskInstance.hoursOffset == 0 && taskInstance.hour == 12 ) {
            // hoursOffset == 0 means  AM is used. hour==12 translates into hour==0 based on 0-23 clock
            // (note: that 12:00 am is BEFORE 1:00 am, and hence appears as such in the dropdown)
            taskInstance.hour = 0;
        }
        else if( taskInstance.hoursOffset == 12 && taskInstance.hour == 12 ){
            // hoursOffset == 12 means PM is used. hour==12 translates into hour==12 based on 0-23 clock
            // (note : that 12:00 pm is BEFORE 1:00 pm, and hence appears as such in the dropdown)
            taskInstance.hour = 12;            
        }
        else {
            taskInstance.hour = taskInstance.hoursOffset + taskInstance.hour;
        }
    }

    /**
     * Deletes the specified task from the database, it does not trigger the
     * web service call for the removing the task from the group associated
     * with this task.  That responsibility is left up to the caller.  This is
     * due to the fact that groups deleting all their tasks use "clearTasks"
     * instead of individually deleteing each task individually.
     *
     * @param taskInstance
     */
    def delete(ScheduledTask taskInstance) {
        ScheduledTaskService.delete(taskInstance.id)
        delete(taskInstance,false);
    }

    /**
     * Deletes the specified task removing it from the group if required
     *
     * @param taskInstance
     * @param removeFromGroup
     */
    def delete(ScheduledTask taskInstance, boolean removeFromGroup ) {

        // have to remove the task from the group first or else there will be
        // as cascade exception
        if ( removeFromGroup ) {
            Group group = taskInstance.group;
            group.removeFromTasks(taskInstance);
            saveGroup(group);
        }

        scheduledTaskStatusService.delete(taskInstance.id)
        taskInstance.delete();
        if ( taskInstance.hasErrors() ) {
            taskInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbScheduledTaskException(scheduledTaskInstance:taskInstance);
        }
    }

     
    /**
     * Create a Scheduled Task from an xml fragment
     *
     * The map passed in is a linking between the ids for the groups in the xml
     * document and their id after those xmlFragments have been turned into Group
     * objects and persisted to the database
     *
     * @param xmlFragment
     * @param groupIdMap <xmlId,group.id>
     */
    def fromXml(GPathResult xmlFragment, Map groupIdMap) {
        // scheduled task
        ScheduledTask taskInstance = new ScheduledTask();
        // group for the task
        Group groupInstance;

        // find the group
        groupInstance = Group.get(groupIdMap[xmlFragment.group.@id.text()]);
        if ( !groupInstance ) {
            taskInstance.errors.rejectValue('group','scheduledTask.group.nullable.error',"Task must have a valid group");
            m_log.error("Unable to match group ${xmlFragment.group.@id.text()} skipping");
            throw new SbScheduledTaskException(scheduledTaskInstance:taskInstance);
        }

        // set the attributes on the group
        taskInstance.group = groupInstance;
        taskInstance.actions = xmlFragment.actions.text();
        taskInstance.loggingLevel = xmlFragment.loggingLevel.text().toInteger();
        taskInstance.periodType = xmlFragment.period.@type.text().toInteger();
        taskInstance.periodIncrement = xmlFragment.period.@increment.text().toInteger();
        taskInstance.hour = xmlFragment.time.@hour.text().toInteger();
        taskInstance.minute = xmlFragment.time.@minute.text().toInteger();

        // add the task to the group
        groupInstance.addToTasks(taskInstance);

        // save the task and the group
        save(taskInstance);
        saveGroup(groupInstance);

        // audit log
        auditLogService.logTask("import",taskInstance.taskIdentifier);

        // return the instance
        return taskInstance;
    }

    /**
     * Convert the task instance to xml
     *
     * @param taskInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(ScheduledTask taskInstance,boolean includePreamble,Writer writer) throws Exception {

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            task(id:taskInstance.id) {
                group(id:taskInstance.group.id)
                actions(taskInstance.actions)
                loggingLevel(taskInstance.loggingLevel)
                period(type:taskInstance.periodType,increment:taskInstance.periodIncrement)
                time(hour:taskInstance.hour,minute:taskInstance.minute)
            }
        }

        // create the transformer
        Transformer transformer = TransformerFactory.newInstance().newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, 'yes');
        transformer.setOutputProperty('{http://xml.apache.org/xslt}indent-amount', '4');
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, includePreamble ? "no" : "yes");

        // create the output stream
        Result result = new StreamResult(writer);

        // transform
        transformer.transform(new StreamSource(new StringReader(createdXml.toString())), result);
    }


    /**
     * Convert the scheduled task to be xml
     *
     * @param taskInstance
     * @param includePreamble
     * @return returns a String representation of the task's xml
     */
    String toXmlString(ScheduledTask taskInstance, boolean includePreamble)
    throws Exception {
        StringWriter taskWriter = new StringWriter();
        toXml(taskInstance,false,taskWriter);
        return taskWriter.toString();
    }
}
