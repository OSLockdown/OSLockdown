/*
 * Original file generated in 2010 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.util;

import org.apache.log4j.Logger

import com.trustedcs.sb.clientregistration.ClientRegistrationRequest;
import com.trustedcs.sb.web.notifications.Notification;

/**
 *
 * @author amcgrath
 */
class SessionAlertUtil {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.util.SessionAlertUtil");

    /**
     *
     */
    public static void updateAutoRegistrationCount(def session) {
        // list of registrations
        def registrationList;

        // get the current time
        def calendar = Calendar.getInstance();
        def now = calendar.getTime();

        // check to see if there has been a poll before now
        if ( ! (session.lastRegistrationPoll) ) {
            // set the lastRegistrationPoll to be last login
            session.lastRegistrationPoll = session.lastLogin;
        }

        m_log.debug ( "last access ${session.lastRegistrationPoll}");
        registrationList = ClientRegistrationRequest.withCriteria {
            between('timeStamp',session.lastRegistrationPoll,now)
        }
        m_log.debug("size of existing registration list ${session.registrationCount}");
        m_log.debug("size of registration list ${registrationList.size()}");
        if ( session.registrationCount ) {
            session.registrationCount = session.registrationCount + registrationList.size();
        }
        else {
            session.registrationCount = registrationList.size();
        }

        m_log.debug("new registration list total ${session.registrationCount}");

        // set the date in the session
        session.lastRegistrationPoll = now;

    }

    /**
     *
     */
    public static void updateNotificationCount(def session) {
        // list of notifications
        def notificationList;

        // get the current time
        def calendar = Calendar.getInstance();
        def now = calendar.getTime();

        // check to see if there has been a poll before now
        if ( ! (session.lastNotificationPoll) ) {
            // set the lastNotificationPoll to be last login
            session.lastNotificationPoll = session.lastLogin;
        }

        m_log.debug ( "last access ${session.lastNotificationPoll}");
        notificationList = Notification.withCriteria {
            between('timeStamp',session.lastNotificationPoll,now)
        }
        m_log.debug("size of existing notification list ${session.notificationCount}");
        m_log.debug("size of notification list ${notificationList.size()}");
        if ( session.notificationCount ) {
            session.notificationCount = session.notificationCount + notificationList.size();
        }
        else {
            session.notificationCount = notificationList.size();
        }

        m_log.debug("new notification list total ${session.notificationCount}");

        // set the date in the session
        session.lastNotificationPoll = now;
    }
}

