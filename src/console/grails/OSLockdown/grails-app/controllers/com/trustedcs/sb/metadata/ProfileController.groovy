/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata;

import org.apache.log4j.Logger;
import org.apache.commons.lang.StringEscapeUtils;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.validator.ProfileOptionsValidator;
import com.trustedcs.sb.reports.util.ProfileComparator;
import com.trustedcs.sb.reports.util.ReportsHelper;
import com.trustedcs.sb.reports.util.ReportType;
import com.trustedcs.sb.reports.util.ReportRenderType;
import com.trustedcs.sb.metadata.util.SbProfileHelper;
import com.trustedcs.sb.exceptions.SecurityProfileException;
import org.hibernate.criterion.Order

class ProfileController {
    
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.metadata.web.profile");

    // injected services
    def messageSource;
    def securityProfileService;
    def reportsService;
    def auditLogService;

    // render report location
    static final String VIEW_RENDERED_REPORT = "viewRenderedReport";
    
    // prefix for checkboxes that are used to show which modules are in the profile 
    static String selectedPrefix = "module.selected.";
	
    // the delete, save and update actions only accept POST requests
    static allowedMethods = [delete:'POST', save:'POST', update:'POST']

    def index = {
        m_log.info("Profile Index");

        redirect(action:"list",params:params);
    }

    def list = {

        def offset       = params.offset ? params.offset : "0"
        def max          = params.max ? params.max : "25"

        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table. Default is writeProtected
        // ordered in a desc order (i.e. Industry Profiles first) followed by asc name sort.
        def sort
        def sortOrder
        if( params.sort && params.order &&
            // sort (columns) that are user sortable (user can pass different invalid values on the url)
            ( params.sort == "name" || params.sort == "shortDescription" || params.sort == "writeProtected" ) &&
            // valid sortOrder values (user can pass different invalid values on the url)
            ( params.order == "asc" || params.order == "desc" )
          ){
            sort = params.sort
            sortOrder = params.order
        }
        def profileList = Profile.createCriteria().list( max:max, offset:offset) {
            // User sorted the columns with valid sort column and valid sort order. Use it for sorting
            if( sort && sortOrder ){
		       order( new Order(sort, sortOrder=='asc').ignoreCase() )
            }
            // Either user did not sort, or he changed columns to invalid once, sort by Industry Profile and then by name (default)
            else {
                order("writeProtected","desc");
            }
            order(new Order ("name",sortOrder!="asc").ignoreCase())  
        }

        [ profileList:profileList, maxPerPage:max ]
    }

