/*
 * Copyright 2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.scheduler;
import com.trustedcs.sb.web.pojo.Client;

class ClientCommStatus {

    String clientName;
    String lastState;
    Date lastCheck;
        
    // constraints
    static constraints = {
    	clientName(nullable: false, blank:false, unique:true)
        lastState( nullable:false, blank:false)
        lastCheck (nullable:true)
    }

    static mapping = {
        datasource 'memory'
    }
    
    String toString()
    {
      "Client ${clientName} lastCheck=${reachable} lastState=${lastReachble}"
    }
    
}         


