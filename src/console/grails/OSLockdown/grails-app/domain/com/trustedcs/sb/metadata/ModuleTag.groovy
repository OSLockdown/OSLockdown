/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata;

class ModuleTag implements Serializable, Comparable {    
    String name;
    
    static hasMany = [modules:SecurityModule];

    static belongsTo = SecurityModule;

    static constraints = {
        name(unique:true,blank:false);
    }   
    
    String toString() {
        return name;
    }
    
    /**
     * Comparable interface method
     */
    int compareTo(Object o) {
        
        if ( o instanceof ModuleTag ) {
            def tag = (ModuleTag)o;
            if ( tag.name != name ) { 
                return name.compareTo( tag.name );
            }
        }
        else {
            throw new ClassCastException("A ModuleTag object expected.");
        }
        return 0;         
    }

    // Define equals() for remove() to work
    boolean equals( Object o )
    {
        if ( o instanceof ModuleTag ) {
            def moduleTag = (ModuleTag) o;
            return id == moduleTag.id;
        }
        else {
            return false;
        }
    }
}
