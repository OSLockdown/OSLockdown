/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.scheduler;

import org.apache.log4j.Logger;
import com.trustedcs.sb.scheduler.ClientTaskStatus

class ScheduledTaskStatus {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.scheduler.ScheduledTask");
	
    Long taskId
    Date expectedFireTime
    Long clientCount = 0
    
    // probably should have these as a separate table rather than two maps, but this is short term simple....
    Map clientStatus = [:]
    
    static hasMany = [clientStatus:ClientTaskStatus]
    
    static transients = ['clientCount']
      
    static mapping = {
        datasource 'memory'
        clientStatus cascade: "all-delete-orphan"
    }
    
    // constraints
    static constraints = {
    	taskId(nullable: false, blank:false, unique:true)
        expectedFireTime( nullable:false, blank:false)
        clientCount (nullable:true)
    }
    
    String toString()
    {
      "  Task=${taskId} Trigger=${expectedFireTime} ClientCount=${clientCount} Status -> ${clientStatus}"
    }
    
    def getClientCount() {
        return ScheduledTask.get(taskId)?.group?.clients.size() ?: 0
    }
}         


