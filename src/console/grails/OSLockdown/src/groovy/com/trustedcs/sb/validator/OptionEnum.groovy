/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.validator



/**
 * @author amcgrath
 *
 */
public class OptionEnum {	
	def value;
	def moduleRef;
	def optionRef;
	def displayString;
	
	String toString() {
		return "value[$value] moduleRef[$moduleRef] optionRef[$optionRef] displayString[$displayString]"
	}
}
