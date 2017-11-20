/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.notification;

public interface OSLockdownNotificationListener {

	/**
	 * 
	 * @param notificationEvent
	 */
	public void notificationReceived(
			OSLockdownNotificationEvent notificationEvent);

	/**
	 * 
	 * @param notificationEvent
	 */
	public void statusReceived(
			OSLockdownNotificationEvent notificationEvent);

	/**
	 * 
	 * @param notificationEvent
	 */
	public void infoReceived(OSLockdownNotificationEvent notificationEvent);
}