    /**
     * 1. WEBFLOW for creating new Profiles and editing existing Profiles ONLY. All other actions that
     * were initially part of this webflow: listing of Profiles, copyProfile, deleteProfile and importProfile have been
     * moved out of it as they don't belong in it since they are separate action without a flow.
     *
     * 2. Web flow states have been organized to be in the order of execution from top to bottom,
     * starting from the start state and ending in the endState. However, be careful as in 1.2.2 web flows
     * work weirdly (if put println() in endState() it will be shown even without reaching that state. See
     * Notes in the endState for more weirdness of webflows, particularly in the endState)
     */
    def profileBuilderFlow = {
        def profile;
        def tagList;
        def cpeList;
        def compliancyList;
        def profileList;
        def error;

        // Start webflow state
        start {
            action {
                flow.error = "";
                // These are done to build all of the metadata that the
                // search is using in basicModuleSelector and advancedModsortuleSelector states
                flow.profileList = Profile.withCriteria {
                    order("writeProtected","desc");
                    order("name","asc"); }

                flow.userProfileList = Profile.withCriteria {
                    eq('writeProtected',false);
                    order("name","asc"); }
					
                flow.systemProfileList = Profile.withCriteria {
                    eq('writeProtected',true);
                    order("name","asc"); }
					
                flow.masterModuleList = SecurityModule.withCriteria {
                    order("name","asc");
                }
					
                flow.tagList = ModuleTag.list(sort:'name');
                flow.cpeList = CommonPlatformEnumeration.withCriteria {
                    order("part","asc");
                    order("vendor","asc");
                    order("product","asc");
                    order("productVersion","asc"); };
                flow.compliancyList = Compliancy.withCriteria {
                    order("source","asc");
                    order("name","asc");
                    order("version","asc");
                    order("item","asc"); };

                // Existing Profile Editing (params.id contains profile id)
                if ( params.id ) {
                    flow.profile = Profile.get(params.id);
                }
                // New Profile Creation, create flow.profile
                else {                    
                    flow.profile = new Profile()
                }

                // Invoke createEditProfile event programmatically to transition to modifyProfile state
                createEditProfile();
            }

            on( 'createEditProfile' ).to 'modifyProfile'
            on( Exception ).to 'modifyProfile'
        }

        // Modify Profile state is called for Creation / Editing of a Profile.
        modifyProfile {
            render(view:"editProfile")

            on('basicModuleSelector') {
                flow.profile = this.updateProfileInfo(flow.profile,params);
                flow.profile = this.updateProfileModules(flow.profile,params);
            }.to 'basicModuleSelector'

            on('save') {
                flow.profile = this.updateProfileInfo(flow.profile,params);
                flow.profile = this.updateProfileModules(flow.profile,params);
            }.to 'save'

            on('cancel').to 'cancel'
            on('finish').to 'cancel'
        }

        cancel {
            action {
                if ( flow.profile ) {
                    flow.profile.discard();
                }
            }
            on('success').to 'endState'
        }
						
        basicModuleSelector {
            render(view:"basicModuleSelector")
            on('save') {
                flow.profile = this.updateProfileModules(flow.profile,params);
            }.to 'save'
				
            on('back') {
                flow.profile = this.updateProfileModules(flow.profile,params);
            }.to 'modifyProfile'
            on('advanced') {
                flow.profile = this.updateProfileModules(flow.profile,params);
            }.to 'advancedModuleSelector'
            on('cancel').to 'cancel'
            on('finish').to 'cancel'
        }
			
        advancedModuleSelector {
            render(view:"advancedModuleSelector")
				
            on('search').to 'search'
            on('addModules').to 'addModules'
				
            on('save') {
                flow.profile = this.updateProfileModules(flow.profile,params);
            }.to 'save'
				
            on('back').to 'basicModuleSelector'
            on('cancel').to 'cancel'
            on('finish').to 'cancel'
        }

        search {
            action {
                flash.moduleList = this.queryModules(flow.profile,params);
                flash.settingsMap = this.getModuleSettings(flash.moduleList,params);
                flash.tags = request.getParameterValues('module.tag.id');
                flash.clearTexts = request.getParameterValues('module.clearText.id');
                flash.cpes = request.getParameterValues('module.cpe.id');
                flash.compliancies = request.getParameterValues('module.compliancy.id');
                flash.moduleSource = params.moduleSource;
                flash.useSystemProfile = params.loadSystemProfile;
                flash.useUserProfile = params.loadUserProfile;
            }
            on('success').to 'advancedModuleSelector'
        }
			
        addModules {
            action {
                flow.profile = this.updateProfileModules(flow.profile,params,false);
            }
            on('success').to 'modifyProfile'
        }
			
        save {
            action {
                // update profile information
                flow.profile = this.updateProfileModules(flow.profile,params);
					
                // validation of configuration options of the profile
                def resultsMap = this.validateProfileOptions(flow.profile);
                flash.error = "";
                if ( !resultsMap.isEmpty() ) {
                    resultsMap.each { key, value ->
                        flash.error += "$key - $value<br/>";
                    }
                    return hadError();
                }

                // profile has to have at least one module
                if ( !(flow.profile.securityModules) ) {
                    flash.error += "A profile requires at least one module<br/>";
                    return hadError();
                }

                // persist the profile to disk					
                try {
                    // is the profile new
                    boolean existingProfile = false;
                    if ( flow.profile.id ) {
                        existingProfile = true;
                    }
                    
                    // persist using the service
                    // merge the object due to webflow issues
                    Profile securityProfile = flow.profile.merge();
                    if ( securityProfile ) {
                        securityProfileService.save(securityProfile);
                    }
                    else {
                        // HACK to fix the issue with merge returning a null object
                        // when the profile name hasn't been set.
                        securityProfileService.save(flow.profile);
                    }

                    // audit trail
                    if ( existingProfile ){
                        auditLogService.logProfile("modify",flow.profile.name);
                    }
                    else {
                        auditLogService.logProfile("add",flow.profile.name);
                    }
                }
                catch ( SecurityProfileException securityProfileException ) {
                    flash.error = g.renderErrors(bean:securityProfileException.securityProfile,as:"list");
                    hadError();
                }
            }
            on('success').to 'finish'
            on('hadError').to 'modifyProfile'
        }

        finish {
            action {
            }
            
            on('success').to 'endState'
        }

        endState {
            // End state is redirecting to profile/list. Can't use dynamic parameter to affect sorting for example
            // (see Notes below).
            // Could potentially implement this via creation of 2 separate states : one for successful new Profile
            // creation that would pass in the params: [sort:"id",order"desc"], however, this might be too invasive
            // to the user if they had previously had a sort order. Also, most users probably have less than 25 profiles
            // so new Profile would be added at the end of the list (and still on the current page) so this is not an issue.

            // IMPORTANT: need to have include controller:"profile" piece as otherwise without it get the famouse exception
            //      "No SecurityManager accessible to the calling code, either bound to the org.apache.shiro.util.ThreadContext or
            //      as a vm static singleton.  This is an invalid application configuration."
            // as we are still inside the Web Flow at this point, and we need to redirect to the ProfileController
            // which is considered by this Web Flow to be outside of it.
            redirect( controller:"profile", action:"list" )

            // Notes -- Can't use dynamic parameter in the above redirect() to affect sorting for example)
            //
            // 1. End state logic does not work correctly in 1.2.2 as println() put in here show
            // that println()s enter immediately after entering this webflow (without first going thru all
            // of the actions() in action states (also it's flacky sometimes a println() put before start{} does show
            // up and in other cases it doesn't. Because endState() is entered immediately (rather than after all
            // states execute as it should) putting any sort of dynamic behavior based on variable from the flow
            // or global ones (such as
            //  endState {
            //      if( sort && sortOrder OR flow.sort && flow.sortOrder ){
            //          redirect(controller:"profile", action:"list", params: ["sort":sort,"order":sortOrder ] /* ["sort": flow.sort,"order":flow.sortOrder ]*/ )
            //      }
            //      else {
            //          redirect(controller:"profile", action:"list" )
            //      }
            //  }
            // does not work. Putting this sort of logic into action part does work in development, however will
            // not work in production based on the http://grails.1312388.n4.nabble.com/Ending-a-webflow-td1312432.html
            // which is fixed as of Grails 1.2.4 (so we missed the boat) and 1.3.4 per http://jira.grails.org/browse/GRAILS-5811)
            //
            // 2. Also flow object has access to the Hibernate's SessionImpl and is serializing the entire session
            // upon transitioning between states which is very wasteful. On more on this see http://jira.grails.org/browse/GRAILS-6984
            // as well as a more detailed explanation http://stackoverflow.com/questions/1691853/grails-webflow-keeping-things-out-of-flow-scope
        }
    }   

