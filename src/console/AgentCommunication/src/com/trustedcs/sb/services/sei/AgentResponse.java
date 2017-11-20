/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class AgentResponse extends SBResponse {
	
	/**
	 * 
	 */
	public AgentResponse() {
		
	}
	
	/**
	 * 
	 * @param code
	 * @param reasonPhrase
	 */
	public AgentResponse(int code, String reasonPhrase)
	{
		super(code,reasonPhrase);
	}

	public AgentResponse(int code, String reasonPhrase, String body)
	{
		super(code,reasonPhrase,body);
	}

	public AgentResponse(int code, String reasonPhrase, String body, String transactionId)
	{
		super(code,reasonPhrase,body,transactionId);
	}
}
