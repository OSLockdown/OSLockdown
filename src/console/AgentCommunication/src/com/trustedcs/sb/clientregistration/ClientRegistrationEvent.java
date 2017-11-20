/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.clientregistration;

public class ClientRegistrationEvent {
	private String m_clientName;
	private String m_hostAddress;
	private int m_port;
	private String m_location;
	private String m_contact;
    private String m_procinfo;
	private String m_clientCertificate;
	
	/**
	 * Parameterless constructor
	 */
	public ClientRegistrationEvent() {
		
	}
	
	/**
	 * Parameter constructor
	 * @param clientName
	 * @param hostAddress
	 * @param port
	 */
	public ClientRegistrationEvent(String clientName , String hostAddress, int port , String location, String contact, String procinfo, String clientCertificate) {
		m_clientName = clientName;
		m_hostAddress = hostAddress;
		m_port = port;
		m_location = location;
		m_contact = contact;
        m_procinfo = procinfo;
		m_clientCertificate = clientCertificate;
	}
	
	/**
	 * 
	 * @return
	 */
	public String getClientName() {
		return m_clientName;
	}
	
	/**
	 * 
	 * @param clientName
	 */
	public void setClientName(String clientName) {
		m_clientName = clientName;
	}
	
	/**
	 * 
	 * @return
	 */
	public String getHostAddress() {
		return m_hostAddress;
	}
	
	/**
	 * 
	 * @param hostAddress
	 */
	public void setHostAddress(String hostAddress) {
		m_hostAddress = hostAddress;
	}
	
	/**
	 * 
	 * @return
	 */
	public int getPort() {
		return m_port;
	}

	/**
	 * 
	 * @param port
	 */
	public void setPort(int port) {
		m_port = port;
	}
	
	public String getLocation() {
		return m_location;
	}

	public void setLocation(String location) {
		m_location = location;
	}

	public String getContact() {
		return m_contact;
	}

	public void setContact(String contact) {
		m_contact = contact;
	}

	public String getProcinfo() {
		return m_procinfo;
	}

	public void setProcinfo(String procinfo) {
		m_procinfo = procinfo;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer();
		buf.append("ClientRegistrationEvent\n");
		buf.append("name[ "+getClientName()+" ] ");
		buf.append("hostAddress[ "+ getHostAddress()+ " ] ");
		buf.append("port[ "+ getPort() + " ] ");
		buf.append("location[ "+getLocation()+ " ] ");
		buf.append("contact[ "+getContact()+ " ] ");
        buf.append("procinfo [ "+getProcinfo()+ " ] ");
		return buf.toString();
	}	
}
