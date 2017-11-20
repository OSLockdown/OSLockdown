/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.notification;

import java.util.logging.Logger;

public class OSLockdownNotificationLogger implements
		OSLockdownNotificationListener {
	
	private static java.util.logging.Logger m_log 
		= Logger.getLogger("com.trustedcs.sb.notification.OSLockdownNotificationLogger");	

	@Override
	public void infoReceived(OSLockdownNotificationEvent notificationEvent) {
		// TODO Auto-generated method stub
		m_log.info(notificationEvent.toString());
	}

	@Override
	public void notificationReceived(
			OSLockdownNotificationEvent notificationEvent) {
		// TODO Auto-generated method stub
		m_log.info(notificationEvent.toString());
	}

	@Override
	public void statusReceived(
			OSLockdownNotificationEvent notificationEvent) {
		// TODO Auto-generated method stub
		m_log.info(notificationEvent.toString());
	}

}
