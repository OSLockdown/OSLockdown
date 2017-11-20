/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.help;

import org.apache.log4j.Logger;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.xml.SBSchemaEntityResolver;

/**
 * @author amcgrath
 *
 */
public class OnlineHelp {
    static def m_log = Logger.getLogger("com.trustedcs.sb.help.OnlineHelp");
	
    static def moduleMap = [:];
    static def adminMap = [:];

    /**
     * Method to return the html anchor link for the requested module
     * @param moduleLibrary
     * @return the module's html help file
     */
    public static String moduleHtmlFile(String moduleLibrary) {
        if ( moduleLibrary ) {
            // lazy load due to grails requirements
            if ( !moduleMap ) {                
                try {
                    // parse the file
                    def slurper = new XmlSlurper(false,false);
                    // added to get rid of error due to CVE-2013-4590 fixes in Tomcat
                    slurper.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false)
                    slurper.setEntityResolver(new SBSchemaEntityResolver());
                    def xml = slurper.parse(SBFileSystemUtil.get(SB_LOCATIONS.MODULE_HELP_FILE));
                    xml.mapID.each {
                        moduleMap[it.@target.text()] = it.@url.text();
                    }
                }
                catch ( Exception e ) {
                    m_log.error("Unable to parse: ${SBFileSystemUtil.get(SB_LOCATIONS.MODULE_HELP_FILE)}",e);
                    return "index.html";
                }
            }
            return moduleMap[moduleLibrary];
        }
        else {
            return "index.html";
        }
    }
	
    /**
     * Method to return the html anchor link for the requested admin section
     * @param adminSection
     * @return the admin section html help file.
     */
    public static String adminHtmlFile(String adminSection) {
        m_log.debug ("requested[${adminSection}]");
        if ( adminSection ) {
            // lazy load due to grails requirements
            if ( !adminMap ) {                
                try {
                    // parse the file
                    def slurper = new XmlSlurper(false,false);
                    // added to get rid of error due to CVE-2013-4590 fixes in Tomcat
                    slurper.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false)
                    slurper.setEntityResolver(new SBSchemaEntityResolver());
                    def xml = slurper.parse(SBFileSystemUtil.get(SB_LOCATIONS.ADMIN_HELP_FILE));
                    xml.mapID.each {
                        adminMap[it.@target.text()] = it.@url.text();
                    }
                }
                catch ( Exception e ) {
                    m_log.error("Unable to parse: ${SBFileSystemUtil.get(SB_LOCATIONS.ADMIN_HELP_FILE)}");
                    m_log.error(e.message);
                    return "index.html";
                }
            }            
            return adminMap[adminSection];
        }
        else {
            return "index.html";
        }
    }
	
}
