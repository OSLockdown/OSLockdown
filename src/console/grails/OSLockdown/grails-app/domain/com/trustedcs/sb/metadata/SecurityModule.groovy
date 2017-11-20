/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata;

class SecurityModule implements Comparable, Serializable {
    
    // attributes
    String name;    
    String library;
    String description = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.";
    int scanWeight;
    int actionWeight;
    int severityLevel;    
    Boolean ignoreLegacyOptions;
    
    // relationships
    List options;
    static hasMany = [cpes:CommonPlatformEnumeration,
        compliancies:Compliancy,
        moduleTags:ModuleTag,
        options:ModuleOption,
        libraryDependencies:ModuleLibraryDependency]; 
        
    static mapping = {
        // 1-to-Many relationships : This allows removal by simply removing the object from the below list.
        options cascade: "all-delete-orphan"
        libraryDependencies cascade: "all-delete-orphan"

        // Many-to-Many relationships : This allows removal by simply removing the object from the below list.
        cpes cascade: "all-delete-orphan"
        compliancies cascade: "all-delete-orphan"
        moduleTags cascade: "all-delete-orphan"
    }

    // SecurityModuleGroup moduleGroup;

    // constraints
    static constraints = {
        name(blank:false,unique:true);
        library(blank:false);
        description(nullable:true,blank:true)
        scanWeight(range:1..10);
        actionWeight(range:1..10);
        severityLevel(range:1..10); 
        ignoreLegacyOptions(nullable:true)               
    }
    
    /**
     * Comparable interface method to make it so that the modules will
     * show up in order base on their name.
     * 
     */
    int compareTo(Object o) {
    	if ( o instanceof SecurityModule ) {
            return name.compareTo( ((SecurityModule)o).name );
    	}    	
    	throw new ClassCastException("A SecurityModule object expected."); 
    }
    
    /**
     * Returns a string representation of the module
     */
    String toString() {
        return name;
    }

    // Define equals() for contains() to work
    boolean equals( Object o )
    {
        if ( o instanceof SecurityModule ) {
            def securityModule = (SecurityModule) o;
            return id == securityModule.id;
        }
        else {
            return false;
        }
    }
}
