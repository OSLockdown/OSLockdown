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

import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.util.SBDetachmentUtil;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.ClientInfo;
import com.trustedcs.sb.web.notifications.Notification;
import com.trustedcs.sb.util.ClientType;
import com.trustedcs.sb.reports.util.ReportType;

import com.trustedcs.sb.exceptions.SbClientException;
import com.trustedcs.sb.exceptions.ReportsException;
import com.trustedcs.sb.exceptions.DispatcherCommunicationException;

import com.trustedcs.sb.clientregistration.ClientRegistrationRequest;

import com.trustedcs.sb.ws.client.ReportsCommunicator;

import org.codehaus.groovy.grails.commons.GrailsApplication;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult

class ClientService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ClientService");

    // Reference to Grails application.
    def grailsApplication    

    // transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def auditLogService;
    def dispatcherCommunicationService;
    def reportsService;

    // Duration of sleep (wait) before new Assessment or Baseline Notifications are checked.
    static private final long SLEEPING_BETWEEN_NOTIFICATION_POLLING = 5000
    // Commenting this out for now as the duration of the Detachment operation (including Baseline and Assessment
    // reports for multiple Clients might take hours even days on really slow networks
    //  static private final long NOTIFICATION_POLLING_MAX_DURATION     = 120000 (120 sec = 2 min)

    static final String DATE_FORMAT_FOR_DB_EXPORT_IMPORT = "yyyy-MM-dd HH:mm:ss.S";

   
    /**
    *  Check to see if a prospective Client *could* be allowable based on current license counts...
    *  This method will return if so, otherwise an exception is raised.
    */
    def verifyClientCanBeAdded(Client clientInstance) {
        def isAllowable = true

        // catch some cases where we can't accept this client because:
        //   bulk license and not a bulk client
        //   not a bulk license but a bulk client
        //   enterprise client and license count exceeded.

        if (SbLicense.instance.isBulk() && clientInstance.clientType != ClientType.CLIENT_BULK) {
            String licenseType =  SbLicense.LOCK_AND_RELEASE_LICENSE ;
            clientInstance.errors.reject("client.bulk.clients.only", [licenseType] as Object[], null);
            throw new SbClientException(clientInstance:clientInstance);
        }
        else if ( ! SbLicense.instance.isBulk() && clientInstance.clientType == ClientType.CLIENT_BULK) {
            String licenseType = SbLicense.instance.isBulk() ? SbLicense.LOCK_AND_RELEASE_LICENSE : SbLicense.ENTERPRISE_LICENSE;
            clientInstance.errors.reject("client.cannot.register.bulk.clients", [licenseType] as Object[], null);
            throw new SbClientException(clientInstance:clientInstance);        
        }
        else if ( SbLicense.instance.isStandAlone() && clientInstance.clientType != ClientType.CLIENT_STANDALONE) {
            String licenseType = SbLicense.instance.isBulk() ? SbLicense.LOCK_AND_RELEASE_LICENSE : SbLicense.ENTERPRISE_LICENSE;
            clientInstance.errors.reject("client.standalone.clients.only", [licenseType] as Object[], null);
            throw new SbClientException(clientInstance:clientInstance);        
        }
       
       
    }

    /**
     * Saves the instance of the client to the database, but does not immediate flushes it to db.
     * @param clientInstance
     */
    def save(Client clientInstance) {
        save( clientInstance, false /* don't immediately flush the object to db */ );
    }

    /**
     * Saves the instance of the client to the database
     * @param clientInstance
     * @param flush - if flush is true immediately flushes the object to the db
     */
    def save(Client clientInstance, boolean flush) {
        // save Client to the database
        
        // if this instance doesn't have an id, then it isn't in the database yet
        // which means we need to check the license limits....
        if (clientInstance.id == null) {
          verifyClientCanBeAdded(clientInstance)
        }
        if (!clientInstance.hasErrors() && clientInstance.save( flush:flush ) ) {
            m_log.info("Client Saved");
        }
        else {
            m_log.error("Unable to save Client");
            clientInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbClientException(clientInstance:clientInstance);
        }
    }

    /**
     * Deletes the instance of the client and archives all reports that are
     * associated with the client
     *
     * @param clientInstance
     */
    def delete(Client clientInstance) {
        
        // double cascade problem: if we delete the client it tries to delete a
        // group , showed up during upgrade to 1.2.2        
        if ( clientInstance.group ) {
            m_log.error(messageSource.getMessage("client.association.error",
                    [clientInstance.name, clientInstance.group.name] as Object[],
                    null));
            clientInstance.errors.reject("client.association.error",
                [clientInstance.name, clientInstance.group.name] as Object[],
                null);
            throw new SbClientException(clientInstance:clientInstance);
        }        
        
        // delete
        clientInstance.delete();
        if ( clientInstance.hasErrors() ) {
            clientInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbClientException(clientInstance:clientInstance);
        }

        // we don't have an explicit 1:m relation ship from Clients to Notifications, so we need to
        // go through and delete Notificiations explicitly
        
        def notifList = Notification.findBySourceId(clientInstance.id)
        notifList*.delete()               

        // archive reports
        try {
            def tStamp = ( System.currentTimeMillis() / 1000 ).toInteger();
            File clientDir = SBFileSystemUtil.getClientDirectory(clientInstance.id);
            if ( clientDir.exists() ) {
                File archiveDir = new File ( SBFileSystemUtil.get(SB_LOCATIONS.ARCHIVE_CLIENTS),
                                             "${clientInstance.name.replaceAll(' ','_')}-${tStamp}" );
                FileUtils.moveDirectory(clientDir,archiveDir);
                m_log.info("Client reports moved to ${archiveDir.absolutePath}");
            }
        }
        catch (IOException ioe) {
            m_log.error("Unable to archive reports",ioe);
        }
    }

    /**
     * Merged this method from ClientInfoService, which I am deleting. Update the client info for the given client using the map
     *
     * @param clientInstance
     * @param hostInfoMap
     */
    def updateClientInfo(Client clientInstance, Map hostInfoMap) {
        // client info
        ClientInfo info = clientInstance.info;
        info.clientVersion = hostInfoMap[ClientInfo.CLIENT_VERSION];
        info.nodeName = hostInfoMap[ClientInfo.NODE_NAME];
        info.distribution = hostInfoMap[ClientInfo.DISTRIBUTION];
        info.kernel = hostInfoMap[ClientInfo.KERNEL];
        info.uptime = hostInfoMap[ClientInfo.UPTIME];
        info.architecture = hostInfoMap[ClientInfo.ARCHITECTURE];
        info.loadAverage = hostInfoMap[ClientInfo.LOAD_AVERAGE];
        info.memory = hostInfoMap[ClientInfo.MEMORY];
        info.corehours = hostInfoMap[ClientInfo.COREHOURS];
        info.maxload = hostInfoMap[ClientInfo.MAXLOAD];
        info.errorMsg = ""
        
        // save the client, it will cascade to the info
        save(clientInstance);
    }

    /**
     * Merged this method from ClientInfoService, which I am deleting. Update the client info for the given client using the map
     *
     * @param clientInstance
     * @param hostInfoMap
     */
    def updateClientInfo(Client clientInstance, String msg) {
        // client info
        ClientInfo info = clientInstance.info;
        info.errorMsg = msg
        
        
        info.distribution = ClientInfo.UNDETERMINED_DEFAULT;
        info.clientVersion = ClientInfo.UNDETERMINED_DEFAULT;
        info.kernel = ClientInfo.UNDETERMINED_DEFAULT;
        info.uptime = ClientInfo.UNDETERMINED_DEFAULT;
        info.architecture = ClientInfo.UNDETERMINED_DEFAULT;
        info.loadAverage = ClientInfo.UNDETERMINED_DEFAULT;
        info.memory = ClientInfo.UNDETERMINED_DEFAULT;
        info.corehours = ClientInfo.UNDETERMINED_DEFAULT;
        info.maxload = ClientInfo.UNDETERMINED_DEFAULT;

        // save the client, it will cascade to the info
        save(clientInstance);
    }

    /**
     * Creates a client from an xml fragment
     *
     * @param xmlFragment
     */
    def fromXml(GPathResult xmlFragment) {
        // create the client
    	Client client = new Client();
        // set properties on the client
        client.name = xmlFragment.name.text();
        // Description is a new field added in 4.0.6 -- which may not be present in DB snapshots
        // taken prior to 4.0.6 so check if it's not null
        client.description = xmlFragment?.description?.text();
        client.hostAddress = xmlFragment.hostAddress.text();
        client.location = xmlFragment.location.text();
        client.contact = xmlFragment.contact.text();
        client.port = xmlFragment.port.text().toInteger();
        client.clientType = ClientType.byName(xmlFragment.clientType.text());

        if( SbLicense.instance.isBulk() ){

            // There should always be a dateCreated
            if( xmlFragment.dateCreated && xmlFragment.dateCreated.text() ){
                client.dateCreated = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, xmlFragment.dateCreated.text() );
            }

            // There might not be dateDetached (the Client was not detached at a time DB snapshot was taken)
            if( xmlFragment.dateDetached && xmlFragment.dateDetached.text() ){
                client.dateDetached = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, xmlFragment.dateDetached.text() );

                // Import detachDataMap attributes for a detached Client (as they should have been exported)
                if( xmlFragment.detachDataMap ){
                    client.detachDataMap = [:]
                    client.detachDataMap[ Client.DETACHMENT_MAP_GROUP_NAME_KEY ] = xmlFragment.detachDataMap."${Client.DETACHMENT_MAP_GROUP_NAME_KEY}".text();
                    client.detachDataMap[ Client.DETACHMENT_MAP_GROUP_NAME_ID_KEY ] = xmlFragment.detachDataMap."${Client.DETACHMENT_MAP_GROUP_NAME_ID_KEY}".text();
                    client.detachDataMap[ Client.DETACHMENT_MAP_SECURITY_PROFILE_NAME_KEY ] = xmlFragment.detachDataMap."${Client.DETACHMENT_MAP_SECURITY_PROFILE_NAME_KEY}".text();
                    client.detachDataMap[ Client.DETACHMENT_MAP_SECURITY_PROFILE_ID_KEY ] = xmlFragment.detachDataMap."${Client.DETACHMENT_MAP_SECURITY_PROFILE_ID_KEY}".text();
                    client.detachDataMap[ Client.DETACHMENT_MAP_BASELINE_PROFILE_NAME_KEY ] = xmlFragment.detachDataMap."${Client.DETACHMENT_MAP_BASELINE_PROFILE_NAME_KEY}".text();
                    client.detachDataMap[ Client.DETACHMENT_MAP_BASELINE_PROFILE_ID_KEY ] = xmlFragment.detachDataMap."${Client.DETACHMENT_MAP_BASELINE_PROFILE_ID_KEY}".text();
                }

                // Import clientInfo for a detached Client (as they should have been exported)
                if( xmlFragment.clientInfo ){
                    client.info = new ClientInfo();
                    client.info.clientVersion   = xmlFragment.clientInfo.clientVersion;
                    client.info.nodeName        = xmlFragment.clientInfo.nodeName;
                    client.info.distribution    = xmlFragment.clientInfo.distribution;
                    client.info.kernel          = xmlFragment.clientInfo.kernel;
                    client.info.uptime          = xmlFragment.clientInfo.uptime;
                    client.info.architecture    = xmlFragment.clientInfo.architecture;
                    client.info.loadAverage     = xmlFragment.clientInfo.loadAverage;
                    client.info.memory          = xmlFragment.clientInfo.memory;
                }
            }
        }

        // save the client
        save(client);
        auditLogService.logClient("import",client.name);
        // return the created group
    	return client;
    }

    /**
     * Createst a client from a Auto Registration Request
     *
     * @param registrationRequest
     */
    def fromAutoRegistrationRequest(ClientRegistrationRequest registrationRequest) {
        // create the client
        Client clientInstance = new Client(name:registrationRequest.name,
            hostAddress:registrationRequest.hostAddress,
            port:registrationRequest.port,
            location:registrationRequest.location,
            clientType:registrationRequest.clientType,
            contact:registrationRequest.contact);
        // return the client instance
        return clientInstance;
    }
    
    /**
     * Convert the client instance to xml
     *
     * @param clientInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(Client clientInstance,boolean includePreamble,Writer writer) throws Exception {    	

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            client(id:clientInstance.id) {
                name(clientInstance.name)
                description(clientInstance.description)
                hostAddress(clientInstance.hostAddress)
                location(clientInstance.location)
                contact(clientInstance.contact)
                port(clientInstance.port)
                clientType(clientInstance.clientType.name)

                if( SbLicense.instance.isBulk() ){

                    // There should always be dateCreated
                    dateCreated( clientInstance.dateCreated.format( DATE_FORMAT_FOR_DB_EXPORT_IMPORT ) );

                    // There might not be dateDetached                    
                    if( clientInstance.dateDetached ){
                        dateDetached( clientInstance.dateDetached.format( DATE_FORMAT_FOR_DB_EXPORT_IMPORT ) );

                        // export detachDataMap HashMap values ...
                        if( clientInstance.detachDataMap ){

                            detachDataMap {
                                clientInstance.detachDataMap.each{ key, value ->
                                    // important: need to use "${key}" as key does not work
                                    "${key}"( value )
                                }
                            }
                        }

                        // export clientInfo if it exists (and for a detachedClient is should always
                        // exist as hostInfo() call (which populates clientInfo) was made during the 1st Phase of Client detachment)
                        if( clientInstance.info && clientInstance.info.clientVersion ){
                            clientInfo {
                                clientVersion(clientInstance.info.clientVersion)
                                nodeName(clientInstance.info.nodeName)
                                distribution(clientInstance.info.distribution)
                                kernel(clientInstance.info.kernel)
                                uptime(clientInstance.info.uptime)
                                architecture(clientInstance.info.architecture)
                                loadAverage(clientInstance.info.loadAverage)
                                memory(clientInstance.info.memory)
                            }
                        }
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
     * Convert the client to be xml
     *
     * @param client
     * @param includePreamble
     * @return returns a String representation of the client's xml
     */
    String toXmlString(Client clientInstance, boolean includePreamble)
    throws Exception {
        StringWriter clientWriter = new StringWriter();
        toXml(clientInstance,false,clientWriter);
        return clientWriter.toString();
    }

    /**
     * Detaches all of the Clients which are passed in List<Client> clients by
     * 0. doing some basic checks on all Client (to NOT process any Client that fails these basic checks)
     * 1. invoking a Baseline action on *all Clients*,
     * 2. waiting for all of them to finish generating Baseline reports
     * 3. invoking an Assessment action on *all Clients*,
     * 4. waiting for all of them to finish generating Assessment reports
     * 5. fetching Baseline and Assessment reports
     */
    Map<String, String> detachClients( List<Client> clients, Integer loggingLevel ){

        def clientMap = [:]

        String errorMessage
        try {
            SBDetachmentUtil.getInstance().startDetachment()
        }
        catch( Exception e ){
            errorMessage = e.message
        }

        if( errorMessage ){
            clientMap[ "0" ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"
        }
        else {

            def clientIdToClientMap = [:]
            boolean stopDetachmentRequested = false

            if( clients ){

                Client clientInstance
               
                clients.each {

                    clientInstance = it

                    String clientId = clientInstance.id+""

                    // 1. Store Clients keyed off by their id for easy access later inside
                    clientIdToClientMap[ clientId ] = clientInstance

                    // 2. If there was no status (detachDataMap) OR there was previously a status set (which is due to previously attempted Detacth
                    // that failed, as a successful detachment clears out clientInstance.detachDataMap[ "status" ] for a Client), clear it out
                    // for this Detach operation. This is needed so that previous errors (stored in detachDataMap[ "status" ]) wouldn't
                    // be shown during a new detach operation.
                    if( !clientInstance.detachDataMap || ( clientInstance.detachDataMap && clientInstance.detachDataMap[ "status" ] ) ){

                        if( !clientInstance.detachDataMap ){
                            clientInstance.detachDataMap = [:]
                        }

                        // Reset status to 0 (which is always a successful one - no :Error after it)
                        clientInstance.detachDataMap[ "status" ] = SBDetachmentUtil.DETACH_PHASE_ZERO_PREPARE_FOR_DETACHMENT_ID.toString() /* "0" */
                        // ... and persist it
                        try {
                            // Note: not checking the params.version here as done in the update() case
                            //  clientService.save(clientInstance);
                            save( clientInstance,
                                true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );
                        }
                        catch( SbClientException e ) {
                            // silently ignore -- status won't be set
                        }
                        catch( Exception exp ){
                            // silently ignore -- status won't be set
                        }
                    }
                }

                // Allowed previous map to run for all Clients, now see if in the meanwhile stop detachment was requested
                stopDetachmentRequested = SBDetachmentUtil.getInstance().stopDetachmentRequested()
                if( !stopDetachmentRequested ){

                    Map<String, Client> clientIdToClientInstanceToProcessFurther = [:]

                    //
                    // Level I relatively easy, fast steps :
                    // =====================================
                    //
                    // 1. Check that the Client is not already detached, has a Group, and a Group has a Security and Baseline Profile (if this is not the case
                    //    do not proceed to next step for this Client, and record the error)
                    // 2. Fetch the last details for the Client (if get an error during this step then don't proceed to next step for this Client, and record the error)
                    // 3. Put the Client on the list to be processed for Baseline and Assess actions and fetching their associated reports
                    //
                    for( def aClientInstance : clients ){

                        errorMessage = null

                        // Check if stop is requested for the detach. Set flag break from the loop.
                        if( SBDetachmentUtil.getInstance().stopDetachmentRequested() ){
                            stopDetachmentRequested = true

                            break
                        }

                        clientInstance = aClientInstance

                        if( clientInstance ){
                            // Client is not detached (don't detach an already detached Client) -- note there is also this same check
                            // below right before the Client is persisted (and in there we just silently allow to be updated -- but here
                            // we don't as here is the beginning of the detachment process)
                            if( !clientInstance.dateDetached ){
                                // Client has a Group
                                if( clientInstance.group ){
                                    // Client's group has a security profile
                                    if( clientInstance.group.profile ) {
                                        // Client's group has a baseline profile
                                        if( clientInstance.group.baselineProfile ){
                                            // 1. Client has a Group with a Security and Baseline Profiles

                                            // 2. Fetch the hostInfo (also checks if can contact the Client)
                                            try {
                                                if ( !(clientInstance.info) ) {
                                                    clientInstance.info = new ClientInfo();
                                                }
                                                def hostInfoMap = dispatcherCommunicationService.hostInfo(clientInstance);
                                                updateClientInfo(clientInstance,hostInfoMap);
                                            }
                                            catch ( SbClientException clientException) {
                                                errorMessage = clientException.message;
                                            }
                                            catch ( DispatcherCommunicationException communicationException ) {
                                                errorMessage = communicationException.message;
                                            }
                                            catch( Exception e ){
                                                // catch any other uncaught exception not specifically caught above
                                                errorMessage = "Could not contact the Dispatcher for Client "+clientInstance.name+"."+ e.message
                                            }
                                        }
                                        else {
                                            errorMessage = messageSource.getMessage("dispatcher.baselineProfile.missing",
                                                [clientInstance.name, clientInstance.group.name] as Object[],null)
                                        }
                                    }
                                    else {
                                        errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                                            [clientInstance.name, clientInstance.group.name] as Object[],null)
                                    }
                                }
                                else {
                                    errorMessage = messageSource.getMessage("dispatcher.group.missing", [clientInstance.name] as Object[], null)
                                }
                            }
                            else {
                                errorMessage = messageSource.getMessage("client.alreadyDetached", [clientInstance.name] as Object[], null)
                            }
                        }
                        else {
                            errorMessage = messageSource.getMessage("client.not.found",[it] as Object[], null)
                        }

                        String clientId = clientInstance.id+""

                        //If there were an error set it into the Map
                        if( errorMessage ){
                            clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"
                        }
                        // Otherwise, no error, 3. Put the Client on the map to be processed for Baseline and Assess actions
                        // and fetching their associated reports
                        else {
                           clientIdToClientInstanceToProcessFurther[ clientId ] = clientInstance
                        }

                        // Store error for level 1 ...
                        clientInstance.detachDataMap[ "status" ] =
                            SBDetachmentUtil.DETACH_PHASE_ONE_SANITY_CHECKS_AND_HOST_INFO_FETCH_ID + ( errorMessage ? ":${errorMessage}" : "" )

                        // ... and persist it
                        try {
                            // Note: not checking the params.version here as done in the update() case
                            //  clientService.save(clientInstance);
                            save( clientInstance,
                                true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );

                        }
                        catch( SbClientException e ) {
                            // silently ignore -- status won't be set
                        }
                        catch( Exception exp ){
                            // silently ignore -- status won't be set
                        }
                    }

                    // Level II longer, complicated steps :
                    // ====================================
                    // 4. Invoke Baseline Action on *all Clients*  which passed basic validation and were up and running
                    if( !stopDetachmentRequested && clientIdToClientInstanceToProcessFurther ){

                        long initialActionTimeInMillisForQuery = System.currentTimeMillis()

                        // Keep track of clientIds upon which the Baseline action was invoked. In case Stop Detach
                        // is invoked while this loop is processing an Abort action will be called on these clients.
                        List<String> invokedBaselineClientIds = []

                        // 4. Invoke Baseline Action
                        //                                  Make a copy of key set to avoid java.util.ConcurrentModificationException
                        //                                  as in case of an error the entry is removed from clientIdToClientInstanceToProcessFurther
                        Iterator clientsIdIterator = new HashSet( clientIdToClientInstanceToProcessFurther.keySet() ).iterator();
                        while( clientsIdIterator.hasNext() ){
                            String clientId = clientsIdIterator.next()
                            clientInstance = clientIdToClientInstanceToProcessFurther[ clientId ]

                            errorMessage = null

                            // If stop was requested, immediately break from this loop (and don't update status
                            // on this Client, it will still remain in 0 phase). If there were any
                            // invoked Baselines for Clients which were proceessed earlier within this loop, then
                            // they would complete (whenever they will complete), but this logic will not call Abort
                            // on these (since currently Abort is non-funcional on Baselines and also has issues even for Assessments).
                            if( SBDetachmentUtil.getInstance().stopDetachmentRequested() ){
                                stopDetachmentRequested = true

                                break
                            }
                            else {

                                try {
            // println "--->> ClientController.detachRetainReportsAjax #1 BEFORE invoking BASELINE action for Client ["+clientInstance+"]"

                                    dispatcherCommunicationService.baselineWithProfile( loggingLevel, clientInstance );

                                    // Record a clientId for which Baseline was invoked
                                    invokedBaselineClientIds << clientId

            // println "--->> ClientController.detachRetainReportsAjax #2 AFTER invoking BASELINE action for Client ["+clientInstance+"]"
                                }
                                catch ( DispatcherCommunicationException e ) {
                                    errorMessage = e.message;
                                }
                                catch( Exception exp ){
                                    // catch any other uncaught exception not specifically caught above
                                    errorMessage = exp.message;
                                }
                            }

                            //If there were an error set it into the Map
                            if( errorMessage ){
                                clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"

                                // ... and remove clientInstance from clientIdToClientInstanceToProcessFurther (don't want to invoke Assessment on it)
                                clientIdToClientInstanceToProcessFurther.remove( clientId )
                            }
                            // Otherwise, no error, keep clientInstance on clientIdToClientInstanceToProcessFurther to also invoke Assessment action

                            // Store error for level 2 ...
                            clientInstance.detachDataMap[ "status" ] =
                                SBDetachmentUtil.DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_ID + ( errorMessage ? ":${errorMessage}" : "" )

                            // ... and persist it
                            try {
                                // Note: not checking the params.version here as done in the update() case
                                //  clientService.save(clientInstance);
                                save( clientInstance,
                                    true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );
                            }
                            catch( SbClientException e ) {
                                // silently ignore -- status won't be set
                            }
                            catch( Exception exp ){
                                // silently ignore -- status won't be set
                            }
                        }

                        // If there was a Stop Detachment request done during previous loop make sure to ONLY call
                        // postBaselineInvocationProcessing() on the clients that had Baseline action actually invoked on them.
                        // (Ex. had 5 clients, previous loop successfully invoked Baseline action on first 2 clients; the
                        // postBaselineInvocationProcessing() should only be invoked on first 2, and not on all 5 -- as that
                        // would cause postBaselineInvocationProcessing() to never return since last 3 clients had NEVER
                        // Baseline action invoked upon them and hence, no Baseline notification would be generated for them).
                        // Note: if there was an error during Baseline invocation then {clientId, clientInstance} is already removed
                        // from the clientIdToClientInstanceToProcessFurther[:].
                        if( stopDetachmentRequested && invokedBaselineClientIds ){

                            // ONLY leave {clientId, clientInstance} on clientIdToClientInstanceToProcessFurther[:] whose
                            // ids appear in invokedBaselineClientIds
                            clientIdToClientInstanceToProcessFurther.keySet().each {
                                if( !invokedBaselineClientIds.contains( it ) ){
                                    clientIdToClientInstanceToProcessFurther.remove( it )
                                }
                            }
                        }

                        //
                        // Level III longer, complicated steps :
                        // ====================================

                        // 1. wait for baseline notifications
                        // 2. once baseline notification is received store baseline report name, and invoke assessment
                        // 3. once assessment notification is received store assessment report name AND fetch both baseline and assessment reports
                        //  from the Client box
                        // 4. if both baseline and assessment reports were fetched for a Client, then call performFinalPhaseOfDetachment() on it with the
                        //  intention of having it completely detached (eager detachment completion strategy).
                        postBaselineInvocationProcessing( clientIdToClientInstanceToProcessFurther, clientMap,
                            initialActionTimeInMillisForQuery, loggingLevel )
                    }
                }
            }
            // There were no clients passed. Populate error on a dummy id=0 Client just to be displayed on the Client.
            else {
                clientMap[ "0" ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}There were no Clients to detach."
            }

            // Check one more time in case Stop Detachment request was received
            stopDetachmentRequested = SBDetachmentUtil.getInstance().stopDetachmentRequested()

            // After detachment was allowed to run and ran and there were NO stop detachment request
            // make sure to stop and complete the detachment.
            try {
                // If stop detachment was not requested then explicitly call stopDetachment so could also call completeDetachment()
                if( !stopDetachmentRequested ){
                    SBDetachmentUtil.getInstance().stopDetachment()
                }
                else {
                    // If stop detach was requested, set the latest persisted status to clientMap[] for each client which
                    // did not error, but was in the middle of an operation
                    clientIdToClientMap.each{ clientId, aClientInstance ->

                        String clientMapValue = clientMap[ clientId ]                        

                        // If this Client was not fully detached, but it did not error out yet at the point when
                        // a stop detachment was called (if it did clientMapValue would have contained actual failure rather than
                        // DETACHMENT_OPERATION_STOPPED_ERROR), populate the last state it was in at the time stop detachment was received
                        if( !aClientInstance.dateDetached && !clientMapValue ){

                            String status = aClientInstance.detachDataMap[ "status" ]

                            // Status contains a integer of the phase nothing else
                            // if( status && ! status.contains( ":" ) ){

                            // If successfully Aborted the Baseline action, have the message display 
                            // "detachment operation was stopped while Running Baseline action ..."
                            if( status == SBDetachmentUtil.DETACH_PHASE_ABORT_BASELINE_ACTION_ID+"" ){
                                status = SBDetachmentUtil.DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_ID+""
                            }
                            // If successfully Aborted the Assessment action, have the message display
                            // "detachment operation was stopped while Running Assessment action ..."
                            else if( status == SBDetachmentUtil.DETACH_PHASE_ABORT_ASSESS_ACTION_ID+"" ){
                                status = SBDetachmentUtil.DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_ID+""
                            }

                            String progressMessage = SBDetachmentUtil.getUserFormattedStatusMessage( status )
                            String clientMapMessage = "${aClientInstance.name} ${SBDetachmentUtil.DETACHMENT_OPERATION_STOPPED_ERROR} while ${progressMessage}"

                            // Update map (remember to prepand Error as it's still an error)
                            clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${clientMapMessage}"
                        }
                    }
                }

                // Always call completeDetachment to remove the lock on ONLY one detach operation in the system
                SBDetachmentUtil.getInstance().completeDetachment()
            }
            catch( Exception e ){
                // If gotten an exception here, force a reset of SBDetachmentUtil to a NOT_RUNNING state so next detachment operation could be started
                SBDetachmentUtil.getInstance().detachmentOperationState        = SBDetachmentUtil.NOT_RUNNING
                SBDetachmentUtil.getInstance().detachmentOperationUserId       = null
                SBDetachmentUtil.getInstance().detachmentOperationStartDate    = null
            }
        }

// println "---- ClientService return clientMap ["+clientMap+"]"

        // Return client map
        return clientMap;
    }

    // Used by detachClients() logic.
    //
    // Assumes that there was *no stopDetachmentRequest* made during the previous invocation of Baseline actions on all Clients loop.
    // If there was, that loop should have ended immediately despite the fact that there might be baseline operations in progress, which
    // should REALLY be aborted in here, but *can't* due to the Abort logic not yet implemented for Baseline and currently broken for Baselines
    // and Assessment actions.
    //
    // Does the following :
    // 1. wait (till receive all notifications or till user Stops Detach Action) for any baseline notifications (multiple baseline notifications might be proceessed at this point)
    // 2. once a baseline notification is received for a Client store baseline report name, and invoke assessment action for that Client
    // 3. once assessment notification is received for a Client store assessment report name AND fetch both baseline and assessment reports from the Client box
    // 4. if both baseline and assessment reports were fetched for a Client, then call performFinalPhaseOfDetachment() on its clientInstace object with the
    //  intention of having it completely detached (eager detachment completion strategy).
    private void postBaselineInvocationProcessing( Map<String, Client> clientIdToClientInstanceMap, Map<String, String> clientMap,
        long initialActionTimeInMillisForQuery, Integer loggingLevel ){

        if( clientIdToClientInstanceMap ){

            // Create a baseline and assessment clientId lists ...
            List<String> baselineClientIds = []
            List<String> assessmentClientIds = []

            clientIdToClientInstanceMap.each { clientId, aClientInstance ->

                // initialize baselineClientIds to all clientIdToClientInstanceMap clientIds as initially
                // all Clients are waiting on the Baseline notification
                baselineClientIds << clientId
            }

            // Create a {clientId, baselineReportName}
            Map<String, String> clientIdBaselineReportMap = [:]
            // Create a {clientId, assessmentReportName}
            Map<String, String> clientIdAssessmentReportMap = [:]

            // This boolean should ONLY be set to true by checkIfStopDetachmentRequestedAndInvokeAbort()
            // and IFF user requested to stop the Detachment process. This will ensure checkIfStopDetachmentRequestedAndInvokeAbort()
            // runs at most ONCE.
            boolean abortActionInvoked = false

            // initialActionTimeInMillisForQuery is the timestamp when the first action (out of many) started.
            // Used in query for Notifications
            Date initialActionDateForQuery = new Date( initialActionTimeInMillisForQuery )

            while( true ){

                // Check if user requested Stop Detachment and if yes invoke Abort action on all clients AT MOST ONCE
                // that invoked Baselines or Assessments. This code will really execute an Abort action ONLY once so it's safe
                // to put it many times in this loop.
                abortActionInvoked = checkIfStopDetachmentRequestedAndInvokeAbort( baselineClientIds, assessmentClientIds,
                    abortActionInvoked, clientIdToClientInstanceMap, clientMap, loggingLevel )
                
                //
                // Process phase 4 Clients -- a. receive Baseline Notification, b. if baseline report is available (baseline was successful)
                // store baseline report into clientIdBaselineReportMap and invoke Assessment action on the Client
                //
                if( baselineClientIds ){

                    // Check for Baseline Notifications
                    def baselineNotificationList = Notification.withCriteria {

                        // Check for Baseline Notifications from initialActionDateForQuery till now
                        between( "timeStamp", initialActionDateForQuery, new Date() )

                        // Type is an int and 4 is for Baselines (see com.trustedcs.sb.web.notifications.NotificationTypeEnum)
                        // where Baseline is 5th
                        eq( "type", 4 )

                        // transaction id starts with clientID: (ex. 4:172.16.130.135:6443:1299175844653, where "4:%" is what we are matching on here)
                        or {
                            baselineClientIds.each{
                                ilike( "transactionId", "${it}:%" )
                            }
                        }
                    }

                    if( baselineNotificationList ){

                        for( def baselineNotification : baselineNotificationList ) {

                            String clientId = baselineNotification.transactionId.substring( 0, baselineNotification.transactionId.indexOf( ":" ) )
                            String errorMessage = null
                            int phaseId

//println "--->> ClientController.waitAndFetchForAssessmentOrBaselineReports processing notification clientId ["+clientId+"] transactionId ["+it.transactionId+"] it.dataMap ["+it.dataMap+"]"

                            Client clientInstance = clientIdToClientInstanceMap[ clientId ]

                            if( baselineNotification.successful && baselineNotification.dataMap && baselineNotification.dataMap[ "fileName" ] ){

                                if( baselineNotification.aborted ){
                                    // Baseline Action was successfully aborted. However, don't set errorMessage = "Baseline action was Aborted"
                                    // in here as detachClients() will take care of setting the correct error message (including Client name)
                                    // for Clients that did not have any errors, but were stopped by the user ...

                                    // ... and also remove Client from clientIdToClientInstanceMap so it doesn't get processed further
                                    clientIdToClientInstanceMap.remove( clientId )

                                    // Set to Baseline Abort phase
                                    phaseId = SBDetachmentUtil.DETACH_PHASE_ABORT_BASELINE_ACTION_ID
                                }
                                else {
                                    // Baseline Action completed successfully and it was NOT aborted. it.dataMap[ "fileName" ] contains the name of 
                                    // the generated Baseline report

                                    if( !SBDetachmentUtil.getInstance().stopDetachmentRequested() ){
                                        // Only proceed to invoking the Assessment action if Detachment wasn't stopped by the user ...

                                        // 1. Store Baseline report name to be fetched later ...
                                        clientIdBaselineReportMap[ clientId ] = baselineNotification.dataMap[ "fileName" ]

                                        // 2. ... and invoke an Assessment action
                                        try {
        // println "--->> ClientController.detachRetainReportsAjax #1 BEFORE invoking ASSESSMENT action for Client ["+clientInstance+"]"

                                            dispatcherCommunicationService.scan( loggingLevel, clientInstance );

                                            // If Assessment invocation was successful add this clientId to assessmentClientIds list
                                            // so that this method can check for Assessment notifications for the Client. This Client
                                            // is always removed from the baselineClientIds.
                                            assessmentClientIds << clientId

        // println "--->> ClientController.detachRetainReportsAjax #2 AFTER invoking ASSESSMENT action for Client ["+clientInstance+"]"
                                        }
                                        catch ( DispatcherCommunicationException e ) {
                                            errorMessage = e.message;
                                        }
                                        catch( Exception exp ){
                                            // catch any other uncaught exception not specifically caught above
                                            errorMessage = exp.message;
                                        }
                                        
                                        // set phaseId to be 3
                                        phaseId = SBDetachmentUtil.DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_ID
                                    }
                                    else {
                                        // If Detachment was stopped by the user don't invoke Assess and don't add clientId to assessmentClientIds.
                                        // There will be a call to checkIfStopDetachmentRequestedAndInvokeAbort() made AFTER all Baseline
                                        // notifications are proceeded which will call abort() on all Baselines and Assessments
                                        // in progress. However, client with clientId won't be processed by it since below
                                        // it will remove from baselineClientIds (baselineClientIds.remove( clientId )) and not
                                        // added to the assessmentClientIds. Also do not set abortActionInvoked in here as ONLY
                                        // checkIfStopDetachmentRequestedAndInvokeAbort() should do it ONCE.

                                        // keep at phase 2. Call to
                                        phaseId = SBDetachmentUtil.DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_ID
                                    }
                                }
                            }
                            else {
                                // 1. Baseline Action failed, construct (our own) error message ...
                                errorMessage = "Baseline action failed"
                                if( baselineNotification.exceptions ){
                                    baselineNotification.exceptions.each { exception ->
                                        errorMessage += " ${exception.message}"
                                    }
                                }

                                // ... and keep at phase 2
                                phaseId = SBDetachmentUtil.DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_ID
                            }

                            //
                            // errorMessage would be non-null if a. Notification has a failure in it, b. invoke Assess failed
                            //
                            if( errorMessage ){
                                // 1. set error into clientMap
                                clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"

                                // ... 2. and also remove Client from clientIdToClientInstanceMap so it doesn't get processed further
                                clientIdToClientInstanceMap.remove( clientId )
                            }

                            // Remove clientIs from baselineClientIds as this Client is done Baseline processing
                            // (regardless whether it was a success or failure or if it was Aborted)
                            baselineClientIds.remove( clientId )

                            // Store status
                            clientInstance.detachDataMap[ "status" ] = phaseId + ( errorMessage ? ":${errorMessage}" : "" )
                                
                            // ... and persist it
                            try {
                                // Note: not checking the params.version here as done in the update() case
                                //  clientService.save(clientInstance);
                                save( clientInstance,
                                    true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );
                            }
                            catch( SbClientException e ) {
                                // silently ignore -- status won't be set
                            }
                            catch( Exception exp ){
                                // silently ignore -- status won't be set
                            }
                        }
                    }
                }

                // Check if user requested Stop Detachment and if yes invoke Abort action on all clients AT MOST ONCE
                // that invoked Baselines or Assessments. This code will really execute an Abort action ONLY once so it's safe
                // to put it many times in this loop.
                abortActionInvoked = checkIfStopDetachmentRequestedAndInvokeAbort( baselineClientIds, assessmentClientIds,
                    abortActionInvoked, clientIdToClientInstanceMap, clientMap, loggingLevel )

                //
                // Process phase 5 Clients -- a. receive Assessment Notification, b. if assessment report is available (assessment was successful)
                // store assessment report into clientIdAssessReportMap, fetch BOTH reports from the Client box, AND fetch oslockdown.log
                // (Client Application log) from the Client
                //
                if( assessmentClientIds ){

                    // Check for Baseline Notifications
                    def assessmentNotificationList = Notification.withCriteria {

                        // Check for Baseline Notifications from initialActionDateForQuery till now
                        between( "timeStamp", initialActionDateForQuery, new Date() )

                        // Type is an int and 0 is for Assessments (see com.trustedcs.sb.web.notifications.NotificationTypeEnum)
                        eq( "type", 0 )

                        // transaction id starts with clientID: (ex. 4:172.16.130.135:6443:1299175844653, where "4:%" is what we are matching on here)
                        or {
                            assessmentClientIds.each{
                                ilike( "transactionId", "${it}:%" )
                            }
                        }
                    }

                    if( assessmentNotificationList ){

                        for( def assessmentNotification : assessmentNotificationList ){

                            String clientId = assessmentNotification.transactionId.substring( 0, assessmentNotification.transactionId.indexOf( ":" ) )
                            String errorMessage = null
                            int phaseId

    //println "--->> ClientController.waitAndFetchForAssessmentOrBaselineReports processing notification clientId ["+clientId+"] transactionId ["+it.transactionId+"] it.dataMap ["+it.dataMap+"]"

                            Client clientInstance = clientIdToClientInstanceMap[ clientId ]

                            if( assessmentNotification.successful && assessmentNotification.dataMap && assessmentNotification.dataMap[ "fileName" ] ){

                                if( assessmentNotification.aborted ){
                                    // Assessment Action was successfully aborted. However, don't set errorMessage = ""Assessment action was Aborted"
                                    // in here as detachClients() will take care of setting the correct error message (including Client name)
                                    // for Clients that did not have any errors, but were stopped by the user ...

                                    // ... and also remove Client from clientIdToClientInstanceMap so it doesn't get processed further
                                    clientIdToClientInstanceMap.remove( clientId )

                                    // Note if assessment was Aborted proceedIntoFinalPhase = false and final phase is not done
                                    
                                    phaseId = SBDetachmentUtil.DETACH_PHASE_ABORT_ASSESS_ACTION_ID
                                }
                                else {
                                    // Assessment Action completed successfully and it was NOT aborted. it.dataMap[ "fileName" ] contains the name of
                                    // the generated Assessment report

                                    if( !SBDetachmentUtil.getInstance().stopDetachmentRequested() ){
                                        // Only proceed to fetching Reports and log if Detachment wasn't stopped by the user ...

                                        String assessmentReportName = assessmentNotification.dataMap[ "fileName" ]

                                        // 1. Fetch Baseline and Assessment Report
                                        try {
        // println "--->> ClientController.FETCHING FILES FOR ["+(assessOrBaseline?"ASSESSMENT":"BASELINE")+"] ACTION #1 BEFORE fetching ["+(assessOrBaseline?"ASSESSMENT":"BASELINE")+"] report for Client ["+mapEntry.key+"] REPORT IS ["+mapEntry.value+"]"

                                            String baselineReportName = clientIdBaselineReportMap[ clientId ]

                                            File reportFile = reportsService.getReport( clientInstance, ReportType.BASELINE, baselineReportName, false )
                                            if( !reportFile ){
                                                errorMessage = "Can't fetch latest baseline report "+baselineReportName+"."
                                            }
                                            else {

                                                reportFile = reportsService.getReport( clientInstance, ReportType.ASSESSMENT, assessmentReportName, false )
                                                if( !reportFile ){
                                                    errorMessage = "Can't fetch latest assessment report "+assessmentReportName+"."
                                                }
                                                else {

                                                    //
                                                    // Fetch oslockdown.log from client into /reports/ec/clients/${clientId}/logs. If oslockdown.log
                                                    // already exists there (from previously done log pull for this client) overwrite it with latest obtained here.
                                                    //
                                                    def clientLogDir = SBFileSystemUtil.getClientLogsDirectory( clientInstance.id );
                                                    if ( !clientLogDir.exists() ) {
                                                        m_log.info("create client logging directory: ${clientLogDir.absolutePath}");
                                                        clientLogDir.mkdirs();
                                                    }
                                                    File logFile = new File(clientLogDir,"oslockdown.log");

                                                    ReportsCommunicator agent = new ReportsCommunicator( clientInstance.id, clientInstance.hostAddress,
                                                        clientInstance.port, grailsApplication.config.tcs.sb.console.secure.toBoolean() /* useHttps */ );
                                                    def reportsResponse = agent.getSbAppLog();

                                                    // check reports response
                                                    if ( reportsResponse && reportsResponse.code < 400 ) {
                                                        // parse the response body
                                                        if ( reportsResponse.content ) {
                                                            logFile.withOutputStream { outStream ->
                                                                outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                                                            }
                                                            m_log.info("Retained Client ["+clientInstance.name+"] oslockdown.log.");
                                                        }
                                                    }
                                                    else {

                                                        String reasonPhrase = reportsResponse?.reasonPhrase
                                                        if( !reasonPhrase ){
                                                            errorMessage = "Can't fetch oslockdown.log."
                                                        }
                                                        else {
                                                            if( !reasonPhrase.contains( SBDetachmentUtil.SB_LOG_MAXIMUM_5MB_SIZE_EXCEEDED_ERROR ) ){

                                                                // response code[500] reason[ : File /var/lib/oslockdown//logs/oslockdown.log is 27907329 bytes,
                                                                // which is larger than the maximum allowed transfer size of 5 MB]
                                                                errorMessage = "Can't fetch oslockdown.log [${reasonPhrase}]."
                                                            }
                                                            else {  // If reasonPhrase.contains( SBDetachmentUtil.SB_LOG_MAXIMUM_5MB_SIZE_EXCEEDED_ERROR )
                                                                    // don't consider it as a detachment error (as it's really not), but log it anyway
                                                                m_log.info("Could not retain Client ["+clientInstance.name+"] oslockdown.log. ${reasonPhrase}");
                                                            }
                                                        }
                                                    }
                                                }
                                            }
        // println "--->> ClientController.FETCHING FILES FOR ASSESS ACTION #2 AFTER fetching ASSESSMENT report for Client ["+mapEntry.key+"] REPORT IS ["+mapEntry.value+"]"

                                        }
                                        catch ( ReportsException e ) {
                                            errorMessage = e.message
                                        }
                                        catch( IOException ie ){
                                            errorMessage = ie.message
                                        }
                                        catch( Exception exp ){
                                            // catch any other uncaught exception not specifically caught above
                                            errorMessage = exp.message;
                                        }

                                        // Set to phase 4 (regardless of error or not)
                                        phaseId = SBDetachmentUtil.DETACH_PHASE_FOUR_FETCH_BASELINE_ASSESS_REPORTS_AND_SB_CLIENT_APP_LOG_ID
                                    }
                                    else {
                                        // If Detachment was stopped by the user don't fetch Reports and log file.
                                        // There will be a call to checkIfStopDetachmentRequestedAndInvokeAbort() made AFTER all Assessment
                                        // notifications are proceeded which will call abort() on all Baselines and Assessments
                                        // in progress. However, client with clientId won't be processed by it since below
                                        // it will remove from assessmentClientIds (assessmentClientIds.remove( clientId )). Also
                                        // do not set abortActionInvoked in here as ONLY checkIfStopDetachmentRequestedAndInvokeAbort() should do it ONCE.

                                        // keep at phase 3
                                        phaseId = SBDetachmentUtil.DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_ID
                                    }
                                }
                            }
                            else {
                                // 1. Assessment Action failed, construct (our own) error message ...
                                errorMessage = "Assessment action failed"
                                if( assessmentNotification.exceptions ){
                                    assessmentNotification.exceptions.each { exception ->
                                        errorMessage += " ${exception.message}"
                                    }
                                }

                                // ... and keep at phase 3
                                phaseId = SBDetachmentUtil.DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_ID
                            }

                            //
                            // errorMessage would be non-null if a. Notification has a failure in it, b. fetching either Baseline or Assessment report
                            // or oslockdown.log failed for any reason.
                            //
                            if( errorMessage ){
                                // 1. set error into clientMap
                                clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"

                                // ... 2. and also remove Client from clientIdToClientInstanceMap so it doesn't get processed further
                                clientIdToClientInstanceMap.remove( clientId )
                            }

                            // Remove clientIs from assessmentClientIds as this Client is done Assessment processing
                            // (regardless whether it was a success or failure or if it was Aborted)
                            assessmentClientIds.remove( clientId )

                            // Store status
                            clientInstance.detachDataMap[ "status" ] = phaseId + ( errorMessage ? ":${errorMessage}" : "" )
                                
                            // ... and persist it
                            try {
                                // Note: not checking the params.version here as done in the update() case
                                //  clientService.save(clientInstance);
                                save( clientInstance,
                                    true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );

                                //
                                // If phase 4 was successful without an error (and its status got correctly saved as well -- i.e save() did not
                                // throw any exceptions) proceed to the final phase and don't check for SBDetachmentUtil.getInstance().stopDetachmentRequested()
                                // (i.e. allow final phase to complete for this Client, then this loop will exist on
                                // SBDetachmentUtil.getInstance().stopDetachmentRequested() check done right before Thread.currentThread().sleep() below)
                                //
                                if( !errorMessage && 
                                    phaseId == SBDetachmentUtil.DETACH_PHASE_FOUR_FETCH_BASELINE_ASSESS_REPORTS_AND_SB_CLIENT_APP_LOG_ID ){
                                    
                                    performFinalPhaseOfDetachment( clientInstance, clientMap )                             
                                }
                            }
                            catch( SbClientException e ) {
                                // silently ignore -- status won't be set
                            }
                            catch( Exception exp ){
                                // silently ignore -- status won't be set
                            }
                        }
                    }
                }

                // If processed all Baselines and Assessments notifications (either successfully or not) break from this infinite loop. Normal
                // case for completion without the Stop Detachment command.
                if( !baselineClientIds && !assessmentClientIds ){
                    break
                }

                // Check if user requested Stop Detachment and if yes invoke Abort action on all clients AT MOST ONCE
                // that invoked Baselines or Assessments. This code will really execute an Abort action ONLY once so it's safe
                // to put it many times in this loop.
                abortActionInvoked = checkIfStopDetachmentRequestedAndInvokeAbort( baselineClientIds, assessmentClientIds,
                    abortActionInvoked, clientIdToClientInstanceMap, clientMap, loggingLevel )

                // If did not process all Baselines and Assessments notifications AND did not receive a Stop Detachment command
                // sleep for 5 sec and wash and repeat
                Thread.currentThread().sleep( SLEEPING_BETWEEN_NOTIFICATION_POLLING /* 5000 millis = 5 seconds */ )
            }
        }
    }

    //
    // Used by the postBaselineInvocationProcessing() method. Real Abort processing will be invoked ONLY once.
    //
    private boolean checkIfStopDetachmentRequestedAndInvokeAbort( List<String> baselineClientIds, List<String> assessmentClientIds,
        boolean abortActionInvoked, Map<String, Client> clientIdToClientInstanceMap, Map<String, String> clientMap, Integer loggingLevel )
    {
        // If received a Detachment Stop request, then invoke Abort on all clients that are still in progress
        // (either processing Baseline or Assessment actions) BUT only make sure to invoke it once
        if( SBDetachmentUtil.getInstance().stopDetachmentRequested() && !abortActionInvoked ){

            def clientIdsToInvokeAbortOn = []
            if( baselineClientIds ){
                clientIdsToInvokeAbortOn.addAll( baselineClientIds )
            }
            if( assessmentClientIds ){
                clientIdsToInvokeAbortOn.addAll( assessmentClientIds )
            }

            if( clientIdsToInvokeAbortOn ){

                clientIdsToInvokeAbortOn.each {

                    String errorMessage = null
                    Client clientInstance = clientIdToClientInstanceMap[ it ]

                    // Invoke Abort action. Note that in case Baseline or Assessment actions
                    // are NOT currently running on the box, this call will not throw any exceptions or errors.
                    try {
                        dispatcherCommunicationService.abort( loggingLevel, clientInstance );
                    }
                    catch ( DispatcherCommunicationException e ) {
                        errorMessage = e.message;
                    }
                    catch( Exception exp ){
                        // catch any other uncaught exception not specifically caught above
                        errorMessage = exp.message;
                    }

                    //
                    // errorMessage would be non-null if invoke Abort failed
                    //
                    if( errorMessage ){
                        // 1. set error into clientMap
                        clientMap[ it ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"

                        // ... 2. and also remove Client from clientIdToClientInstanceMap so it doesn't get processed further
                        clientIdToClientInstanceMap.remove( it )
                    }

                    int phaseId = baselineClientIds.contains( it ) ? SBDetachmentUtil.DETACH_PHASE_ABORT_BASELINE_ACTION_ID :
                                                                     SBDetachmentUtil.DETACH_PHASE_ABORT_ASSESS_ACTION_ID

                    // Store status
                    clientInstance.detachDataMap[ "status" ] = phaseId + ( errorMessage ? ":${errorMessage}" : "" )

                    // ... and persist it
                    try {
                        // Note: not checking the params.version here as done in the update() case
                        //  clientService.save(clientInstance);
                        save( clientInstance,
                            true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );
                    }
                    catch( SbClientException e ) {
                        // silently ignore -- status won't be set
                    }
                    catch( Exception exp ){
                        // silently ignore -- status won't be set
                    }
                }
            }

            // set flag to true so only invoke Abort once
            abortActionInvoked = true
        }

        return abortActionInvoked
    }

    // Used by detachClients() logic.
    //
    // Does not consider whether a Stop Detachment request was made WHILE THIS METHOD WAS CALLED OR NOT
    // (i.e. if this method was called for clientInstance, at the end of this method clientInstance will be either :
    // a. correctly detached (assuming there are no exceptions in it) signified by clientMap having
    //  {key=this clientId and value=Stringified detachedDate} OR
    // b. not detached, if there was any error signified by clientMap having {key=this clientId and value=Error{Actual error message}}
    //
    // This is coded that way as part of the Detachment Eager Completion strategy -- i.e. if there was a successful Baseline,
    // followed by a successful Assessment, and BOTH reports were fetched successfully then this method should be called (regardless
    // of the stop detachment request) with the intention of this Client being detached after this method's successful execution)
    private void performFinalPhaseOfDetachment( Client clientInstance, Map<String, String> clientMap ){
        
        if( clientInstance ){

            String errorMessage = null
            String clientId = clientInstance.id+""

            // Only run actual detachment on non-Detached (active) Clients only. Currently, due to the 
            // SBDetachUtil.startDetachment() ensuring that there is only *ONE* detachment operation in the system
            // it should not be possible for any Client to have clientInstance.dateDetached != null.
            if( !clientInstance.dateDetached ){

                // If client has a group then store all of the pertinent detachment info into the Map, including
                // backing up the security and baseline profiles
                if( clientInstance.group ){

                    // Store group name and id
                    clientInstance.detachDataMap[ Client.DETACHMENT_MAP_GROUP_NAME_KEY ] = clientInstance.group.name
                    clientInstance.detachDataMap[ Client.DETACHMENT_MAP_GROUP_NAME_ID_KEY ] = clientInstance.group.id+""

                    // Store security profile name and id (if any)
                    if( clientInstance.group.profile ){
                        clientInstance.detachDataMap[ Client.DETACHMENT_MAP_SECURITY_PROFILE_NAME_KEY ] = clientInstance.group.profile.name
                        clientInstance.detachDataMap[ Client.DETACHMENT_MAP_SECURITY_PROFILE_ID_KEY ] = clientInstance.group.profile.id+""

                        // Make sure Clients reports directory exists
                        File clientDir = SBFileSystemUtil.getClientDirectory( clientInstance.id );
                        try {
                            if ( !clientDir.exists() ) {
                                clientDir.mkdir()
                            }
                        }
                        catch( SecurityException se ){
                            errorMessage = se.message
                        }
                        catch( Exception exp ){
                            // catch any other uncaught exception not specifically caught above
                            errorMessage = exp.message;
                        }

                        if( !errorMessage ){

                            // Copy/overwrite the security-profile from /var/lib/oslockdown/profiles/${profile} to
                            // /var/lib/oslockdown/reports/ec/clients/${clientID}/security-profile-at-detachment.xml
                            try {
                                File sourceSecurityProfileFile = new File( SBFileSystemUtil.get(SB_LOCATIONS.PROFILES), clientInstance.group.profile.fileName);
                                File destinationSecurityProfileFile = new File( clientDir, Client.DETACHMENT_SECURITY_PROFILE_FILE_NAME );

                                FileUtils.copyFile( sourceSecurityProfileFile, destinationSecurityProfileFile );
                                m_log.info("Retained Client ["+clientInstance.name+"] security profile ["+clientInstance.group.profile.fileName+"]");

                                // Store baseline profile name and id (if any)
                                if( clientInstance.group.baselineProfile ){
                                    clientInstance.detachDataMap[ Client.DETACHMENT_MAP_BASELINE_PROFILE_NAME_KEY ] = clientInstance.group.baselineProfile.name
                                    clientInstance.detachDataMap[ Client.DETACHMENT_MAP_BASELINE_PROFILE_ID_KEY ] = clientInstance.group.baselineProfile.id+""

                                    // Copy/overwrite the baseline-profile from /var/lib/oslockdown/baseline-profiles/${baselineProfile} to
                                    // var/lib/oslockdown/reports/ec/clients/${clientID}/baseline-profile-at-detachment.xml
                                    File sourceBaselineProfileFile = new File( SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_PROFILES), clientInstance.group.baselineProfile.fileName);
                                    File destinationBaselineProfileFile = new File( clientDir, Client.DETACHMENT_BASELINE_PROFILE_FILE_NAME );

                                    FileUtils.copyFile( sourceBaselineProfileFile, destinationBaselineProfileFile );
                                    m_log.info("Retained Client ["+clientInstance.name+"] baseline profile ["+clientInstance.group.baselineProfile.fileName+"]");
                                }
                                else {
                                    errorMessage = messageSource.getMessage("dispatcher.baselineProfile.missing",
                                        [clientInstance.name, clientInstance.group.name] as Object[],null)
                                }
                            }
                            catch( IOException ie ){
                                errorMessage = ie.message
                            }
                            catch( Exception exp ){
                                // catch any other uncaught exception not specifically caught above
                                errorMessage = exp.message;
                            }
                        }
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                            [clientInstance.name, clientInstance.group.name] as Object[],null)
                    }
                }
                else {
                    errorMessage = messageSource.getMessage("dispatcher.group.missing", [clientInstance.name] as Object[], null)
                }
            }

            // Final processing for this client
            if( errorMessage ){
                clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"

                // Store status for phaseId 5
                clientInstance.detachDataMap[ "status" ] = "${SBDetachmentUtil.DETACH_PHASE_FIVE_RETAIN_PROFILES_AND_COMPLETE_DETACHMENT_ID} ${errorMessage}"
            }
            else {
                // After we saved off the group info and its associated profiles disconnect the Client from the Group
                clientInstance.group = null;

                // Set the detachDate to now
                clientInstance.dateDetached = new Date()

                // Clear the status flag used by the progress timer
                clientInstance.detachDataMap[ "status" ] = null
            }

            try {
                // Note: not checking the params.version here as done in the update() case
                //  clientService.save(clientInstance);
                save( clientInstance,
                    true /* immediately flush to db so that ClientController.checkDetachStatus() can get freshest value */ );

                // For successful detach, log as such and set clientMap[ clientId ] to the formatted detached date
                if( !errorMessage ){

                    m_log.info("Detached client ["+clientInstance.name+"]");
                    auditLogService.logClient("detach",clientInstance.name + " detachMap ["+clientInstance.detachDataMap+"]");

                    // Indicate a successful detachment by storing a detachment date MMM-dd-yyyy String. Otherwise, clientMap[ clientId ]
                    // starts with Error and contains an error
                    clientMap[ clientId ] = clientInstance.dateDetached.format( Client.DETACHED_DATE_FORMAT )
                }
            }
            catch( SbClientException e ) {
                // Can't call g.renderErrors from Service
                //  flash.error += g.renderErrors(bean:e.clientInstance,as:"list");

                // If got error only during the try {} catch, and there were no error previously; if there was
                // already an errorMessage, then clientMap[ clientId ] already contains it so don't change it
                if( !errorMessage ){

                    if( e.clientInstance?.hasErrors() ){
                        e.clientInstance.errors.allErrors.each { error ->
                            if( errorMessage )
                                errorMessage += messageSource.getMessage( error, null );
                            else
                                errorMessage = messageSource.getMessage( error, null );
                        }
                    }
                    else {
                        errorMessage = "Saving of the Client at detachment failed."+e.message
                    }
                    
                    clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"
                }
            }
            catch( Exception exp ){
                // catch any other uncaught exception not specifically caught above

                // If got error only during the try {} catch, and there were no error previously; if there was
                // already an errorMessage, then clientMap[ clientId ] already contains it so don't change it
                if( !errorMessage ){

                    errorMessage = "Saving of the Client at detachment failed."+exp.message;

                    clientMap[ clientId ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}${errorMessage}"
                }
            }
        }
    }

    // Assumes there is a currently running detach operation in progrss (otherwise throws an exception).
    // Invokes a stop detach request that causes detachClients() to finish up its detach logic and return
    // what it has already processed.
    // @return non-null error message in case of a failed stop detachment request and null in case of success
    String stopDetachClients(){

        String errorMessage
        try {
            SBDetachmentUtil.getInstance().stopDetachment()
        }
        catch( Exception e ){
            errorMessage = e.message
        }

        return errorMessage
    }

}
