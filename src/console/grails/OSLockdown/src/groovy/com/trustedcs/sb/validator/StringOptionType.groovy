/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.validator;

import java.util.regex.Pattern;

/**
 * @author amcgrath
 *
 */
public class StringOptionType extends ProfileOptionType {
	
	int minLength = 1;
	int maxLength = Integer.MAX_VALUE;
	boolean isPassword;
	boolean isMultiline;
	Pattern pattern;
	
	/**
	 * Constructor
	 */
	StringOptionType() {
		type = "string";
	}
			
	/**
	 * @param value
	 * @param configurationMap 
	 */	
	boolean validate(def value, def configurationMap) {
		if ( minLength > value.length() || 
			 value.length() > maxLength ) {
			return false;
		}
		
		if ( pattern ) {
			def matching = ( value ==~ pattern ); 
			if ( !matching ) {
				return false;
			}
		}
		
		return true;
	}
	
	/**
	 * Display String
	 * @return a displayable string for the restrictions of the option
	 */
	String displayString() {
		def buf = "requires a String";		
		if ( pattern ) {
			buf += " that matches the regular expression of ${pattern}";			
		}
		else {
			if ( minLength > 0 ) {
	            buf += " with a minimum of ${minLength} character(s)";            
	        }       
	        if ( maxLength != Integer.MAX_VALUE ) {
	            if ( minLength > 0 ) {
	                buf += " and "
	            }
	            buf += "a maximum of ${maxLength} characters";
	        }
		}
		return buf;
	}
	
	/**
	 * @return a string representation of the object
	 */
	String toString() {
		return """String [$name]
  minLength[$minLength]
  maxLength[$maxLength]
  isPassword[$isPassword]
  isMultiline[$isMultiline]
  pattern[$pattern]
  enumList[$validValues]
		""";
	}

}
