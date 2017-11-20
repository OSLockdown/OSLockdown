/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.validator;

import java.util.regex.Pattern;

/**
 * @author amcgrath
 *
 */
public class ProfileOptionsValidator {
	
    // singleton instance
    private static ProfileOptionsValidator instance;
	
    // option type mapping name -> object
    def optionTypes = [:];
	
    /**
     * Private Constructor
     */
    private ProfileOptionsValidator() {
				
    }
	
    /**
     * Singleton fetch
     */
    static ProfileOptionsValidator getInstance() {
        if ( !instance ) {
            instance = new ProfileOptionsValidator();
        }
        return instance;
    }
	
    /**
     * @param file
     */
    void loadConfiguration(def file) throws Exception {
		
        def profileOptionType;
		
        try {
            def slurpedConfig = new XmlSlurper().parse(file);
            for ( optionType in slurpedConfig.optionType ) {
                for ( numberType in optionType.number ) {
                    // number type
                    profileOptionType = new NumberOptionType();
                    // name
                    profileOptionType.name = optionType.@name.text();
                    // precision
                    profileOptionType.precision = numberType.@precision.text();
                    // range
                    if ( numberType.range ) {
                        if ( numberType.range.min.size() > 0 ) {
                            profileOptionType.min = new NumberOptionRestriction(value:numberType.range.min.@value.text(),
                                isMin:true,
                                moduleRef:numberType.range.min.@moduleRef.text(),
                                optionRef:numberType.range.min.@optionRef.text(),
                                isInclusive:numberType.range.min.@inclusive.text().toBoolean());
                            if ( profileOptionType.precision.equalsIgnoreCase("integer") ) {
                                profileOptionType.min.value = numberType.range.min.@value.text().toInteger();
                            }
                            else if ( profileOptionType.precision.equalsIgnoreCase("long") ) {
                                profileOptionType.min.value = numberType.range.min.@value.text().toLong();
                            }
                        }
                        if ( numberType.range.max.size() > 0 ) {
                            profileOptionType.max = new NumberOptionRestriction(value:numberType.range.max.@value.text(),
                                isMin:false,
                                moduleRef:numberType.range.max.@moduleRef.text(),
                                optionRef:numberType.range.max.@optionRef.text(),
                                isInclusive:numberType.range.max.@inclusive.text().toBoolean());
                            if ( profileOptionType.precision.equalsIgnoreCase("integer") ) {
                                profileOptionType.max.value = numberType.range.max.@value.text().toInteger();
                            }
                            else if ( profileOptionType.precision.equalsIgnoreCase("long") ) {
                                profileOptionType.max.value = numberType.range.max.@value.text().toLong();
                            }
                        }
                    }
                    // enum
                    for ( enumOption in numberType.enumList.enum ) {
                        profileOptionType.validValues << new OptionEnum(value:enumOption.@value.text(),displayString:enumOption.text());
                    }
                }
                for ( stringOption in optionType.string ) {
                    // string type
                    profileOptionType = new StringOptionType();
                    // name
                    profileOptionType.name = optionType.@name.text();
                    // is multiline
                    profileOptionType.isMultiline = stringOption.@multiLine.text().toBoolean();
                    // is password
                    profileOptionType.isPassword = stringOption.@password.text().toBoolean();
                    // min length
                    if ( stringOption.@minLength.text() ) {
                        profileOptionType.minLength = stringOption.@minLength.text().toInteger();
                    }
                    // max length
                    if ( stringOption.@maxLength.text() ) {
                        profileOptionType.maxLength = stringOption.@maxLength.text().toInteger();
                    }
                    // pattern
                    if ( stringOption.regexp.@value.text() ) {
                        profileOptionType.pattern = Pattern.compile(stringOption.regexp.@value.text());
                    }
                    // enum
                    for ( enumOption in stringOption.enumList.enum ) {
                        profileOptionType.validValues << new OptionEnum(value:enumOption.@value.text(),displayString:enumOption.text());
                    }
                }
                optionTypes[profileOptionType.name] = profileOptionType;
            }
        }
        catch ( Exception e ) {
            throw e;
        }
		
    }
	
    /**
     * Creates a string represenation of the object
     */
    String toString() {
        def buf = "";
        optionTypes.each { name, option ->
            buf += option.toString();
            buf += "\n";
        }
        return buf;
    }

    /**
     * @param args
     */
    static void main(def args) {
        def validator = ProfileOptionsValidator.getInstance();
        validator.loadConfiguration(args[0]);
        println validator;
    }
	
}
