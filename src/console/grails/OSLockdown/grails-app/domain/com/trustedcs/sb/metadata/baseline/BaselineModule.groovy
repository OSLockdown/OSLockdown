/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.metadata.baseline;

/**
<module name="Routing"  pyModulePath="Network/Routing">
<info>
<description>Provide a description of the module like netstat -rn</description>
<reportSubtitle>Output of netstat</reportSubtitle>
<storageSpecs sizeCategory='Small' avgKbPerReport='20'/>
<systemLoadImpact value='Low'/>
<forensicsImportance value='High'/>
<help uri="/OSLockdown/help/NetworkRouting.html"/>
</info>
<parameter optionType="None"/>
</module>
 */
class BaselineModule implements Serializable, Comparable {

    // module properties
    String name;
    String pyModulePath;

    // info properties
    String description;
    String reportSubtitle;
    String sizeCategory;
    int avgKbPerReport;
    String systemLoadImpact;
    String forensicsImportance;
    String helpId;
    
    // parameter
    String optionType;

    //
    // Note: baselineModule.subOptions are not set since they are not in the baselines-modules.xml
    // (but they are still in the baseline-profile.xml and should probably be removed from there).
    //
    // has many
    static hasMany = [subOptions:BaselineSuboption];
    SortedSet subOptions;

    static transients = ['systemLoadImpactInteger','forensicImportanceInteger'];

    // constraints
    static constraints = {
        // module properties
        name(nullable:false, blank:false );
        pyModulePath(nullable:false, blank:false );

        // info properties
        description(nullable:false, blank:false );
        reportSubtitle(nullable:false, blank:false );
        sizeCategory(nullable:false, blank:false );
        avgKbPerReport(nullable:false, min:0);
        systemLoadImpact(nullable:false, blank:false );
        forensicsImportance(nullable:false,blank:false );
        helpId ( nullable:false, blank:false );
        
        // parameter
        optionType(nullable:false, blank:false );
    }

    Integer getSystemLoadImpactInteger() {
        return levelStringToInteger(systemLoadImpact);
    }

    Integer getForensicImportanceInteger() {
        return levelStringToInteger(forensicsImportance);
    }

    public static Integer levelStringToInteger(String level) {
        Integer integerResult = 0;
        if ( level.equalsIgnoreCase("high") ) {
            integerResult = 3;
        }
        else if ( level.equalsIgnoreCase("medium") ) {
            integerResult = 2;
        }
        else if ( level.equalsIgnoreCase("low") ) {
            integerResult = 1;
        }
        return integerResult;
    }

    /**
     * Return a domain class for the passed in xml
     * @param node
     */
    public static BaselineModule fromXml(def node) {
        // parameters map used to create the object
        def parameters = [:];

        // module properties
        parameters['name'] = node.@name.text();
        parameters['pyModulePath'] = node.@pyModulePath.text();

        // info properties
        def infoNode = node.info;
        parameters['description'] = infoNode.description.text();
        parameters['reportSubtitle'] = infoNode.reportSubtitle.text();
        parameters['sizeCategory'] = infoNode.storageSpecs.@sizeCategory.text();
        parameters['avgKbPerReport'] = infoNode.storageSpecs.@avgKbPerReport.text();
        parameters['systemLoadImpact'] = infoNode.systemLoadImpact.@value.text();
        parameters['forensicsImportance'] = infoNode.forensicsImportance.@value.text();
        parameters['helpId'] = infoNode.help.@uri.text();

        // optionType
        parameters['optionType'] = node.parameter.@optionType.text();

        // create the domain class with the parameters map
        def baselineModule = new BaselineModule(parameters);

        def baselineSuboption;
        node.subOption.each { subOptionXml ->
            baselineSuboption = BaselineSuboption.fromXml(subOptionXml);
            baselineModule.addToSubOptions(baselineSuboption);
        }
        return baselineModule;
    }

    /**
     * Comparable interface method to make it so that the modules will
     * show up in order base on their name.
     *
     */
    public int compareTo(Object o) {
    	if ( o instanceof BaselineModule ) {
            return name.compareTo( ((BaselineModule)o).name );
    	}
    	throw new ClassCastException("A BaslineModule object expected.");
    }

    // Define equals() for contains() to work
    boolean equals( Object o )
    {
        if ( o instanceof BaselineModule ) {
            def baselineModule = (BaselineModule) o;
            return id == baselineModule.id;
        }
        else {
            return false;
        }
    }
}
