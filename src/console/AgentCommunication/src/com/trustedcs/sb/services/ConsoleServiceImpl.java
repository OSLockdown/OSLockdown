/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import com.trustedcs.sb.services.sei.ConsoleService;
import com.trustedcs.sb.services.sei.ConsoleResponse;
import com.trustedcs.sb.services.sei.ConsoleNotification;

import com.trustedcs.sb.notification.OSLockdownNotificationEvent;
import com.trustedcs.sb.notification.OSLockdownNotifier;
import com.trustedcs.sb.notification.OSLockdownNotificationListener;

import javax.jws.WebParam;
import javax.jws.WebService;

import org.apache.log4j.Logger;

@WebService
public class ConsoleServiceImpl implements ConsoleService {
	
	private static Logger m_log = Logger.getLogger("com.trustedcs.sb.services.ConsoleService");

	/**
	 * Status message from the client/agent
	 * 
	 * @param notification
	 *            the notification object
	 */
	public ConsoleResponse reportStatus(@WebParam(name = "notification") ConsoleNotification notification) {
		try { 
			OSLockdownNotificationEvent event = new OSLockdownNotificationEvent(notification);
			OSLockdownNotifier.getInstance().notifyListeners(event);
		}
		catch (Exception e ) {
			m_log.error("Unable to create event",e);
			return new ConsoleResponse(500, e.getMessage());
		}
		return new ConsoleResponse(200, "Notification Received");
	}

	/**
	 * Notification message of something that has been either completed or
	 * failed.
	 * 
	 * @param notification
	 *            the notification object
	 */
	public ConsoleResponse notify(@WebParam(name = "notification") ConsoleNotification notification) {
		try {
			OSLockdownNotificationEvent event = new OSLockdownNotificationEvent(notification);
			OSLockdownNotifier.getInstance().notifyListeners(event);
		}
		catch ( Exception e ) {
			m_log.error("Unable to create event",e);
			return new ConsoleResponse(500, e.getMessage());
		}
		return new ConsoleResponse(200, "Notification Received");
	}

	/**
	 * Info message from the client
	 * 
	 * @param notification
	 *            the notification object
	 */
	public ConsoleResponse reportInfo(@WebParam(name = "notificationId") ConsoleNotification notification) {
		try {
			OSLockdownNotificationEvent event = new OSLockdownNotificationEvent(notification);
			OSLockdownNotifier.getInstance().notifyListeners(event);
		}
		catch (Exception e) {			
			m_log.error("Unable to create event",e);
			return new ConsoleResponse(500, e.getMessage());
		}
		return new ConsoleResponse(200, "Notification Received");
	}
}
