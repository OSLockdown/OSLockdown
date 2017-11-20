/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports;

import grails.util.Environment;

import org.apache.log4j.Logger;

import com.trustedcs.sb.metadata.SecurityModule;

import com.trustedcs.sb.metadata.Profile;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.ClientInfo;
import com.trustedcs.sb.web.pojo.Group;

import com.trustedcs.sb.util.LoggingLevel;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.reports.groupassessment.*;

import com.trustedcs.sb.reports.util.*;

import com.trustedcs.sb.ws.client.ReportsCommunicator;
import com.trustedcs.sb.ws.client.AgentCommunicator;
import com.trustedcs.sb.ws.client.AgentCommunicator.ProductType;

import com.trustedcs.sb.exceptions.DispatcherCommunicationException;
import com.trustedcs.sb.exceptions.ReportsException;

import javax.xml.transform.stream.StreamResult;
import com.trustedcs.sb.xsl.*;

class ReportController {

    //	 logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.reports.controller");

    // injected services
    def messageSource;
    def securityProfileService;
    def dispatcherCommunicationService;
    def reportsService;
    def groupAssessmentService;
    def groupAssetService;
    def auditLogService;
    
    // view rendered report action
    static final String VIEW_RENDERED_REPORT = "viewRenderedReport";

    /**
     * Index redirect to viewReports
     */
    def index = {
    	redirect(action: ReportType.ASSESSMENT.viewLocation);
    }

