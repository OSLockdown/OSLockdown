/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.actions;

import org.apache.log4j.Logger;

import javax.servlet.http.Cookie;

import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.ClientInfo;

import com.trustedcs.sb.ws.client.AgentCommunicator;
import com.trustedcs.sb.ws.client.AgentCommunicator.AgentAction;
import com.trustedcs.sb.ws.client.AgentCommunicator.ProductType;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.exceptions.SbClientException;
import com.trustedcs.sb.exceptions.SbGroupException;
import com.trustedcs.sb.exceptions.DispatcherCommunicationException;

import org.apache.shiro.SecurityUtils;

import grails.util.Environment;

class PolicyApplicationController {
	
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.metadata.web.actions.policyApplication");
    
    // injected services
    def messageSource;
    def clientService;
    def groupService;
    def dispatcherCommunicationService;
    def auditLogService;

    // redirect to policy actions
    def index = { 
        redirect(action: 'policyActions', params: params);
    }
    
    // display action page
    def policyActions = {
    		
    	// security profile listing
    	def securityProfileList = Profile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        // baseline profile listing
    	def baselineProfileList = BaselineProfile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }
    	
    	// client information
    	def clientList = Client.getAll();
        Client clientInstance;
        ClientInfo clientInfo;
        Group groupInstance;
        if ( clientList ) {
            clientInstance = clientList[0];
            // Get the info from the Client                
            clientInfo = clientInstance?.info;
            if ( !clientInfo ) {    		
                clientInfo = new ClientInfo();
            }               
            // get the group for the client
            groupInstance = clientInstance.group;
        }
        else {
            flash.error = messageSource.getMessage("standalone.client.missing",null,null);
        }
        
        // if the user's role is security officer then there are a different
        // list of actions available to the user
        def actionList = [];        
        
        if ( SecurityUtils.getSubject().hasRole("Security Officer") ) {
            actionList << AgentAction.SCAN.displayString;
            actionList << AgentAction.QUICK_SCAN.displayString;
            actionList << AgentAction.BASELINE.displayString;
        } 
        else {
            actionList << AgentAction.SCAN.displayString;
            actionList << AgentAction.QUICK_SCAN.displayString;
            actionList << AgentAction.APPLY.displayString;
            actionList << AgentAction.UNDO.displayString;
            actionList << AgentAction.BASELINE.displayString;
        }
        
        boolean sendQueries = false;
        if ( session.fromLogin ) {
            session.fromLogin = false;
            sendQueries = true;
        }
        
        // get the cookie for what the last logging level was            
        def cookieValue = g.cookie(name: "tcs.sb.loggingLevel");
        def loggingLevel;        
                    
        // if the cookie exists
        if ( cookieValue ) {
            loggingLevel = cookieValue.toInteger();            
        }
        else {
            loggingLevel = 5;
        }

    	// model
    	[ clientInstance : clientInstance,
            groupInstance : groupInstance,
            clientInfo : clientInfo,
            securityProfileList : securityProfileList,
            baselineProfileList : baselineProfileList,
            actionList : actionList,
            sendQueries:sendQueries,
            loggingLevel:loggingLevel]
    }
    
    /**
     * Called when the user clicks "run" on the policyActions page
     */
    def standAloneAction = {
        // clear flash of information
    	flash.error = "";
    	flash.message = "";
    	flash.warning = "";
    	
    	// logging level set on cookie
        Integer loggingLevel = params.loggingLevel.toInteger();
        Cookie cookie = new Cookie("tcs.sb.loggingLevel", loggingLevel.toString());
        cookie.setPath("/OSLockdown");
        cookie.setMaxAge(2592000);                      
        response.addCookie(cookie);
    	
    	// create an enum for the action    	
    	AgentAction dispatcherAction = AgentAction.createEnum(params.dispatcherAction);
    	
    	// create the correct client ws-proxy
    	Client clientInstance;
        // get the client
        def clientList = Client.getAll();
        if ( clientList ) {
            clientInstance = clientList[0];
        }
                
        // get the value of the agent port
        Integer agentPort;
        try {
            agentPort = params.agentPort.toInteger();
            // if the agent port has changed we have to update it in the database
            if ( agentPort != clientInstance.port ) {
                // set new port on the client
                clientInstance.port = agentPort;
                // save the client using the client service
                try {
                    clientService.save(clientInstance);
                }
                catch ( SbClientException clientException ) {
                    // set the errors on the flash error
                    clientException.clientInstance.errors.allErrors.each { error ->
                        flash.error += messageSource.getMessage(error,null);
                    }                    
                }                
            }
        }
        catch ( NumberFormatException nfe ) {
            // we can't set the new port but will continue
            flash.error = messageSource.getMessage("client.port.integer.error",[] as Object[],null);
        }
        
        // get the security profile
        Profile securityProfile;
        if ( params.securityProfile) {
            securityProfile = Profile.get(params.securityProfile.toLong());
        }
        else {
            flash.error += messageSource.getMessage("standalone.securityProfile.missing",null,null);
            // redirect user to display info
            redirect(action:'policyActions',params:params);
            return;
        }

        // get the baseline profile
        BaselineProfile baselineProfile;
        if ( params.baselineProfile ) {
            baselineProfile = BaselineProfile.get(params.baselineProfile.toLong());             
        }   
        else {
            flash.error += messageSource.getMessage("standalone.baselineProfile.missing",null,null);
            // redirect user to display info
            redirect(action:'policyActions',params:params);
            return;
        }

        // store what profile is being used for the client
        try {
            // find the group
            Group group = clientInstance.group;
            group.profile = securityProfile;
            group.baselineProfile = baselineProfile;
            groupService.save(group);
        }
    	catch ( SbGroupException groupException ) {
            // set the errors on the flash error
            groupException.groupInstance.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
        }    	

        // make the call out to the dispatcher
    	try {
            switch(dispatcherAction) {
                case AgentAction.SCAN:                
                flash.message += "${dispatcherAction.displayString} is processing with profile ${securityProfile.name}<br/>"
                dispatcherCommunicationService.scan(loggingLevel,clientInstance);
                break;

                case AgentAction.QUICK_SCAN:                
                flash.message += "${dispatcherAction.displayString} is processing with profile ${securityProfile.name}<br/>"
                dispatcherCommunicationService.quickScan(loggingLevel,clientInstance);
                break;

                case AgentAction.APPLY:                
                flash.message += "${dispatcherAction.displayString} is processing with profile ${securityProfile.name}<br/>"
                dispatcherCommunicationService.apply(loggingLevel,clientInstance);
                break;

                case AgentAction.UNDO:                
                flash.message += "${dispatcherAction.displayString} is processing with profile ${securityProfile.name}<br/>"
                dispatcherCommunicationService.undo(loggingLevel,clientInstance);
                break;

                case AgentAction.BASELINE:                
                flash.message += "${dispatcherAction.displayString} is processing with profile ${baselineProfile.name}<br/>"
                dispatcherCommunicationService.baselineWithProfile(loggingLevel,clientInstance);
                break;
            }
    	}
    	catch ( DispatcherCommunicationException communicationException ) {
            m_log.error("Unable to ${dispatcherAction.displayString}: ${communicationException.message}");
            flash.error += "${dispatcherAction.displayString} failed : ${communicationException.message}";
    	}    	
    	
    	// redirect user to display info
    	redirect(action:'policyActions',params:params);
    }
}
