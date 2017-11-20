/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.ssl;

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
	    return true;
	}		
}
