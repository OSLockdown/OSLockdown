/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import grails.util.Environment;

// client and group objects
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Processor;

// client registration objects
import com.trustedcs.sb.clientregistration.ClientRegistrationRequest;
import com.trustedcs.sb.exceptions.ClientRegistrationException;

// listener for the webservice event generation
import com.trustedcs.sb.clientregistration.ClientRegistrationListener;
import com.trustedcs.sb.clientregistration.ClientRegistrationEvent;

// generates crypto information for the client response
import com.trustedcs.sb.clientregistration.ClientRegistrationEngineHandlerInterface;
import com.trustedcs.sb.clientregistration.ClientRegistrationCrypto;

// for clientType stuff
import com.trustedcs.sb.util.ClientType;
import com.trustedcs.sb.license.SbLicense;

class ClientRegistrationService implements ClientRegistrationListener, ClientRegistrationEngineHandlerInterface {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ClientRegistrationService");

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def groupService;
    def clientService;
    def auditLogService;
    def processorService;
    /**
     * Save the client auto registration requestion from the database
     */
    def save(ClientRegistrationRequest clientRegistrationInstance) {
        // save Client Auto Registration to the database
        if (!clientRegistrationInstance.hasErrors() && clientRegistrationInstance.save()) {
            m_log.info("Client Auto Registration Saved");
            auditLogService.logGenericAction("register","client",clientRegistrationInstance.name);
        }
        else {
            m_log.error("Unable to save Client Auto Registration");
            clientRegistrationInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new ClientRegistrationException(clientRegistrationInstance:clientRegistrationInstance);
        }
    }

    /**
     * Delete the client auto registration requestion from the database
     */
    def delete(ClientRegistrationRequest clientRegistrationInstance) {
        // delete from db
        clientRegistrationInstance.delete();
        // iterate errors
        if ( clientRegistrationInstance.hasErrors() ) {
            clientRegistrationInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new ClientRegistrationException(clientRegistrationInstance:clientRegistrationInstance);
        }
    }

    /**
     * Allow the client registration
     * The client will be associated with the group
     *
     * @param clientRegistrationInstance
     * @param groupInstance
     */
    def allow(ClientRegistrationRequest clientRegistrationInstance, Group groupInstance) {
        ClientType clientType = clientRegistrationInstance.clientType;
        
        if (clientRegistrationInstance.processorName) {
            // If we have a processorName, see if it is registered.
            // If it is not, and we already have exceeded the processor count, then raise an exception.
            // If it is not, and we are still under the cap, then add it
            // otherwise just add the Client.

            // If we're not registered, then go ahead and register this processor
            if (!Processor.findByName(clientRegistrationInstance.processorName)) {
                processorService.save(clientRegistrationInstance.processorName, clientRegistrationInstance.clientType); 
            }            
        }
          
        // create the client instance from the registration request
        Client clientInstance = clientService.fromAutoRegistrationRequest(clientRegistrationInstance);

        // save the client
        clientService.save(clientInstance);

        if (groupInstance != null) {
            // add the client to the group
            groupInstance.addToClients(clientInstance);
        // save the group
            groupService.save(groupInstance);
        }
        
        // delete the registration request
        delete(clientRegistrationInstance);
    }


    /**
     * Deny the auto registration
     *
     * @param clientRegistrationInstance
     */
    def deny(ClientRegistrationRequest clientRegistrationInstance) {
        // delete client registration
        delete(clientRegistrationInstance);
    }

    /**
     * A client request has come for auto registration
     * Method is called by the ClientRegistrationNotifier
     *
     * @param event the registration event
     */
    public void clientRegistrationRequest(ClientRegistrationEvent event) {
        try {
            m_log.info(event.toString());
            // create the time stamp
            def calendar = Calendar.getInstance();
            def date = calendar.getTime();
            def procStrings = ""
            // create client registration request            
            // Note - the procinfo *string* from the ClientRegistrationEvent needs to be processed by 
            // splitting it on '|' into a clientType and a processorName, both are stored with the
            // request as hidden fields, and massaged into a displayText string for display
        
            String     displayText="None";
            String     processorName="";
            ClientType clientType=null;
            ClientType defClientType;
            
            if (SbLicense.instance.isBulk()) {
                defClientType = ClientType.CLIENT_BULK;
            } 
            else if (SbLicense.instance.isStandAlone()) {
                defClientType = ClientType.CLIENT_STANDALONE;
            }
            else {
                defClientType = ClientType.CLIENT_ENTERPRISE;
            }

            if (event.procinfo) {
                m_log.error("Client claims processor information '${event.procinfo}'");
                procStrings = event.procinfo.split("\\|",-1)
                def ptype = ClientType.byName(procStrings[0]);
                if (ptype) {
                    clientType = ptype;
                }
                else {
                  m_log.error("Unrecognized processor declaration: client:${event.clientName} procinfo:${event.procinfo}");
                }
            }
            if (clientType == null) {
              clientType = defClientType;
              m_log.error("Client will be treated as a(n) ${defClientType.name} Client for registration purposes");
              m_log.error("-->Client will be treated as a(n) ${clientType.name} Client for registration purposes");
            }
            displayText = "${clientType.name}"
            if (clientType.usableAsProcType) {
                processorName = "${procStrings[1]}";
                displayText += " (${processorName})"
            }
            ClientRegistrationRequest registrationRequest = new ClientRegistrationRequest(timeStamp:date,
                name:event.clientName,
                hostAddress:event.hostAddress,
                port:event.port,
                displayText:displayText,
                processorName:processorName,
                clientType:clientType,
                location:event.location,
                contact:event.contact);
            save(registrationRequest);
        }
        catch ( ClientRegistrationException autoRegistrationException ) {
            m_log.error("Unable to persist client registration request",e);
        }
    }

    /**
     * Creates the client crypto information and returns it in an object
     * Method is called from the ClientRegistrationEngine
     *
     * @param clientCertificate
     * @return
     */
    public ClientRegistrationCrypto generateClientCrypto(String clientCertificate) throws Exception {

        ClientRegistrationCrypto crypto = new ClientRegistrationCrypto();
        if ( Environment.current == Environment.PRODUCTION ) {
            crypto.setCaCert(new File("/var/lib/oslockdown/files/certs/cacert.pem").text);
            crypto.setDispatcherCert(new File("/var/lib/oslockdown/files/certs/Disp.pem").text);
            crypto.setDispatcherPassphrase(new File("/var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat").text);
        }
        else {
            crypto.setCaCert("Junk CA Certificate");
            crypto.setDispatcherCert("Junk Dispatcher Certicate");
            crypto.setDispatcherPassphrase("Junk Passphrase");
        }
        return crypto;
    }
}
