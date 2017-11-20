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

import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.scheduler.ScheduledTask;
import org.apache.log4j.Logger;

import com.trustedcs.sb.exceptions.SbGroupException;
import com.trustedcs.sb.exceptions.DispatcherCommunicationException;

import com.trustedcs.sb.util.SBJavaToJavaScriptUtil;

import com.trustedcs.sb.ws.client.AgentCommunicator;
import com.trustedcs.sb.ws.client.AgentCommunicator.ProductType;
import com.trustedcs.sb.ws.client.SchedulerCommunicator;
import com.trustedcs.sb.services.client.agent.AgentResponse;
import com.trustedcs.sb.services.client.scheduler.SchedulerResponse;
import com.trustedcs.sb.services.client.scheduler.DispatcherTask;

import grails.util.Environment;
import grails.orm.PagedResultList;

import org.apache.commons.io.FileUtils;
import com.trustedcs.sb.util.SBDetachmentUtil;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import org.hibernate.criterion.Order

class GroupController {
	
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.GroupController");

    // service injection
    def messageSource;
    def groupService;
    def clientService;
    def auditLogService;
    def dispatcherCommunicationService;
    def grailsApplication;

    static final String GROUP_BY_CLIENTS_COUNT_QUERY_PREFIX =
                        "SELECT g.id FROM Group g LEFT JOIN g.clients AS clients GROUP BY g.id ORDER BY COUNT(clients) "
    
    /**
     * Redirect index to list
     */
    def index = { 
        redirect(action:list,params:params)
    }

    // the delete, save and update actions only accept POST requests
    static allowedMethods = [delete:'POST',detach:'POST',save:'POST', update:'POST']

    /**
     * Show all the groups
     */
    def list = {
        m_log.info(params);

        def offset       = params.offset ? params.offset : "0"
        def max          = params.max ? params.max: "25"
        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table
        def sort         = ( params.sort == "clients" || params.sort == "profile" || params.sort == "baselineProfile" ||
                             params.sort == "name" || params.sort == "description" ) ? params.sort  : "name"
        def sortOrder    = ( params.order == "asc" || params.order == "desc" ) ? params.order : "asc"

        def groupList

        if( sort != "clients" ){
            //
            // Non "clients" sort property
            //
            groupList = Group.createCriteria().list( offset:offset, max:max ){

                // for sort == "profile", sort by profile.name. This also sorts correctly if profile is null
                if( sort == "profile" ){
                    createAlias ('profile','_profile',org.hibernate.criterion.CriteriaSpecification.LEFT_JOIN)
                    order (new Order('_profile.name', sortOrder=="asc").ignoreCase()) 
                }
                else if( sort == "baselineProfile" ){
                    createAlias ('baselineProfile','_baselineProfile',org.hibernate.criterion.CriteriaSpecification.LEFT_JOIN)
                    order (new Order('_baselineProfile.name', sortOrder=="asc").ignoreCase()) 
                }
                else if( sort == "baselineProfile2" ){
                    baselineProfile (org.hibernate.criterion.CriteriaSpecification.LEFT_JOIN){
                        order( new Order("name", sortOrder=="asc").ignoreCase() )
                    }
                }
                // sort is a valid, direct property of Group use it in order
                else if( sort == "name" || sort == "description" ){
                     order( new Order(sort, sortOrder=="asc").ignoreCase() )
                }
            }
        }
        else if (sort == "clients") {
            String hql = "SELECT g FROM Group g order by size(g.clients) ${sortOrder == "desc" ? "DESC" : "ASC"}, upper(g.name) ${sortOrder == "desc" ? "DESC" : "ASC"}"
            groupList = Group.executeQuery( hql, [max:max, offset:offset] )
            print groupList
            print hql
        }
        else {
            //
            // "clients" sort property is a complex one.
            //

            // 1. First figure out the Group ids ordered from largest / smallest based on sortOrder.
            String hql = "${GROUP_BY_CLIENTS_COUNT_QUERY_PREFIX} ${sortOrder == "desc" ? "DESC" : "ASC"}"
            // idList contains ids in CORRECT order, and it also contains the correct page. Unfortunately, Group.executeQuery()
            // does not return PagedResultList, but we know that we are going over all Groups so we can figure out the totalCount
            // just by doing Group.count() (which still sucks as it's an additional, although inexpensive query)
            def groupIdList = Group.executeQuery( hql, [max:max, offset:offset] )

            def resultingGroupList
            if( groupIdList ){
                // 2. Now let's fetch Groups corresponding to groupIdList to ensure the order of objects returned is exactly as on the in().
                // This can be done with (ex. if groupIdList=[4,5,1])
                //    hql = "SELECT g from Group as g where g.id in (4,5,1) ORDER BY CASE g.id when 4 then 1 when 5 then 2 when 1 then 3 end"
                // however, that is very messy, instead just use Group.getAll( [4,5,1] )
                // Note: getAll() can't be used with paginate parameters,
                resultingGroupList = Group.getAll( groupIdList )
            }
            else {
                resultingGroupList = []
            }

            // 3. Figure out total Group Count
            int totalGroupCount = Group.count()

            // 4. Finally construct PagedResultList object passing in correct page with Groups (resultingGroupList) and
            // totalGroupCount which is used on the .gsp to know whether to show page buttons
//            groupList = new PagedResultList( resultingGroupList, totalGroupCount )
            groupList = resultingGroupList
        }

        // isBulk is used by the list and _actionbar_multi
        [ groupList:groupList, totalCount:Group.count(), maxPerPage:max, isBulk:SbLicense.instance.isBulk() ]
    }
	
