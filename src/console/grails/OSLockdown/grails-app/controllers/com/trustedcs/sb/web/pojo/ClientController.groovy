/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo;

import org.apache.log4j.Logger;
import com.trustedcs.sb.services.client.agent.AgentResponse;
import com.trustedcs.sb.ws.client.AgentCommunicator;
import com.trustedcs.sb.ws.client.AgentCommunicator.ProductType;
import com.trustedcs.sb.metadata.Profile;

import grails.util.Environment;
import grails.orm.PagedResultList;

import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.reports.util.ReportType;

import org.apache.commons.io.FileUtils;
import com.trustedcs.sb.util.SBDetachmentUtil;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.util.SBJavaToJavaScriptUtil;

import com.trustedcs.sb.exceptions.SbClientException;
import com.trustedcs.sb.exceptions.ReportsException;
import com.trustedcs.sb.exceptions.DispatcherCommunicationException;


import org.hibernate.criterion.Order

class ClientController {
	
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.client");

    // inject services
    def messageSource;
    def clientService;
    def dispatcherCommunicationService;
    def reportsService;
    def auditLogService;
    def grailsApplication;
    
    // the delete, detach, save and update actions only accept POST requests
    static allowedMethods = [delete:'POST', detach:'POST', save:'POST', update:'POST'];

    static final String DETACHED_DATE_FORMAT = "MMM-dd-yyyy";

    // index redirect
    def index = { 
        redirect(action:list,params:params);
    }

    def list = {

        // params.max = Math.min( params.max ? params.max.toInteger() : 25,  100)

        m_log.info( "Client List Parameters: ${params}");

        def offset       = params.offset ? params.offset : "0"
        def max          = params.max    ? params.max    : "25"
        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table
        def sort         = ( params.sort == "group" || params.sort == "name" || params.sort == "hostAddress" || params.sort == "location" ||
                             params.sort == "dateCreated" || params.sort == "dateDetached" ) ? params.sort  : "name"
        def sortOrder    = ( params.order == "asc" || params.order == "desc" ) ? params.order : "asc"

        // Set detachedOnlyFilter and unDetachedOnlyFilter (applicable only for bulk mode)
        boolean isBulk = SbLicense.instance.isBulk()
        boolean detachedOnlyFilter = false;
        boolean unDetachedOnlyFilter = false;                
        if( isBulk && params.detachFilter ) {
            if( params.detachFilter == Client.DETACHMENT_CLIENTS_DETACHED ){
                detachedOnlyFilter = true
            }
            else if( params.detachFilter == Client.DETACHMENT_CLIENTS_ATTACHED ){
                unDetachedOnlyFilter = true
            }
        }

        PagedResultList clientResultList =
            Client.createCriteria().list( offset:offset, max:max ){

                // If params.search is passed use it to also search by Client name
                if( params.search ){
                    ilike( "name", "%${params.search}%" )
                    /* order( "name", sortOrder ) */
                }
                
                // For Bulk (aka Single-use) also include the detachFilter
                if( detachedOnlyFilter ){
                    isNotNull( "dateDetached" )
                }
                else if( unDetachedOnlyFilter ){
                    isNull( "dateDetached" )
                }
                // else (in Bulk) is All so no need to apply any filter -- this is the default; 
                // else (in Enterprise) do all undetached as all Clients are undetached

                // for sort == "group", sort by group.name. This also sorts correctly if group is null
                if( sort == "group" ){
                    createAlias ('group','_group',org.hibernate.criterion.CriteriaSpecification.LEFT_JOIN)
                    order( new Order ("_group.name", sortOrder == "asc").ignoreCase())
	                order( new Order (sort, sortOrder == "asc").ignoreCase())
                                        
                }
                // sort is a valid, direct property of Client use it in order
                else if( sort == "name" || sort == "hostAddress" || sort == "location" || sort == "dateCreated" || sort == "dateDetached" ){
	               order( new Order (sort, sortOrder == "asc").ignoreCase())
                }
            }

        // These are common parameters for both Enterprise and Bulk ...
        def finalResultMap = [ clientResultList:clientResultList, maxPerPage:max, search:params.search,
            // isBulk and isEnterprise are being used by list and _actionbar_multi as well
            isBulk:isBulk, isEnterprise:SbLicense.instance.isEnterprise() ]

        // ... in bulk also add one or two additional ones
        if( isBulk ){

            // Add logic -- controlls whether to show Actions+Logging Level + Client - Detach
            boolean atLeastOneUndetachedClient = false
            if( unDetachedOnlyFilter ){
                atLeastOneUndetachedClient = true
            }
            else if( !detachedOnlyFilter ){ // all filter ( !unDetachedOnlyFilter && !detachedOnlyFilter )
                // All filter so there is a mix of detached and undetached within the clientResultList.
                // Go over it and see if there is at least one undetached Client
                if( clientResultList ){
                    for ( def client : clientResultList ){
                        if( !client.dateDetached ){
                            atLeastOneUndetachedClient = true
                            
                            break
                        }
                    }
                }

            }
            finalResultMap[ "atLeastOneUndetachedClient" ] = atLeastOneUndetachedClient

            // Add detachFilter if present (if not filter=All) is assumed by the template
            if( params.detachFilter ){
                finalResultMap[ "detachFilter" ] = params.detachFilter
            }
        }

        // render list template with finalResultMap
        finalResultMap
    }

