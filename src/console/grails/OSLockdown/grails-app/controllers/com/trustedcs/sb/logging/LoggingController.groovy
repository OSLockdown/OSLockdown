/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.logging;

import grails.util.Environment;

import org.apache.log4j.Logger;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.metadata.SecurityModule;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.util.LoggingLevel;

import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.auth.shiro.ShiroUser;

import com.trustedcs.sb.ws.client.ReportsCommunicator;

class LoggingController {
	
    //	logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.logging.controller");
	
    // drop down statics
    static final def actionList = ["scan","quick scan","apply","undo","baseline","add","modify","delete","detach","import","view","login","logout"];
    static final def highlightOptions = ['filter':'[-Filter Out Unmatching Lines-]',
	                                     'highlight':'[-Highlight Matching Lines-]'];    
    static final def loggingLevels = ["DEBUG","INFO","NOTICE","WARNING","ERROR","CRITICAL"];

    // injected services
    def messageSource;
    def auditLogService;
	
    /**
     * Adds a filter to the logging filters
     */
    def addFilter = {
			
        m_log.info("params $params");
        def dataSet;
	
        if ( params.filterType == 'user' ) {
            dataSet = ShiroUser.withCriteria {
                order("username","asc");
            }
        }
        else if ( params.filterType == 'action' ) {
            dataSet = actionList;
        }
        else if ( params.filterType == 'profile' ) {
            dataSet = Profile.withCriteria {
                order('writeProtected',"desc");
                order("name","asc");
            }
        }
        else if ( params.filterType == 'group' ) {
            dataSet = Group.withCriteria {
                order("name","asc");
            }
        }
        else if ( params.filterType == 'client' ) {
            dataSet = Client.listOrderByName();
        }
        else if ( params.filterType == 'module' ) {
            dataSet = SecurityModule.withCriteria {
                order("name","asc");
            }
        }

        [dataSet:dataSet]
    }
	
    /**
     * Removes a filter from the logging filters
     */
    def removeFilter = {
			
    }

    /**
     * Displays the audit log
     */
    def viewAuditLog = {
        clearFlash();
        auditLogService.logReport("view","log","oslockdown-audit");
        
        params.each { key, value ->
            m_log.info("$key [ ${request.getParameterValues(key)} ]");
        }         
        
        // matching on a pattern        
        def filterList = [];
        def patternList = [];
        if ( params.user ) {
            request.getParameterValues('user').each {
                patternList.add(~/actor\[$it\]/);
            }
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];	
        }
        
