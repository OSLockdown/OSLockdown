/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.clientregistration;

public interface ClientRegistrationListener {

	/**
	 * Notifies the listen that a client has requested registration
	 * @param event the registration event
	 */
	public void clientRegistrationRequest(ClientRegistrationEvent event);
	
}