    // Deletes selected Profiles
    def deleteMulti = {

        // clear flash error
        flash.error = "";

        // get the ids of baseline profile
        def ids = request.getParameterValues('securityProfileList')?.collect { id ->
            id.toLong();
        }

        m_log.info("ids to delete "+ids);

        def securityProfile;
        ids.each { id ->
            securityProfile = Profile.get(id);
            if ( securityProfile ) {
                try {
                    securityProfileService.delete(securityProfile);
                    auditLogService.logProfile("delete",securityProfile.name);
                }
                catch ( SecurityProfileException profileException ) {
                    profileException.securityProfile.errors.allErrors.each { profileError ->
                        flash.error += messageSource.getMessage(profileError,null)+"<br/>";
                    }
                }
                catch ( Throwable e ) {
                    m_log.error("unable to delete",e);
                    flash.error += "Unable to delete profile ${securityProfile.name}: ${e.message}<br/>";
                }
            }
            else {
                flash.error += messageSource.getMessage("profile.not.found",[params.id] as Object[],null);
            }
        }
        redirect(action:'list');
    }

    // Imports a Profile chosen from a file, creating a new Profile
    def importSecurityProfile = {

        flash.error = "";

        try {
            m_log.info(request);
            def file = request.getFile('profileFile');
            if ( file.isEmpty() ) {
                m_log.error("File is empty");
                flash.error = "File to import is empty";
            }
            else {
                Profile importedProfile = securityProfileService.fromXml(file.getInputStream());
                auditLogService.logProfile("import",importedProfile);
            }
        }
        catch ( SecurityProfileException securityProfileException ) {
            m_log.error("Unable to import profile",securityProfileException);
            if ( securityProfileException.securityProfile ) {
                securityProfileException.securityProfile.errors.allErrors.each { profileError ->
                    flash.error += messageSource.getMessage(profileError,null)+"<br/>";
                }
            }
            else {
                flash.error = securityProfileException.message;
            }
        }

        redirect( action:'list' );
    }

