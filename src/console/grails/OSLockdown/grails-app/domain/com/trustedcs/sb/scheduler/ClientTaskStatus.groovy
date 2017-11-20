/*
 * Modifications are Copyright 2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.scheduler;


class ClientTaskStatus {
    Date lastUpdateTime
    Integer lastStatus
    
    static mapping = {
        datasource 'memory'
    }
    
    static constraints = {
        lastUpdateTime(nullable:false)
        lastStatus(nullable:false)
    }
    
    String toString()
    {
      return "Time ${lastUpdateTime} Status ${lastStatus}"
    }
}
