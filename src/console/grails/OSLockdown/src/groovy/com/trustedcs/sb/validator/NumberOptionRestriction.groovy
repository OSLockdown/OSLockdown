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

import com.trustedcs.sb.metadata.SecurityModule;
import com.trustedcs.sb.metadata.ModuleOption;
import org.apache.log4j.Logger;

/**
 * @author amcgrath
 *
 */
public class NumberOptionRestriction {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.validator.NumberOptionRestriction");

    def moduleRef;
    def optionRef;
    def value;
    def isInclusive = true;
    def isMin;    
     
    /**
     * If the min or max requires an external reference
     */
    boolean hasExternalReference() {
        return moduleRef && optionRef ? true : false;
    }
     
    /**
     * @param val
     */
    boolean validate(def val, def configurationMap, def precision) {
    	 
        def module;
        def option;
        def refValue;
    	 
        // find the value of the external reference
        if ( hasExternalReference() ) {
            module = SecurityModule.findByName(moduleRef);
            option = ModuleOption.findByName(optionRef);            
            
            if ( precision.equalsIgnoreCase('integer') ) {
                refValue = configurationMap[module.id+'.'+option.id]?.toInteger();
            }
            else if ( precision.equalsIgnoreCase('long') ) {
                refValue = configurationMap[module.id+'.'+option.id]?.toLong();
            }

            m_log.info("External Reference value [${refValue}]");
        }
         
        if ( isMin ) {
            // min
            if ( isInclusive ) {
                if ( hasExternalReference() ) {
                    return val >= refValue;
                }
                else {
                    return val >= value;
                }
            }
            else {
                if ( hasExternalReference() ) {
                    return val > refValue;
                }
                else {
                    return val > value;
                }
            }
        }
        else {
            // max
            if ( isInclusive ) {
                if ( hasExternalReference() ) {
                    return val <= refValue;
                }
                else {
                    return val <= value;
                }
            }
            else {
                if ( hasExternalReference() ) {
                    return val < refValue;
                }
                else {
                    return val < value;
                }
            }
        }
        return true;
    }
     
    /**
     * @return a string representation of the object
     */
    String toString() {
        return "isMin[$isMin] isInclusive[$isInclusive] value[$value] moduleRef[$moduleRef] optionRef[$optionRef]";
    }
}
