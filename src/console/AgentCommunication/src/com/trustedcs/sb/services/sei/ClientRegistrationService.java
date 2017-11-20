/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public interface ClientRegistrationService {

	/**
	 * Registers a client with the console
	 * @param name
	 * @param hostName
	 * @param port
	 * @param location
	 * @param contact
     * @param procinfo
     * @param clientCertificate
	 * @return
	 */
	public ClientRegistrationResponse registerClient(String name, 
													 String hostName, 
													 int port,
													 String location,
													 String contact,
                                                     String procinfo,
													 String clientCertificate);
}