        if ( params.action ) {
            request.getParameterValues('action').each {
                patternList.add(~/action\[$it\]/);
            }
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];   
        }
        
        if ( params.profile ) {   
            request.getParameterValues('profile').each {
                patternList.add(~/profile\[$it\]/);
            }
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];   
        }
        
        if ( params.group ) {
            request.getParameterValues('group').each {
                patternList.add(~/group\[$it\]/);
            }
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];   
        }
        
        if ( params.client ) {
            request.getParameterValues('client').each {
                patternList.add(~/client\[$it\]/);
            }
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];   
        }
        
        try {
            if ( params.word ) {                
                request.getParameterValues('word').each {
                    patternList.add(~/$it/);
                }
            }
            if ( patternList ) {
                filterList << patternList;
                patternList = [];   
            }            
        }
        catch(Exception e) {
            flash.error = "Invalid search expression: ${e.message}"
        }
        
        // display type
        def highlight = params.highlight == 'highlight' ? true : false;
        
        // filter Log
        def content = filterLog(highlight,
            filterList,
            SBFileSystemUtil.get(SB_LOCATIONS.AUDIT_LOG_FILE));
        
        // m_log.info("content:$content");
        if (!content) {
            content = [[highlight:false, line:"No log contents were found"]];
        }
        
        // return data
        def model = [userList:ShiroUser.withCriteria {
                order("username","asc");
            },
            highlightOptions:highlightOptions,
            actionList:actionList,
            profileList:Profile.withCriteria {
                order('writeProtected',"desc");
                order("name","asc"); },
            logContents:content];
        
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            model['clientList'] = Client.listOrderByName();
            model['groupList'] = Group.listOrderByName();
        }
        
        return model;
    }   
        
    /**
     * Displays the OS Lockdown log for a given client
     * if the product is in standalone mode then it pulls the log directly from disk
     * 
     * The enterprise behavior should pull the log for the client only when it's requested
     * this log should be persisted to disk with some sort of identifier so that
     * it doesn't have to be pulled from the client everytime the user selects something
     */
    def viewSbLog = {
        clearFlash();
        auditLogService.logReport("view","log","oslockdown");
        params.each { key, value ->
            m_log.info("$key [ ${request.getParameterValues(key)} ]");
        }                
        // static options
        
        // information sent back to the page
        def clientName;     
        def filterList = [];
        def patternList = [];
        
        // logging level
        if ( params.level ) {
            def maxLevel = params.level.toInteger();
            def levelString;
            while ( maxLevel >= 0 ) {
                levelString = LoggingLevel.createEnum(maxLevel).getDisplayString().toUpperCase();
                patternList.add(~/$levelString:/);
                maxLevel--;
            }
            filterList.add(patternList);
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];   
        }
        
        // modules
        if ( params.module ) {
            request.getParameterValues('module').each {
                patternList.add(~/\[$it\]/);
            }
        	
        }
        if ( patternList ) {
            filterList << patternList;
            patternList = [];   
        }
        
        // regexp
        try {
            if ( params.word ) {
                request.getParameterValues('word').each {
                    patternList.add(~/$it/);
                }                
            }
            if ( patternList ) {
                filterList << patternList;
                patternList = [];   
            }
        }
        catch ( Exception e ) {
            flash.error = "Invalid search expression: ${e.message}"         
        }
            
        // find the log
        File logFile;
        if ( SbLicense.instance.isStandAlone() ) {
            logFile = SBFileSystemUtil.get(SB_LOCATIONS.LOG_FILE);
            clientName = "localhost";
        } 
        else {
            // pull the log file from the client if necessary and store it locally          
            if ( params.clientId ) {                
                // get the client
                Client client = Client.get(params.clientId);                
                if ( client ) {         
                    // set the client name
                    clientName = client.name;
                    // find the logging directory
                    def clientLogDir = SBFileSystemUtil.getClientLogsDirectory(params.clientId);
                    if ( !clientLogDir.exists() ) {
                        m_log.info("create client logging directory: ${clientLogDir.absolutePath}");
                        clientLogDir.mkdirs();
                    }
                    
                    // File the log file
                    logFile = new File(clientLogDir,"oslockdown.log");

                    // For Standalone and Enterprise always to the check below. For Bulk only do check for undetached Client.
                    if( !SbLicense.instance.isBulk() || !client.dateDetached ){

                        // In Enterprise go fetch or refetch it from the Client
                        if ( !logFile.exists() || params.submitType == 'refreshLog') {
                            // fetch the log file
                            ReportsCommunicator agent = createReportsCommunicator(client);
                            def reportsResponse = agent.getSbAppLog();

                            // check reports response
                            if ( reportsResponse && reportsResponse.code < 400 ) {
                                // parse the response body
                                if ( reportsResponse.content ) {
                                    logFile.withOutputStream { outStream ->
                                        outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                                    }
                                }
                            }
                            else {
                                m_log.error("getSbLog[] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");
                                flash.error += "Unable to get log from agent ${reportsResponse?.reasonPhrase}<br/>"
                            }
                        }
                    }
                    // else if( SbLicense.instance.isBulk() && client.dateDetached )
                    //      In Bulk mode for a Detached Client the logFile should be present and exist locally. Do not go fetch it from the Client
                    //      as the Client is "detached".
                }
                else {
                    flash.error = "Selected client could not be found in database.";
                }
            }
            else {
                clientName = "unselected";
            }                       
        }
        
        // pattern filtered content
        def highlight = params.highlight == 'highlight' ? true : false;
        def content = filterLog(highlight,filterList,logFile);     

	if (!content) {
            content = [[highlight:false, line:"No log contents were found"]];
        }
        
        // model 
        def model = [clientName:clientName,
            clientList:Client.listOrderByName(),
            highlightOptions:highlightOptions,
            modules:SecurityModule.withCriteria { order("name","asc"); },
            loggingLevels:loggingLevels,
            logContents:content];
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            model['clientList'] = Client.listOrderByName();
        } 

        return model;
    }
    
    /**
     * Filters the content of the file based on the patterns that have been passed 
     * @param highlight
     * @param patternList
     * @param file
     */
    private def filterLog(boolean highlight, def filterList, File file) {
        def content;
        boolean lineMatch = true;
        def contentBuilder = new StringBuilder();
        boolean ifAnyMatch = true;
        def outText = []

	if ( file?.exists() ) {
            if ( filterList ) {                
                file?.eachLine { line ->
                    // reset line match
                    lineMatch = true;
                    ifAnyMatch = true;                    
                    // closure to find out if all the patterns match.
                    for ( patternList in filterList ) {                    	                    		
                        ifAnyMatch = patternList.any { anyPattern ->
                            line =~ anyPattern;
                        }                            
                        if ( !ifAnyMatch ) {
                            lineMatch = false;
                            break;
                        }
                    }              
                
                    // if the line matched we add it to the content with its correct highlighting if needed
                    if ( lineMatch ) {
                        if ( highlight ) {
		            outText << ['highlight':true, 'line':line]
                        } else {
		            outText << ['highlight':false, 'line':line]
                        }
                    }
                    else {
                        // if the line didn't match we still include it if the method is in highlight mode
                        if ( highlight ) {
		            outText << ['highlight':false, 'line':line]
                        }                       
                    }
                }
            } else {
                // we have no patterns so we just return the contents of the file;
                content = file?.getText();
		file?.getText().eachLine { line ->
		  outText << ['highlight':false, 'line':line]
		}
            }

	    return outText
        }
        else {
            m_log.error("${file?.absolutePath} not found");
        }        
    }    
    
    /**
     * Clears the flash of all messages that are currently set on it
     */
    private clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }    
    
    /**
     * Creates a web services client proxy object of the given client
     * @param client the client to create the webservice proxy agent from
     */
    private ReportsCommunicator createReportsCommunicator(Client client) {
    	boolean useHttps = grailsApplication.config.tcs.sb.console.secure.toBoolean();
        return new ReportsCommunicator(client.id,
            client.hostAddress,
            client.port,
            useHttps );
    }       
}