    def exportProfile = {

        def profileList = Profile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        [profileList: profileList]
    }

    def performExportProfile = {

        // Performs the export of security profile

        def initialProfile;
        try {
            if ( params.profileId ) {
                initialProfile = Profile.get(params.profileId);
                def profileXML = securityProfileService.toXmlString(initialProfile, true)
                response.setHeader('Content-disposition', "attachment; filename=\"${initialProfile.name}\"");
                response.contentType = "text/xml"
                response.outputStream << profileXML
                response.outputStream.flush()
            }
            else {
                flash.error = "No profile was selected<br/>";
            }
        }
        catch ( Exception e ) {
            m_log.error("unable to export",e);
            flash.error = "Unable to export ${initialProfile?.name}: ${e.message}<br/>";
        }

// Can't redirect with a response also, so just return.  GSP has a return button.
//        redirect( action: "list" )
    }

    def copyProfile = {

        def profileList = Profile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        [profileList: profileList]
    }

    def performCopyProfile = {

        // Performs the copy of security profile

        def initialProfile;
        def clonedProfile;
        try {
            if ( params.profileId ) {
                if ( params.profileName ) {
                    initialProfile = Profile.get(params.profileId);
                    clonedProfile = securityProfileService.clone(initialProfile);
                    clonedProfile.name = params.profileName;
                    clonedProfile.fileName = SbProfileHelper.createFilename(clonedProfile.name);
                    try {
                        securityProfileService.save(clonedProfile);
                    }
                    catch ( SecurityProfileException securityProfileException ) {
                        flash.error = g.renderErrors(bean:securityProfileException.securityProfile,as:"list");
                    }
                }
                else {
                    flash.error = "No profile name was given<br/>";
                }
            }
            else {
                flash.error = "No profile was selected<br/>";
            }
        }
        catch ( Exception e ) {
            m_log.error("unable to copy",e);
            flash.error = "Unable to copy ${initialProfile?.name}: ${e.message}<br/>";
        }

        redirect( action: "list" )
    }

    /**
     * Show the display page for profile comparison
     */
    def profileCompare = {
        // get the profile list
        def profileList = Profile.withCriteria {
            order("writeProtected","desc");
            order("name","asc"); }

        // existing comparisons
        def reportMap = reportsService.getReportMap(ReportType.PROFILE_COMPARISON);

        [profileList:profileList,
            existingComparisons:reportMap];
    }

    /**
     * Create or display the requested comparison
     */
    def viewProfileComparison = {
        clearFlash();
        m_log.info("PARAMS:"+ params);

        // check to see if we're just displaying a report that already existed
        if ( params.reportSource == 'existing') {
            if ( params.dataSet ) {
                redirect(controller:'report',action:VIEW_RENDERED_REPORT,params:params);
                return;
            }
            else {
                flash.warning = "Comparison not selected"
                redirect(action:ReportType.PROFILE_COMPARISON.viewLocation,params:params);
                return;
            }
        }

        // check to see if the reports are the same
        if ( params.profile1 == params.profile2 ) {
            flash.warning = "Profiles to compare are the same"
            redirect(action:ReportType.PROFILE_COMPARISON.viewLocation,params:params);
            return;
        }

        // check to see if there are actually two reports
        if ( !(params.profile1 && params.profile2) ) {
            flash.warning = "You must select two different profiles"
            redirect(action:ReportType.PROFILE_COMPARISON.viewLocation,params:params);
            return;
        }

        // find the two profiles
        Profile profileA = Profile.get(params.profile1.toLong());
        Profile profileB = Profile.get(params.profile2.toLong());

        // output file name        
        String outputFileName = ReportsHelper.getProfileComparisonFilename(profileA,profileB);

        // output file
        File outputFile = new File(SBFileSystemUtil.get(SB_LOCATIONS.PROFILE_COMPARISONS),outputFileName);
        m_log.info("profile comparison output file:"+outputFile.getAbsolutePath());
        if ( outputFile.exists() ) {
            m_log.info("assessment comparison already exists");
        }
        else {

            // logger
            auditLogService.logReport("add",ReportType.PROFILE_COMPARISON.displayString,outputFileName);

            // create the comparator and generate the delta
            if ( profileA && profileB ) {
                ProfileComparator comparator = new ProfileComparator(profileA,profileB);
                comparator.deltaReport(outputFile);
            }
            else {
                flash.error("Profile missing");
                redirect(action:ReportType.PROFILE_COMPARISON.viewLocation,params:params);
                return;
            }
        }

        params['dataSet'] = outputFile.name;
        params['reportType'] = ReportType.PROFILE_COMPARISON.ordinal();
        redirect(controller:'report',action:VIEW_RENDERED_REPORT,params:params);
        return;
    }
    
