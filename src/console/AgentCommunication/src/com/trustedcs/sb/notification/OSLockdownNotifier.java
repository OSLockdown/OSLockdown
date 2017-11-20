/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.notification;

import java.util.ArrayList;

import com.trustedcs.sb.services.sei.ConsoleNotification;

public class OSLockdownNotifier {
	
	// the singleton instance
	static OSLockdownNotifier m_instance = null;
	
	// holds all the listeners that have been registered
	private ArrayList<OSLockdownNotificationListener> m_listeners = null;
	
	/**
	 * Private Constructor for the singleton instance
	 */
	private OSLockdownNotifier() {
		m_listeners = new ArrayList<OSLockdownNotificationListener>();
	}
	
	/**
	 * Singleton get method
	 * @return the singleton instance
	 */
	public static OSLockdownNotifier getInstance() {
		if ( m_instance == null ) {
			m_instance = new OSLockdownNotifier();
		}
		return m_instance;
	}

	/**
	 * Iterate through all the listeners that are registered
	 * and notify them of the event that has happened
	 * @param event
	 */
	public synchronized void notifyListeners(OSLockdownNotificationEvent event) {
		sendNotificationEvent(event);
	}
	
	/**
	 * Sends the info event to all registered listeners
	 * @param event
	 */
	private void sendInfoEvent(OSLockdownNotificationEvent event) {		
		for(OSLockdownNotificationListener listener : m_listeners) {
			listener.infoReceived(event);
		}		
	}
	
	/**
	 * Sends the notification event to all registered listeners
	 * @param event
	 */
	private void sendNotificationEvent(OSLockdownNotificationEvent event) {
		for(OSLockdownNotificationListener listener : m_listeners) {
			listener.notificationReceived(event);
		}	
	}
	
	/**
	 * Sends the status event to all registered listeners
	 * @param event
	 */
	private void sendStatusEvent(OSLockdownNotificationEvent event) {
		for(OSLockdownNotificationListener listener : m_listeners) {
			listener.statusReceived(event);
		}	
	}
	
	/**
	 * Register the passed listener with the singleton
	 * @param listener the listener to be registered
	 */
	public void registerListener(OSLockdownNotificationListener listener) {
		m_listeners.add(listener);
	}
	
	/**
	 * Test main method to validate that the listeners are being called properly
	 * @param argv
	 */
	public static void main(String argv[]) {
		OSLockdownNotifier instance = OSLockdownNotifier.getInstance();
		OSLockdownNotificationLogger listenerLogger = new OSLockdownNotificationLogger();
		instance.registerListener(listenerLogger);
	}
}
