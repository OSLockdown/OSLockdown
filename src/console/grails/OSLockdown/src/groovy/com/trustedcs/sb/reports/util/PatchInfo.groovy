/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.reports.util

/**
 * @author amcgrath
 *
 */
public class PatchInfo {
    
    def name;
    def pkg;
    
    PatchInfo() {
        
    }
    
    PatchInfo(def node) {
        name = node.@name.text();
        pkg = node.@pkg.text();
    }
    
    boolean equals (Object other) {
        // other object is null
        if ( null == other) {
            return false;
        }
        
        // other object isn't and instance of PatchInfo
        if ( ! ( other instanceof PatchInfo) ) {
            return false;
        }
        
        // properties comparison
        if ( name != other.name ||              
             pkg != other.pkg) {
            return false;
        }
            
        return true;
    }       
}
