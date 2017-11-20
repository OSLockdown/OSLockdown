/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.notifications;

class NotificationException implements Serializable {
	
	String level;
	String message;

    static constraints = {
    	level(nullable:false);
    	message(nullable:false);
    }
    
    static belongsTo = Notification;
    
    String toString() {
    	return "level[${level}] message[${message}]";
    }
}
