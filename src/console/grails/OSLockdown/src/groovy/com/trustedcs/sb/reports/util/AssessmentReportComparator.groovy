/*
 * Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

import groovy.util.slurpersupport.GPathResult;
import org.codehaus.groovy.grails.commons.ApplicationHolder;
import com.trustedcs.sb.reports.assessment.*;
import org.apache.log4j.Logger;

/**
 * @author amcgrath
 *
 */
public class AssessmentReportComparator {

    private static Logger m_log =
    Logger.getLogger("com.trustedcs.sb.reports.util.AssessmentReportComparator");    
	
    // map total
    LinkedHashMap moduleMap;
	
    // first report
    GPathResult oldAssessmentXML;
    LinkedHashMap oldAssessmentMap;
	
    // second report
    GPathResult newAssessmentXML;
    LinkedHashMap newAssessmentMap;
	
    /**
     * Constructor
     * @param oldReport location of the old report ( string path )
     * @param newReport location of the new report ( string path )
     */
    AssessmentReportComparator(String oldReport, String newReport) {
        init(oldReport,newReport);      
    }
    
    /**
     * Constructor
     * @param oldReport file location
     * @param newReport file location
     */
    AssessmentReportComparator(File oldReport, File newReport) {
        init(oldReport,newReport);  
    }
    
    /**
     * Init method using file paths as strings
     * @param oldReport
     * @param newReport
     */
    private init(String oldReport, String newReport) {
        init ( new File(oldReport), new File(newReport) ); 
    }
    
    /**
     * Init method using file objects
     * @param oldReport
     * @param newReport
     */
    private init(File oldReport, File newReport ) {
    	// total map
    	moduleMap = new LinkedHashMap();
    	
    	// old report
        oldAssessmentXML = new XmlSlurper().parse(oldReport);
        oldAssessmentMap = new LinkedHashMap();
        oldAssessmentXML.modules.module.each { xmlModule -> 
            oldAssessmentMap[xmlModule.@name.text()] = xmlModule.@results.text();
            if ( !moduleMap.containsKey(xmlModule.@name.text()) ) {
                moduleMap[xmlModule.@name.text()] = new AssessmentModule(xmlModule);
            }
        }
        m_log.debug("old assessment module count = ${oldAssessmentMap.size()}");
        
        // new report
        newAssessmentXML = new XmlSlurper().parse(newReport);
        newAssessmentMap = new LinkedHashMap();
        newAssessmentXML.modules.module.each { xmlModule -> 
            newAssessmentMap[xmlModule.@name.text()] = xmlModule.@results.text();
            if ( !moduleMap.containsKey(xmlModule.@name.text()) ) {
                moduleMap[xmlModule.@name.text()] = new AssessmentModule(xmlModule);
            }
        }
        m_log.debug("new assessment module count = ${newAssessmentMap.size()}");
    }
    
