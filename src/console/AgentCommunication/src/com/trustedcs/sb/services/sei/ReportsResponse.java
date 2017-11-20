/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class ReportsResponse extends SBResponse {
	
	private String m_content;
	private byte[] m_compressed;

	public ReportsResponse() {
		
	}
	
	public ReportsResponse(int code, String reasonPhrase) {
		super(code,reasonPhrase);
	}
	
	public void setContent(String content) {
		m_content = content;
	}
	
	public String getContent() {
		return m_content;
	}
	
	public byte[] getCompressed() {
		return m_compressed;
	}
	
	public void setCompressed(byte[] compressed) {
		m_compressed = compressed;
	}
}