    /**
     * Display a page that will have assessment report options
     *
     * clientId = Client.id
     */
    def assessmentReport = {
        // model for the view
        def model = [:];
        // the map of <filename,date>
        def dataSetMap = new TreeMap();
    
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
           
            if (params.clientId) {
                // locate the client
                Client client = Client.get(params.clientId.toLong());

                if( client ){

                    // only show this one client in the Client dropdown, by setting a one-element list with a Client in it
                    model['clientList'] = [ client ]
                    
                    // Special processing for showing latest assessment report of a client, in which case
                    // the name of the report is passed in params.dataSet parameter, there is no need to fetch
                    // this client's reportMap and *only* this one client and one reportName should be shown on the
                    // page making the Client and Report dropdowns containing only one element (see bug 12206)
                    if( params.dataSet && params.dataSet.startsWith( "assessment-report" ) ){

                        // don't fetch reportsMap for this one client, params.dataSet already contains the report name
                        dataSetMap[ params.dataSet ] = ReportsHelper.parseFilename( ReportType.ASSESSMENT, params.dataSet );
                    }
                    else {
                        try {
                            // get the map from the client
                            dataSetMap = reportsService.getReportMap(client,ReportType.ASSESSMENT,false);
                        }
                        catch ( ReportsException reportsException ) {
                            // if the is an exception try local cache
                            dataSetMap = reportsService.getReportMap(client,ReportType.ASSESSMENT,true);
                        }
                    }
                }
            }

            // If clientList was not set (in case params.clientId was not passed), set it to all Clients
            if( !model['clientList'] ){
                model['clientList'] = Client.listOrderByName();
            }
        }
        else {
            // get the assessment mapping from the local file system
            dataSetMap = reportsService.getReportMap(ReportType.ASSESSMENT);
        }
        // set the map on the model
        model['dataSetMap'] = dataSetMap;
        // return the model
        return model;
    }

    /**
     * Display a page that will have baseline report options
     *
     * clientId = Client.id
     */
    def baselineReport = {
        // model for the view
        def model = [:];
        // the map of <filename,date>
        def dataSetMap = new TreeMap();
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {

            if (params.clientId) {
                
                // locate the client
                Client client = Client.get(params.clientId.toLong());
                if( client ){

                    // only show this one client in the Client dropdown, by setting a one-element list with a Client in it
                    model['clientList'] = [ client ]
                    
                    // Special processing for showing latest baseline report of a client, in which case
                    // the name of the report is passed in params.dataSet parameter, there is no need to fetch
                    // this client's reportMap and *only* this one client and one reportName should be shown on the
                    // page making the Client and Report dropdowns containing only one element (see bug 12206)
                    if( params.dataSet && params.dataSet.startsWith( "baseline-report" ) ){

                        // don't fetch reportsMap for this one client, params.dataSet already contains the report name
                        dataSetMap[ params.dataSet ] = ReportsHelper.parseFilename( ReportType.BASELINE, params.dataSet );
                    }
                    else {
                        try {
                            // get the map from the client
                            dataSetMap = reportsService.getReportMap(client,ReportType.BASELINE,false);
                        }
                        catch ( ReportsException reportsException ) {
                            // if the is an exception try local cache
                            dataSetMap = reportsService.getReportMap(client,ReportType.BASELINE,true);
                        }
                    }
                }
            }

            // If clientList was not set (in case params.clientId was not passed), set it to all Clients
            if( !model['clientList'] ){
                model['clientList'] = Client.listOrderByName();
            }
        }
        else {
            // get the assessment mapping from the local file system
            dataSetMap = reportsService.getReportMap(ReportType.BASELINE);
        }
        // set the map on the model
        model['dataSetMap'] = dataSetMap;
        // return the model
        return model;
    }

    /**
     * Display a page that will have apply report options
     *
     * clientId = Client.id
     */
    def applyReport = {
        // model for the view
        def model = [:];
        // the map of <filename,date>
        def dataSetMap = new TreeMap();
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            model['clientList'] = Client.listOrderByName();
            // if the client id is coming in already then we should retrieve the list
            // of reports for the client
            if (params.clientId) {
                // locate the client
                Client client = Client.get(params.clientId.toLong());
                try {
                    // get the map from the client
                    dataSetMap = reportsService.getReportMap(client,ReportType.APPLY,false);
                }
                catch ( ReportsException reportsException ) {
                    // if the is an exception try local cache
                    dataSetMap = reportsService.getReportMap(client,ReportType.APPLY,true);
                }
            }
        }
        else {
            // get the apply mapping from the local file system
            dataSetMap = reportsService.getReportMap(ReportType.APPLY);
        }
        // set the map on the model
        model['dataSetMap'] = dataSetMap;
        // return the model
        return model;
    }

    /**
     * Display a page that will have undo report options
     *
     * clientId = Client.id
     */
    def undoReport = {
        // model for the view
        def model = [:];
        // the map of <filename,date>
        def dataSetMap = new TreeMap();
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            model['clientList'] = Client.listOrderByName();
            // if the client id is coming in already then we should retrieve the list
            // of reports for the client
            if (params.clientId) {
                // locate the client
                Client client = Client.get(params.clientId.toLong());
                try {
                    // get the map from the client
                    dataSetMap = reportsService.getReportMap(client,ReportType.UNDO,false);
                }
                catch ( ReportsException reportsException ) {
                    // if the is an exception try local cache
                    dataSetMap = reportsService.getReportMap(client,ReportType.UNDO,true);
                }
            }
        }
        else {
            // get the undo mapping from the local file system
            dataSetMap = reportsService.getReportMap(ReportType.UNDO);
        }
        // set the map on the model
        model['dataSetMap'] = dataSetMap;
        // return the model
        return model;
    }
    
    /**
     * AJAX AHAH call to change the dataset
     * params.clientId ( client id )
     * params.reportType ( report type )
     */
    def ajaxClientSelection = {
        m_log.info(params);
        clearFlash();
        def dataSetMap = new TreeMap();
        // get the report type
        ReportType reportType = ReportType.getEnumFromOrdinal(params.reportType.toInteger());
        // find the client
        if (params.clientId) {
            // get the client
            Client clientInstance = Client.get(params.clientId.toLong());
            // use the client instance and the report type to get map
            try {
                dataSetMap = reportsService.getReportMap(clientInstance,reportType,false);
                if ( !dataSetMap ) {
                    // get the map from the local file system
                    dataSetMap = reportsService.getReportMap(clientInstance,reportType,true);
                    // data was returned
                    if ( dataSetMap ) {
                        flash.warning = "Local Cache used to list reports.";
                    }
                }
            }
            catch ( ReportsException reportsException ) {
                dataSetMap = reportsService.getReportMap(clientInstance,reportType,true);
                flash.warning = "Local Cache used to list reports.";
            }
        }
        // We've got issues using flash in ajax calls, so use this map instead
        def ajaxFlash = [:]
        ajaxFlash.warning = flash.warning
        ajaxFlash.error = flash.error
        ajaxFlash.messages = flash.messages
        clearFlash()
        // set the model on the ajax view
        [dataSetMap:dataSetMap, ajaxFlash:ajaxFlash];
    }

    /**
     * Renders choosen report back to the user
     */
    def viewRenderedReport = {
        // clear flash
        clearFlash();

        // report file
        m_log.info("viewRenderedReport: ${params}");

        // report type
        ReportType reportType = ReportType.getEnumFromOrdinal(params.reportType.toInteger());

        // report data set
        File reportFile;
        if ( !(params.dataSet) ) {
            flash.error = "No report was selected to be viewed.";
            redirect(action:reportType.viewLocation);
            return;
        }

        // log the report request
        auditLogService.logReport("view",reportType.displayString,params.dataSet);

        // render options
        ReportRenderType renderType = ReportRenderType.getEnumFromString(params.renderAs);

        // find the dataset
        try {
            // locate the report
            if ( SbLicense.instance.isStandAlone() ) {
            	reportFile = reportsService.getReport(reportType,params.dataSet);
            }
            else {
            	switch ( reportType ) {
                    case ReportType.BASELINE_COMPARISON:
                    case ReportType.ASSESSMENT_COMPARISON:
                    case ReportType.PROFILE_COMPARISON:
                        reportFile = reportsService.getReport(reportType,params.dataSet);
                        break;
                    case ReportType.GROUP_ASSESSMENT:
                    case ReportType.GROUP_ASSET:
                    Group groupInstance = Group.get(params.group.toLong());
                        reportFile = reportsService.getReport(groupInstance,reportType,params.dataSet);
                        break;
                    default :
                        Client clientInstance = Client.get(params.clientId.toLong());
                        reportFile = reportsService.getReport(clientInstance,reportType,params.dataSet);
                        break;
            	}
            }
            // does the file exist?
            if ( !(reportFile?.exists()) ) {
            	flash.error = "Report does not exist";
                m_log.error("Report (${reportFile}) does not exist");
                redirect(action:reportType.viewLocation);
                return;
            }
        }
        catch ( ReportsException e ) {
            m_log.error("Unable to display report",e);
            flash.error = "Unable to display report: ${e.message}";
            redirect(action:reportType.viewLocation);
            return;
        }

        // see if we need to render the report as html or pdf
        ByteArrayOutputStream transformedOutputStream = new ByteArrayOutputStream();
        if ( renderType == ReportRenderType.PDF ) {
            try {
                // create a name for the pdf
                // find the correct sb -> fo xslt
                String pdfFileName = ReportsHelper.getRenderReportFilename(reportFile,renderType);

                // sbdata -> pdf transform
                byte[] pdfBytes = ReportsHelper.renderPdf(reportType,reportFile);

                // response modification
                response.contentType = 'application/octet-stream';
                response.setHeader('Content-disposition', "attachment; filename=\"${pdfFileName}\"");
                response.outputStream << pdfBytes;
                response.outputStream.flush();
                return;
            }
            catch ( Exception e ) {
                m_log.error("Unable to render pdf report",e);
                flash.error = "Unable to render report: ${e.message}";
                redirect(action:reportType.viewLocation);
                return;
            }
        }
        else if ( renderType == ReportRenderType.HTML ) {
            // find the correct sb -> fo xslt
            File xslFile = ReportsHelper.getXslFile(reportType,renderType);

            def reportParams = ['css.file':ReportsHelper.getCssLocation(reportType),
	                            'header.display':'true',
				    'logo.display':'true',
	                            'footer.display':'true'];
            // output stream for the xsl transform
            SbReportTransformer.transform(new SbURIResolver(renderType),
                new FileInputStream(xslFile),
                new FileInputStream(reportFile),
                transformedOutputStream,
                reportParams);
            render(contentType:"text/html",
                text:new String(transformedOutputStream.toByteArray()),
                encoding:"UTF-8");
            return;
        }
        else {
            m_log.info("Render Type ${renderType}");
            try {
                String fileName = ReportsHelper.getRenderReportFilename(reportFile,renderType);
                m_log.info("returned file name ${fileName}");
                File xslFile = ReportsHelper.getXslFile(reportType,renderType);
                SbReportTransformer.transform(new SbURIResolver(renderType),
                    new FileInputStream(xslFile),
                    new FileInputStream(reportFile),
                    transformedOutputStream,
                    [:]);

                // response modification
                response.contentType = 'application/octet-stream';
                response.setHeader('Content-disposition', "attachment; filename=\"${fileName}\"");
                response.outputStream << transformedOutputStream.toByteArray();
                response.outputStream.flush();
                return;
            }
            catch ( Exception e ) {
                m_log.error("Unable to render ${renderType.displayString} report",e);
                flash.error = "Unable to render report: ${e.message}";
                redirect(action:reportType.viewLocation);
                return;
            }
        }
    }

    /**
     * Display the list of reports that are available to be compared
     * The initial list comes from either the stand alone baseline directory
     * or from the enterprise first client in the list.
     */
    def assessmentCompare = {
        // controller's model
        def model = reportComparisonModel(ReportType.ASSESSMENT_COMPARISON,ReportType.ASSESSMENT);

        // return the model
        return model;
    }

    /**
     * Compare two baseline reports and display the delta back to the screen
     */
    def compareAssessmentReports = {
        clearFlash();
        m_log.info("PARAMS:"+ params);
        // set the comparison type
        ReportType comparisonType = ReportType.ASSESSMENT_COMPARISON;
        // set the report type that the comparison is created from
        ReportType reportType = ReportType.ASSESSMENT;

        // check to see if we're just displaying a report that already existed
        if ( params.reportSource == 'existing') {
            if ( params.dataSet ) {
                redirect(action:VIEW_RENDERED_REPORT,params:params);
                return;
            }
            else {
                flash.warning = "Report not selected"
                redirect(action:comparisonType.viewLocation,params:params);
                return;
            }
        }

        /* As a fix for Bug 9868 - compare fails if two machines have baseline report at "same time"
         * we'll comment out this check, so that even if 2 (Assessment or Baseline) reports happen to be run within the same
         * timeframe down to a sec, we will compare them normally

        // check to see if the reports are the same
        if ( params.report1 == params.report2 ) {
            flash.warning = "Reports to compare are the same"
            redirect(action:comparisonType.viewLocation,params:params);
            return;
        }
        */

        // check to see if there are actually two reports
        if ( !(params.report1 && params.report2) ) {
            flash.warning = "You must select two reports"
            redirect(action:comparisonType.viewLocation,params:params);
            return;
        }

        // output file name
        File outputFile;
        // generate the comparison report
        try {
            if ( SbLicense.instance.isStandAlone() ) {
                // create the comparison
                outputFile = reportsService.createComparison(comparisonType, reportType,
                    params.report1,params.report2);
            }
            else {
                // get the client instances
                Client client1 = Client.get(params.client1.toLong());
                Client client2 = Client.get(params.client2.toLong());
                // create the comparison
                outputFile = reportsService.createComparison(comparisonType, reportType,
                    client1,params.report1,
                    client2,params.report2);
            }
        }
        catch ( ReportsException reportsException ) {
            // render the errors back to the user
            m_log.error("Unable to generate comparison report",reportsException);
            flash.error = reportsException.message;
            redirect(action:comparisonType.viewLocation,params:params);
        }

        // model map
        params['dataSet'] = outputFile.name;
        params['reportType'] = comparisonType.ordinal();
        redirect(action:VIEW_RENDERED_REPORT,params:params);
        return;
    }

    /**
     * Display the list of reports that are available to be compared
     * The initial list comes from either the stand alone baseline directory
     * or from the enterprise first client in the list.
     */
    def baselineCompare = {
        // controller's model
        def model = reportComparisonModel(ReportType.BASELINE_COMPARISON,ReportType.BASELINE);

        // return the model
        return model;
    }

    /**
     * Compare two baseline reports and display the delta back to the screen
     */
    def compareBaselineReports = {
        clearFlash();
        m_log.info("PARAMS:"+ params);
        // set the comparison type
        ReportType comparisonType = ReportType.BASELINE_COMPARISON;
        // set the report type that the comparison is created from
        ReportType reportType = ReportType.BASELINE;

        // check to see if we're just displaying a report that already existed
        if ( params.reportSource == 'existing') {
            if ( params.dataSet ) {
                redirect(action:VIEW_RENDERED_REPORT,params:params);
                return;
            }
            else {
                flash.warning = "Report not selected"
                redirect(action:comparisonType.viewLocation,params:params);
                return;
            }
        }

        /* As a fix for Bug 9868 - compare fails if two machines have baseline report at "same time"
         * we'll comment out this check, so that even if 2 (Assessment or Baseline) reports happen to be run within the same
         * timeframe down to a sec, we will compare them normally
        
        // check to see if the reports are the same
        if ( params.report1 == params.report2 ) {
            flash.warning = "Reports to compare are the same"
            redirect(action:comparisonType.viewLocation,params:params);
            return;
        }
        */

        // check to see if there are actually two reports
        if ( !(params.report1 && params.report2) ) {
            flash.warning = "You must select two reports"
            redirect(action:comparisonType.viewLocation,params:params);
            return;
        }

        // output file name
        File outputFile;
        // generate the comparison report
        try {
            if ( SbLicense.instance.isStandAlone() ) {
                // create the comparison
                outputFile = reportsService.createComparison(comparisonType, reportType,
                    params.report1,params.report2);
            }
            else {
                // get the client instances
                Client client1 = Client.get(params.client1.toLong());
                Client client2 = Client.get(params.client2.toLong());
                // create the comparison
                outputFile = reportsService.createComparison(comparisonType, reportType,
                    client1,params.report1,
                    client2,params.report2);
            }
        }
        catch ( ReportsException reportsException ) {
            // render the errors back to the user
            m_log.error("Unable to generate comparison report",reportsException);
            flash.error = reportsException.message;
            redirect(action:comparisonType.viewLocation,params:params);
        }

        // model map
        params['dataSet'] = outputFile.name;
        params['reportType'] = comparisonType.ordinal();
        redirect(action:VIEW_RENDERED_REPORT,params:params);
        return;
    }

    /**
     * Handles the AJAX AHAH requests for baselineCompare.gsp
     * @params.clientId the id of the client
     * @params.comparisonId which report selection it is 1 or 2
     */
    def ajaxComparisonSelection = {
        clearFlash();
        def reportMap = new TreeMap();
        ReportType reportType = ReportType.getEnumFromOrdinal(params.reportType.toInteger());
        if (params.clientId) {
            // get the client
            Client clientInstance = Client.get(params.clientId.toLong());
            // use the client instance and the report type to get map
            try {
                reportMap = reportsService.getReportMap(clientInstance,reportType,false);
                if ( !reportMap ) {
                    // get the map from the local file system
                    reportMap = reportsService.getReportMap(clientInstance,reportType,true);
                }
            }
            catch ( ReportsException reportsException ) {
                reportMap = reportsService.getReportMap(clientInstance,reportType,true);
            }
        }
        // We've got issues using flash in ajax calls, so use this map instead
        def ajaxFlash = [:]
        ajaxFlash.warning = flash.warning
        ajaxFlash.error = flash.error
        ajaxFlash.messages = flash.messages
        clearFlash()

        [reportMap:reportMap, ajaxFlash:ajaxFlash];
    }

    /**
     * Show the list of initial group assessments
     */
    def groupAssetReport = {
        def groupList = Group.withCriteria {
            order('name','asc');
        };

        def reportMap = new TreeMap();
        if ( params.group ) {
            Group group = Group.get(params.group.toLong());
            reportMap = reportsService.getReportMap(groupInstance,ReportType.GROUP_ASSET);
        }

        [groupList:groupList, reportMap:reportMap]
    }

    /**
     * Creates the group asset report
     */
    def viewGroupAsset = {
	m_log.info("viewGroupAsset ${params}");
        // if viewing existing report
        if ( params.reportSource == 'existing' ) {
            // check group
            if ( !(params.group) ) {
                flash.error = "Group not selected.<br/>"
                redirect(action:ReportType.GROUP_ASSET.viewLocation);
                return;
            }
            if ( !(params.report) ) {
                flash.error = "Report dataset not selected.<br/>"
                redirect(action:ReportType.GROUP_ASSET.viewLocation);
                return;
            }

            params['dataSet'] = params.report;
            params['reportType'] = ReportType.GROUP_ASSET.ordinal();
            redirect(action:VIEW_RENDERED_REPORT,params:params);
            return;
        }

        // check group
        if ( !(params.groupId) ) {
            flash.error = "Group not selected."
            redirect(action:ReportType.GROUP_ASSET.viewLocation);
            return;
        }
        
        // generate the report
        File outputFile;
        try {
            Group group = Group.get(params.groupId.toLong());
            outputFile = groupAssetService.createReport(group,params.infoSource == 'query' ? true : false);
        }
        catch ( ReportsException reportsException ) {
            flash.error = reportsException.message;
            redirect(action:ReportType.GROUP_ASSET.viewLocation);
            return;
        }

        // maps map
        params['group'] = params.groupId;
        params['dataSet'] = outputFile.name;
        params['reportType'] = ReportType.GROUP_ASSET.ordinal();

        // redirect to rendered report
        redirect(action:VIEW_RENDERED_REPORT,params:params);
    }

    /**
     * Show the list of initial group assessments
     */
    def groupAssessmentReport = {
        def groupList = Group.withCriteria {
            order('name','asc');
        };

        def reportMap = new TreeMap();
        if ( params.group ) {
            Group groupInstance = Group.get(params.group.toLong());
            reportMap = reportsService.getReportMap(groupInstance,ReportType.GROUP_ASSESSMENT)
        }

        [groupList:groupList, reportMap:reportMap]
    }

    /**
     * Ajax request for the group related pages
     */
    def ajaxGroupSelection = {

        def reportMap = new TreeMap();
        if ( params.id ) {
            ReportType reportType = ReportType.getEnumFromOrdinal(params.reportType.toInteger());
            Group groupInstance = Group.get(params.id.toLong());
            reportMap = reportsService.getReportMap(groupInstance,reportType);
        }

        [reportMap:reportMap]
    }

    /**
     * Displays either the group assessment selected or spawns off the group assessment
     * creation.
     */
    def viewGroupAssessment = {
        clearFlash();
        m_log.info("viewGroupAssessment ${params}");

        // the location of the created group assessment
        File groupAssessmentFile;
        // the group that should have the assessment created for it
        Group group;

        // existing report?
        if ( params.reportSource == 'existing' ) {
            // check group
            if ( !(params.group) ) {
                flash.error = "Group not selected.<br/>"
                redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
                return;
            }
            if ( !(params.report) ) {
                flash.error = "Report dataset not selected.<br/>"
                redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
                return;
            }

            // set the params so that the report can be rendered
            params['dataSet'] = params.report;
            params['reportType'] = ReportType.GROUP_ASSESSMENT.ordinal();
            redirect(action:VIEW_RENDERED_REPORT,params:params);
            return;
        }

        // validate group selection        
        if ( params.groupId ) {
            // locate the group
            group = Group.get(params.groupId.toLong());

            // check to see if the group exists
            if ( !group ) {
                flash.error = "Group not found.";
                redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
                return;
            }

            // check to see if the group has any clients
            if ( !(group.clients) ) {
                flash.error = "Group has no clients.";
                redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
                return;
            }
        }
        else {
            flash.error = "No group selected.";
            redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
            return;
        }

        // set the group on the params for our universal report view action
        params['group'] = params.groupId;

        // check for report creation
        if ( params.infoSource == "existingScansOnDisk" ) {
            // create the report from disk
            groupAssessmentFile = groupAssessmentService.createReport(group,false);
            // params to be used by the report render method
            params['dataSet'] = groupAssessmentFile.name;
            params['reportType'] = ReportType.GROUP_ASSESSMENT.ordinal();
            redirect(action:VIEW_RENDERED_REPORT,params:params);
            return;
        }
        else if ( params.infoSource == "existingScansOnClient" ) {
            // create the report from the latest scans on the clients
            groupAssessmentFile = groupAssessmentService.createReport(group,true);
            // params to be used by the report render method
            params['dataSet'] = groupAssessmentFile.name;
            params['reportType'] = ReportType.GROUP_ASSESSMENT.ordinal();
            redirect(action:VIEW_RENDERED_REPORT,params:params);
            return;
        }
        else if ( params.infoSource == "newScansOnClient" ) {
            // group must have a profile so it can be scanned.
            if ( !group.profile ) {
                flash.error = "Group is missing a profile.";
                redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
                return;
            }
            // group must have clients that can be scaned
            if ( !(group.clients) ) {
                flash.error = "Group has no clients.";
                redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
                return;
            }

            // create new scans on the clients and start the
            // group assessment statemachine in motion
            try {
                groupAssessmentService.createReport(group,params.loggingLevel.toInteger());
                // set the flash message to show to the user
                flash.message = "Group Assessment started, a notification will inform you when the report has completed.";
            }
            catch ( ReportsException reportsException ) {
                flash.error = "Group Assessment Failed : [${reportsException.message}]";
            }
            // direct to a view location
            redirect(action:ReportType.GROUP_ASSESSMENT.viewLocation);
            return;
        }

    }  

    /**
     * Returns a model map for the comparison report type
     *
     * @param comparisonType the comparison type
     * @param reportType the type that the comparison is built from
     * @return a model map
     */
    private Map reportComparisonModel(ReportType comparisonType, ReportType reportType) {
        // controller's model
        def model = [:];

        // existing baseline comparisons
        def existingComparisons = reportsService.getReportMap(comparisonType);
        model['existingComparisons'] = existingComparisons;

        // client instance
        Client clientInstance;

        // product type check
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            // client list
            model['clientList'] = Client.listOrderByName();

            // client 1 mapping
            def clientReportMap1 = new TreeMap();
            model['clientReportMap1'] = clientReportMap1
            // client 2 mapping
            def clientReportMap2 = new TreeMap();
            model['clientReportMap2'] = clientReportMap2

            // check client 1
            if ( params.client1 ) {
                try {
                    // get the client
                    clientInstance = Client.get(params.client1.toLong());
                    // get the report map from the service
                    clientReportMap1 = reportsService.getReportMap(clientInstance,reportType,false);
                    // if there is no map contents look local
                    if ( !clientReportMap1 ) {
                        // get the local map from the service
                        clientReportMap1 = reportsService.getReportMap(clientInstance,reportType,true);
                    }
                }
                catch ( ReportsException reportException ) {
                    // get the local map from the service
                    clientReportMap1 = reportsService.getReportMap(clientInstance,reportType,true);
                }
                // set map on the model
                model['clientReportMap1'] = clientReportMap1;
            }

            // check client 2
            if ( params.client2 ) {
                try {
                    // get the client
                    clientInstance = Client.get(params.client2.toLong());
                    // get the report map from the service
                    clientReportMap2 = reportsService.getReportMap(clientInstance,reportType,false);
                    // if there is no map contents look local
                    if ( !clientReportMap2 ) {
                        // get the local map from the service
                        clientReportMap2 = reportsService.getReportMap(clientInstance,reportType,true);
                    }
                }
                catch ( ReportsException reportException ) {
                    // get the local map from the service
                    clientReportMap2 = reportsService.getReportMap(clientInstance,reportType,true);
                }
                // set map on the model
                model['clientReportMap2'] = clientReportMap2;
            }
        }
        else {
            // stand-alone
            def clientReportMap = reportsService.getReportMap(reportType);
            // set the map for both the client 1 and client 2 map
            model['clientReportMap1'] = clientReportMap;
            model['clientReportMap2'] = clientReportMap;
        }

        // return the model
        return model;
    }

    /**
     * Clears the flash of all messages that are currently set on it
     */
    private clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }
}