    /**
     * @param outputFile
     */
    public void deltaReport(File outputFile) {
    	// removed from old report
    	def removedModules = oldAssessmentMap.keySet() - newAssessmentMap.keySet();
    	m_log.info("removed modules = ${removedModules.size()}");
    	removedModules.each { moduleName ->
            m_log.debug( moduleName );
    	}    	
    	
    	// added to old report
        def addedModules = newAssessmentMap.keySet() - oldAssessmentMap.keySet();
    	m_log.info("added modules = ${addedModules.size()}");
    	addedModules.each { moduleName ->
            m_log.debug( moduleName );
    	}
    	
    	// common modules
    	def commonModules = oldAssessmentMap.keySet() - removedModules;
    	m_log.debug("common modules = ${commonModules.size()}");
        
        // same | different
        def unchangedModules = [];
        def changedModules = [];
        commonModules.each { moduleName ->
            if ( oldAssessmentMap[moduleName] == newAssessmentMap[moduleName] ) {
                unchangedModules << moduleName;
            }
            else {
                changedModules << moduleName;
            }
        }
        
        // Look for any modules that just failed, but were not 'failed' before.  This will
        // catch places where a Module was just added.
        def newFailures = [];
        newAssessmentMap.keySet().each { moduleName -> 
            def thisVal = newAssessmentMap[moduleName];
            def lastVal = oldAssessmentMap.get(moduleName, 'NoValue')
            if (thisVal == 'Fail' && lastVal != 'Fail') 
            {
                newFailures << moduleName;
            }
        }
        
        // Look for any modules that errored.
        def errors = [];
        newAssessmentMap.keySet().each { moduleName -> 
            if (newAssessmentMap[moduleName] == 'Error')
            {
                errors << moduleName;
            }
        }
        
        
        m_log.debug( "unchanged modules = ${unchangedModules.size()}" );
        m_log.debug( "changed modules = ${changedModules.size()}" );
        
        def writer = new BufferedWriter(new FileWriter(outputFile));
        def builder = new groovy.xml.MarkupBuilder(writer);
        
        // xml document creation        
        builder.AssessmentReportDelta(created:new Date().format(ReportsHelper.CREATED_DATE_FORMAT),
            sbVersion:ApplicationHolder.application.metadata['app.version']) {
            // report 1
            report(profile:oldAssessmentXML.report.@profile.text(),
                hostname:oldAssessmentXML.report.@hostname.text(),
                dist:oldAssessmentXML.report.@dist.text(),
                distVersion:oldAssessmentXML.report.@distVersion.text(),
                kernel:oldAssessmentXML.report.@kernel.text(),
                cpuInfo:oldAssessmentXML.report.@cpuInfo.text(),
                arch:oldAssessmentXML.report.@arch.text(),
                totalMemory:oldAssessmentXML.report.@totalMemory.text(),
                created:oldAssessmentXML.report.@created.text());
            // report 2
            report(profile:newAssessmentXML.report.@profile.text(),
                hostname:newAssessmentXML.report.@hostname.text(),
                dist:newAssessmentXML.report.@dist.text(),
                distVersion:newAssessmentXML.report.@distVersion.text(),
                kernel:newAssessmentXML.report.@kernel.text(),
                cpuInfo:newAssessmentXML.report.@cpuInfo.text(),
                arch:newAssessmentXML.report.@arch.text(),
                totalMemory:newAssessmentXML.report.@totalMemory.text(),
                created:newAssessmentXML.report.@created.text());
            // added modules
            added() {
                addedModules.each { moduleName ->
                    def assessmentModule = moduleMap[moduleName];
                    module(name:moduleName,
                        results:newAssessmentMap[moduleName],
                        severity:assessmentModule.severity,
                        severityLevel:assessmentModule.severityLevel) {
                        description(assessmentModule.description)
                        views() {
                            assessmentModule.views.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            assessmentModule.compliancyLineItems.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.version,
                                    item:lineItem.item)
                            }
                        }
                    }
                }
            }
            // removed modules
            removed() {
                removedModules.each { moduleName ->
                    def assessmentModule = moduleMap[moduleName];
                    module(name:moduleName,
                        results:oldAssessmentMap[moduleName],
                        severity:assessmentModule.severity,
                        severityLevel:assessmentModule.severityLevel) {
                        description(assessmentModule.description)
                        views() {
                            assessmentModule.views.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            assessmentModule.compliancyLineItems.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.version,
                                    item:lineItem.item)
                            }
                        }
                    }
                }
            }
            // changed modules
            changed() {
                changedModules.each { moduleName ->
                    def assessmentModule = moduleMap[moduleName];
                    module(name:moduleName,
                        resultsA:oldAssessmentMap[moduleName],
                        resultsB:newAssessmentMap[moduleName],
                        severity:assessmentModule.severity,
                        severityLevel:assessmentModule.severityLevel) {
                        description(assessmentModule.description)
                        views() {
                            assessmentModule.views.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            assessmentModule.compliancyLineItems.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.version,
                                    item:lineItem.item)
                            }
                        }
                    }
                }
            }
            // unchanged modules
            unchanged() {
                unchangedModules.each { moduleName ->
                    def assessmentModule = moduleMap[moduleName];
                    module(name:moduleName,
                        results:oldAssessmentMap[moduleName],
                        severity:assessmentModule.severity,
                        severityLevel:assessmentModule.severityLevel) {
                        description(assessmentModule.description)
                        views() {
                            assessmentModule.views.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            assessmentModule.compliancyLineItems.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.version,
                                    item:lineItem.item)
                            }
                        }
                    }
                }
            }
            // anything worthy of an upstream notification (new findings/errors)
            upstreamSummary(
               modulesRun:newAssessmentMap.size(),
               addedCount:addedModules.size(),
               removedCount:removedModules.size(),
               changedCount:changedModules.size(),
               failuresCount:newFailures.size(),
               errorsCount:errors.size())
        }
    }

    
    /**
     * Main method for testing
     * @param args
     * <p> args[0] the 'older' baseline</p>
     * <p> args[1] the 'newer' baseline</p>
     * <p> args[2] if specified this will be the output file</p>
     */
    static void main(args) {        
        AssessmentReportComparator comparator = new AssessmentReportComparator(args[0],args[1]);
        def outputFile;
        if ( args.size() > 2 ) {
            outputFile = new File(args[2]);
        } 
        else {          
            outputFile = File.createTempFile("assessment-compare-temp",".xml");
        }
        comparator.deltaReport(outputFile);
    }
}
