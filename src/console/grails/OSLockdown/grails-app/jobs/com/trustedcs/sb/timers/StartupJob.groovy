/*
 * Original file generated in 2015 by Grails v2.3.7 under the Apache 2 License.
 * Modifications are Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.timers



class StartupJob {
    def group = "SBTimers"
    def periodicService
    
    static triggers = {
      simple repeatCount: 0, repeatInterval: 5000l // execute job once after a delay of 5 seconds
    }

    def concurrent = false

    def execute() {
        // execute job
        
        // Ok, try and start our regularly scheduled jobs....
        periodicService.initializeAllJobs()
    }
}
