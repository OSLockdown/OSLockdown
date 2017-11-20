/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import org.apache.commons.io.FileUtils;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.scheduler.ScheduledTask;

import com.trustedcs.sb.exceptions.SbGroupException;
import com.trustedcs.sb.exceptions.SbClientException;
import com.trustedcs.sb.exceptions.SbScheduledTaskException;
import com.trustedcs.sb.exceptions.SchedulerCommunicationException;

import com.trustedcs.sb.services.client.scheduler.DispatcherTask;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

class GroupService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.GroupService");

    // transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def clientService;
    def schedulerCommunicationService;
    def scheduledTaskService;
    def auditLogService;

    /**
     * Save the group to the database
     *
     * @param groupInstance
     */
    def save(Group groupInstance) {
        // save group to the database
        if (!groupInstance.hasErrors() && groupInstance.save()) {
            m_log.info("Group Saved");
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
     * Save the group to the database using the params map to set
     * any important information.
     *
     * @param groupInstance
     * @param params
     * @param clientIds
     */
    def save(Group groupInstance, Map params, List<Long> clientIds) {

        // set the security profile
    	groupInstance.profile = Profile.get(params.profileId)
        // set the baseline profile
        groupInstance.baselineProfile = BaselineProfile.get(params.baselineProfileId);

    	Client client;
    	// adding clients to the group
    	clientIds.each { clientId ->
            client = Client.get(clientId);
            groupInstance.addToClients(client);
    	}

    	// save the instance
        save(groupInstance);
    }

    /**
     * Update the group using a parameter map and a list of new client ids
     *
     * @param groupInstance
     * @param params
     * @param newClientIds
     */
    def update(Group groupInstance, Map params, List<Long> newClientIds) {

    	def dispatcherTask;
        def scheduler;
        def schedulerResponse;
        def problems = []
        
    	// update the instance
    	groupInstance.properties = params;
    	groupInstance.profile = Profile.get(params.profileId)
        groupInstance.baselineProfile = BaselineProfile.get(params.baselineProfileId);

        // client instance
    	def client;

        // get the list of old client ids
        def oldClientIds = [];
        oldClientIds = groupInstance.clients?.collect {
            it.id;
        };

        // added clients
        def addedIds = [];
        if ( newClientIds ) {
            addedIds = newClientIds - oldClientIds;
        }

        // removed clients
        def removedIds = [];
        if ( oldClientIds ) {
            removedIds = oldClientIds - newClientIds;
        }

    	// remove the marked clients from the group
        removedIds.each { removedId ->
            // removing
            client = Client.get(removedId);
            groupInstance.removeFromClients(client);
    	}

    	// added
    	addedIds.each { addedId ->
            client = Client.get(addedId);
            groupInstance.addToClients(client);
    	}

    	// save the instance
        save(groupInstance);

        // only after we have successfully saved the group can we do actions
        // involving group tasks
        if ( groupInstance.tasks?.size() > 0 ) {
            m_log.info("Group ${groupInstance.name} has tasks");

            // add the list of tasks to the clients
            addedIds.each { clientId ->

                // create the list of dispatcher tasks with correct id assignments...
                
                List<DispatcherTask> dispatcherTaskList = new ArrayList<DispatcherTask>();
                groupInstance.tasks.each { groupTask ->
                    // create the task that can be sent on the wire
                    dispatcherTask = schedulerCommunicationService.schedulerToDispatcherTask(groupTask);
                    // set the id on the dispatcher task
                    dispatcherTask.id = "${groupTask.id}:${client.id}:${groupInstance.id}";

                    // add the dispatcher task to the task list
                    dispatcherTaskList << dispatcherTask;
                }
                m_log.info("Dispatcher Task List: ${dispatcherTaskList}");
                try {
                    client = Client.get(clientId);
                    schedulerCommunicationService.updateTaskList(client,dispatcherTaskList);
                }
                catch ( SchedulerCommunicationException e ) {
                    // swallowing this exception TODO: better solution
                    m_log.error("Client ${client.name} was unable to add task ${dispatcherTask.id} : ${e.message}");
                    problems << "Client ${client.name} was unable to add task ${dispatcherTask.id} : ${e.message}";
                }
            }

            // cycle through all the clients that have been removed in order
            // to remove the taks from each of them
            removedIds.each { clientId ->
                try {
                    client = Client.get(clientId);
                    schedulerCommunicationService.clearTasks(client);
                }
                catch ( SchedulerCommunicationException e ) {
                    // if an exception is caught here it can be swallowed due to the fact
                    // that the client will try and 'dial-home' for verification that its
                    // task still exists when the time comes for it to run
                    m_log.error("Client ${client.name} was unable to clear its tasks : ${e.message}");
                    problems << "Client ${client.name} was unable to clear its tasks : ${e.message}"; 
                }
            }
        }
        else {
            m_log.info("Group ${groupInstance.name} has no tasks");
        }
        return problems
    }

    /**
     * Removes the group from the database
     * archiving all reports for the group
     *
     * @param groupInstance
     */
    def delete(Group groupInstance) {

        // find all clients associated with this group
        def clientList = Client.withCriteria {
            eq('group',groupInstance);
        }
        if( clientList ){
            groupInstance.errors.reject("group.remove.error", [groupInstance.name] as Object[], null);
            throw new SbGroupException(groupInstance:groupInstance);
        }            
        /* no longer needed as we disallow deletion of group with at least one client, see bugzilla
         * Bug 12066 - Console should not allow deleting a group that has attached clients
        clientList.each { client ->
            try {
                client.group = null;
                clientService.save(client);
                m_log.info("Removed group ${groupInstance.name} from client ${client.name}");
                // TODO: audit trail
            }
            catch ( SbClientException e ) {
                groupInstance.errors.reject("group.remove.client.error",
                    [client.name, groupInstance.name] as Object[],
                    null);
                throw new SbGroupException(groupInstance:groupInstance);
            }
        }
        */

        // Find out if any tasks exist because we must try and communicate with
        // the dispatcher to remove the tasks from the clients if they have any
        // associated with them
        def taskList = ScheduledTask.withCriteria {
            eq('group',groupInstance);
        }
        taskList.each { task ->
            try {
                scheduledTaskService.delete(task);
                // TODO: audit trail
            }
            catch(SbScheduledTaskException e) {
                groupInstance.errors.reject("group.remove.task.error",
                    [task.id, groupInstance.name] as Object[],
                    null);
                throw new SbGroupException(groupInstance:groupInstance);
            }
        }

        // db instance
        groupInstance.delete();
        if ( groupInstance.hasErrors() ) {
            groupInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbGroupException(groupInstance:groupInstance);
        }

        // clear the tasks for each of the clients in the group
        if ( taskList.size() > 0 ) {
            m_log.info("Removing tasks from the group's clients via webservice");
            clientList.each { client ->
                try {
                    schedulerCommunicationService.clearTasks(client);
                }
                catch ( SchedulerCommunicationException e ) {
                    // if an exception is caught here it can be swallowed due to the fact
                    // that the client will try and 'dial-home' for verification that its
                    // task still exists when the time comes for it to run
                    m_log.error("Client ${client.name} was unable to clear its tasks : ${e.message}");
                }
            }
        }

        // archive
        m_log.info("Archive Group Reports");
        try {
            def tStamp = ( System.currentTimeMillis() / 1000 ).toInteger();
            File groupDir = SBFileSystemUtil.getGroupDirectory(groupInstance.id);
            if ( groupDir.exists() ) {
                File archiveDir = new File ( SBFileSystemUtil.get(SB_LOCATIONS.ARCHIVE_GROUPS),
                                             "${groupInstance.name.replaceAll(' ','_')}-${tStamp}" );
                FileUtils.moveDirectory(groupDir,archiveDir);
                m_log.info("Group reports moved to ${archiveDir.absolutePath}");
            }
        }
        catch (IOException ioe) {
            m_log.error("Unable to archive reports",ioe);
        }
    }


    /**
     * Create a group from an xml fragment
     *
     * The map passed in is a linking between the ids for the clients in the xml
     * document and their id after those xmlFragments have been turned into Client
     * objects and persisted to the database
     *
     * @param xmlFragment
     * @param clientIdMap <xmlId,client.id>
     */
    def fromXml(GPathResult xmlFragment, Map clientIdMap) {
        // group
        Group groupInstance = new Group();
        // client
        Client client;

        // set group attributes
        groupInstance.name = xmlFragment.name.text();
        groupInstance.description = xmlFragment.description.text();

        // security Profile
        def securityProfile = Profile.findByName(xmlFragment.profile?.text());
        if ( securityProfile ) {
            groupInstance.profile = securityProfile;
        }
        else {
            m_log.error("Unable to match security profile [${xmlFragment.profile?.text()}] skipping");
        }

        // baseline profile
        def baselineProfile = BaselineProfile.findByName(xmlFragment.baselineProfile?.text());
        if ( baselineProfile ) {
            groupInstance.baselineProfile = baselineProfile;
        }
        else {
            m_log.error("Unable to match baseline profile [${xmlFragment.baselineProfile?.text()}] skipping");
        }

        // add clients
        xmlFragment.clientList.client.each { clientXml ->
            client = Client.get(clientIdMap[clientXml.@id.text()]);
            if ( client ) {
                groupInstance.addToClients(client);
            }
            else {
                m_log.error("Unable to match client ${clientXml.@id.text()} skipping");
            }
        }
        save(groupInstance);
        auditLogService.logGroup("import",groupInstance.name);
        return groupInstance;
    }

    /**
     * Convert the group instance to xml
     *
     * @param groupInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(Group groupInstance,boolean includePreamble,Writer writer) throws Exception {

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            group(id:groupInstance.id) {
                name(groupInstance.name)
                description(groupInstance.description)
                profile(groupInstance.profile?.name)
                baselineProfile(groupInstance.baselineProfile?.name)
                clientList() {
                    groupInstance.clients?.each { clientInstance ->
                        client(id:clientInstance.id)
                    }
                }
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
     * Convert the group to be xml
     *
     * @param group
     * @param includePreamble
     * @return returns a String representation of the group's xml
     */
    String toXmlString(Group groupInstance, boolean includePreamble)
    throws Exception {
        StringWriter groupWriter = new StringWriter();
        toXml(groupInstance,false,groupWriter);
        return groupWriter.toString();
    }
}