    def search = {

        def paramsMapForList = [search:params.search,offset:params.offset,max:params.max,sort:params.sort,order:params.order]

        // For bulk also include the detachFilter
        if( SbLicense.instance.isBulk() && params.detachFilter ){
            paramsMapForList[ "detachFilter" ] = params.detachFilter
        }

        // Search redirects to list() with all parameters and *adds the search parameter as well* entered by the user into the search text field
        redirect( action:"list", params:paramsMapForList )
    }

    def show = {
        def clientInstance = Client.get( params.id )

        if(!clientInstance) {
            flash.error = messageSource.getMessage("client.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }
                
        // Get the real-time status from the Client
        // TODO: Update once we have the messaging finished, for now simulate
        def clientInfo = clientInstance.info;
        if ( !(clientInfo) ) {
            clientInfo = new ClientInfo();
        }

        return [ clientInstance : clientInstance, clientInfo : clientInfo,
            // isBulk and isEnterprise are being used by show and _actionbar as well
            isBulk:SbLicense.instance.isBulk(), isEnterprise:SbLicense.instance.isEnterprise() ]
    }

    /**
     * Delete an individual client
     */
    def delete = {
        clearFlash();
        Client clientInstance = Client.get(params.id);
        if ( clientInstance ) {
            try {
                clientService.delete(clientInstance);
                auditLogService.logClient("delete",clientInstance.name);
            }
            catch ( SbClientException e ) {
                flash.error += g.renderErrors(bean:e.clientInstance);
                redirect(action:'show',id:'id');
            }
        }
        else {
            flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
        }
        redirect(action:'list');
    }
    
    /**
     * Removes multiple clients from the list
     */
    def deleteMulti = {
        // clear flash
        clearFlash();

        // get the ids of clients that will be deleted
        def ids = request.getParameterValues('clientList')?.collect { id ->
            id.toLong();
        }

        // delete each client in the list
        m_log.info("delete client ids" + ids);
        def clientInstance;
        ids.each { id ->
            clientInstance = Client.get(id);
            if ( clientInstance ) {
                try {
                    clientService.delete(clientInstance);
                    auditLogService.logClient("delete",clientInstance.name);
                }
                catch ( SbClientException e ) {
                    flash.error += g.renderErrors(bean:e.clientInstance);
                }
                }
            else {
                flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
            }
        }
        redirect(action:'list');
    }

    /**
     * Edit the client's configuration
     */
    def edit = {
    	m_log.info("Inside edit: ${params.id}");    		
        Client clientInstance = Client.get( params.id )
        if(!clientInstance) {
            flash.error = messageSource.getMessage("client.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }
        else {
            m_log.info("Client found")
            clientInstance.properties = params
            return [ clientInstance : clientInstance ]
        }
    }

    /**
     * Creating a new client.
     */
    def create = {
    	
        Client clientInstance = new Client()
        clientInstance.properties = params
        return ['clientInstance':clientInstance]
    }

    /**
     * Save created client
     */
    def save = {
    	clearFlash();
        // create the client instance
        Client clientInstance = new Client(params);
        try {
            clientService.save(clientInstance);
            auditLogService.logClient("add",clientInstance.name);
        }
        catch( SbClientException e ) {
            flash.error += g.renderErrors(bean:e.clientInstance,as:"list");
            // redirect to create action rather than render so that the error stored in flash is
            // only shown once. If render() is used rather than redirect() and the user clicks on Clients->List
            // (client/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
            // of list action as then error won't be displayed if get an error in the allowMulti() case.
            redirect(action:'create',params:params);
            return;
        }

        // show the newly created instance
        redirect(action:show,id:clientInstance.id)
    }

    /**
     * Abort any action on the client currently running
     */
    def abort = {
        clearFlash();
    	m_log.info("Client: abort for ${params.id}");
        flash.message = "Abort requested for client.";
        try {
            Client clientInstance = Client.get(params.id);
            dispatcherCommunicationService.abort(params.loggingLevel.toInteger(),clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to abort client action",e);
            flash.error = e.message;
        }
        redirect(action:show,id:params.id);
    }

    /**
     * Abort any action running on the selected clients
     */
    def abortMulti = {
    	clearFlash();
    	flash.message = "Abort requested for Clients.<br/>"
    	m_log.info("Action abort applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();

        // iterate over the ids and call apply on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    dispatcherCommunicationService.abort(loggingLevel,clientInstance);
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to abort client action",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);
    }

    /**
     * update client
     */
    def update = {
    	clearFlash();
        def clientInstance = Client.get( params.id )
        if(clientInstance) {
            if(params.version) {
                def version = params.version.toLong()
                if(clientInstance.version > version) {
                    clientInstance.errors.rejectValue("version", "client.optimistic.locking.failure", "Another user has updated this Client while you were editing.")
                    render(view:'edit',model:[clientInstance:clientInstance])
                    return
                }
            }
            clientInstance.properties = params;
            try {
                clientService.save(clientInstance);
                auditLogService.logClient("modify",clientInstance.name);
            }
            catch( SbClientException e ) {
                flash.error += g.renderErrors(bean:e.clientInstance,as:"list");
                // redirect to edit action rather than render so that the error stored in flash is
                // only shown once. If render() is used rather than redirect() and the user clicks on Clients->List
                // (client/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
                // of list action as then error won't be displayed if get an error in the allowMulti() case.
                redirect(action:'edit',params:params);
                return;
            }

            // Show the updated instance.
            // Fix for bugzilla #Bug 11015 - Editing (updating) client information from the console produces 500 exception
            // 1. MUST have a non-blank line here, as otherwise will get big problems
            // as there are no corresponding update.gsp and Grails throws No SecurityManager accessible exceptions.
            // 2. redirect to the show action as update() and save() are POST methods.
            redirect(action:show,id:clientInstance.id)
        }
        else {
            flash.error = messageSource.getMessage("client.not.found",[params.id] as Object[],null);
            redirect(action:'list');
        }
    }
    
    /**
     * Called from the show page of the client, will do an apply for the currently viewed client
     */
    def apply = {
        clearFlash();
    	m_log.info("Client: apply for ${params.id}");
        flash.message = "Apply requested for client.";
        try {
            Client clientInstance = Client.get(params.id);
            dispatcherCommunicationService.apply(params.loggingLevel.toInteger(),clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to apply profile",e);
            flash.error = e.message;
        }
        redirect(action:show,id:params.id);
    }
     
    /**
     * Executes an apply command on all the clients that have been selected
     */
    def applyMulti = { 	
    	clearFlash();
    	flash.message = "Apply requested for Clients.<br/>"    		 
    	m_log.info("Action Apply applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();

        // iterate over the ids and call apply on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    dispatcherCommunicationService.apply(loggingLevel,clientInstance);
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to apply profile",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);    	
    }
    
    /**
     * Called from the show page of the client, will do a scan for the currently viewed client
     */
    def scan = {
    	clearFlash();
    	m_log.info("Client: scan for ${params.id}");
        flash.message = "Scan requested for client.<br/>";
        try {
            Client clientInstance = Client.get(params.id);
            dispatcherCommunicationService.scan(params.loggingLevel.toInteger(),clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to scan profile",e);
            flash.error = e.message;
        }
        redirect(action:show,id:params.id);
    }
     
    /**
     * Executes a scan command on all clients that have been selected
     */
    def scanMulti = {
    	clearFlash();
    	flash.message = "Scan requested for Clients.<br/>"
    	m_log.info("Action Scan applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();

        // iterate over the ids and call apply on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    dispatcherCommunicationService.scan(loggingLevel,clientInstance);
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to scan",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);
    }
     
    def quickScan = {
    	clearFlash();
    	m_log.info("Client: quick scan for ${params.id}");
        flash.message = "Quick Scan requested for client.<br/>";
        try {
            Client clientInstance = Client.get(params.id);
            dispatcherCommunicationService.quickScan(params.loggingLevel.toInteger(),clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to quick scan profile",e);
            flash.error = e.message;
        }
        redirect(action:show,id:params.id);
    }
     
    /**
     * Executes a quick scan command on all clients that have been selected
     */
    def quickScanMulti = {
    	clearFlash();
    	flash.message = "Quick Scan requested for Clients.<br/>"
    	m_log.info("Action Quick Scan applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();

        // iterate over the ids and call apply on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    dispatcherCommunicationService.quickScan(loggingLevel,clientInstance);
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to quick scan",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);
    }    
     
    /**
     * Called from the show page of the client, will do an undo for that currently viewed
     * client.   
     */
    def undo = {
    	clearFlash();
    	m_log.info("Client: undo for ${params.id}");
        flash.message = "Undo requested for client.<br/>";
        try {
            Client clientInstance = Client.get(params.id);
            dispatcherCommunicationService.undo(params.loggingLevel.toInteger(),clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to undo profile",e);
            flash.error = e.message;
        }
        redirect(action:show,id:params.id);
    }
    
    /**
     * Executes an undo command on all clients that have been selected
     */
    def undoMulti = { 	
    	clearFlash();
    	flash.message = "Undo requested for Clients.<br/>"
    	m_log.info("Action undo applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();

        // iterate over the ids and call apply on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    dispatcherCommunicationService.undo(loggingLevel,clientInstance);
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to undo profile",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);
    }        
    
    /**
     * Called from the show page of the client, will do a baseline for that currently viewed
     * client.  
     */
    def baseline = {
    	clearFlash();
    	m_log.info("Client: baseline for ${params.id}");
        flash.message = "Baseline requested for client.<br/>";
        try {
            Client clientInstance = Client.get(params.id);
            dispatcherCommunicationService.baselineWithProfile(params.loggingLevel.toInteger(),clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to baseline client",e);
            flash.error = e.message;
        }
        redirect(action:show,id:params.id);
    }
     
    /**
     * Executes a baseline command on all clients that have been selected
     */
    def baselineMulti = {    	
    	clearFlash();
    	flash.message = "Baseline requested for Clients.<br/>"
    	m_log.info("Action baseline applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();

        // iterate over the ids and call apply on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    dispatcherCommunicationService.baselineWithProfile(loggingLevel,clientInstance);
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to baseline client",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);
    }
     
    /**
     * Show the latest client assessment report
     * will redirect to the report controller
     */
    def showAssessmentReport = {
    	clearFlash();
    	def reportFile;
        try {
            Client clientInstance
            if( params.id ){
                clientInstance = Client.get( params.id.toLong() );
                if( clientInstance ){

                    // If it's a Bulk mode and client is detached grab latest report from the local file system rather than from client.
                    // Otherwise, always go to the Client first.
                    boolean useFileSystem = ( SbLicense.instance.isBulk() && clientInstance.dateDetached )

                    reportFile = reportsService.getLatestReport( clientInstance, ReportType.ASSESSMENT, useFileSystem );
                }
            }

            if( !clientInstance ){            
                String missingClientMessage = messageSource.getMessage("client.not.found",[params.id] as Object[],null);
                String errorMessage = "Unable to get latest assessment from client with id ["+params.id+"] error ["+missingClientMessage+"]";
                m_log.error( errorMessage );
                flash.error = errorMessage;
                redirect(action:show,id:params.id);
                return;
            }
        }
        catch ( ReportsException e ) {
            m_log.error(e);
            flash.error = e.message;
            redirect(action:show,id:params.id);
            return;
        }
		
        redirect(controller:'report',
            action:ReportType.ASSESSMENT.viewLocation,
            params:["clientId":params.id,
                        "dataSet":reportFile.name]);
    }
     
    /**
     * Show the latest client baseline report
     * will redirect to the report controller
     */
    def showBaselineReport = {
        clearFlash();
    	def reportFile;
        try {
            Client clientInstance
            if( params.id ){
                clientInstance = Client.get( params.id.toLong() );
                if( clientInstance ){

                    // If it's a Bulk mode and client is detached grab latest report from the local file system rather than from client.
                    // Otherwise, always go to the Client first.
                    boolean useFileSystem = ( SbLicense.instance.isBulk() && clientInstance.dateDetached )

                    reportFile = reportsService.getLatestReport( clientInstance, ReportType.BASELINE, useFileSystem );
                }
            }

            if( !clientInstance ){
                String missingClientMessage = messageSource.getMessage("client.not.found",[params.id] as Object[],null);
                String errorMessage = "Unable to get latest baseline from client with id ["+params.id+"] error ["+missingClientMessage+"]";
                m_log.error( errorMessage );
                flash.error = errorMessage;
                redirect(action:show,id:params.id);
                return;
            }
            
        }
        catch ( ReportsException e ) {
            m_log.error(e);
            flash.error = e.message;
            redirect(action:show,id:params.id);
            return;
        }
    	        
        redirect(controller:'report',
            action:ReportType.BASELINE.viewLocation,
            params:["clientId":params.id,
                        "dataSet":reportFile.name]);
    }
     
    /**
     * AJAX taconite AHAH request handler queries the client
     * and returns the status of the client
     */
    def updateClientStatus = {
    	clearFlash();
        m_log.info("Dispatcher status requested: ${params}");
    	def statusMap = [:];
        try {
            Client clientInstance = Client.get(params.clientId);
            statusMap = dispatcherCommunicationService.dispatcherStatus(clientInstance);
        }
        catch ( DispatcherCommunicationException e ) {
            // display error message
            m_log.error(e.message);
            flash.error = e.message;
        }
        // We've got issues using flash in ajax calls, so use this map instead
        def ajaxFlash = [:]
        ajaxFlash.warning = flash.warning
        ajaxFlash.error = flash.error
        ajaxFlash.messages = flash.messages
        clearFlash()

    	// send the model to the taconite page
        [statusMap:statusMap, ajaxFlash:ajaxFlash];    	
    }
     
    /**
     * AJAX taconite AHAH request handler queries the client
     * and returns the status of the client
     */
    def updateClientInfo = {
    	clearFlash();
        m_log.info("Host info requested: ${params}");
        def hostInfoMap = [:];
        Client clientInstance;
        try {
            clientInstance = Client.get(params.clientId);
            if ( !(clientInstance.info) ) {
                clientInstance.info = new ClientInfo();
            }
            hostInfoMap = dispatcherCommunicationService.hostInfo(clientInstance);
            clientService.updateClientInfo(clientInstance,hostInfoMap);
        }
        catch ( SbClientException clientException) {
            m_log.error(clientException.message);
            flash.error = clientException.message;
        }
        catch ( DispatcherCommunicationException communicationException ) {
            // display error message
            m_log.error(communicationException.message);
            flash.error = communicationException.message;
        }

        // We've got issues using flash in ajax calls, so use this map instead
        def ajaxFlash = [:]
        ajaxFlash.warning = flash.warning
        ajaxFlash.error = flash.error
        ajaxFlash.messages = flash.messages
        clearFlash()

    	// send the model to the taconite page
        [clientInfo:clientInstance.info, ajaxFlash:ajaxFlash];
    }
     
    /**
     * Clears the flash of all messages that are currently set on it
     */
    private void clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }

    /**
     * This is an Ajax call method. Only allowed on POST. Real work is done by the ClientService.detachClients() method.
     */
    def detach = {

        clearFlash();

        List idsAsList = SBJavaToJavaScriptUtil.convertJavaScriptListToJavaList( params.clientIdList )
        def ids = idsAsList.collect { id ->
            id.toLong();
        }

        def clients
        if( ids ){
            clients = Client.getAll( ids )
        }

        Map<String, String> clientMap = clientService.detachClients( clients, params.loggingLevel.toInteger() )

        // If invoked from Client Show page AND the detach was successful then also include that one ClientInfo information in the returned Map
        // which will be used to populate the Client Detail area of the page
        if( params.fromClientShow && clients && clients.size() == 1 &&
            clientMap && ! clientMap[ clients[0].id+"" ].startsWith( Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX ) ){

            def clientInfo = clients[0].info
            if( clientInfo ){
                clientMap[ ClientInfo.CLIENT_VERSION ]  = clientInfo.clientVersion
                clientMap[ ClientInfo.NODE_NAME ]       = clientInfo.nodeName
                clientMap[ ClientInfo.DISTRIBUTION ]    = clientInfo.distribution
                clientMap[ ClientInfo.KERNEL ]          = clientInfo.kernel
                clientMap[ ClientInfo.UPTIME ]          = clientInfo.uptime
                clientMap[ ClientInfo.ARCHITECTURE ]    = clientInfo.architecture
                clientMap[ ClientInfo.LOAD_AVERAGE ]    = clientInfo.loadAverage
                clientMap[ ClientInfo.MEMORY ]          = clientInfo.memory
                clientMap[ ClientInfo.COREHOURS ]       = clientInfo.corehours
                clientMap[ ClientInfo.MAXLOAD ]          = clientInfo.maxload
            }
        }

        String clientMapAsString = SBJavaToJavaScriptUtil.convertJavaMapToJavaScriptMap( clientMap )

        // Because with Ajax page is not resubmitted can't do this to set the errors. Instead
        // pass errors in the resulting map and construct errors
        //  flash.error = "There was an BIG error"
        render clientMapAsString
    }

    def checkDetachStatus = {

        Map<String, String> clientMap

        List idsAsList = SBJavaToJavaScriptUtil.convertJavaScriptListToJavaList( params.clientIdList )
        def ids = idsAsList.collect { id ->
            id.toLong();
        }

        if( ids ){

            clientMap = [:]

            Client clientInstance
            ids.each {

                String detachmentStatus = null

                clientInstance = Client.get( it )
                
                if( clientInstance && clientInstance.detachDataMap ){
                    detachmentStatus = clientInstance.detachDataMap[ "status" ]
                }

                // If no detachmentStatus return status unavailable
                if( !detachmentStatus ){
                    detachmentStatus = SBDetachmentUtil.DETACHMENT_STATUS_UNAVAILABLE
                }
                else { // Otherwise format if property and consistently
                    detachmentStatus = SBDetachmentUtil.getUserFormattedStatusMessage( detachmentStatus )
                }

                // {key=Client name, value=Status}
                clientMap[ clientInstance.name ] = detachmentStatus
            }
        }

        // If if no ids or couldn't fetch clients, etc. set a generic error without listing Client name.
        if( !clientMap ){
            clientMap = [:]
            clientMap[ "0" ] = SBDetachmentUtil.DETACHMENT_STATUS_UNAVAILABLE
        }

        String clientMapAsString = SBJavaToJavaScriptUtil.convertJavaMapToJavaScriptMap( clientMap )

        // Because with Ajax page is not resubmitted can't do this to set the errors. Instead
        // pass errors in the resulting map and construct errors
        //  flash.error = "There was an BIG error"
        render clientMapAsString
    }

    def stopDetachClients = {

        String errorMessage = clientService.stopDetachClients()
        render errorMessage ?: "success"
    }
            
    /**
     * Called from the show page of the client, will do an autoUpdate for the currently viewed client
     */
    def autoUpdate = {
        clearFlash();
    	m_log.info("Client: AutoUpdate for ${params.id}");
        flash.message = "AutoUpdate requested for client.";

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();
        def autoupdateon = params.autoupdateon.toInteger();
        byte [] firstUpdater 
        byte [] updaterFile 
        boolean forceUpdate = false
        
        try {
            updaterFile = new File("/var/lib/oslockdown/files/ClientUpdates/autoupdate.tgz").readBytes()
        }
        catch (Exception e) {
            flash.error += e.message
        }
        
        // Set our options based on the autoupate options
        if (autoupdateon == 1)
        {
          firstUpdater = updaterFile
        }
        if (autoupdateon == 2)
        {
          firstUpdater = updaterFile
          forceUpdate = true
        }

        try {
            Client clientInstance = Client.get(params.id);
            String updateStatus = dispatcherCommunicationService.autoUpdate(firstUpdater, forceUpdate, loggingLevel, clientInstance);
            m_log.info("AutoUpdate Query : ${updateStatus}")

            // If the client indicates a difference in major version number, then kickdown the updater core.
            if (updateStatus.contains("Update Required") && updaterFile)
            {
                System.out.println("Sending secondary update command")
                updateStatus = dispatcherCommunicationService.autoUpdate(updaterFile, forceUpdate, loggingLevel, clientInstance);            
            }
            // and finally flash up whatever is left (in other words - update in progress, update not required)
            flash.message = clientInstance.name + " : " + updateStatus;
        }
        catch ( DispatcherCommunicationException e ) {
            m_log.error("Unable to issue AutoUpdate to Client",e);
            flash.error += e.message;
        }
        redirect(action:show,id:params.id);
    }
     
    /**
     * Executes an AutoUpdate command on all the clients that have been selected
     */
    def autoUpdateMulti = { 	
    	clearFlash();
    	flash.message = "AutoUpdate requested for Clients.  Refer to Notification page for status results.<br/>"    		 
    	m_log.info("Action AutoUpdate applied to multiple clients: ${params.clientList.toString()}")

        // get the selected clients and convert them to longs
    	def ids = request.getParameterValues('clientList').collect { clientId ->
            clientId.toLong();
        }

        // get the logging level
        def loggingLevel = params.loggingLevel.toInteger();
        def autoupdateon = params.autoupdateon.toInteger();
        byte [] firstUpdater   
        byte [] updaterFile  
        boolean forceUpdate = false

        try {
            updaterFile = new File("/var/lib/oslockdown/files/ClientUpdates/autoupdate.tgz").readBytes()
        }
        catch (Exception e) {
            flash.error += e.message
        }

        // Set our options based on the autoupate options
        if (autoupdateon == 1)
        {
          firstUpdater = updaterFile
        }
        if (autoupdateon == 2)
        {
          firstUpdater = updaterFile
          forceUpdate = true
        }
        
        // iterate over the ids and call  on all the clients
        ids.each { id ->
            try {
                Client clientInstance = Client.get(id);
                if ( clientInstance ) {
                    String updateStatus = dispatcherCommunicationService.autoUpdate(firstUpdater, forceUpdate, loggingLevel,clientInstance);
                    m_log.info("AutoUpdate Query : ${updateStatus}")

                    // If the client indicates a difference in major version number, then kickdown the updater core.
                    if (updateStatus.contains("Update Required") && updaterFile )
                    {
                        System.out.println("Sending secondary update command")
                        updateStatus = dispatcherCommunicationService.autoUpdate(updaterFile, forceUpdate, loggingLevel, clientInstance);    
                    }
            // and finally flash up whatever is left (in other words - update in progress, update not required)
                }
                else {
                    flash.error += messageSource.getMessage("client.not.found",[id] as Object[],null);
                }
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to issue AutoUpdate to Client",e);
                flash.error += "${e.message}<br>";
            }
        }

        // redirect to the client list
    	redirect(action:list,params:[clientList:request.getParameterValues('clientList')]);    	
    }
    


}
