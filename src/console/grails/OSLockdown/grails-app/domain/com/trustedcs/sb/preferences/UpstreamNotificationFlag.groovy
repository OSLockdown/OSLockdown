/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.preferences;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.util.ConsoleTaskPeriodicity;

class UpstreamNotificationFlag {

    UpstreamNotificationTypeEnum upstreamNotificationType;
    Boolean enabled = false;
    ConsoleTaskPeriodicity periodicity = ConsoleTaskPeriodicity.DEFAULT
    
    static constraints = {
        upstreamNotificationType (nullable:false, unique:true);
        enabled (nullable:false)
        
    }
    
    static mapping = {
        autoTimestamp false
    }
    String toString()
    {
      return "id [$id] UpstreamNotificationTypeEnum[${upstreamNotificationType.getDisplayString()}] enabled[${enabled}] periodicity[${periodicity}]"
    }
}
