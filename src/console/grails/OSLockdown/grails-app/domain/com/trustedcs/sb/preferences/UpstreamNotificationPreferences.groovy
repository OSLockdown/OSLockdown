/*
 *Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.preferences;
import com.trustedcs.sb.util.SyslogAppenderLevel;
import com.trustedcs.sb.util.SyslogFacility;

class UpstreamNotificationPreferences {

    // Where to send 
    String syslogHost = "localhost";
    
    // What port to use
    Integer syslogPort = 514;
    
    // What facility to use
    SyslogFacility syslogFacility = SyslogFacility.LOG_USER;
    Boolean syslogEnabled = false
    
    // When was the last time we changed....
    Date lastChanged=new Date();

    static constraints = {
        syslogHost(nullable:false, maxsize:100);
        syslogFacility(nullable:false, maxsize:100);
        syslogPort(min:1,max:65536)
        syslogEnabled(nullable:false)
    }
    static mapping = {
        autoTimestamp false
    }
    String toString()
    {
      return "id [$id]  syslogHost[$syslogHost] syslogFacility[$syslogFacility] syslogEnabled[$syslogEnabled] "
    }
}
