/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata;

import org.apache.log4j.Logger;
import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;

import com.trustedcs.sb.metadata.util.SbProfileHelper;

class Profile implements Serializable, Cloneable {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.metadata.Profile");

    // Attributes
    String name;
    String fileName;
    String shortDescription = "";
    String description = "";
    String comments = "";
    boolean writeProtected = false;

    // modules that are assoicated with the profile
    static hasMany = [securityModules:SecurityModule];
    // the modules should be a sorted set ( comparator sorts by name )
    SortedSet securityModules;

    // options associated with each of the modules
    // [${module.id}.${option.id}:value]
    HashMap<String,String> optionValues = new HashMap<String,String>();

    // constraints
    static constraints = {
        name(maxSize:50,blank:false,nullable:false,unique:true)
    	description(nullable:true);
    	shortDescription(nullable:true);
    	comments(nullable:true);
    }

    /**
     * Pretty string for displaying contents of the object
     *
     * @returns string represenation of the object
     */
    String toString() {
    	return name;
    }

    /**
     * Debug String of the object that contains more detailed information than
     * just the name
     *
     * @returns debug level string representation of the object
     */
    String toDebugString() {
    	return "name ${name}\nmodules ${securityModules}\nvalues ${optionValues}";
    }
}