    /**
     * Takes the modules that have been returned by the query and creates a map
     * of setting values for the advanced page to display as the values of the 
     * module configuration parameters.
     * @param modules
     * @param params
     */
    private Map getModuleSettings(Collection modules, Map params) {
    	def settingsMap = [:];
    	
    	// are the values coming from an external source other than the defaults
        Profile sourceProfile;
        if ( params.moduleSource == 'useSystemProfile' ) {
            sourceProfile = Profile.get(Long.parseLong(params.loadSystemProfile));                         
        }
        else if ( params.moduleSource == 'useUserProfile' ) {
            sourceProfile = Profile.get(Long.parseLong(params.loadUserProfile));
        }
        
        m_log.info("Source Profile : ${sourceProfile?.name}");
        m_log.info("Source options : ${sourceProfile?.optionValues}");
        
        // iterate the collection of modules
        modules.each { module ->
            // iterate the list of module options
            module.options.each { option ->
                if ( sourceProfile ) {
                    settingsMap["${module.id}.${option.id}"] = sourceProfile.optionValues["${module.id}.${option.id}"];
                }
                else {
                    settingsMap["${module.id}.${option.id}"] = option.defaultValue;
                }
            }
        }
        m_log.info("Settings map: ${settingsMap}");
        return settingsMap;
    }
	
    /**
     * Queries the module repository for modules that match the criteria
     * passed in the params map.
     * 
     * @param currentProfile
     * @param params
     * @return collection     
     */
    private Collection queryModules(Profile currentProfile, Map params)
    {
        m_log.info("Query Modules");
        // module list
        def moduleList;
        def aggregateList;
		
        // log the request parameters just to see what filters are there.
    	params.each { entry ->
            m_log.info("${entry.key}[${entry.value}]");
    	}
		
    	// apply the filter first
    	def criteriaResults = applyCriteria();  
    	
    	m_log.info("criteriaResults.size[${criteriaResults.size()}]");
    	
    	// if the user is matching against a specific profile we intersect the 
    	// results of the query with the modules that are in that actual profile.
    	if ( params.moduleSource == 'useSystemProfile' || 
            params.moduleSource == 'useUserProfile') {
            m_log.info("criteria is from "+params.moduleSource);
            Profile sourceProfile;
            if ( params.moduleSource == 'useSystemProfile' ) {
                sourceProfile = Profile.get(Long.parseLong(params.loadSystemProfile));
            }
            else if ( params.moduleSource == 'useUserProfile' ) {
                sourceProfile = Profile.get(Long.parseLong(params.loadUserProfile));
            }
        	
            if ( sourceProfile ) {
                moduleList = criteriaResults.intersect(sourceProfile.securityModules);
            }
    	}
    	else {
            m_log.info("criteria is from all modules")
            moduleList = criteriaResults;
    	}  
    	
    	// check to see if the results returned have dependencies that are not in the 
    	// result set and also not in the profile in the tmp session, if there are some
    	// add those modules to the result set and set a message in the flash scope that
    	// will be displayed to the user.
    	def dependencies = [];
    	def dependModule
    	moduleList.each { securityModule ->
            if ( securityModule.libraryDependencies.size() > 0 ) {
                securityModule.libraryDependencies.each {
                    dependModule = SecurityModule.findByLibrary(it.moduleLib);
                    if ( !moduleList.contains(dependModule) &&
                        !currentProfile?.securityModules?.contains(dependModule) ) {
                        dependencies << dependModule;
                    }
                }
            }
    	}    	
    	
    	m_log.info("dependencies found [${dependencies.size()}]")
    	if ( dependencies.size() > 0 ) {    		
            moduleList += dependencies;
            flash.message = "Search returned suggested modules in addition to query results."
    	}
    	
    	m_log.info("module list after dependencies [${moduleList.size()}]")
    	
    	// compare to the profile if one was specified
    	aggregateList = moduleList;
    	m_log.info("AggregateList size : " + aggregateList.size() );
    	return aggregateList;
    } // queryModules(Profile,Map)
    
