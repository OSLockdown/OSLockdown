/*
 * Original file generated in 2012 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2012 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.util;

/**
 * @author rsanders
 *
 */
public enum AutoUpdateOptions {

    RELNUM("Release Number"),
    PKGVERS("Package Versions"),
    FORCE("Force");
    
    AutoUpdateOptions(String display) {
        displayString = display;        
    }
    
    private String displayString;
    
    public String getDisplayString() {
        return displayString;
    }    
    
    public static List<String> displayList() {
        ArrayList<String> list = new ArrayList<String>();
        for (AutoUpdateOptions option : AutoUpdateOptions.values()) {
            list.add(option.getDisplayString());
        }
        return list;
    }
    
    public static def displayMap() {
    	def map = [:];
        for (AutoUpdateOptions option : AutoUpdateOptions.values()) {
            map[option.ordinal()] = option.getDisplayString();
        }
        return map;
    }
    
    public static AutoUpdateOptions createEnum(String enumString) {
        if ( enumString.equals("Relese Number") ) {
            return AutoUpdateOptions.RELNUM;
        }
        else if ( enumString.equals("Package Versions") ) {
            return AutoUpdateOptions.PKGNUM;
        }
        else if ( enumString.equals("Force") ) {
            return AutoUpdateOptions.FORCE;
        }
        
        return null;
    }
    
    public static AutoUpdateOptions createEnum(int enumOrdinal) {
    	switch (enumOrdinal) {
    		case AutoUpdateOptions.RELNUM.ordinal():
    			return AutoUpdateOptions.RELNUM;
    			break;
    		case AutoUpdateOptions.PKGNUM.ordinal():
    			return AutoUpdateOptions.PKGNUM;
    			break;
    		case AutoUpdateOptions.FORCE.ordinal():
                return AutoUpdateOptions.FORCE;
                break;    			
            default:
            	return AutoUpdateOptions.RELNUM;
            	break;
    	}    	
    }
}
