/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

import com.trustedcs.sb.reports.assessment.*;
import org.apache.log4j.Logger;
import org.codehaus.groovy.grails.commons.ApplicationHolder;

/**
 * This class is responsible for merging a list of assessment reports into a group
 * report.
 * 
 * Proper usage of the class is demostrated in the test main function.
 */
class ReportMerger {
	 
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.reports.util.ReportMerger");
	 
    // mapping [clientName:assessmentReport]
    def reports = [:];
	 
    //mapping [moduleName:assessmentModule]
    def modules = [:];
	
    // missing reports
    def missingReports = [];
	
    /**
     * Method to merge together multiple assessment reports
     * @param locationMap [clientName<String>:locationPath<String>]
     */
    def merge( String groupName, String securityProfileName, def locationMap, File outputFile ) {
        m_log.info("merge started outputFile[${outputFile.absolutePath}]");
        def assessmentXml;
        def assessmentReport;
        def assessmentModule;
		 
        locationMap.each { clientName, assessmentFile ->
		 
            // slurp the document
            if ( assessmentFile?.exists() ) {
                assessmentXml = new XmlSlurper().parse(assessmentFile);
			 	
                // build the assessment report
                assessmentReport = new AssessmentReport(assessmentXml.report);
                assessmentReport.clientName = clientName;
                reports[clientName] = assessmentReport;
			 	
                // create the module map adding any modules that are not in exists already
                assessmentXml.modules.module.each {
                    // check if the module is already in the map
                    if ( !( modules.containsKey( it.@name.text() ) ) ) {
                        // create the module and add it to the map
                        assessmentModule = new AssessmentModule(it);
                        modules[assessmentModule.name] = assessmentModule;
                    }
			 		
                    // set the results for the client
                    modules[it.@name.text()].results[clientName] = it.@results.text();
                }
            }
        }
		 
        // create the builder
        def writer = new BufferedWriter(new FileWriter(outputFile));
        def builder = new groovy.xml.MarkupBuilder(writer);
		
        builder.GroupAssessmentReport(created:new Date().format("yyyy-MM-dd HH:mm:ss Z"),
            groupName:groupName,
            sbVersion:ApplicationHolder.application.metadata['app.version']) {
            reports() {
                reports.each { clientName, clientReport ->
                    report(created:clientReport.created,
                        profile:securityProfileName,
                        hostname:clientReport.hostname,
                        dist:clientReport.dist,
                        distVersion:clientReport.distVersion,
                        kernel:clientReport.kernel,
                        cpuInfo:clientReport.cpuInfo,
                        arch:clientReport.arch,
                        totalMemory:clientReport.totalMemory) {
                        description "${clientReport.description}"
                    }
                }
            }
            missing() {
                missingReports.each { missingReport ->
                    client(hostname:missingReport.clientName,
                        code:missingReport.code,
                        reason:missingReport.reasonPhrase);
                }
            }
            modules() {
                modules.each { moduleName , reportModule ->
                    module(name:moduleName,
                        severity:reportModule.severity,
                        severityLevel:reportModule.severityLevel) {
                        description "${reportModule.description}";
                        views() {
                            reportModule.views.each {
                                view "$it";
                            }
                        }
                        compliancy() {
                            reportModule.compliancyLineItems.each { item ->
								'line-item'(source:item.source,
                                    name:item.name,
                                    version:item.version,
                                    item:item.item);
                            }
                        }
                        clients() {
                            reportModule.results.each { clientName, result ->
                                client(name:clientName,
                                    hostname:reports[clientName].hostname,
                                    dist:reports[clientName].dist,
                                    distVersion:reports[clientName].distVersion,
                                    results:result);
                            }
                        }
                    }
                }
            }
        }
		
        m_log.info("Merge completed");
    }
	
    /**
     * Add a report that is missing for a given client.
     * @param name
     * @param code
     * @param reasonPhrase
     */
    void addMissing(String name, int code, String reasonPhrase) {
        MissingReport report = new MissingReport();
        report.clientName = name;
        report.code = code;
        report.reasonPhrase = reasonPhrase;
        missingReports << report;
    }
	
	
    /**
     * @param args
     */
    static void main(def args) {
        def clientLocationMap = [:];
        def file;
        args.each {
            file = new File(it);
            clientLocationMap[file.name.substring(0,file.name.length()-4)] = file.absolutePath
        }
        ReportMerger merger = new ReportMerger();
        def groupAssessment = merger.merge("exampleGroup",clientLocationMap,new File("group-assessment.xml"));
    }
}