    // AJAX METHODS
    /**
     * Check the dependencies for the clicked option
     */
    def dependencyCheck = {
    	m_log.info("Dependency Check");
    	def dependencies = [:];
    	def securityModule = SecurityModule.get(params.moduleId);
    	def dependencyModule;
    	StringBuffer alertBuffer = new StringBuffer();
    	alertBuffer.append("Selecting this module automatically selects the following modules in order to completely configure the security setting.\\n\\n")    	
    	if ( securityModule.libraryDependencies.size() > 0 )
    	{
            securityModule.libraryDependencies.each {
                dependencyModule = SecurityModule.findByLibrary(it.moduleLib);
                dependencies[dependencyModule.id] = it.selected;
                alertBuffer.append(dependencyModule.name);
                alertBuffer.append(" ");
                alertBuffer.append( it.selected ? "selected" : "deselected")
                alertBuffer.append("\\n");
            }
            flash.message = "Modules were selected/deselected as a result of security suggestions."
    	}
    	m_log.info("number of dependencies: "+dependencies.size());
    	[dependencies:dependencies,
            alertString:alertBuffer.toString()]
    } // closure dependencyCheck
 
    /**
     * Remove the filter criteria
     */
    def removeSearchFilter = {
        m_log.debug("Remove Search Filter");
    }  // closure removeDropDown 
   
    /**
     * Add the filter criteria option
     */
    def addSearchFilter = {             
        m_log.debug("Add Search Filter");
        [ tagList:ModuleTag.list(sort:'name'),          
            cpeList:CommonPlatformEnumeration.withCriteria {
                order("part","asc");
                order("vendor","asc");
                order("product","asc");
                order("productVersion","asc");
            } ,
            compliancyList:Compliancy.withCriteria {
                order("source","asc");
                order("name","asc");
                order("version","asc");
                order("item","asc");
            }]
    }
     
    def checkboxAction = {
    	m_log.info("Checkbox Action");
    } // closure checkboxAction
    
    /**
     * Using the filter criteria passed in the params map create a list
     * of modules that match that criteria
     * @return the list of modules that match the filter
     */     
    List applyCriteria()
    {
    	def criteria = SecurityModule.withCriteria {
            
            // tag
            def tagIds = request.getParameterValues('module.tag.id');
            if ( tagIds ) {
                moduleTags {                        
                    or {
                        for ( tagId in tagIds ) {
                            eq('id',Long.parseLong(tagId));                                
                        }
                    }                        
                }     
            }
            else {
                m_log.info("no tag filters");
            }
            
            // group
            def groupIds = request.getParameterValues('module.group.id');
            if ( groupIds ) {
                moduleGroup {
                    or {
                        for ( groupId in groupIds ) {
                            eq('id',Long.parseLong(groupId));        
                        }
                    }
                }
            }
            else {
                m_log.info("no group filters");
            }
            
            // cpe
            def cpeIds = request.getParameterValues('module.cpe.id');
            if ( cpeIds ) {
                cpes {
                    or {
                        for ( cpeId in cpeIds ) {
                            eq('id',Long.parseLong(cpeId));        
                        }
                    }
                }
            }
            else {
                m_log.info("no cpe filters");
            }
            
            // compliancy
            def compliancyIds = request.getParameterValues('module.compliancy.id');
            if ( compliancyIds ) {
                compliancies {
                    or {
                        for (compliancyId in compliancyIds ) {
                            m_log.info("compliancyId[${compliancyId}]")
                            eq('id',Long.parseLong(compliancyId));
                        }
                    }
                }
            }
            else {
                m_log.info("no compliancy filters");
            }
            
            // clear text
            def clearTextSearches = request.getParameterValues('module.clearText.id');
            if ( clearTextSearches ) {
            	or {
                    for (clearText in clearTextSearches ) {
                        // check if its an empty field
                        if ( clearText ) {
                            m_log.info("clearText[${clearText}]")
                            ilike('name',"%${clearText}%");
                            ilike('description',"%${clearText}%");
                        }
                    }
                }
            }
            else {
                m_log.info("no clear text filters");
            }            
            
            order("name","asc");
            
        }.unique();
    	return criteria;
    }  // applyCriteria
    
