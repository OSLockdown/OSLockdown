/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
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
public class BaselineSection{
	
	String name;
	def subsections = [:];

	/**
	 * Constructor
	 * @param documentSection
	 */
	BaselineSection( def documentSection ) {
		name = documentSection.@name.text();
		def subsection;
		documentSection.subSection.each {
			subsection = new BaselineSubSection(it);
			subsections[subsection.name] = subsection;
		}
	}
	
	String toString() {
		return """section(@name=$name)
  $subsections
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
        if ( !(other instanceof BaselineSection) ) {
            return false;
        }
        if ( name != other.name) {
            return false;
        }
        if ( subsections.keySet() != other.subsections.keySet() ) {
        	return false;
        }
        subsections.each { subsectionName, subsection ->
        	if ( subsection != other.subsections[subsectionName] ) {
        		return false;
        	}
        }        
        return true;
    }	
}