    /**
     * Create a new group by redirecting the request to the edit page
     */
    def create = {
        clearFlash();

        // empty group
        Group groupInstance = new Group();

    	// list of unassociated clients
    	def missingClients = Client.withCriteria {
            order("name","asc");
            isNull("group");

            // In Bulk mode only include Non-detached Clients
            if( SbLicense.instance.isBulk() ){
                isNull("dateDetached");
            }
    	};

    	// list of clients for *this* group
    	def groupClients = []

    	def securityProfileList = Profile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        def baselineProfileList = BaselineProfile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        return [ groupInstance : groupInstance,
            missingClients:missingClients,
            groupClients:groupClients,
            securityProfileList:securityProfileList,
            baselineProfileList:baselineProfileList]
    }

    /**
     * Edit the group
     */
    def edit = {
        clearFlash();
    	m_log.info("Inside edit: ${params.id}");

        // find the group
        Group groupInstance = Group.get( params.id )
        if(!groupInstance) {
            flash.error = messageSource.getMessage("group.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }

    	// list of unassociated clients
    	def missingClients = Client.withCriteria {
            order("name","asc");
            isNull("group");

            // In Bulk mode only include Non-detached Clients
            if( SbLicense.instance.isBulk() ){
                isNull("dateDetached");
            }
    	};
    	// list of clients for *this* group
    	def groupClients = Client.withCriteria {
            order("name","asc");
            eq("group",groupInstance);

            // In Bulk mode only include Non-detached Clients
            if( SbLicense.instance.isBulk() ){
                isNull("dateDetached");
            }
    	};

    	def securityProfileList = Profile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        def baselineProfileList = BaselineProfile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }
        return [ groupInstance : groupInstance,
            missingClients:missingClients,
            groupClients:groupClients,
            securityProfileList:securityProfileList,
            baselineProfileList:baselineProfileList]
    }

    /**
     * Show the group in question
     */
    def show = {
        def groupInstance = Group.get( params.id )

        if(!groupInstance) {
            flash.error = messageSource.getMessage("group.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }

        return [ groupInstance : groupInstance, isBulk:SbLicense.instance.isBulk() ]
    }

    /**
     * Save created client
     */
    def save = {
    	print params
        clearFlash();
        // create the group instance
        Group groupInstance = new Group(params);
        // the clients that will be the set for the group
    	def clientIds = request.getParameterValues('selectedList').collect {
            it.toLong();
    	}

        // save the group with the service
        try {
            groupService.save(groupInstance,params,clientIds);
            auditLogService.logGroup("add",groupInstance.name);
        }
        catch( SbGroupException e ) {
            flash.error += g.renderErrors(bean:e.groupInstance,as:"list");
            render(view:'create',model:[groupInstance:e.groupInstance]);
            return;
        }

        // show the newly created instance
        redirect(action:show,id:groupInstance.id)
    }

    /**
     * Update and existing client
     */
    def update = {
        print params
        clearFlash();
        // find the group instance
        Group groupInstance = Group.get(params.id);
        if(!groupInstance) {
            flash.error = messageSource.getMessage("group.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }

        // the clients that will be the set for the group
    	def clientIds = request.getParameterValues('selectedList').collect {
            it.toLong();
    	}

        // use the group service to update the group
        try {
            def problems
            problems = groupService.update(groupInstance,params,clientIds);
            if (problems) {
                flash.error = problems.join("<br>")
            }
            auditLogService.logGroup("modify",groupInstance.name);
        }
        catch( SbGroupException e ) {
            flash.error += g.renderErrors(bean:e.groupInstance,as:"list");
            render(view:'edit',model:[groupInstance:e.groupInstance]);
            return;
        }
        redirect(action:show,id:groupInstance.id);
    }

    /**
     * Delete the group instance
     */
    def delete = {
        // clear flash
        clearFlash();

        // find the group
        Group groupInstance = Group.get(params.id);
        if ( groupInstance ) {
            try {
                groupService.delete(groupInstance);
                auditLogService.logGroup("delete",groupInstance.name);
            }
            catch ( SbGroupException e ) {
                flash.error += g.renderErrors(bean:e.groupInstance);
            }
        }
        else {
            flash.error += messageSource.getMessage("group.not.found",[id] as Object[],null);
        }

        // redirect back to the group list
        redirect(action:'list');
    }
	
    /**
     * Removes multiple groups from the DB based on the ID list that
     * is gathered from selected combo boxes
     */
    def deleteMulti = {
        // clear flash
        clearFlash();

        // get the ids of the groups
        def ids = request.getParameterValues('groupList')?.collect { id ->
            id.toLong();
        }

        // delete each group in the list
        m_log.info("delete group ids" + ids);
        def groupInstance;
        ids.each { id ->
            groupInstance = Group.get(id);
            if ( groupInstance ) {
                try {
                    groupService.delete(groupInstance);
                    auditLogService.logGroup("delete",groupInstance.name);
                }
                catch ( SbGroupException e ) {
                    flash.error += g.renderErrors(bean:e.groupInstance);
                }
            }
            else {
                flash.error += messageSource.getMessage("group.not.found",[id] as Object[],null);
            }
        }
        redirect(action:'list');
    }

    /**
     * This is an Ajax call method. Only allowed on POST. Real work is done by the ClientService.detachClients() method.
     */
    def detach = {

        clearFlash();

        Map<String, String> clientMap

        Long groupId
        if( params.groupId ){
            try {
                groupId = params.groupId.toLong();
            }
            catch( Exception e){
                groupId = null
            }
        }

        if( !groupId ){
            // throw an exception

            clientMap = [:]
            clientMap[ "0" ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}Detach Clients should be performed exactly on one Group."
        }
        else {
            // Exactly one Group was selected. Try to fetch the Group and its Clients. Don't check if Group also has
            // a Security and a Baseline Profile as that is already done in the ClientController.detach which this method invokes.
            Group groupInstance = Group.get( groupId );
            if( groupInstance ){

                List<Client> clientsList = groupInstance.clients?.collect { it }
                
                                                         // Pass group Clients
                clientMap = clientService.detachClients( clientsList, params.loggingLevel.toInteger() )
            }
            else {
                // Error
                clientMap = [:]
                clientMap[ "0" ] = "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}Nonexistent Group with id ["+idsAsList[ 0 ]+"]."
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

        Long groupId
        if( params.groupId ){
            try {
                groupId = params.groupId.toLong();
            }
            catch( Exception e){
                groupId = null
            }
        }

        if( groupId ){

            // Exactly one Group was selected. Try to fetch the Group and its Clients. Don't check if Group also has
            // a Security and a Baseline Profile as that is already done in the ClientController.detach which this method invokes.
            Group groupInstance = Group.get( groupId );

            def orderedByNameGroupsClients
            if( groupInstance ){
                // Make sure to get Group's clients in asc order of their name. Otherwise (if use group.clients for exaple), the Client status
                // order of the clients is different almost on every call and it's very annoying
                orderedByNameGroupsClients = Client.findAllByGroup( groupInstance, [sort: 'name', order:'asc'] )
            }

            if( orderedByNameGroupsClients){

                clientMap = [:]

                // iterate over the ids and call scan on all the clients
                orderedByNameGroupsClients.each { clientInstance ->

                    String detachmentStatus = null

                    if( clientInstance ){
                        
                        if( clientInstance.detachDataMap ){
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
            }
        }

        // If Group was not valid or had no Clients set a generic error without listing Client name.
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

    def abort = {
        clearFlash();
        flash.message = "Abort requested for Group.<br/>";

        // find the group
        Group groupInstance = Group.get(params.id);

        // grap the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);

        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                dispatcherCommunicationService.abort(loggingLevel,clientInstance);
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to abort actions on client",e);
                flash.error += "${e.message}<br/>";
            }
        }

        // redirect to show page
        redirect(action:show,id:groupInstance.id);
    }

    def abortMulti = {
        clearFlash();
        flash.message = "Abort requested for Groups.<br/>"
        // the group
        def group;

        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }

        def loggingLevel = Integer.parseInt(params.loggingLevel);
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    dispatcherCommunicationService.abort(loggingLevel,clientInstance);
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to abort actions on client",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }

        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }

    def quickScan = {
        clearFlash();
        flash.message = "Quick Scan requested for Group.<br/>"

        // find the group
        Group groupInstance = Group.get(params.id);

        // capture the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);

        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                dispatcherCommunicationService.quickScan(loggingLevel,clientInstance);
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to quick scan client",e);
                flash.error += "${e.message}<br>";
            }
        }

        // send back to the list
        redirect(action:show,id:groupInstance.id);
    }
	
    def quickScanMulti = {
        clearFlash();
        flash.message = "Quick Scan requested for Groups.<br/>"
        // the group
        def group;

        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }

        def loggingLevel = Integer.parseInt(params.loggingLevel);
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    dispatcherCommunicationService.quickScan(loggingLevel,clientInstance);
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to quick scan client",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }

        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }

    /**
     * Scan the group with its configured profile
     */
    def scan = {
        clearFlash();
        flash.message = "Scan requested for Group.<br/>"

        // find the group
        Group groupInstance = Group.get(params.id);

        // capture the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);

        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                dispatcherCommunicationService.scan(loggingLevel,clientInstance);
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to scan client",e);
                flash.error += "${e.message}<br>";
            }
        }

        // send back to the group show page
        redirect(action:show,id:groupInstance.id);
    }
	
    /**
     * Scan the groups with its configured profile
     */
    def scanMulti = {
        clearFlash();
        flash.message = "Scan requested for Groups.<br/>"
        // the group
        def group;        
		
        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }
		
        def loggingLevel = Integer.parseInt(params.loggingLevel);		
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    dispatcherCommunicationService.scan(loggingLevel,clientInstance);
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to scan client",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }
		
        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }

    /**
     * Apply the group's configured profile
     */
    def apply = {
        clearFlash();
        flash.message = "Apply requested for Group.<br/>"

        // find the group
        Group groupInstance = Group.get(params.id);

        // capture the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);

        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                dispatcherCommunicationService.apply(loggingLevel,clientInstance);
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to apply profile",e);
                flash.error += "${e.message}<br>";
            }
        }

        // send back to the list
        redirect(action:show,id:groupInstance.id);
    }
	 
