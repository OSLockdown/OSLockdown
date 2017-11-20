/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.notifications;

import com.trustedcs.sb.web.notifications.NotificationTypeEnum;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;

class Notification implements Serializable {
	
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.web.notifications.Notification");
	
    Date timeStamp;
    int type;
    String info;
    boolean successful;
    Boolean hasFileName;
    Integer sourceId;
    boolean aborted;
    String transactionId;
    Map dataMap;
    
    static hasMany = [exceptions:NotificationException];

    static constraints = {
    	info(nullable:true);
    	dataMap(nullable:true);    	
    	transactionId(nullable:true);
        successful(nullable:false)
        aborted(nullable:false)
        hasFileName(nullable:true)
        sourceId(nullable:true)
    }
    
    String toString() {
    	def str = "\n";
    	str += "date[${timeStamp}]\n";
    	str += "type["+typeAsString()+"]\n";
    	str += "info[${info}]\n";
    	str += "successful[${successful}]\n";
    	str += "aborted[${aborted}]\n";
    	str += "transactionId[${transactionId}]\n";
        str += "sourceId[${sourceId}]\n";
        str += "hasFileName[${hasFileName}]\n";
    	str += "dataMap ->\n"
        dataMap.each { key,value ->
            str += "  ${key}[${value}]\n";
    	}
    	str += "exceptions ->\n";
    	exceptions.each { exception ->
            str += "  ${exception}\n"
    	}    	
    	return str;
    }
    
    /**
     * Returns the type of the notification as a string using the 
     * notification type enum class
     */
    String typeAsString() {    	
    	return NotificationTypeEnum.getDisplayString(type);
    }
    
    String sourceAsString() {
        // def source;
        def name = "Unknown";
    	try {
            def enumType = NotificationTypeEnum.getEnumFromOrdinal(type);
	    	
            switch( enumType ) {
                case NotificationTypeEnum.GROUP_ASSESSMENT:
                    // source = "Group";
                    if ( sourceId ) {
                        def group = Group.get(sourceId.toLong());
                        if ( group ) {
                            name = group.name;
                        }
                        else {
                            name = "Unknown"
                        }
                    }
                    break;
                default:
                    // source = "Client";
                    if ( sourceId && Client.exists(sourceId.toLong())  ) {
                        def client = Client.get(sourceId.toLong());
                        if ( client ) {
                            name = client.name;
                        }
                        else {
                            name = "Unknown"
                        }
                    }
                    break;
            }
    	}
    	catch ( Exception e ) {
            e.printStackTrace();
            return "Unknown";
    	}
    	// return "${source} : ${name}";
    	return name;
    }
}
