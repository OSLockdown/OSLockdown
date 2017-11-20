/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

/* example xml
    <section name="Network" pyModulePath="Network">
*/

package com.trustedcs.sb.metadata.baseline;

class BaselineSection implements Serializable, Comparable {

    // properties
    String name;
    String pyModulePath;

    // has many
    static hasMany = [baselineModules:BaselineModule];
    SortedSet baselineModules;
    
    // constraints
    static constraints = {
        name(nullable:false, blank:false);
        pyModulePath(nullable:false, blank:false);
    }

    /**
     * Return a domain class for the passed in xml
     * @param node
     */
    public static BaselineSection fromXml(def node) {
        // parameters map used to create the object
        def parameters = [:];

        // properties
        parameters['name'] = node.@name.text();
        parameters['pyModulePath'] = node.@pyModulePath.text();

        // create the domain class with the parameters map
        def baselineSection = new BaselineSection(parameters);

        def baselineModule;
        node.module.each { moduleXml ->
            baselineModule = BaselineModule.fromXml(moduleXml);
            baselineSection.addToBaselineModules(baselineModule);
        }

        return baselineSection;
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
}
