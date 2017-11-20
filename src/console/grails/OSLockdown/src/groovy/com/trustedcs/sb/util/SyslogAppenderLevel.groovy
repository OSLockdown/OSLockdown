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
 * @author amcgrath
 *
 */
public enum SyslogAppenderLevel {

    OFF("Off", 1),
    FATAL("Fatal", 2),
    ERROR("Error", 3),
    WARN("Warn", 4) ,
    INFO("Info", 5),
    DEBUG("Debug", 6),
    TRACE("Trace", 7),
    ALL("All", 8),
    
    String levelStr;
    int rank;
    
    SyslogAppenderLevel(String levelStr, int rank)
    {
      this.levelStr = levelStr
      this.rank = rank
    }  
    String toString() {
        return this.levelStr
    }

    String getKey() {
        name()
    }

    static SyslogAppenderLevel byLevelStr(String enumString) {
        values().find {it.levelStr == enumString}
    }
     
    int rank() {
        return rank;
    }
}
