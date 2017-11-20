/*
 * Copyright 2013-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo;

import org.apache.log4j.Logger;

class InFlight implements Serializable {

    static def m_log = Logger.getLogger("com.trustedcs.sb.web.pojo.InFlight");

    String transactionID;
    String action;
    Date startTime;
    Date endTime;
    
    static constraints = {
        transactionID(blank:false, unique:true);
        action(blank:false);
    }


    String toString() {
    	return "id [$transactionID] action [$action] start[$start] endTime[$endTime]";
    }
}
