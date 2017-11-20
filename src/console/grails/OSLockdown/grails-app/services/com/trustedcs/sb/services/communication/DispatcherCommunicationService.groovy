/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services.communication;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Processor;
import com.trustedcs.sb.web.pojo.ClientInfo;
import com.trustedcs.sb.web.pojo.InFlight;
import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.services.client.agent.AgentResponse;
import com.trustedcs.sb.ws.client.AgentCommunicator;
import com.trustedcs.sb.ws.client.AgentCommunicator.ProductType;

import com.trustedcs.sb.exceptions.DispatcherCommunicationException;

class DispatcherCommunicationService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.communication.DispatcherCommunicationService");

    // transactional service
    boolean transactional = false;

    // injected services
    def messageSource;
    def grailsApplication;
    def securityProfileService;
    def baselineProfileService;
    def auditLogService;

    def logTransaction(String transactionID, String action) {
        Calendar calendar = Calendar.getInstance();
        Date date = calendar.getTime();
        InFlight inFlight = new InFlight(
            startTime:date,
            transactionID:transactionID,
            action:action)
        m_log.info("Transaction "+transactionID+" In flight")
        inFlight.save()
    }

    def getProcsForClient(Client clientInstance) {
        List<String> procList = []
        Processor.findAllByClientType(clientInstance.clientType).each { processor ->
            procList << processor.name
        };
        return procList;
    } 


    /**
     * Aborts the current action running on the oslockdown dispatcher
     * @param clientInstance
     */
    def abort(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // error message for the exception
        def errorMessage;
        try {
            agent = createAgentCommunicator(clientInstance);
            agentResponse = agent.abort(loggingLevel);
        }
        catch(Exception e) {
            m_log.error("Unable to abort actions",e)
            errorMessage = messageSource.getMessage("dispatcher.abort.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("agent[abort] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
        if ( !(agentResponse) || agentResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to abort ${agentResponse?.reasonPhrase}");
            if ( agentResponse ) {
                errorMessage = messageSource.getMessage("dispatcher.abort.error",
                    [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
            }
            else {
                errorMessage = messageSource.getMessage("dispatcher.response.null",
                    [clientInstance.name] as Object[],null);
            }
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // Audit log
        auditLogService.logClient("abort",clientInstance.name);
    }

    /**
     * Scans the client with the given transaction id, using the agent that was
     * already created ( also passed in ). This method most likely will only be
     * called by something creating a group assessment report.
     *
     * @param transactionId
     * @param agent
     * @param loggingLevel
     * @param clientInstance
     * @throws DispatcherCommunicationExeption
     */
    def scan(String transactionId, AgentCommunicator agent,
        Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // check to see if there is a group with a profile
        def errorMessage;
        if ( clientInstance.group ) {
            if ( clientInstance.group.profile ) {
                try {
                    agent = createAgentCommunicator(clientInstance);
//                    logTransaction(transactionId, 'scan')
                    agentResponse = agent.scan(transactionId,
                        securityProfileService.toXmlString(clientInstance.group.profile,true),
                        getProcsForClient(clientInstance),
                        loggingLevel);
                }
                catch(Exception e) {
                    m_log.error("Unable to scan profile",e)
                    errorMessage = messageSource.getMessage("dispatcher.scan.error",
                        [clientInstance.name, e.message] as Object[],null);
                    m_log.error(errorMessage);
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // response may or may not have been returned
                m_log.info("agent[scan] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
                if ( !(agentResponse) || agentResponse.code >= 400 ) {
                    m_log.error("Client ${clientInstance.name} unable to scan ${agentResponse?.reasonPhrase}");
                    if ( agentResponse ) {
                        errorMessage = messageSource.getMessage("dispatcher.scan.error",
                            [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.response.null",
                            [clientInstance.name] as Object[],null);
                    }
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // Audit log
                auditLogService.logClientAction("scan",clientInstance.name,clientInstance.group.profile.name);
            }
            else {
                // profile missing
                errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                    [clientInstance.name, clientInstance.group.name] as Object[],null)
                m_log.error(errorMessage);
                throw new DispatcherCommunicationException(message:errorMessage);
            }
        }
        else {
            // group missing
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.group.missing",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Invokes a scan on the client
     *
     * @param clientInstance
     */
    def scan(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // check to see if there is a group with a profile
        def errorMessage;
        if ( clientInstance.group ) {
            if ( clientInstance.group.profile ) {
                try {
                    agent = createAgentCommunicator(clientInstance);
                    // if the product has an enterprise license we send the entire xml
                    if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
                        agentResponse = agent.scan(securityProfileService.toXmlString(clientInstance.group.profile,true),getProcsForClient(clientInstance), loggingLevel);
                    }
                    else {
                        // stand alone just sends the profile absolute path
                        agentResponse = agent.scan(securityProfileService.getXmlLocation(clientInstance.group.profile).absolutePath, getProcsForClient(clientInstance), loggingLevel);
                    }
//                    logTransaction(agentResponse.getTransactionId(), 'scan')

                }
                catch(Exception e) {
                    m_log.error("Unable to scan profile",e)
                    errorMessage = messageSource.getMessage("dispatcher.scan.error",
                        [clientInstance.name, e.message] as Object[],null);
                    m_log.error(errorMessage);
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // response may or may not have been returned
                m_log.info("agent[scan] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
                if ( !(agentResponse) || agentResponse.code >= 400 ) {
                    m_log.error("Client ${clientInstance.name} unable to scan ${agentResponse?.reasonPhrase}");
                    if ( agentResponse ) {
                        errorMessage = messageSource.getMessage("dispatcher.scan.error",
                            [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.response.null",
                            [clientInstance.name] as Object[],null);
                    }
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // Audit log
                auditLogService.logClientAction("scan",clientInstance.name,clientInstance.group.profile.name);
            }
            else {
                // profile missing
                errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                    [clientInstance.name, clientInstance.group.name] as Object[],null)
                m_log.error(errorMessage);
                throw new DispatcherCommunicationException(message:errorMessage);
            }
        }
        else {
            // group missing
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.group.missing",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Invokes a quick scan on the client
     *
     * @param clientInstance
     */
    def quickScan(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // check to see if there is a group with a profile
        def errorMessage;
        if ( clientInstance.group ) {
            if ( clientInstance.group.profile ) {
                try {
                    agent = createAgentCommunicator(clientInstance);                    
                    // if the product has an enterprise license we send the entire xml
                    if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
                        agentResponse = agent.quickScan(securityProfileService.toXmlString(clientInstance.group.profile,true), getProcsForClient(clientInstance), loggingLevel);
                    }
                    else {
                        // stand alone just sends the profile absolute path
                        agentResponse = agent.quickScan(securityProfileService.getXmlLocation(clientInstance.group.profile).absolutePath, getProcsForClient(clientInstance),loggingLevel);
                    }
                }
                catch(Exception e) {
                    m_log.error("Unable to quick scan profile",e)
                    errorMessage = messageSource.getMessage("dispatcher.quickscan.error",
                        [clientInstance.name, e.message] as Object[],null);
                    m_log.error(errorMessage);
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // response may or may not have been returned
                m_log.info("agent[quick scan] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
                if ( !(agentResponse) || agentResponse.code >= 400 ) {
                    m_log.error("Client ${clientInstance.name} unable to quick scan ${agentResponse?.reasonPhrase}");
                    if ( agentResponse ) {
                        errorMessage = messageSource.getMessage("dispatcher.quickscan.error",
                            [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.response.null",
                            [clientInstance.name] as Object[],null);
                    }
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // Audit log
                auditLogService.logClientAction("quick scan",clientInstance.name,clientInstance.group.profile.name);
            }
            else {
                // profile missing
                errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                    [clientInstance.name, clientInstance.group.name] as Object[],null)
                m_log.error(errorMessage);
                throw new DispatcherCommunicationException(message:errorMessage);
            }
        }
        else {
            // group missing
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.group.missing",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Invokes and apply on the client
     *
     * @param clientInstance
     */
    def apply(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // check to see if there is a group with a profile
        def errorMessage;
        if ( clientInstance.group ) {
            if ( clientInstance.group.profile ) {
                try {
                    agent = createAgentCommunicator(clientInstance);                    
                    // if the product has an enterprise license we send the entire xml
                    if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
                        agentResponse = agent.apply(securityProfileService.toXmlString(clientInstance.group.profile,true), getProcsForClient(clientInstance), loggingLevel);
                    }
                    else {
                        // stand alone just sends the profile absolute path
                        agentResponse = agent.apply(securityProfileService.getXmlLocation(clientInstance.group.profile).absolutePath, getProcsForClient(clientInstance), loggingLevel);
                    }
                }
                catch(Exception e) {
                    m_log.error("Unable to apply profile",e)
                    errorMessage = messageSource.getMessage("dispatcher.apply.error",
                        [clientInstance.name, e.message] as Object[],null);
                    m_log.error(errorMessage);
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // response may or may not have been returned
                m_log.info("agent[apply] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
                if ( !(agentResponse) || agentResponse.code >= 400 ) {
                    m_log.error("Client ${clientInstance.name} unable to apply ${agentResponse?.reasonPhrase}");
                    if ( agentResponse ) {
                        errorMessage = messageSource.getMessage("dispatcher.apply.error",
                            [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.response.null",
                            [clientInstance.name] as Object[],null);
                    }
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // Audit log
                auditLogService.logClientAction("apply",clientInstance.name,clientInstance.group.profile.name);
            }
            else {
                // profile missing
                errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                    [clientInstance.name, clientInstance.group.name] as Object[],null)
                m_log.error(errorMessage);
                throw new DispatcherCommunicationException(message:errorMessage);
            }
        }
        else {
            // group missing
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.group.missing",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Invoke an undo on the client
     *
     * @param clientInstance
     */
    def undo(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // check to see if there is a group with a profile
        def errorMessage;
        if ( clientInstance.group ) {
            if ( clientInstance.group.profile ) {
                try {
                    agent = createAgentCommunicator(clientInstance);                    
                    // if the product has an enterprise license we send the entire xml
                    if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
                        agentResponse = agent.undo(securityProfileService.toXmlString(clientInstance.group.profile,true), getProcsForClient(clientInstance), loggingLevel);
                    }
                    else {
                        // stand alone just sends the profile absolute path
                        agentResponse = agent.undo(securityProfileService.getXmlLocation(clientInstance.group.profile).absolutePath, getProcsForClient(clientInstance), loggingLevel);
                    }
                }
                catch(Exception e) {
                    m_log.error("Unable to undo profile",e)
                    errorMessage = messageSource.getMessage("dispatcher.undo.error",
                        [clientInstance.name, e.message] as Object[],null);
                    m_log.error(errorMessage);
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // response may or may not have been returned
                m_log.info("agent[undo] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
                if ( !(agentResponse) || agentResponse.code >= 400 ) {
                    m_log.error("Client ${clientInstance.name} unable to undo ${agentResponse?.reasonPhrase}");
                    if ( agentResponse ) {
                        errorMessage = messageSource.getMessage("dispatcher.undo.error",
                            [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.response.null",
                            [clientInstance.name] as Object[],null);
                    }
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // Audit log
                auditLogService.logClientAction("undo",clientInstance.name,clientInstance.group.profile.name);
            }
            else {
                // profile missing
                errorMessage = messageSource.getMessage("dispatcher.securityProfile.missing",
                    [clientInstance.name, clientInstance.group.name] as Object[],null)
                m_log.error(errorMessage);
                throw new DispatcherCommunicationException(message:errorMessage);
            }
        }
        else {
            // group missing
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.group.missing",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * @param loggingLevel
     * @param clientInstance
     */
    def baseline(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // check to see if there is a group with a profile
        def errorMessage;

        // create the agent
        try {
            agent = createAgentCommunicator(clientInstance);
            agentResponse = agent.baseline(loggingLevel,  getProcsForClient(clientInstance));
        }
        catch(Exception e) {
            m_log.error("Unable to baseline client",e)
            errorMessage = messageSource.getMessage("dispatcher.baseline.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("agent[baseline] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
        if ( !(agentResponse) || agentResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to baseline ${agentResponse?.reasonPhrase}");
            if ( agentResponse ) {
                errorMessage = messageSource.getMessage("dispatcher.baseline.error",
                    [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
            }
            else {
                errorMessage = messageSource.getMessage("dispatcher.response.null",
                    [clientInstance.name] as Object[],null);
            }
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // Audit log
        auditLogService.logClient("baseline",clientInstance.name);
    }

    /**
     * Invokes a basline on the client
     *
     * @param clientInstance
     */
    def baselineWithProfile(Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // check to see if there is a group with a profile
        def errorMessage;
        if ( clientInstance.group ) {
            if ( clientInstance.group.baselineProfile ) {
                // create the agent
                try {
                    agent = createAgentCommunicator(clientInstance);                    
                    // if the product has an enterprise license we send the entire xml
                    if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
                        agentResponse = agent.baseline(baselineProfileService.toXmlString(clientInstance.group.baselineProfile,true), getProcsForClient(clientInstance), loggingLevel);
                    }
                    else {
                        // stand alone just sends the profile absolute path
                        agentResponse = agent.baseline(baselineProfileService.getXmlLocation(clientInstance.group.baselineProfile).absolutePath, getProcsForClient(clientInstance), loggingLevel);
                    }
                }
                catch(Exception e) {
                    m_log.error("Unable to baseline client",e)
                    errorMessage = messageSource.getMessage("dispatcher.baseline.error",
                        [clientInstance.name, e.message] as Object[],null);
                    m_log.error(errorMessage);
                    throw new DispatcherCommunicationException(message:errorMessage);
                }

                // Baseline profiles were introduced in version 4.0.3.  If the client
                // does not understand baseline profiles then we have to call the default
                // baseline method.  How we know if the client is of a version that
                // can't handle 'withProfile' is if the request throws a SOAP exception
                // and has a message string in it that denotes that the method doesn't exist
                // we could most likely use the version information in the ClientInfo object
                // but for now we'll just fall back on exception.  The exception is changed
                // into an AgentResponse with a 501 error code.

                // response may or may not have been returned
                m_log.info("agent[baseline] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
                if ( !(agentResponse) || agentResponse.code >= 400 ) {
                    m_log.error("Client ${clientInstance.name} unable to baseline ${agentResponse?.reasonPhrase}");
                    if ( agentResponse ) {
                        // check to see if we are in the corner case of a client not having
                        // the ability to use baseline profiles
                        if ( agentResponse.code == 501 ) {
                            // attempt to baseline without a profile
                            baseline(loggingLevel, clientInstance);
                            errorMessage = messageSource.getMessage("dispatcher.method.missing.baselineWithProfile",
                                [clientInstance.name] as Object[],null);
                            throw new DispatcherCommunicationException(message:errorMessage);
                        }
                        else {
                            errorMessage = messageSource.getMessage("dispatcher.baseline.error",
                                [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
                            throw new DispatcherCommunicationException(message:errorMessage);
                        }
                    }
                    else {
                        errorMessage = messageSource.getMessage("dispatcher.response.null",
                            [clientInstance.name] as Object[],null);
                        throw new DispatcherCommunicationException(message:errorMessage);
                    }
                    
                }

                // Audit log
                auditLogService.logClientAction("baseline",clientInstance.name,clientInstance.group.baselineProfile.name);
            }
            else {
                // profile missing
                errorMessage = messageSource.getMessage("dispatcher.baselineProfile.missing",
                    [clientInstance.name, clientInstance.group.name] as Object[],null)
                m_log.error(errorMessage);
                throw new DispatcherCommunicationException(message:errorMessage);
            }
        }
        else {
            // group missing
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.group.missing",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns a boolean true/false if we were able to connect w/the dispatcher
     * use the 'status' hook as it is the simplest, we're discarding the data
     * and just looking for a good connect
     *
     * @param clientInstance
     * @return Boolean true/false for good connect w/dispatcher
     */
    def pingDispatcher(Client clientInstance) throws DispatcherCommunicationException {
        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // error message for the exception
        def errorMessage;
        try {
            agent = createAgentCommunicator(clientInstance);
            agentResponse = agent.ping();
        }
        catch(Exception e) {
            m_log.error("Unable to get dispatcher status",e)
            errorMessage = messageSource.getMessage("dispatcher.status.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new DispatcherCommunicationException(message:errorMessage);
        }
        
        // return either 'Ok', or the anonymous reason for why...
        return  (agentResponse?.code == 200) ? "Ok" : agentResponse.reasonPhrase.split(":")[-1].split("\\.")[0] 
    }

    /**
     * Returns the status of the dispatcher as a map
     *
     * @param clientInstance
     * @return Map<String,String> name value pairs of dispatcher status information
     */
    def dispatcherStatus(Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // error message for the exception
        def errorMessage;
        try {
            agent = createAgentCommunicator(clientInstance);
            agentResponse = agent.status();
        }
        catch(Exception e) {
            m_log.error("Unable to get dispatcher status",e)
            errorMessage = messageSource.getMessage("dispatcher.status.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new DispatcherCommunicationException(message:errorMessage);
        }
        
        // response may or may not have been returned
        m_log.info("agent[status] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
        if ( !(agentResponse) || agentResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to get dispatcher status ${agentResponse?.reasonPhrase}");
            if ( agentResponse ) {
                errorMessage = messageSource.getMessage("dispatcher.status.error",
                    [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
            }
            else {
                errorMessage = messageSource.getMessage("dispatcher.response.null",
                    [clientInstance.name] as Object[],null);
            }
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // parse the body of the response
        def statusMap = [:];
        m_log.debug("agent[status] body[${agentResponse.body}]");
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(true);
            def xml = slurper.parseText(agentResponse.getBody());
            xml.pair.each {
                statusMap[it.@name.text()] = it.@value.text();
            }
        }
        catch (Exception e) {
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.status.parse.error",
                    [clientInstance.name] as Object[],null));
        }

        // return the created map
        m_log.debug("statusMap ${statusMap}");
        return statusMap;
    }

    /**
     * Returns information about the client as a map
     * 
     * @param clientInstance
     */
    def hostInfo(Client clientInstance) throws DispatcherCommunicationException {
        
        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // error message for the exception
        def errorMessage;
        try {
            agent = createAgentCommunicator(clientInstance);
            agentResponse = agent.info();
        }
        catch(Exception e) {
            m_log.error("Unable to get client details",e)
            errorMessage = messageSource.getMessage("dispatcher.hostInfo.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("agent[info] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
        if ( !(agentResponse) || agentResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to get host info ${agentResponse?.reasonPhrase}");
            if ( agentResponse ) {
                errorMessage = messageSource.getMessage("dispatcher.hostInfo.error",
                    [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
            }
            else {
                errorMessage = messageSource.getMessage("dispatcher.response.null",
                    [clientInstance.name] as Object[],null);
            }
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // parse the body of the response
        def hostInfoMap = [:];
        m_log.debug("agent[info] body[${agentResponse.body}]");
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(true);
            def xml = slurper.parseText(agentResponse.getBody());
            xml.pair.each {
                hostInfoMap[it.@name.text()] = it.@value.text();
            }
        }
        catch (Exception e) {
            throw new DispatcherCommunicationException(message:messageSource.getMessage("dispatcher.hostInfo.parse.error",
                    [clientInstance.name] as Object[],null));
        }

        // return the created map
        m_log.debug("hostInfoMap ${hostInfoMap}");
        return hostInfoMap;
    }

    /**
     * Create a web service client that can talk to the oslockdown
     * dispatcher located on the client
     *
     * @param client
     */
    AgentCommunicator createAgentCommunicator(Client client) {
        // should the communication
        boolean useHttps = grailsApplication.config.tcs.sb.console.secure.toBoolean();

        // create the client
        AgentCommunicator communicator = new AgentCommunicator(client.id,
            client.hostAddress,
            client.port,
            useHttps );

        // set the product type
        // Note - *legacy* (pre4.1.2) sent STANDALONE/ENTERPRISE/BULK as product type
        // This was defined in teh AgentCommunicator.java code  in 
        // AgentCommunication/src/com/trustedcs/sb/ws/client/AgentCommunicator.java
        // Now we'll define the types in the Grails side as ClientType, and pass the 
        // *ORDINAL* value down.  Note that the Dispatcher must be kept in sync if there
        // is clientType dependent behavior
        //

        communicator.setProductType(client.clientType.ordinal())

        // notification address for the response
        def notificationAddress = "${grailsApplication.config.tcs.sb.console.ip}:${grailsApplication.config.tcs.sb.console.port}"
        communicator.setNotificationAddress(grailsApplication.config.tcs.sb.console.ip, grailsApplication.config.tcs.sb.console.port);

        // return the web service client
        return communicator;
    }

    /**
     * Aborts the current action running on the oslockdown dispatcher
     * @param updateFlag   // True = do update if needed ;  False = dry run - indicate if update would have been needed 
     * @param loggingLevel
     * @param clientInstance
     */
    def autoUpdate(byte [] updater, boolean forceFlag, Integer loggingLevel, Client clientInstance) throws DispatcherCommunicationException {

        // the agent response
        AgentResponse agentResponse;

        // the ws client proxy
        AgentCommunicator agent;

        // error message for the exception
        def errorMessage;
        def version = grailsApplication.metadata["app.version"].split("-")[0]
        
        try {
            agent = createAgentCommunicator(clientInstance);
            agentResponse = agent.updateAgent(version, updater, forceFlag, loggingLevel);
        }
        catch(Exception e) {
            m_log.error("Unable to initiate AutoUpdate action",e)
            errorMessage = messageSource.getMessage("dispatcher.autoupdate.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("agent[autoUpdate] response code[${agentResponse?.code}] reason[${agentResponse?.reasonPhrase}]");
        if ( !(agentResponse) || agentResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to initiate autoUpdate ${agentResponse?.reasonPhrase}");
            if ( agentResponse && (agentResponse.code == 500) && (agentResponse.reasonPhrase.contains("not implemented"))){
                errorMessage = messageSource.getMessage("dispatcher.method.autoupdate.missing",
                    [clientInstance.name] as Object[],null);
            }
            else if ( agentResponse ) {
                errorMessage = messageSource.getMessage("dispatcher.autoupdate.error",
                    [clientInstance.name, agentResponse.reasonPhrase] as Object[],null);
            }
            else {
                errorMessage = messageSource.getMessage("dispatcher.response.null",
                    [clientInstance.name] as Object[],null);
            }
            throw new DispatcherCommunicationException(message:errorMessage);
        }

        // Audit log
        auditLogService.logClient("autoupdate",clientInstance.name);
        return agentResponse.reasonPhrase;
    }
}
