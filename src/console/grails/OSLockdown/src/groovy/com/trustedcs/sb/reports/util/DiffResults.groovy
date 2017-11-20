/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

public class DiffResults {
	boolean hasChanged = false;
	def added = [];	
	def changed = [];
	def removed = [];

	/**
	 * Constructor
	 */
	public DiffResults() {
		
	}	
	
	boolean deltaExists() {
		if ( hasChanged ) {
			return true;
		}		
		if ( added.size() > 0 ) {
			return true;
		}
        if ( changed.size() > 0 ) {
            return true;
        }
        if ( removed.size() > 0 ) {
            return true;
        }        
        return false;
	}
}
