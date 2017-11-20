/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import javax.jws.WebParam;
import javax.jws.WebService;
//import javax.annotation.Resource;
//import javax.xml.ws;

import org.apache.log4j.Logger;

import com.trustedcs.sb.clientregistration.ClientRegistrationCrypto;
import com.trustedcs.sb.clientregistration.ClientRegistrationEngine;
import com.trustedcs.sb.clientregistration.ClientRegistrationEvent;
import com.trustedcs.sb.clientregistration.ClientRegistrationNotifier;
import com.trustedcs.sb.services.sei.ClientRegistrationResponse;
import com.trustedcs.sb.services.sei.ClientRegistrationService;
import com.trustedcs.sb.services.sei.TaskVerificationResponse;

@WebService
public class ClientRegistrationServiceImpl implements ClientRegistrationService {
	
	private static Logger m_log = Logger.getLogger("com.trustedcs.sb.services.ConsoleService");
    
//    @Resource
//    WebServiceContext wsContext;
        
	@Override
	public ClientRegistrationResponse registerClient(@WebParam(name = "name") String name, 
													 @WebParam(name = "hostName") String hostName,
													 @WebParam(name = "port") int port,
													 @WebParam(name = "location") String location,
													 @WebParam(name = "contact") String contact, 
                                                     @WebParam(name = "procinfo") String procinfo,		
													 @WebParam(name = "clientCertificate") String clientCertificate) {		
		
		// notify any interested parties that a client is trying to auto register
		if (port != 0) {
            m_log.info("Client registration received for <"+name+">");
            try { 
	    		ClientRegistrationEvent event = new ClientRegistrationEvent(name,hostName,port,location,contact,procinfo,clientCertificate);			
		    	ClientRegistrationNotifier.getInstance().notifyListeners(event);			
		    }
		    catch (Exception e ) {
			    m_log.error("Unable to create event",e);
			    return new ClientRegistrationResponse(500, e.getMessage());
		    }
		}
        else {
            
            m_log.info("SSL Certs requested by "+name);
        }
		// crypto information for the client
		ClientRegistrationCrypto clientCrypto = null;
		try {
			clientCrypto = ClientRegistrationEngine.getInstance().generateClientCrypto(clientCertificate);
		}
		catch ( Exception e ) {
			m_log.error("Unable to create crypto information",e);
			return new ClientRegistrationResponse(500, e.getMessage());			
		}
		
        ClientRegistrationResponse response;
        if (port != 0) {
		    response = 
				    new ClientRegistrationResponse(200,"Registration Pending");
		} 
        else {
		    response = 
				    new ClientRegistrationResponse(200,"Current SSL certificates fetched");
        }
		// set the crypto information on the response
		if ( clientCrypto != null ) {
			if ( clientCrypto.getCaCert() != null ) {
				m_log.info("Providing CA public certificate");
				response.setCaCert(clientCrypto.getCaCert());	
			}
			else {
				m_log.info("Unable to provide CA public certificate");
			}
			if ( clientCrypto.getDispatcherCert() != null ) {
				m_log.info("Providing Dispatcher certificate");
				response.setDispatcherCert(clientCrypto.getDispatcherCert());	
			}
			else {
				m_log.info("Unable to provide Dispatcher certificate");
			}
			if ( clientCrypto.getDispatcherPassphrase() != null ) {
				m_log.info("Providing Dispatcher private passphrase");
				response.setDispatchPassphrase(clientCrypto.getDispatcherPassphrase());	
			}
			else {
				m_log.info("Unable to provide Dispatcher private passphrase");
			}
		}

		// return the SOAP response
		return response;
	}

}
