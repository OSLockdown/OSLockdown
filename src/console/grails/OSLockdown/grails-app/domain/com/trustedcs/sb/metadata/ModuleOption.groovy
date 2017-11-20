/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata

class ModuleOption implements Serializable, Comparable {
    String name;
    String description;
    String defaultValue = "";
    String type;
    String unit;    
    
    static belongsTo = SecurityModule;
    
    static constraints = {
    
    }
    
    String toString() {
        "name[$name] description[$description] type[$type] unit[$unit] default[$defaultValue]"
    }
    
    /**
     * Comparable interface method
     */
    int compareTo(Object o) {
        
        if ( o instanceof ModuleOption ) {
            def moduleOption = (ModuleOption)o;
            if ( moduleOption.name != name ) { 
                return name.compareTo( moduleOption.name );
            }
        }
        else {
            throw new ClassCastException("A ModuleOption object expected.");
        }
        return 0;         
    }

    // Define equals() for remove() to work
    boolean equals( Object o )
    {
        if ( o instanceof ModuleOption ) {
            def moduleOption = (ModuleOption)o;
            return id == moduleOption.id;
        }
        else {
            return false;
        }
    }
}
