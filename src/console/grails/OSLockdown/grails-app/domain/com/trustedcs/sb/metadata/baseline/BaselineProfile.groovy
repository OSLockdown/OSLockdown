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

import org.apache.log4j.Logger;
import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;

class BaselineProfile implements Serializable {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.metadata.baseline.BaselineProfile");
    private static final def specialCharList = [
' ','\\(','\\)','\\\\','/',':',';',
'#','\\*','\\?','<','>','\\|','@',
'\\!','\\$','\'','\"','\\^'];

    // Attributes
    String name;
    String fileName;
    String summary = "";
    String description = "";
    String comments = "";
    boolean writeProtected = false;

    // key "${module.id}_${suboption.id}"
    HashMap<String,String> subOptionValues = new HashMap<String,String>();
    
    int estimatedReportSize;
    BigDecimal estimatedForensicImportance;
    BigDecimal estimatedSystemLoad;

    static transients = ['estimatedReportSize','estimatedForensicImportance','estimatedSystemLoad'];

    static hasMany = [baselineModules:BaselineModule];
    SortedSet baselineModules;

    static constraints = {
        name(maxSize:30,blank:false,nullable:false,unique:true)
        summary(nullable:true);
    	description(nullable:true);
    	comments(nullable:true);
        // Require BaselineProfile to have at least one BaselineModule. Need nullable:false to handle
        // the creation case (as in that case minSize:1 is not validated !!!)
        baselineModules(nullable:false,minSize:1);
    }

    int getEstimatedReportSize() {
        int total = 0;
        baselineModules?.each { baselineModule ->
            total += baselineModule.avgKbPerReport;
        }
        return total;
    }

    BigDecimal getEstimatedForensicImportance() {
        int total = 0;
        baselineModules?.each { baselineModule ->
            total += baselineModule.getForensicImportanceInteger();
        }
        if ( baselineModules ) {
            total /= baselineModules.size();
        }
        return total;
    }

    BigDecimal getEstimatedSystemLoad() {
        int total = 0;
        baselineModules?.each { baselineModule ->
            total += baselineModule.getSystemLoadImpactInteger();
        }
        if ( baselineModules ) {
            total /= baselineModules.size();
        }
        return total;
    }
}
