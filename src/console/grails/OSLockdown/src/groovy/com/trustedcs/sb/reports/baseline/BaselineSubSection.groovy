/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.reports.baseline

/**
 * @author amcgrath
 *
 */
public class BaselineSubSection {

	enum SubSectionType { 
        FILES, CONTENT, PACKAGES, PATCHES   
    }

	String name;
	String fingerprint = 'xx';	 
	SubSectionType type;	
	def children = [];
	
	BaselineSubSection(def documentSubSection) {
		name = documentSubSection.@name.text();
		fingerprint = documentSubSection.@fingerprint.text();
		if ( documentSubSection.packages.size() > 0 ) {
			type = SubSectionType.PACKAGES;
		}
		else if ( documentSubSection.patches.size() > 0 ) {
			type = SubSectionType.PATCHES;
		}
		else if ( documentSubSection.content.size() > 0 ) {
			type = SubSectionType.CONTENT;
		}
		else if ( documentSubSection.files.size() > 0 ) {
			type = SubSectionType.FILES;
			documentSubSection.files.each { file ->
				children << file.@path.text();
			}
		}
	}
	
	/**
	 * Returns a string representation of the object
	 */
	String toString() {
		return """subsection[@name=$name @fingerprint=$fingerprint]
  $type
  $children
"""
	}
	
	/**
	 * Comparison Method
	 * @param other
	 */
	boolean equals(Object other) {
		if ( other == null ) {
			return false;
		}
		if ( !(other instanceof BaselineSubSection) ) {			
			return false;
		}
		if ( name != other.name) {			
			return false;
		}
		if ( fingerprint != other.fingerprint ) {			
			return false;
		}
		return true;
	}
}
