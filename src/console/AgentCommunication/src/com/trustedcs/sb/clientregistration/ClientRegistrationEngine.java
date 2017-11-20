/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.clientregistration;

import com.trustedcs.sb.services.sei.ClientRegistrationResponse;

public class ClientRegistrationEngine {

	// the singleton instance
	static ClientRegistrationEngine m_instance= null;
	
	private ClientRegistrationEngineHandlerInterface m_handler = null;
	
	/**
	 * Private Constructor for the singleton instance
	 */
	private ClientRegistrationEngine() {
		
	}
	
	/**
	 * Singleton get method
	 * @return the singleton instance
	 */
	public static ClientRegistrationEngine getInstance() {
		if ( m_instance == null ) {
			m_instance = new ClientRegistrationEngine();
		}
		return m_instance;
	}
	
	/**
	 * Returns the crypto information for the client
	 * @return the crypto information
	 */
	public ClientRegistrationCrypto generateClientCrypto(String clientCertificate) throws Exception {
		if ( m_handler == null ) {		
			throw new Exception("Handler not registered, license could be invalid.");
		}
		else {
			return m_handler.generateClientCrypto(clientCertificate);	
		}		
	}
	
	/**
	 * Sets the handler that will be responsible for creating all the crypto information
	 * for the client
	 * @param handler
	 */
	public void setClientRegistrationHandler(ClientRegistrationEngineHandlerInterface handler) {
		m_handler = handler;
	}	
	
}
