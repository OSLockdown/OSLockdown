/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

public class FileInfo {
	
	def path;
	def mode;
	def mtime;
    def uid;
    def suid;
    def gid;    
    def sgid;
    def xattr;
    def sha1;    

	/**
	 * Constructor
	 */
	public FileInfo() {
		
	}	
	
	public FileInfo(def node) {		
    	path = node.@path.text();
    	mode = node.@mode.text();
    	mtime = node.@mtime.text();
        uid = node.@uid.text();
        suid = node.@suid.text();
        gid = node.@gid.text();        
        sgid = node.@sgid.text();
        xattr = node.@xattr.text();
        sha1 = node.@sha1.text();
	}
	
	boolean equals (Object other) {
		// other object is null
		if ( null == other) {
			return false;
		}
		
		// other object isn't and instance of FileInfo
		if ( ! ( other instanceof FileInfo) ) {
			return false;
		}
		
		// properties comparison
		if ( path != other.path ) {
			return false;
		}
		
		if (mode != other.mode) {
			return false;
		}
		
        if ( mtime != other.mtime ) {
            return false;
        }		
		
		if ( uid != other.uid ) {
            return false;
        }
		
		if ( suid != other.suid ) {
			return false;
		}
			  
		if ( gid != other.gid ) {
			return false;
		}
		
		if ( sgid != other.sgid ) {
            return false;
        }
		
		if ( xattr != other.xattr ) {
            return false;
        }

		if ( sha1 != other.sha1 ) {
            return false;
        }
			
		return true;
	}	
}
