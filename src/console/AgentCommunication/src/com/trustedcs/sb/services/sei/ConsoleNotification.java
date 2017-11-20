/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class ConsoleNotification {
	
	private int m_type;
	private String m_info;
	private String m_body;
	private String m_transactionId;
	
	public ConsoleNotification() {
		
	}
	
	public ConsoleNotification(int type, 
							   String transactionId, 
							   String info, 
							   String body) {	
		m_type = type;
		m_transactionId = transactionId;
		m_info = info;
		m_body = body;
	}
	
	public int getType() {
		return m_type;
	}

	public void setType(int type) {
		m_type = type;
	}
	
	public String getTransactionId() {
		return m_transactionId;
	}
	
	public void setTransactionId(String id) {
		m_transactionId = id;
	}

	public String getInfo() {
		return m_info;
	}

	public void setInfo(String info) {
		m_info = info;
	}

	public String getBody() {
		return m_body;
	}

	public void setBody(String body) {
		m_body = body;
	}
	
	public String toString() {		
		StringBuffer buffer = new StringBuffer();
		buffer.append("type[");
		buffer.append(m_type);
		buffer.append("] transactionId [");
		buffer.append(m_transactionId);
		buffer.append("] info[");
		buffer.append(m_info);	
		buffer.append("] body[");
		buffer.append(m_body);
		buffer.append("]");
		return buffer.toString();		
	}
}
