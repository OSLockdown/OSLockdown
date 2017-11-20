/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.clientregistration;

public interface ClientRegistrationEngineHandlerInterface {

	/**
	 * Creates the client crypto information and returns it in an object
	 * @param clientCertificate TODO
	 * @return
	 */
	public ClientRegistrationCrypto generateClientCrypto(String clientCertificate) throws Exception;
	
}
