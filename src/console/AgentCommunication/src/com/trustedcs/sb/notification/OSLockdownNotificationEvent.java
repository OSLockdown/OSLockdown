/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.notification;

import java.io.ByteArrayInputStream;
import java.util.List;
import java.util.Map;

import com.trustedcs.sb.notification.parser.NotificationBodyParser;
import com.trustedcs.sb.services.sei.ConsoleNotification;

import org.apache.log4j.Logger;

public class OSLockdownNotificationEvent {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.notification.OSLockdownNotificationEvent");

    private ConsoleNotification m_notification;
    private boolean m_success = false;
    private boolean m_aborted = false;
    private Map m_dataMap = null;
    private Map m_exceptionMap = null;
    private static final String BODY_PARSE_ERROR = "Unable to parse notification body.";

    /**
     * Default constructor
     */
    public OSLockdownNotificationEvent() {
        // TODO Auto-generated constructor stub
    }

    /**
     * Constructor that will actually be used
     * @param notif the notification from the webservice
     */
    public OSLockdownNotificationEvent(ConsoleNotification notif) throws Exception {
        m_notification = notif;
        // parse the ws-notification
        if (notif != null) {
            NotificationBodyParser parser = new NotificationBodyParser();
            if (notif.getBody() != null) {
                try {
                    parser.parse(new ByteArrayInputStream(notif.getBody().getBytes()));
                } catch (Exception e) {
                    if (m_notification.getInfo() != null) {
                        m_notification.setInfo(m_notification.getInfo() + " " + BODY_PARSE_ERROR);
                    } else {
                        m_notification.setInfo(BODY_PARSE_ERROR);
                    }
                    m_log.error("Unable to parse notification transactionId["+notif.getTransactionId()+"]\nbody["+notif.getBody()+"]");
                }
                m_success = parser.wasSuccessful();
                m_aborted = parser.wasAborted();
                m_dataMap = parser.getDataMap();
                m_exceptionMap = parser.getExceptionMap();
            }
        }
    }

    /**
     * Get the notification sei object that was passed
     * back from the webservice layer
     * @return
     */
    public ConsoleNotification getNotification() {
        return m_notification;
    }

    /**
     * Convenience method to pull the transaction id from the sei notification
     * @return the transaction id internal to the sei
     */
    public String getTransactionId() {
        if (m_notification != null) {
            return m_notification.getTransactionId();
        }
        return null;
    }

    /**
     * Convenience method to pull the info string from the sei notification
     * @return the info string internal to the sei
     */
    public String getInfo() {
        if (m_notification != null) {
            return m_notification.getInfo();
        }
        return null;
    }

    /**
     * If the action that the notification is for was successful
     * @return
     */
    public boolean wasSuccessful() {
        return m_success;
    }

    /**
     * If the action that the notification is for was aborted
     * @return
     */
    public boolean wasAborted() {
        return m_aborted;
    }

    /**
     * The data map for the event
     * @return
     */
    public Map getDataMap() {
        return m_dataMap;
    }

    /**
     * The exception map for the event
     * @return Map<String,List<String>>
     */
    public Map getExceptionMap() {
        return m_exceptionMap;
    }

    /**
     * Convenience method to return the notifications action type
     * @return
     */
    public int getActionType() {
        if (m_notification != null) {
            return m_notification.getType();
        }
        return -1;
    }

    public String toString() {
        StringBuffer buf = new StringBuffer();
        buf.append("NotificationEvent\n");
        buf.append("actionType[ " + getActionType() + " ] ");
        buf.append("success[ " + m_success + " ] ");
        buf.append("aborted[ " + m_aborted + " ] ");
        buf.append("transactionId[ " + getTransactionId() + " ] ");
        buf.append("dataMap[ " + m_dataMap + " ]");
        buf.append(m_notification);
        return buf.toString();
    }
}
