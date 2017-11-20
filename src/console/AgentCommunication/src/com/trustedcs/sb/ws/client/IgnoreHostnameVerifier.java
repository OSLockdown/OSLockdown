/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
/**
 * 
 */
package com.trustedcs.sb.ws.client;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLSession;

/**
 * @author amcgrath
 *
 */
public class IgnoreHostnameVerifier implements HostnameVerifier {
	
	/**
	 * @param hostName
	 * @param session
	 */	
	public boolean verify(String hostName, SSLSession session) {
	    System.out.println("Custom HostName Verification should return true");
        return true;
	}		
}
