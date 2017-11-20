/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class ClientRegistrationResponse extends SBResponse {
	
	// private variables
	private String m_caCert;
	private String m_dispatcherCert;
	String m_dispatchPassphrase;

	/**
	 * Parameterless constructor
	 */
	public ClientRegistrationResponse() {
		
	}
	
	/**
	 * Code and reason constructor
	 * @param code
	 * @param reasonPhrase
	 */
	public ClientRegistrationResponse(int code, String reasonPhrase) {
		super(code,reasonPhrase);
	}
	
	/**
	 * 
	 * @return
	 */
	public String getCaCert() {
		return m_caCert;
	}

	/**
	 * 
	 * @param caCert
	 */
	public void setCaCert(String caCert) {
		m_caCert = caCert;
	}

	/**
	 * 
	 * @return
	 */
	public String getDispatcherCert() {
		return m_dispatcherCert;
	}

	/**
	 * 
	 * @param dispatcherCert
	 */
	public void setDispatcherCert(String dispatcherCert) {
		m_dispatcherCert = dispatcherCert;
	}

	/**
	 * 
	 * @return
	 */
	public String getDispatchPassphrase() {
		return m_dispatchPassphrase;
	}

	/**
	 * 
	 * @param dispatchPassphrase
	 */
	public void setDispatchPassphrase(String dispatchPassphrase) {
		m_dispatchPassphrase = dispatchPassphrase;
	}
}
