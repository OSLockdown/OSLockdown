/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.validator;

import org.apache.log4j.Logger;

/**
 * @author amcgrath
 *
 */
public class NumberOptionType extends ProfileOptionType {
	
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.validator.NumberOptionType");    
	
    def precision;
    def min;
    def max;
	
    /**
     * Constructor
     */
    NumberOptionType() {
        type = 'number';
    }
	
    /**
     * @param value
     * @param configurationMap
     */
    boolean validate(def value, def configurationMap) {
    	m_log.info("VALIDATION LOGIC [${value}] "+this.toString());
    	def val;
        try {
            if ( precision.equalsIgnoreCase('integer') ) {
                val = value.toInteger();
            }
            else if ( precision.equalsIgnoreCase('long') ) {
                val = value.toLong();
            }
        } 
        catch ( Exception e ) {
            m_log.error("Invalid number type",e);
            m_log.info(" ----- VALIDATION FAILED ----- ");
            return false;
        }

    	if ( min ) {
            if ( !(min.validate(val,configurationMap,precision)) ) {
                m_log.info(" ----- VALIDATION MIN FAILED ----- ");
                return false;
            }            
        }

        if ( max ) {
            if ( !(max.validate(val,configurationMap,precision)) ) {
                m_log.info(" ----- VALIDATION MAX FAILED ----- ");
                return false;
            }
        }
    	
        m_log.info(" +++++ VALIDATION PASSED +++++ ");
        return true;
    }
    
    /**
     * @returns the display error string for the validation type
     */
    String displayString() {
        def buf = "requires ";
        if ( precision.equalsIgnoreCase("integer")) {
            buf += "an Integer ";
        }
        else {
            buf += "a Long ";
        }
        if ( min || max ) {
            buf += "which is "
        }
    	
        if ( min ) {
            // text for inclusivity
            if ( min.isInclusive ) {
                buf += "greater than or equal to ";
            }
            else {
                buf += "greater than ";
            }
            // text for value
            if ( min.hasExternalReference() ) {
                buf += min.moduleRef + "." + min.optionRef;
            }
            else {
                buf += min.value;
            }
        }
    	
        if ( min && max ) {
            buf += " and ";
        }
    	
        if ( max ) {
            // text for inclusivity
            if ( max.isInclusive ) {
                buf += "less than or equal to ";
            }
            else {
                buf += "less than ";
            }
            // text for value
            if ( max.hasExternalReference() ) {
                buf += max.moduleRef + "." + max.optionRef;
            }
            else {
                buf += max.value;
            }
        }
        return buf;
    }
    
    /**
     * @return a string representation of the object
     */
    String toString() {
        return """Number [$name]
  precision[$precision]
  min[$min]
  max[$max]  
        """;
    }

}
