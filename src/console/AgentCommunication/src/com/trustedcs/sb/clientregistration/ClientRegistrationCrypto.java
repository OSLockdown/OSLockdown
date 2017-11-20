/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.clientregistration;

public class ClientRegistrationCrypto {

	private String m_caCert = null;
	private String m_dispatcherCert = null;
	private String m_dispatcherPassphrase = null;
	
	/**
	 * Empty constructor
	 */
	public ClientRegistrationCrypto() {
		
	}
	
	/**
	 * Parameterized Constructor
	 */
	public ClientRegistrationCrypto(String caCert, 
									String dispatcherCert, 
									String dispatcherPassphrase) {
		m_caCert = caCert;
		m_dispatcherCert = dispatcherCert;
		m_dispatcherPassphrase = dispatcherPassphrase;
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
	public String getDispatcherPassphrase() {
		return m_dispatcherPassphrase;
	}
	
	/**
	 * 
	 * @param dispatcherPassphrase
	 */
	public void setDispatcherPassphrase(String dispatcherPassphrase) {
		m_dispatcherPassphrase = dispatcherPassphrase;
	}
}
