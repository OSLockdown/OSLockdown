/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class SBResponse {
	
	private int m_code;
	private String m_reasonPhrase;
	private String m_body;
    private String m_transactionId;
	
	/**
	 * 
	 */
	public SBResponse() {
		
	}
	
	/**
	 * @param code
	 * @param reasonPhrase
	 */
	public SBResponse(int code, String reasonPhrase) {
		m_code = code;
		m_reasonPhrase = reasonPhrase;
	}
	
	public SBResponse(int code, String reasonPhrase, String body) {
		m_code = code;
		m_reasonPhrase = reasonPhrase;
		m_body = body;
	}
	
	public SBResponse(int code, String reasonPhrase, String body, String transactionId) {
		m_code = code;
		m_reasonPhrase = reasonPhrase;
		m_body = body;
        m_transactionId = transactionId;
	}
	
	/**
	 * @return
	 */
	public int getCode() {
		return m_code;
	}

	/**
	 * @param code
	 */
	public void setCode(int code) {
		m_code = code;
	}

	/**
	 * @return
	 */
	public String getReasonPhrase() {
		return m_reasonPhrase;
	}

	/**
	 * @param reasonPhrase
	 */
	public void setReasonPhrase(String reasonPhrase) {
		m_reasonPhrase = reasonPhrase;
	}
	
	/**
	 * Returns the body content
	 * @return
	 */
	public String getBody() {
		return m_body;
	}
	
	/**
	 * Sets the body content
	 * @param body
	 */
	public void setBody(String body) {
		m_body = body;
	}

	/**
	 * Returns the transactionId content
	 * @return
	 */
	public String getTransactionId() {
		return m_transactionId;
	}
	
	/**
	 * Sets the transactionId content
	 * @param body
	 */
	public void setTransactionId(String transactionId) {
		m_transactionId = transactionId;
	}
	
	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
    public String toString() {
		StringBuffer buffer = new StringBuffer();
		buffer.append("code[");
		buffer.append(m_code);
		buffer.append("] reasonPhrase[");
		buffer.append(m_reasonPhrase);
		buffer.append("] transactionId[");
		buffer.append(m_transactionId);
		buffer.append("]\n");
		buffer.append("body {");
		buffer.append(m_body);
		buffer.append("\n}");
        return buffer.toString();
	}
}
