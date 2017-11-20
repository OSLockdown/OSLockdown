/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util

public class PackageInfo {
	
    def name;
    def release;    
    def version;
    def installLocaltime;
    def installTime;    
    def epoch;
    def summary;	

	PackageInfo() {
		
	}
	
	PackageInfo(def node) {
		name = node.@name.text();
		epoch = node.@epoch.text();
		version = node.@version.text();
		release = node.@release.text();
		installTime = node.@installtime.text();
		installLocaltime = node.@install_localtime.text();
		summary = node.@summary.text();
	}
	
    boolean equals (Object other) {
        // other object is null
        if ( null == other) {
            return false;
        }
        
        // other object isn't and instance of PackageInfo
        if ( ! (other instanceof PackageInfo) ) {
            return false;
        }
        
        // properties comparison
        if ( name != other.name ||        		
             version != other.version) {
            return false;
        }
            
        return true;
    }   	
}
