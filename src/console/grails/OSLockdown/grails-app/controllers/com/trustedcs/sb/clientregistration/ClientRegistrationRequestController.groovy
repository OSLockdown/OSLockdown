/*
 * Original file generated in 2010 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2010-13 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.clientregistration;

import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;

import com.trustedcs.sb.util.SessionAlertUtil;

import com.trustedcs.sb.exceptions.ClientRegistrationException;
import com.trustedcs.sb.exceptions.SbClientException;
import com.trustedcs.sb.exceptions.SbGroupException;

import org.apache.log4j.Logger;

class ClientRegistrationRequestController {
	
    // logger
    static Logger m_log = Logger.getLogger("com.trustedcs.sb.clientregistration.controller");

    // injected services
    def messageSource;
    def clientRegistrationService;
    def auditLogService;

    /**
     * Redirect to list
     */
    def index = {
    	redirect(action:list,params:params); 
    }

    /**
     * List the client registration request
     */
    def list = {
        // Don't call clearFlash(); here as allowMulti redirects to list() action in case
        // of an error, with an error message being stored in the flash

        def newRegistrationCount = session.registrationCount ? session.registrationCount : 0;
        session.registrationCount = 0;
	        
        params.max = Math.min( params.max ? params.max.toInteger() : 25,  100)
        m_log.info( "registration request List Parameters: ${params}");
        // sorted by received 
        [ requestInstanceList: ClientRegistrationRequest.listOrderByTimeStamp( params ), 
            requestInstanceTotal: ClientRegistrationRequest.count(),
            groupList:Group.withCriteria { order('name','asc') }]
    }
        
    /**
     * Shows the detailed information of the auto registration request
     */
    def show = {
        def requestInstance = ClientRegistrationRequest.get(params.id);
        if(!requestInstance) {
            flash.error = "Registration Request not found with id ${params.id}"
            redirect(action:list)
            return;
        }
        [requestInstance:requestInstance,
            groupList:Group.listOrderByName() ]
    }
    
    /**
     * Allows the auto registration
     */
    def allow = {
        params.remove("_action_allow")
        params.remove("action")
        clearFlash();
        ClientRegistrationRequest clientRequest;
        try {
            clientRequest = ClientRegistrationRequest.get(params.id);
            if ( clientRequest ) {
                Group group;
                
                if ( params.groupId ) {
                    group = Group.get(params.groupId.toLong());
                }
                clientRegistrationService.allow(clientRequest,group);
                auditLogService.logGenericAction("allow","client",clientRequest.name);
            }
            else {
                flash.error = messageSource.getMessage("clientRegistrationRequest.not.found",[] as Object[], null);
            }
        }
        catch (SbClientException clientException) {
            flash.error += g.renderErrors(bean:clientException.clientInstance,as:"list");
            m_log.error("Unable to allow client registration",clientException);
            // redirect to show() action rather than render so that the error stored in flash is
            // only shown once. If render() is used rather than redirect() and the user clicks on Clients->Auto-registration requests
            // (clientRegistrationRequest/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
            // of list action as then error won't be displayed if get an error in the allowMulti() case.
            redirect(action:'show',params:params);
            return;
        }
        catch (SbGroupException groupException) {
            flash.error += g.renderErrors(bean:groupException.groupInstance,as:"list");
            m_log.error("Unable to allow client registration",groupException);
            // redirect to show() action rather than render so that the error stored in flash is
            // only shown once. If render() is used rather than redirect() and the user clicks on Clients->Auto-registration requests
            // (clientRegistrationRequest/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
            // of list action as then error won't be displayed if get an error in the allowMulti() case.
            redirect(action:'show',params:params);
            return;
        }
        catch (ClientRegistrationException autoRegistrationException ) {
            flash.error += g.renderErrors(bean:autoRegistrationException.clientRegistrationInstance,as:"list");
            m_log.error ("Unable to allow client registration",autoRegistrationException);
            // redirect to show() action rather than render so that the error stored in flash is
            // only shown once. If render() is used rather than redirect() and the user clicks on Clients->Auto-registration requests
            // (clientRegistrationRequest/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
            // of list action as then error won't be displayed if get an error in the allowMulti() case.
            redirect(action:'show',params:params);
            return;
        }
    	redirect(action:'list',params:params);
    }
    
    /**
     * Denies the auto registration
     */
    def deny = {
        params.remove("_action_deny")
        params.remove("action")
        clearFlash();
        ClientRegistrationRequest clientRequest;
        try {
            clientRequest = ClientRegistrationRequest.get(params.id);
            if ( clientRequest ) {
                clientRegistrationService.deny(clientRequest);
                auditLogService.logGenericAction("deny","client",clientRequest.name);
            }
            else {
                flash.error = messageSource.getMessage("clientRegistrationRequest.not.found",[] as Object[], null);
            }
        }
        catch (ClientRegistrationException autoRegistrationException ) {
            autoRegistrationException.clientRegistrationInstance.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
            m_log.error ("Unable to deny client registration",autoRegistrationException);
            // redirect to show() action rather than render so that the error stored in flash is
            // only shown once. If render() is used rather than redirect() and the user clicks on Clients->Auto-registration requests
            // (clientRegistrationRequest/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
            // of list action as then error won't be displayed if get an error in the allowMulti() case.
            redirect(action:'show',params:params);
            return;
        }
    	redirect(action:'list',params:params);
    }
    
    /**
     * Allows multiple selected registration requests
     */
    def allowMulti = {
        clearFlash();
        // get the request ids
        def ids = request.getParameterValues('requestList').collect { requestId ->
            requestId.toLong();
        }
        
        // find the group if there was one asked to be assigned
        Group groupInstance;

        ClientRegistrationRequest clientRequest;
        // iterate the request ids and allow the requests with the group if it
        // was selected
        ids.each { id ->
            try {
                clientRequest = ClientRegistrationRequest.get(id);
                if ( params.groupId ) {
                    groupInstance = Group.get(params.groupId.toLong());
                }
                clientRegistrationService.allow(clientRequest,groupInstance);
                auditLogService.logGenericAction("allow","client",clientRequest.name);
            }
            catch (SbClientException clientException) {
                flash.error += g.renderErrors(bean:clientException.clientInstance,as:"list");
                m_log.error ("Unable to allow client registration",clientException.message);
                // redirect back to the list action
                // IMPORTANT : this return "break"s from the ids.each {} closure not the whole allowMulti{} closure,
                // hence will call the redirect(action:list); at the bottom of this closure. Don't do redirect(action:list);
                // here as well as get a lovely "A previous call to redirect(..) has already redirected the response" and
                // causing my favorite exception of all "No SecurityManager accessible to the calling code, either bound to
                // the org.apache.shiro.util.ThreadContext or as a vm static singleton".
//                return;
            }
            catch (SbGroupException groupException) {
                flash.error += g.renderErrors(bean:groupException.groupInstance,as:"list");
                m_log.error ("Unable to allow client registration",groupException.message);
                // redirect back to the list action
                // IMPORTANT : this return "break"s from the ids.each {} closure not the whole allowMulti{} closure,
                // hence will call the redirect(action:list); at the bottom of this closure. Don't do redirect(action:list);
                // here as well as get a lovely "A previous call to redirect(..) has already redirected the response" and
                // causing my favorite exception of all "No SecurityManager accessible to the calling code, either bound to
                // the org.apache.shiro.util.ThreadContext or as a vm static singleton".
//                return;
            }
            catch (ClientRegistrationException autoRegistrationException ) {
                if( autoRegistrationException?.clientRegistrationInstance?.errors?.allErrors ){

                    String errorMessage = ""
                    autoRegistrationException.clientRegistrationInstance.errors.allErrors.each { error ->
                        String eachErrorErrorMessage = messageSource.getMessage(error,null)+"<br/>"
                        errorMessage    += eachErrorErrorMessage;
                        flash.error     += eachErrorErrorMessage;
                    }

                    if( errorMessage ){
                        m_log.error( "Unable to allow client registration ${errorMessage}" );
                    }
                    else {
                        m_log.error ("Unable to allow client registration",autoRegistrationException.message);
                    }
                }
                else {
                    m_log.error ("Unable to allow client registration",autoRegistrationException.message);
                }
                // redirect back to the list action
                // IMPORTANT : this return "break"s from the ids.each {} closure not the whole allowMulti{} closure,
                // hence will call the redirect(action:list); at the bottom of this closure. Don't do redirect(action:list);
                // here as well as get a lovely "A previous call to redirect(..) has already redirected the response" and
                // causing my favorite exception of all "No SecurityManager accessible to the calling code, either bound to
                // the org.apache.shiro.util.ThreadContext or as a vm static singleton".
//                return;
            }
        }
        // redirect back to the list
        redirect(action:list);        
    }
    
    /**
     * Denies multiple selected registration requests 
     */
    def denyMulti = {
        clearFlash();
        // get the request ids
        def ids = request.getParameterValues('requestList').collect { requestId ->
            requestId.toLong();
        }

        ClientRegistrationRequest clientRequest;
        // iterate the request ids and allow the requests with the group if it
        // was selected
        ids.each { id ->
            try {
                // find the client request
                clientRequest = ClientRegistrationRequest.get(id);
                // deny the client
                clientRegistrationService.deny(clientRequest);
                auditLogService.logGenericAction("deny","client",clientRequest.name);
            }
            catch (ClientRegistrationException autoRegistrationException ) {
                autoRegistrationException.clientRegistrationInstance.errors.allErrors.each { error ->
                    flash.error += messageSource.getMessage(error,null);
                }
                m_log.error ("Unable to deny client registration",autoRegistrationException);
                // redirect back to the list action
                // IMPORTANT : this return "break"s from the ids.each {} closure not the whole denyMulti{} closure,
                // hence will call the redirect(action:list); at the bottom of this closure. Don't do redirect(action:list);
                // here as well as get a lovely "A previous call to redirect(..) has already redirected the response" and
                // causing my favorite exception of all "No SecurityManager accessible to the calling code, either bound to
                // the org.apache.shiro.util.ThreadContext or as a vm static singleton".
                return;
            }
        }
        // redirect back to the list
        redirect(action:list);
    }	
	
    /**
     * ajax check to see if any new registrations have happened since the last
     * time that this page was accessed.
     */
    def hasNew = {
        // use the session util to update the auto-registration count
        SessionAlertUtil.updateAutoRegistrationCount(session);
    }		
	
    /**
     * Clears the flash of all messages that are currently set on it
     */
    private void clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }	
}
