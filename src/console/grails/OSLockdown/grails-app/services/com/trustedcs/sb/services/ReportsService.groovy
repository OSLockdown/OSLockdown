/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import com.trustedcs.sb.exceptions.ReportsCommunicationException;
import com.trustedcs.sb.exceptions.ReportsException;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;

import com.trustedcs.sb.reports.util.ReportsHelper;
import com.trustedcs.sb.reports.util.ReportType;
import com.trustedcs.sb.reports.util.AssessmentReportComparator;
import com.trustedcs.sb.reports.util.BaselineReportComparator;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.notification.OSLockdownNotificationEvent;
import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.web.notifications.NotificationTypeEnum;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;

import com.trustedcs.sb.util.SyslogAppenderLevel;


class ReportsService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ReportsService");

    // transactional
    boolean transactional = false;

    // injected services
    def messageSource;
    def reportsCommunicationService;
    def auditLogService;
    def upstreamNotificationService;

    /**
     * Returns the report map for the given client and report type
     *
     * @param clientInstance
     * @param reportType
     * @param useFileSystem
     * @throw ReportsException
     */
    def getReportMap(Client clientInstance, ReportType reportType, boolean useFileSystem) throws ReportsException {
        def reportMap = new TreeMap();
        if ( useFileSystem ) {
            // grab local files from disk if there are any
            File  clientDirectory = getReportDirectory(clientInstance,reportType);
            // check to see if the directory exists
            if ( clientDirectory.exists() ) {
                // find all the xml files in the directory
                clientDirectory.eachFileMatch(~/.*\.xml/) { file ->
                    // parse the file name into a date and set the map
                    reportMap[file.name] = ReportsHelper.parseFilename(reportType,file.name);
                }
            }
        }
        else {
            // communicate with the client
            def reportFilenameList = [];
            try {
                // get the report list from the reports communication service
                switch ( reportType ) {
                    // assessments
                    case ReportType.ASSESSMENT:
                    case ReportType.ASSESSMENT_FAILURES:
                        reportFilenameList = reportsCommunicationService.listAssessments(clientInstance);
                        break;
                    case ReportType.BASELINE:
                        reportFilenameList = reportsCommunicationService.listBaselines(clientInstance);
                        break;
                    case ReportType.APPLY:
                        reportFilenameList = reportsCommunicationService.listApplies(clientInstance);
                        break;
                    case ReportType.UNDO:
                        reportFilenameList = reportsCommunicationService.listUndos(clientInstance);
                        break;
                    default:
                        break;
                }
                // create a map from the report list
                reportFilenameList.each { fileName ->
                    reportMap[fileName] = ReportsHelper.parseFilename(reportType,fileName);
                }
            }
            catch( ReportsCommunicationException reportsException ) {
                // throw a report exception due to communication issues
                throw new ReportsException(message:reportsException.message);
            }
        }
        // return the map
        return reportMap;
    }

    /**
     * @param groupInstance
     * @param reportType
     * @throw ReportsException
     */
    def getReportMap(Group groupInstance, ReportType reportType) {
        // the map to return
        def reportMap = new TreeMap();
        // grab local files from disk if there are any
        File  groupDirectory = getReportDirectory(groupInstance,reportType);
        // check to see if the directory exists
        if ( groupDirectory.exists() ) {
            // find all the xml files in the directory
            groupDirectory.eachFileMatch(~/.*\.xml/) { file ->
                // parse the file name into a date and set the map
                reportMap[file.name] = ReportsHelper.parseFilename(reportType,file.name);
            }
        }
        // return the group report mapping
        return reportMap;
    }

    /**
     * Method used by stand alone mode to find the mapping of file name to
     * a useable date format displayed to the user based on the file type.
     *
     * Comparisons and basic reports use different parsing for the their
     * names.
     *
     * @param reportType
     */
    def getReportMap(ReportType reportType) {
        // the sorted map
        def reportMap = new TreeMap();
        // location of the files
        File directory = getReportDirectory(reportType);

        // check to see if the directory exists
        if ( directory.exists() ) {
            // find all the xml files in the directory
            directory.eachFileMatch(~/.*\.xml/) { file ->
                // parse the file name into a date and set the map
                reportMap[file.name] = ReportsHelper.parseFilename(file.name);
                // switch on report type
                switch ( reportType ) {
                    case ReportType.ASSESSMENT_COMPARISON:
                    case ReportType.BASELINE_COMPARISON:
                    // comparisons
                    reportMap[file.name] = ReportsHelper.parseComparisonFilename(file.name);
                    break;
                    case ReportType.PROFILE_COMPARISON:
                    reportMap[file.name] = ReportsHelper.parseProfileComparisonFilename(file.name);
                    break;
                    default:
                    // normal reports
                    reportMap[file.name] = ReportsHelper.parseFilename(file.name);
                    break;
                }
            }
        }
        // return the map
        return reportMap;
    }

    /**
     * Returns the directory for the report type from the local disk
     * Standalone
     *
     * @param reportType
     */
    File getReportDirectory(ReportType reportType) {
        // location of the files
        File directory;
        // switch on report type
        switch ( reportType ) {
            // assessments
            case ReportType.ASSESSMENT:
            case ReportType.ASSESSMENT_FAILURES:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.ASSESSMENTS);
                break;
            // assessment comparisons
            case ReportType.ASSESSMENT_COMPARISON:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.ASSESSMENT_COMPARISONS);
                break;
            // profile comparisons
            case ReportType.PROFILE_COMPARISON:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.PROFILE_COMPARISONS);
                break;
            // baselines
            case ReportType.BASELINE:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.BASELINES);
                break;
            // baseline comparisons
            case ReportType.BASELINE_COMPARISON:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_COMPARISONS);
                break;
            case ReportType.APPLY:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.APPLIES);
                break;
            case ReportType.UNDO:
                directory = SBFileSystemUtil.get(SB_LOCATIONS.UNDOS);
                break;
        }
        // create the directory if it doesn't exist
        if ( !directory.exists() ) {
            if ( !directory.mkdirs() ) {
                m_log.error("Unable to create directory ${directory.absolutePath}");
            }
        }
        // return the directory
        return directory;
    }

    /**
     * Returns the directory for the combination of client and report type
     *
     * @param client
     * @param reportType
     */
    File getReportDirectory(Client clientInstance, ReportType reportType) {
        // client directory root
        File clientDirectory = SBFileSystemUtil.getClientDirectory(clientInstance.id);
        // report directory
        File reportDirectory;
        switch ( reportType ) {
            // assessments
            case ReportType.ASSESSMENT:
            case ReportType.ASSESSMENT_FAILURES:
                reportDirectory = new File(clientDirectory,"assessments");
                break;
            // baselines
            case ReportType.BASELINE:
                reportDirectory = new File(clientDirectory,"baselines");
                break;
            case ReportType.APPLY:
                reportDirectory = new File(clientDirectory,"apply-reports");
                break;
            case ReportType.UNDO:
                reportDirectory = new File(clientDirectory,"undo-reports");
                break;
            default:
                m_log.error("Client Report Type not recognized :${reportType}");
                break;
        }
        // create the directory if it doesn't exist
        if ( !reportDirectory.exists() ) {
            if ( !reportDirectory.mkdirs() ) {
                m_log.error("Unable to create directory ${reportDirectory.absolutePath}");
            }
        }
        // return the reports directory for the client
        return reportDirectory;
    }

    /**
     * Returns the report directory for the given group and repor type
     * combination
     *
     * @param groupInstance
     * @param reportType
     */
    File getReportDirectory(Group groupInstance, ReportType reportType) {
        // client directory root
        File groupDirectory = SBFileSystemUtil.getGroupDirectory(groupInstance.id);
        // report directory
        File reportDirectory;
        switch ( reportType ) {
            // assessments
            case ReportType.GROUP_ASSESSMENT:
            reportDirectory = new File(groupDirectory,"assessments");
            break;
            case ReportType.GROUP_ASSET:
            reportDirectory = new File(groupDirectory,"assets");
            break;
            default:
            m_log.error("Group Report Type not recognized :${reportType}");
            break;
        }
        // create the directory if it doesn't exist
        if ( !reportDirectory.exists() ) {
            if ( !reportDirectory.mkdirs() ) {
                m_log.error("Unable to create directory ${reportDirectory.absolutePath}");
            }
        }
        // return the reports directory for the client
        return reportDirectory;
    }

    /**
     * Retrieves the report based on type and report name from the local disk
     *
     * @param reportType
     * @param reportName
     */
    File getReport(ReportType reportType, String reportName) {
        // get the directory for the report
        File reportDirectory = getReportDirectory(reportType);
        // find the file name in question
        File reportFile = new File(reportDirectory,reportName);
    }

    /**
     * Retrieves the latest report based on the report type and the client
     * that was passed into the method.  This method should only be called for
     * assessments and baselines.
     *
     * @param client
     * @param reportType
     * @param useFileSystem
     */
    File getLatestReport(Client client, ReportType reportType, boolean useFileSystem) throws ReportsException {
        // should we only use the files already on the console in order
        // to find the latest report
        Date newest;
        Date date;
        File latestFile;

        // use the file system to find the latest client
        if ( useFileSystem ) {
            // get the report directory
            File directory = getReportDirectory(client,reportType);
            // look at all the xml files
            directory.eachFileMatch(~/.*\.xml/) { file ->
                // convert the file name into a date object
                date = ReportsHelper.createDateFromFilename(file.name);
                // compare the date with that of the most recent
                if ( newest == null || date > newest ) {
                    // if the date is more recently then what was the previous
                    // most recent assign the newest to the new date and the
                    // file associated with that date to the latest file
                    newest = date;
                    latestFile = file;
                }
            }
        }
        else {
            // get the list of reports from the client
            try {
                def reportList = [];
                switch ( reportType ) {
                    case ReportType.ASSESSMENT :
                        reportList = reportsCommunicationService.listAssessments(client);
                        break;
                    case ReportType.BASELINE :
                        reportList = reportsCommunicationService.listBaselines(client);
                        break;
                    case ReportType.APPLY :
                        reportList = reportsCommunicationService.listApplies(client);
                        break;
                    case ReportType.UNDO :
                        reportList = reportsCommunicationService.listUndos(client);
                        break;
                    default:
                        throw new ReportsException(message:"Invalid report type for latest report request");
                }
                String latestReportName;
                reportList.each { reportName ->
                    // convert the file name into a date object
                    date = ReportsHelper.createDateFromFilename(reportName);
                    // compare the date with that of the most recent
                    if ( newest == null || date > newest ) {
                        // if the date is more recently then what was the previous
                        // most recent assign the newest to the new date and the
                        // file associated with that date to the latest file
                        newest = date;
                        latestReportName = reportName;
                    }
                }

                if( latestReportName ){
                    // get the latest file from the client
                    latestFile = getReport(client,reportType,latestReportName);
                }
            }
            catch ( ReportsCommunicationException communicationException) {
                throw new ReportsException(message:communicationException.message);
            }
        }

        if( !latestFile ) {
            // No reports are available for this Client either on the Client box or the Console's file system, which is possible
            // if no respective action has been run yet
            String errorMessage = messageSource.getMessage("reports.latestreport.error", [reportType.getDisplayString()] as Object[], null)
            throw new ReportsException(message:errorMessage);
        }

        // return the latest file
        return latestFile;
    }

    /**
     * Retrieves the report based on the type, report name and the client first from the local disk (if found) and otherwise from the remote location
     *
     * @param client
     * @param reportType
     * @param reportName
     * @throws ReportsException
     */
    File getReport(Client client, ReportType reportType, String reportName) throws ReportsException {
        return getReport( client, reportType, reportName, true );
    }

    /**
     * Retrieves the report based on the type, report name and the client from
     * either the local disk or from the remote location
     *
     * @param client
     * @param reportType
     * @param reportName
     * @param useFileSystemFirst - if true (default) fetch the file from Console's file system; otherwise fetch from Client
     * @throws ReportsException
     */
    File getReport(Client client, ReportType reportType, String reportName, boolean useFileSystemFirst) throws ReportsException {
        // the report file
        File reportFile;

        if( useFileSystemFirst ){
            // attempt to file the report file locally
            File reportDirectory = getReportDirectory(client,reportType);
            reportFile = new File(reportDirectory,reportName);
            if ( reportFile.exists() ) {
                return reportFile;
            }
        }

        // get the file from the client
        try {
            switch ( reportType ) {
                case ReportType.ASSESSMENT :
                case ReportType.ASSESSMENT_FAILURES :
                    reportFile = reportsCommunicationService.getAssessment(client,reportName);
                    break;
                case ReportType.BASELINE:
                    reportFile = reportsCommunicationService.getBaseline(client,reportName);
                    break;
                case ReportType.APPLY :
                    reportFile = reportsCommunicationService.getApply(client,reportName);
                    break;
                case ReportType.UNDO :
                    reportFile = reportsCommunicationService.getUndo(client,reportName);
                    break;
                default:
                    break;
            }
        }
        catch ( ReportsCommunicationException communicationException ) {
            throw new ReportsException(message:communicationException.message);
        }
        return reportFile;
    }

    /**
     * Retrieves the report based on the report type, the group and the report
     * name.
     *
     * @param groupInstance
     * @param reportType
     * @param reportName
     */
    File getReport(Group groupInstance, ReportType reportType, String reportName) throws ReportsException {
        // report directory
        File reportDirectory = getReportDirectory(groupInstance,reportType);
        // report file location
        File reportFile = new File(reportDirectory,reportName);
        // if the file exists return the file
        if ( reportFile.exists() ) {
            return reportFile;
        }
        else {
            // file doesn't exist
            throw new ReportsException(message:"${reportFile.absolutePath} does not exist");
        }
    }

    /**
     * Creates a comparison report using the two passed in report files. The manner
     * in which the comparison file is created is determined by the comparison type
     *
     * @param comparisonType
     * @param reportType
     * @param reportFile1
     * @param reportFile2
     */
    File createComparison(ReportType comparisonType, ReportType reportType,
        String report1, String report2) throws ReportsException {

        // output filename
        String comparisonName = ReportsHelper.getComparisonName(comparisonType,report1,report2);
        // check to see if the comparison already exists
        File outputFile = findExistingComparison(comparisonType,comparisonName);
        if ( outputFile ) {
            m_log.info("Comparison already exists ${outputFile.absolutePath}");
            return outputFile;
        }
        String outputFilename = ReportsHelper.getComparisonFilename(comparisonName);

        // output file
        outputFile = getReport(comparisonType,outputFilename);

        // report file locations
        File report1File = getReport(reportType,report1);
        File report2File = getReport(reportType,report2);

        // generate the comparison
        return createComparison(comparisonType,report1File,report2File,outputFile);
    }

    /**
     * Enterprise service method for creating comparison reports based on client,
     * report and comparison type.
     *
     * @param comparisonType
     * @param reportType
     * @param client1
     * @param report1
     * @param client2
     * @param report2
     */
    File createComparison(ReportType comparisonType, ReportType reportType,
        Client client1, String report1,
        Client client2, String report2) throws ReportsException {

        // output filename ( does not include .xml extension )
        String comparisonName = ReportsHelper.getComparisonName(comparisonType,
            client1,report1,
            client2,report2);

        // check to see if the comparison already exists
        File outputFile = findExistingComparison(comparisonType,comparisonName);
        if ( outputFile ) {
            m_log.info("Comparison already exists ${outputFile.absolutePath}");
            return outputFile;
        }

        // get the comparison as an xml file name
        String outputFilename = ReportsHelper.getComparisonFilename(comparisonName);

        // output file object for the new comparison
        outputFile = getReport(comparisonType,outputFilename);

        // report file locations
        m_log.info("client1[${client1.name}] report1[${report1}] client2[${client2.name}] report2[${report2}]");
        File client1File = getReport(client1,reportType,report1);
        File client2File = getReport(client2,reportType,report2);

        // generate the comparison
        return createComparison(comparisonType,client1File,client2File,outputFile);
    }

    /**
     * Creates a comparison report using the two passed in report files. The manner
     * in which the comparison file is created is determined by the comparison type
     *
     * @param comparisonType
     * @param reportType
     * @param reportFile1
     * @param reportFile2
     */
    File createComparisonFromScheduledTask(ReportType comparisonType, ReportType reportType,
        String report1, String report2) throws ReportsException {

        // output filename
        String comparisonName = ReportsHelper.getComparisonName(comparisonType,report1,report2);
        // check to see if the comparison already exists
        File outputFile = findExistingComparison(comparisonType,comparisonName);
        if ( outputFile ) {
            m_log.info("Comparison already exists ${outputFile.absolutePath}");
            return outputFile;
        }
        String outputFilename = ReportsHelper.getComparisonFilename(comparisonName);

        // output file
        outputFile = getReport(comparisonType,outputFilename);

        // report file locations
        File report1File = getReport(reportType,report1);
        File report2File = getReport(reportType,report2);

        // generate the comparison
        return createComparison(comparisonType,report1File,report2File,outputFile);
    }

    /**
     * Enterprise service method for creating comparison reports based on client,
     * report and comparison type.
     *
     * @param comparisonType
     * @param reportType
     * @param client1
     * @param report1
     * @param client2
     * @param report2
     */
    File createComparisonFromScheduledTask(ReportType comparisonType, ReportType reportType,
        Client client1, String report1,
        Client client2, String report2) throws ReportsException {

        // output filename ( does not include .xml extension )
        String comparisonName = ReportsHelper.getComparisonName(comparisonType,
            client1,report1,
            client2,report2);

        // check to see if the comparison already exists
        File outputFile = findExistingComparison(comparisonType,comparisonName);
        if ( outputFile ) {
            m_log.info("Comparison already exists ${outputFile.absolutePath}");
            return outputFile;
        }

        // get the comparison as an xml file name
        String outputFilename = ReportsHelper.getComparisonFilename(comparisonName);

        // output file object for the new comparison
        outputFile = getReport(comparisonType,outputFilename);

        // report file locations
        m_log.info("client1[${client1.name}] report1[${report1}] client2[${client2.name}] report2[${report2}]");
        File client1File = getReport(client1,reportType,report1);
        File client2File = getReport(client2,reportType,report2);

        // generate the comparison
        return createComparison(comparisonType,client1File,client2File,outputFile);
    }

    /**
     * Creates a comparison report using the two passed in report files. The manner
     * in which the comparison file is created is determined by the comparison type
     *
     * @param comparisonType
     * @param reportFile1
     * @param reportFile2
     * @param outputFile
     */
    File createComparison(ReportType comparisonType, File reportFile1, File reportFile2, File outputFile) throws ReportsException {

        // check to see if the two report files exist
        if ( reportFile1?.exists() && reportFile2?.exists() ) {
            // TODO: comparison creation based on comparisonType
            switch ( comparisonType ) {
                case ReportType.ASSESSMENT_COMPARISON:
                AssessmentReportComparator comparator = new AssessmentReportComparator(reportFile1,reportFile2);
                comparator.deltaReport(outputFile);
                break;
                case ReportType.BASELINE_COMPARISON:
                BaselineReportComparator comparator = new BaselineReportComparator(reportFile1,reportFile2);
                comparator.deltaReport(outputFile);
                break;
                case ReportType.PROFILE_COMPARISON:
                break;
                default:
                throw new ReportsException("Comparison type [${comparisonType}] not recognized")
            }
        }
        else {
            throw new ReportsException("Requested reports were unable to be retrieved or are missing");
        }
        // logger
        auditLogService.logReport("add",comparisonType.displayString,outputFile.name);
        // return the output file
        return outputFile;
    }

    /**
     * If there is an existing report for this comparision then we return the
     * already existing comparison.
     *
     * @param reportType
     * @param comparisonName
     */
    File findExistingComparison(ReportType reportType, String comparisonName) {
        File reportsDirectory = getReportDirectory(reportType);
        File reportFile = null;
        for ( String filename : reportsDirectory.list() ) {
            if ( filename.startsWith(comparisonName) ) {
                reportFile = new File(reportsDirectory,filename);
                break;
            }
        }
        return reportFile;
    }


    String generateComparisonFromScheduledTask( OSLockdownNotificationEvent event) {
        String[] splits = event.transactionId.split(":");
        String outputName;
        ReportType comparisonType;
        ReportType reportType;
        NotificationTypeEnum actionType = NotificationTypeEnum.values()[event.getActionType()]
        
        // This routine should not ever throw an exception itself, just log if SomethingHappened.
        try {
            if ( splits ) {
                def sourceId = splits[1];                                                                                                                                                                                                                                                                                                                 
                def clientInstance = Client.get(sourceId)                                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                                                                          
                switch ( event.getActionType()) {                                                                                                                                                                                                                                                  
                    case NotificationTypeEnum.SCHEDULED_SCAN.ordinal() :                                                                                                                                                                                                                                                                                  
                        comparisonType = ReportType.ASSESSMENT_COMPARISON;                                                                                                                                                                                                                                                                                
                        reportType = ReportType.ASSESSMENT;                                                                                                                                                                                                                                                                                               
                        break                                                                                                                                                                                                                                                                                                                             
                    case NotificationTypeEnum.SCHEDULED_BASELINE.ordinal() :                                                                                                                                                                                                                                                                              
                        comparisonType = ReportType.BASELINE_COMPARISON;                                                                                                                                                                                                                                                                                  
                        reportType = ReportType.BASELINE;                                                                                                                                                                                                                                                                                                 
                        break                                                                                                                                                                                                                                                                                                                             
                    default:                                                                                                                                                                                                                                                                                                                              
                        return                                                                                                                                                                                                                                                                                                                            
                }                                                                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                   
                def reportMap = getReportMap(clientInstance, reportType, false);
                def dataMap = event.getDataMap();                                                                                                                                                                                                                                                                                                         
                def fileName = dataMap["fileName"]                                                                                                                                                                                                                                                                                                        
                def previousFileName = reportMap.lowerKey(dataMap["fileName"])                                                                                                                                                                                                                                                                            
                if ((previousFileName != null) && (fileName != null)) {                                                                                                                                                                                                                                                                                   
                    File outputFile;                                                                                                                                                                                                                                                                                                                      
                    // generate the comparison report                                                                                                                                                                                                                                                                                                     

                    if ( SbLicense.instance.isStandAlone() ) {                                                                                                                                                                                                                                                                                        
                        // create the comparison                                                                                                                                                                                                                                                                                                      
                        outputFile = createComparisonFromScheduledTask(comparisonType, reportType,                                                                                                                                                                                                                                                    
                            previousFileName,fileName);                                                                                                                                                                                                                                                                                               
                    }                                                                                                                                                                                                                                                                                                                                 
                    else {                                                                                                                                                                                                                                                                                                                            
                        // get the client instances                                                                                                                                                                                                                                                                                                   
                        // create the comparison                                                                                                                                                                                                                                                                                                      
                        outputFile = createComparisonFromScheduledTask(comparisonType, reportType,                                                                                                                                                                                                                                                    
                            clientInstance,previousFileName,                                                                                                                                                                                                                                                                                          
                            clientInstance,fileName);                                                                                                                                                                                                                                                                                                 
                    }                                                                                                                                                                                                                                                                                                                                 
                    outputName = outputFile.name;                                                                                                                                                                                                                                                                                                     
//                    println "Generated ${outputFile.absolutePath}"                                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                          
                    // parse the generated file quickly to find the upstream attributes (if any)                                                                                                                                                                                                   
                    // need to examine these to determine what sort of upstream notification to send                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                          
                    def xmlRpt = new XmlSlurper().parse(new File(outputFile.absolutePath));                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                          
                    def modulesRun  =  xmlRpt.upstreamSummary.@modulesRun                                                                                                                                                                                                                                                                                 
                    def addedCount  =  xmlRpt.upstreamSummary.@addedCount                                                                                                                                                                                                                                                                                 
                    def changedCount  =  xmlRpt.upstreamSummary.@changedCount                                                                                                                                                                                                                                                                             
                    def removedCount  =  xmlRpt.upstreamSummary.@removedCount                                                                                                                                                                                                                                                                             
                    def failuresCount  =  xmlRpt.upstreamSummary.@failuresCount                                                                                                                                                                                                                                                                           
                    def errorsCount  =  xmlRpt.upstreamSummary.@errorsCount                                                                                                                                                                                                                                                                               
                    def profileRun = xmlRpt.report[1].@profile                                                                                                                                                                                                                                                                                            
                    def clientHostName = xmlRpt.report[1].@hostname                                                                                                                                                                                                                                                                                       
                    def clientName = clientInstance.name                                                                                                                                                                                                                                                                                                  
                    def rptTime = xmlRpt.report[1].@created                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                          
                    def addedString = (addedCount != '0')? " added ${addedCount}" : ""                                                                                                                                                                                                             
                    def changedString = (changedCount != '0') ? " changed ${changedCount}" : ""                                                                                                                                                                                                                                                           
                    def removedString = (removedCount!= '0')? " removed ${removedCount}" : ""                                                                                                                                                                                                                                                             
                    def failuresString = (failuresCount!= '0')? " ** FAILURES ${failuresCount} **" : ""                                                                                                                                                                                                                                                   
                    def errorsString = (errorsCount!= '0')? " ** ERRORS ${errorSCount} **" : ""                                                                                                                                                                                                                                                           
                    
                    def findings = [addedString, changedString, removedString, failuresString, errorsString].join(" ")                                                                                                                                                                                                                                                                                                                                     
                    // Ok, walk down in severity
                    
                    if (! findings) findings = "No new findings"                                                                                                                                                                                                                                                                                                          

                    def extensionsList = []
                    extensionsList << "cs5Label=Result"
                    extensionsList << "cs5=Delta Report Summary"
                    extensionsList << "cs2Label=Client"
                    extensionsList << "cs2=${clientName}"
                    extensionsList << "cs3Label=Group"
                    extensionsList << "cs3=${clientInstance.group.name}"
                    extensionsList << "startTime=rptTime"
                    extensionsList << "msg=Profile ${profileRun} processed ${modulesRun} Modules - ${findings}"                                                        
                    def logLevel = SyslogAppenderLevel.DEBUG                                                                                                                                                                                                                                                                                              
                    if (errorsString) {                                                                                                                                                                                                                                                                                                                   
                      logLevel = SyslogAppenderLevel.ERR                                                                                                                                                                                                                                                                                                  
                    } else if (failuresString)  {                                                                                                                                                                                                                                                                                                         
                      logLevel = SyslogAppenderLevel.WARN                                                                                                                                                                                                                                                                                                 
                    } else if (addedString || removedString || changedString)  {                                                                                                                                                                                                                                                                          
                      logLevel = SyslogAppenderLevel.INFO                                                                                                                                                                                                                                                                                                 
                    }                                                                                                                                                                                                                                                                                                                                     
                    
                    upstreamNotificationService.log(logLevel, UpstreamNotificationTypeEnum.TASK_RPT_STATUS,"Scheduled Task Status", extensionsList);                                                                                                                                                                                                                                      
                }                                                                                                                                                                                                                                                                                                                                         
            }                                                                                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                                                                          
            m_log.info("Generate ${actionType} Comparison report for ${event.transactionId}");
        }
        catch ( ReportsException reportsException ) {                                                                                                                                                                                                                                                                                         
            // render the errors back to the user                                                                                                                                                                                                                                                                                             
            m_log.error("Unable to generate ${actionType} comparison report",reportsException);                                                                                                                                                                                                                                               
        }                                                                                                                                                                                                                                                                                                                                     
        catch (Exception e) {
            m_log.error("Unable to generate ${actionType} comparison report",e);                                                                                                                                                                                                                                               
        
        }
    }                                                               
    
    String generateComparisonFromScheduledBaseline( OSLockdownNotificationEvent event) {
        m_log.info("Generate Baseline Comparison report for ${event.transactionId}");
    }
    
    
}

