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

/**
 * @author amcgrath
 *
 */
public abstract class ProfileOptionType {
	// name of the type
	def name;
	def type;
	
	// list of valid values for the parameter
	def validValues = [];

	/**
	 * Interface method for validating the parameter
	 * @param value
	 * @param configurationMap
	 */
	abstract boolean validate(def value, def configurationMap);
	
	abstract String displayString();
}
