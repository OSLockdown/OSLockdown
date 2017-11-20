/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata

class CommonPlatformEnumeration implements Serializable, Comparable {
    // attributes
    String part;
    String vendor;
    String product;
    String productVersion;
    
    static hasMany = [modules:SecurityModule];

    static belongsTo = SecurityModule;

    static constraints = {        
        productVersion(unique:['part','vendor','product']);
    }
    
    String toString() {
        return "cpe:/"+part+":"+vendor+":"+product+":"+productVersion
    }
    
    /**
     * Comparable interface method
     */
    int compareTo(Object o) {
    	
        if ( o instanceof CommonPlatformEnumeration ) {
        	def cpe = (CommonPlatformEnumeration)o;
        	if ( cpe.part != part ) { 
        		return part.compareTo( cpe.part );
        	}
        	if ( cpe.vendor != vendor ) {
        		return vendor.compareTo( cpe.vendor );
        	}
        	if ( cpe.product != product ) {
        		return product.compareTo( cpe.product );
        	}
        	if ( cpe.productVersion != productVersion ) {
        		return productVersion.compareTo( cpe.productVersion);
        	}
        }
        else {
        	throw new ClassCastException("A CommonPlatformEnumeration object expected.");
        }
        return 0;         
    }

    // Define equals() for remove() to work
    boolean equals( Object o )
    {
        if ( o instanceof CommonPlatformEnumeration ) {
            def cpe = (CommonPlatformEnumeration) o;
            return id == cpe.id;
        }
        else {
            return false;
        }
    }
}