    /**
     * Apply the group's configured profile
     */
    def applyMulti = {
        clearFlash();
        flash.message = "Apply requested for Groups.<br/>"
        // the group
        def group;

        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }

        def loggingLevel = Integer.parseInt(params.loggingLevel);
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    dispatcherCommunicationService.apply(loggingLevel,clientInstance);
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to apply profile",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }

        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }

    def undo = {
        clearFlash();
        flash.message = "Undo requested for Group.<br/>"
        // find the group
        Group groupInstance = Group.get(params.id);

        // capture the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);

        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                dispatcherCommunicationService.undo(loggingLevel,clientInstance);
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to undo profile",e);
                flash.error += "${e.message}<br>";
            }
        }

        // send back to the list
        redirect(action:show,id:groupInstance.id);
    }
	
    /**
     * Undo the application of a profile for the group
     */
    def undoMulti = {
        clearFlash();
        flash.message = "Undo requested for Groups.<br/>"
        // the group
        def group;

        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }

        def loggingLevel = Integer.parseInt(params.loggingLevel);
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    dispatcherCommunicationService.undo(loggingLevel,clientInstance);
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to undo profile",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }

        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }

    def baseline = {
        clearFlash();
        flash.message = "Baseline requested for Group.<br/>"
        // find the group
        Group groupInstance = Group.get(params.id);

        // capture the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);

        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                dispatcherCommunicationService.baselineWithProfile(loggingLevel,clientInstance);
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to basline client",e);
                flash.error += "${e.message}<br>";
            }
        }        

        // send back to the list
        redirect(action:show,id:groupInstance.id);
    }
	
    /**
     * Have each client in the group run a baseline
     */
    def baselineMulti = {
        clearFlash();
        flash.message = "Baseline requested for Groups.<br/>"
        // the group
        def group;

        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }

        def loggingLevel = Integer.parseInt(params.loggingLevel);
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    dispatcherCommunicationService.baselineWithProfile(loggingLevel,clientInstance);
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to basline client",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }

        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }

    def autoUpdate = {
        clearFlash();
        flash.message = "AutoUpdate requested for Group.  Refer to Notification page for status results.<br/>";

        // find the group
        Group groupInstance = Group.get(params.id);

        // grap the logging level
        def loggingLevel = Integer.parseInt(params.loggingLevel);
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
        
        // iterate over the ids and call scan on all the clients
        groupInstance.clients?.each { clientInstance ->
            try {
                String updateStatus = dispatcherCommunicationService.autoUpdate(firstUpdater, forceUpdate, loggingLevel,clientInstance);
                m_log.info("AutoUpdate Query : ${updateStatus}")

                // If the client indicates a difference in major version number, then kickdown the updater core.
                if (updateStatus.contains("Update Required") && updaterFile)
                {
                    System.out.println("Sending secondary update command")
                    updateStatus = dispatcherCommunicationService.autoUpdate(updaterFile, forceUpdate, loggingLevel, clientInstance);            
                }
                // and finally flash up whatever is left (in other words - update in progress, update not required)
            }
            catch ( DispatcherCommunicationException e ) {
                m_log.error("Unable to initiate AutoUpdate on client",e);
                flash.error += "${e.message}<br/>";
            }
        }

        // redirect to show page
        redirect(action:show,id:groupInstance.id);
    }

    def autoUpdateMulti = {
        clearFlash();
        flash.message = "AutoUpdate requested for Groups.  Refer to Notification page for status results.<br/>"
        // the group
        def group;

        // find all the groups that are going to be affected
        def ids = request.getParameterValues('groupList').collect { id ->
            id.toLong();
        }

        def loggingLevel = Integer.parseInt(params.loggingLevel);
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
        
        // iterate the groups
        ids.each { groupId ->
            // find the group
            group = Group.get(groupId);
            // iterate over the ids and call scan on all the clients
            group.clients?.each { clientInstance ->
                try {
                    String updateStatus = dispatcherCommunicationService.autoUpdate(firstUpdater, forceUpdate, loggingLevel,clientInstance);
                    m_log.info("AutoUpdate Query : ${updateStatus}")

                    // If the client indicates a difference in major version number, then kickdown the updater core.
                    if (updateStatus.contains("Update Required") && updaterFile)
                    {
                        System.out.println("Sending secondary update command")
                        updateStatus = dispatcherCommunicationService.autoUpdate(updaterFile, forceUpdate, loggingLevel, clientInstance);        
                    }
                    // and finally flash up whatever is left (in other words - update in progress, update not required)
                }
                catch ( DispatcherCommunicationException e ) {
                    m_log.error("Unable to initiate AutoUpdate on client",e);
                    flash.error += "${e.message}<br>";
                }
            }
        }

        // send back to the list
        redirect(action:list,params:[groupList:request.getParameterValues('groupList')]);
    }


	
    /**
     * Clear flash scope of messages
     */
    private void clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }
}
