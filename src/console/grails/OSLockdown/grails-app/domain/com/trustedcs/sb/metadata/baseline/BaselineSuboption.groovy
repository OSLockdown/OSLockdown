/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata.baseline

/**
<subOption name="POSIX ACLs" paramName="posixAcls"/>
 */
//
// Note: baselineModule.subOptions are not set since they are not in the baselines-modules.xml
// (but they are still in the baseline-profile.xml and should probably be removed from there).
//
class BaselineSuboption implements Serializable, Comparable {

    // suboption properties
    String name;
    String paramName;

    // one to many
    static belongsTo = [BaselineModule];

    // constraints
    static constraints = {
        name(nullable:false, blank:false );
        paramName(nullable:false, blank:false );
    }

    /**
     * Return a domain class for the passed in xml
     * @param node
     */
    public static BaselineSuboption fromXml(def node) {
        // parameters map used to create the object
        def parameters = [:];

        // properties
        parameters['name'] = node.@name.text();
        parameters['paramName'] = node.@paramName.text();

        // create the domain class with the parameters map
        def baselineSuboption = new BaselineSuboption(parameters);

        return baselineSuboption;
    }

    /**
     * Comparable interface method to make it so that the modules will
     * show up in order base on their name.
     *
     */
    public int compareTo(Object o) {
    	if ( o instanceof BaselineSuboption ) {
            return name.compareTo( ((BaselineSuboption)o).name );
    	}
    	throw new ClassCastException("A BaselineSuboption object expected.");
    }

    // Define equals() for remove() to work
    boolean equals( Object o )
    {
        if ( o instanceof BaselineSuboption ) {
            def subOption = (BaselineSuboption) o;
            return id == subOption.id;
        }
        else {
            return false;
        }
    }
}