    /**
     * Update the given profile for all its description information with the
     * given parameters from the request
     * @param profile
     * @param params
     */
    private Profile updateProfileInfo(Profile profile, Map params)
    {
    	profile.name = params.name;
        m_log.info("updateProfileInfo ${profile.name}");
    	profile.shortDescription = params.shortDescription;
    	profile.description = params.description;
    	profile.comments = params.comments;
    	if ( !profile.fileName ) {
            profile.fileName = SbProfileHelper.createFilename(profile.name);
    	}
    	return profile;
    } // updateProfileInfo(Profile,Map)
    
    /**
     * Updates the profile's modules
     * This is a convience method to defaultly allow for modules to be removed
     * as well as added.
     * @param profile
     * @param params
     */
    private Profile updateProfileModules(Profile profile, Map params) {
    	return updateProfileModules(profile,params,true); 
    }
    
    /**
     * Updates the given profile with modules that are in its module.selected.${id} keys
     * @param profile
     * @param params
     */
    private Profile updateProfileModules(Profile profile, Map params, boolean allowRemoval)
    {
    	m_log.info("updateProfileModules:${params}");    	
    	// get the list of module ids for the modules that had check boxes selected
    	def selectedModuleIds = params.findAll { entry -> 
            entry.key ==~ /module\.selected\.\d*/;
        }.collect {
            it.key.substring(selectedPrefix.length()).toLong();
        }        
        m_log.info("Selected : ${selectedModuleIds}");
        
        // get the list of original modules
        def originalModuleIds;
        if ( allowRemoval ) {
            originalModuleIds = profile.securityModules.collect {
            	it.id;
            }
            m_log.info("Original : ${originalModuleIds}");
        }          
    	
    	// iterate over the list of selected modules and create a map that 
    	// contains a module group -> list of modules mapping for the modules that 
    	// were selected
    	def securityModule;    	
    	selectedModuleIds.each { moduleId ->
    	
            // get the module
            securityModule = SecurityModule.get( moduleId );
            if ( allowRemoval ) {
                if ( !originalModuleIds.contains(moduleId) ) {
                    m_log.debug("NEWLY ADDED: ${securityModule.name}");
                    profile.addToSecurityModules(securityModule);
                }
            }
            else {
                profile.addToSecurityModules(securityModule);
            }
    		
            // check to see if the module has any configuration
            if ( securityModule.options?.size() > 0 )
            {
                securityModule.options.each {
                    m_log.info("""module.${securityModule.id}.option.${it.id}""");
                    profile.optionValues["${securityModule.id}.${it.id}"] = params["module.${securityModule.id}.option.${it.id}"];
                }
            }
    		
    	}	
    	
    	// if removal is allowed we remove the modules that aren't in the selected list
    	if ( allowRemoval ) {	    	
            // remove any modules that no longer exist in the new list of selected modules
            originalModuleIds.each {
                if ( !selectedModuleIds.contains(it) ) {
                    m_log.debug("REMOVED: ${it}");
                    profile.removeFromSecurityModules(SecurityModule.get(it));
                }
            }
    	}
    	
    	m_log.info("Option Values[:] "+profile.optionValues);
    	return profile;
    } // updateProfileModules(Profile,Map)
    
    /**
     * Validates that the configuration options for the profile are valid
     */
    Map validateProfileOptions(Profile profile) {    	
    	def results = [:];
    	def optionType;
    	def profileOptionValue;
    	
    	profile.securityModules.each { module ->
            module.options.each { moduleOption ->
                // give the option value
                profileOptionValue = profile.optionValues["${module.id}.${moduleOption.id}"];
                // get the option type
                optionType = ProfileOptionsValidator.getInstance().optionTypes[moduleOption.type];
                // validate the option
                if ( optionType.validate( profileOptionValue, profile.optionValues ) ) {            
                    m_log.info("Valid Value '${module.name}' -> ${moduleOption.name} ");              
                }
                else {              
                    results["${module.name} - ${moduleOption.name}"] = optionType.displayString(); 
                    m_log.error("${module.name} ${moduleOption.name} Invalid Value: ${profileOptionValue}");
                }
            }
    	}
    	return results;
    }

    /**
     * Clears the flash of all messages that are currently set on it
     */
    private clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }
}
