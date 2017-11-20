/*
 * Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
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
public enum LoggingLevel {

    EMERG("Emergency"),
    ALERT("Alert"),
    CRIT("Critical"),
    ERR("Error"),
    WARNING("Warning"),
    NOTICE("Notice"),
    INFO("Info"),
    DEBUG("Debug");
    
    LoggingLevel(String display) {
        displayString = display;        
    }
    
    private String displayString;
    
    public String getDisplayString() {
        return displayString;
    }    
    
    public String toString() {
        return displayString;
    }
    
    public static List<String> displayList() {
        ArrayList<String> list = new ArrayList<String>();
        for (LoggingLevel level : LoggingLevel.values()) {
            list.add(level.getDisplayString());
        }
        return list;
    }
    
    public static def displayMap() {
    	def map = [:];
        for (LoggingLevel level : LoggingLevel.values()) {
            map[level.ordinal()] = level.getDisplayString();
        }
        return map;
    }
    
    static LoggingLevel byName(String enumString) {
        values().find {it.displayString == enumString}
    }
    
    String getKey() {
        name() 
    }
    
    public static LoggingLevel createEnum(String enumString) {
        if ( enumString.equals("Emergency") ) {
            return LoggingLevel.EMERG;
        }
        else if ( enumString.equals("Alert") ) {
            return LoggingLevel.ALERT;
        }
        else if ( enumString.equals("Critical") ) {
            return LoggingLevel.CRIT;
        }
        else if ( enumString.equals("Error") ) {
            return LoggingLevel.ERR;
        }
        else if ( enumString.equals("Warning") ) {
            return LoggingLevel.WARNING;
        }
        else if ( enumString.equals("Notice") ) {
            return LoggingLevel.NOTICE;
        }
        else if ( enumString.equals("Info") ) {
            return LoggingLevel.INFO;
        }
        else if ( enumString.equals("Debug") ) {
            return LoggingLevel.DEBUG;
        }
        return null;
    }
    
    public static LoggingLevel createEnum(int enumOrdinal) {
    	switch (enumOrdinal) {
    		case LoggingLevel.EMERG.ordinal():
    			return LoggingLevel.EMERG;
    			break;
    		case LoggingLevel.ALERT.ordinal():
    			return LoggingLevel.ALERT;
    			break;
    		case LoggingLevel.CRIT.ordinal():
                return LoggingLevel.CRIT;
                break;    			
	        case LoggingLevel.ERR.ordinal():
                return LoggingLevel.ERR;
                break;	        	
	        case LoggingLevel.WARNING.ordinal():
                return LoggingLevel.WARNING;
                break;	        	
	        case LoggingLevel.NOTICE.ordinal():
                return LoggingLevel.NOTICE;
                break;	        	
	        case LoggingLevel.INFO.ordinal():
                return LoggingLevel.INFO;
                break;	        	
	        case LoggingLevel.DEBUG.ordinal():
                return LoggingLevel.DEBUG;
                break;
            default:
            	return LoggingLevel.EMERG;
            	break;
    	}    	
    }
}
