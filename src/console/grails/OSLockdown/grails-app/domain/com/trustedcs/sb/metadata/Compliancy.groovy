/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata

class Compliancy implements Serializable 
{
    // attributes
    String source;
    String name;
    String compVersion;
    String item;
    String option;
    
    static hasMany = [modules:SecurityModule];

    static belongsTo = SecurityModule;

    static constraints = {
        item(unique:['source','name','compVersion']);
    }   

    String toString() {
        return ("$source $name ($compVersion): $item");
    }
    
    /**
     * Comparable interface method
     */
    int compareTo(Object o) {
        
        if ( o instanceof Compliancy ) {
            def compliancy = (Compliancy)o;
            if ( compliancy.source != source ) { 
                return source.compareTo( compliancy.source );
            }
            if ( compliancy.name != name ) {
                return name.compareTo( compliancy.name );
            }
            if ( compliancy.compVersion != compVersion ) {
                return compVersion.compareTo( compliancy.compVersion );
            }
            if ( compliancy.item != item ) {
                return item.compareTo( compliancy.item);
            }
            if ( compliancy.option != option ) {
                return option.compareTo( compliancy.option);
            }            
        }
        else {
            throw new ClassCastException("A Compliancy object expected.");
        }
        return 0;         
    }

    // Define equals() for remove() to work
    boolean equals( Object o )
    {
        if ( o instanceof Compliancy ) {
            def compliancy = (Compliancy) o;
            return id == compliancy.id;
        }
        else {
            return false;
        }
    }
}
