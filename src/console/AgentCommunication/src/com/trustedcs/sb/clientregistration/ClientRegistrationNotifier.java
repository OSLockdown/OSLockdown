/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.clientregistration;

import java.util.ArrayList;

public class ClientRegistrationNotifier {
	
	// the singleton instance
	static ClientRegistrationNotifier m_instance = null;
	
	// holds all the listeners that have been registered
	private ArrayList<ClientRegistrationListener> m_listeners = null;
	
	/**
	 * Private Constructor for the singleton instance
	 */
	private ClientRegistrationNotifier() {
		m_listeners = new ArrayList<ClientRegistrationListener>();
	}
	
	/**
	 * Singleton get method
	 * @return the singleton instance
	 */
	public static ClientRegistrationNotifier getInstance() {
		if ( m_instance == null ) {
			m_instance = new ClientRegistrationNotifier();
		}
		return m_instance;
	}

	/**
	 * Iterate through all the listeners that are registered
	 * and notify them of the event that has happened
	 * @param event
	 */
	public synchronized void notifyListeners(ClientRegistrationEvent event) {
		for(ClientRegistrationListener listener : m_listeners) {
			listener.clientRegistrationRequest(event);
		}			
		
	}
	
	/**
	 * Register the passed listener with the singleton
	 * @param listener the listener to be registered
	 */
	public void registerListener(ClientRegistrationListener listener) {
		m_listeners.add(listener);
	}
	
	/**
	 * Test main method to validate that the listeners are being called properly
	 * @param argv
	 */
	public static void main(String argv[]) {
				
	}
}
