/*
 * Copyright 2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.util;

/**
 *
 */
public enum SyslogFacility {

    LOG_USER  ("USER"),
    LOG_LOCAL0("LOCAL0"),
    LOG_LOCAL1("LOCAL1"),
    LOG_LOCAL2("LOCAL2"),
    LOG_LOCAL3("LOCAL3"),
    LOG_LOCAL4("LOCAL4"),
    LOG_LOCAL5("LOCAL5"),
    LOG_LOCAL6("LOCAL6"),
    LOG_LOCAL7("LOCAL7")

    String facility

    SyslogFacility(String facility) {
        this.facility = facility;
    }
    
    static SyslogFacility byName(String name) {
        values().find {it.facility == name}
    }        
    
    String toString() {
        facility
    }

    static SyslogFacility byFacility(String enumString) {
        values().find {it.facility == enumString}
    }
    
    String getKey() {
        name()
    }
}
