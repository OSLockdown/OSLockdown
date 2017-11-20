/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.metadata.Profile;

import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.ws.client.ReportsCommunicator;

import grails.util.Environment;
import java.text.MessageFormat;

//JAXP
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Source;
import javax.xml.transform.Result;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.sax.SAXResult;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.URIResolver;

// FOP
import org.apache.fop.apps.FOUserAgent;
import org.apache.fop.apps.Fop;
import org.apache.fop.apps.FOPException;
import org.apache.fop.apps.FopFactory;
import org.apache.fop.apps.FormattingResults;
import org.apache.fop.apps.MimeConstants;
import org.apache.fop.apps.PageSequenceResults;

import com.trustedcs.sb.xsl.*;

public class ReportsHelper {
	
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.reports.util.ReportsHelper");
	
    // Constants
    public static final String REPORT_FILE_STAMP = "yyyyMMdd_HHmmss";
    public static final String REPORT_DISPLAY_STAMP = "MMM dd HH:mm:ss yyyy";
    public static final String CREATED_DATE_FORMAT = "yyyy-MM-dd HH:mm:ss Z";
    public static final String ASSESSMENT_COMPARISON_FILENAME_PREFIX = "assessment-comparison";
    public static final String ASSESSMENT_FILENAME_PREFIX = "assessment-report-";
    public static final String BASELINE_COMPARISON_FILENAME_PREFIX = "baseline-comparison";
    public static final String BASELINE_FILENAME_PREFIX = "baseline-report-";
    public static final String GROUP_ASSET_FILENAME_PREFIX = "group-asset";
    public static final String GROUP_ASSESSMENT_FILENAME_PREFIX = "group-assessment";
    
    // file constants
    private static File stylesheetDir = new File("/usr/share/oslockdown/cfg/stylesheets");

    // file formats

    // Standalone comparison "${prefix}-${tstamp1}-${tstamp2}"
    private static MessageFormat genericComparisonStandaloneFormat = new MessageFormat("{0}-{1}-{2}");
    // Standalone comparison "${prefix}-${tstamp1}-${tstamp2}-report-${outputTstamp}.xml"
    private static MessageFormat genericComparisonStandaloneFilenameFormat = new MessageFormat("{0}-{1}-{2}-report-{3}.xml");
    
    // Enterprise comparison "${prefix}-${client1.id}-${tstamp1}-${client2.id}-${tstamp2}"
    private static MessageFormat genericComparisonEnterpriseFormat = new MessageFormat("{0}-{1}-{2}-{3}-{4}");
    // Enterprise comparison "${prefix}-${client1.id}-${tstamp1}-${client2.id}-${tstamp2}-report-${outputTstamp}.xml"
    private static MessageFormat genericComparisonEnterpriseFilenameFormat = new MessageFormat("{0}-{1}-{2}-{3}-{4}-report-{5}.xml");

    // comparison report time stamp format
    private static MessageFormat comparisonFilenameFormat = new MessageFormat("{0}-report-{1}.xml");

    // Group Asset "${prefix}-${outputTstamp}.xml"
    private static MessageFormat groupAssetFilenameFormat = new MessageFormat("{0}-{1}.xml");

    // Group Assessment "${prefix}-${ouptputTsamp}.xml"
    private static MessageFormat groupAssessmentFilenameFormat = new MessageFormat("{0}-{1}.xml");
    
    // Profile Comparison "${profileA.id}-${profileB.id}-comparison-${outputTstamp}.xml"
    private static MessageFormat profileComparisonFilenameFormat = new MessageFormat("{0}-{1}-comparison-{2}.xml");
    
    // transformers        
    private static FopFactory fopFactory;    
    private static TransformerFactory transformerFactory;
    static {
    	fopFactory = FopFactory.newInstance();
    	fopFactory.setURIResolver(new SbURIResolver(ReportRenderType.PDF));
        transformerFactory = TransformerFactory.newInstance();  
        transformerFactory.setErrorListener(new SbXslErrorListener());
    }
    
    /**
     * Returns the xsl required to transform the sb data format into something
     * human readable.
     *
     * @param reportType
     * @param renderType
     */
    public static File getXslFile(ReportType reportType, ReportRenderType renderType) {

        File directory = new File(stylesheetDir,renderType.xslSubDirectory);
        return new File(directory,reportType.xslFile);

    }

    /**
     * Returns the CSS location for the report type that is passed
     * @param reportType
     */
    public static String getCssLocation(ReportType reportType) {

        return "/OSLockdown/css/${reportType.cssFile}";
        
    }
    
    /**
     * Method to render a report as a pdf document
     * @param reportType
     * @param reportData
     */
    public static byte[] renderPdf(ReportType reportType, File reportData) {

        // Create the output location
        ByteArrayOutputStream out = new ByteArrayOutputStream();

        // Setup FOP
        Fop fop = fopFactory.newFop(MimeConstants.MIME_PDF, out);
        
        /* 
        // add encryption
        fop.getRendererOptions().put("encryption-params", new PDFEncryptionParams(null, "password", false, false, true, true));
         */

        //Setup Transformer
        Source xsltSrc = new StreamSource(getXslFile(reportType,ReportRenderType.PDF));
        transformerFactory.setURIResolver(new SbURIResolver(ReportRenderType.PDF));
        Transformer transformer = transformerFactory.newTransformer(xsltSrc);

        //Make sure the XSL transformation's result is piped through to FOP
        Result res = new SAXResult(fop.getDefaultHandler());

        //Setup input
        Source src = new StreamSource(reportData);

        //Start the transformation and rendering process
        transformer.transform(src, res);        
        
        //Send content to Browser
        return out.toByteArray();               
    } 
    
    /**
     * Parse the tstamp out of the filename for baselines and assessments
     * baseline comparisons and group assessments will have to have a different
     * parser since they are named with a different convention.
     * @param fileName
     */
    public static Date createDateFromFilename(String fileName) {
        def dateString;
        def date
        try {
            dateString = fileName.tokenize("-")[2];
            dateString = dateString.substring(0,dateString.length()-4);
            date = Date.parse(REPORT_FILE_STAMP,dateString);
        } 
        catch (Exception dateException) {
            return null;
        }
        return date;        
    }    
    
    /**
     * Return the file name tstamp as a human readable date
     * @param fileName
     */
    public static String parseFilename(String fileName) {
        def date = createDateFromFilename(fileName);
        if ( date ) {
            return date.format(REPORT_DISPLAY_STAMP);
        }
        else {
            return fileName;
        }
    }

    /**
     * Return the profile comparison filename as a human readable string
     *
     * "${profileA.id}-${profileB.id}-comparison-${outputTstamp}.xml";
     *
     * @param fileName
     * @return the parsed profile comparison filename
     */
    public static String parseProfileComparisonFilename(String fileName) {
        try {
            def profile1 = "unknown";
            def profile2 = "unknown";
            def tokens = fileName.tokenize("-");
            def date = Date.parse(REPORT_FILE_STAMP,tokens[3]).format(REPORT_DISPLAY_STAMP);
            profile1 = Profile.get(tokens[0].toLong())?.name;
            profile2 = Profile.get(tokens[1].toLong())?.name;
            return "${profile1} \u00BB ${profile2} (${date})";
        }
        catch ( Exception e ) {
            // if we can't parse the date just pass it back
        }
        return fileName;
    }
    
    /**
     * Return the baseline comparison report filename as a human readable string
     *
     * @param fileName
     * @return the parsed comparison file name
     */
    public static String parseComparisonFilename(String fileName) {
        try {
            def tokens = fileName.tokenize("-");
            def client1 = "unknown";
            def report1;
            def client2 = "unknown";
            def report2;
            if ( SbLicense.instance.isStandAlone() ) {
                // baseline-comparison-${tstamp}-${tstamp}.xml
                report1 = Date.parse(REPORT_FILE_STAMP,tokens[2]).format(REPORT_DISPLAY_STAMP);
                client1 = "localhost"
                report2 = Date.parse(REPORT_FILE_STAMP,tokens[3]).format(REPORT_DISPLAY_STAMP);
                client2 = "localhost"
            }
            else {
                report1 = Date.parse(REPORT_FILE_STAMP,tokens[3]).format(REPORT_DISPLAY_STAMP);
                report2 = Date.parse(REPORT_FILE_STAMP,tokens[5]).format(REPORT_DISPLAY_STAMP);
                client1 = Client.get(tokens[2].toLong())?.name;
                client2 = Client.get(tokens[4].toLong())?.name;
            }
            
            return "(${client1}) ${report1} \u00BB (${client2}) ${report2}";
        } catch ( Exception e) {
            // if we can't parse the date just pass it back
        }
        return fileName;
    }

    /**
     * Returns a human readable String for the file name based on
     * report type
     *
     * @param reportType
     * @param fileName
     */
    public static String parseFilename(ReportType reportType, String fileName) {
        switch(reportType) {
            case ReportType.ASSESSMENT:
            case ReportType.ASSESSMENT_FAILURES:
            case ReportType.BASELINE:
            case ReportType.GROUP_ASSESSMENT:
            case ReportType.GROUP_ASSET:
            case ReportType.APPLY:
            case ReportType.UNDO:
                // standard file name
                return parseFilename(fileName);
            case ReportType.ASSESSMENT_COMPARISON:
            case ReportType.BASELINE_COMPARISON:
                // standard comparison file name
                return parseComparisonFilename(fileName);
            case ReportType.PROFILE_COMPARISON:
            // profile comparison file name
            return parseProfileComparisonFilename(fileName);
        }
    }

    /**
     * Creates the filename of report based on its render type and other options
     *
     * @param sourceFile
     * @param renderType
     */
    public static String getRenderReportFilename(File sourceFile, ReportRenderType renderType) {
        String reportFilename = sourceFile.name.substring(0,sourceFile.name.length()-4) + renderType.fileExtension;
        return reportFilename;
    }

    /**
     * Generate the file name for the given combination of report type, and report names
     *
     * @param reportType
     * @param reportName1
     * @param reportName2
     */
    public static String getComparisonName(ReportType reportType, String reportName1, String reportName2) {

        // prefix name based on report type
        String comparisonPrefix;
        String filePrefix;
        switch ( reportType ) {
            case ReportType.ASSESSMENT_COMPARISON:
            comparisonPrefix = ASSESSMENT_COMPARISON_FILENAME_PREFIX;
            filePrefix = ASSESSMENT_FILENAME_PREFIX;
            break;
            case ReportType.BASELINE_COMPARISON:
            comparisonPrefix = BASELINE_COMPARISON_FILENAME_PREFIX;
            filePrefix = BASELINE_FILENAME_PREFIX;
            break;
            default:
            comparisonPrefix = "";
            filePrefix = "";
            break;
        }

        // the timestamp of the first report
        def tstamp1 = reportName1.substring(filePrefix.length(),reportName1.length()-4);
        // the timestamp of the second report
        def tstamp2 = reportName2.substring(filePrefix.length(),reportName2.length()-4);

        // return the file name
        return genericComparisonStandaloneFormat.format([comparisonPrefix,tstamp1,tstamp2] as Object[]);
    }

    /**
     * Returns the comparison file name using the message format.  The comparison name will
     * have been created with either getComparisonName(ReportType,String,String) or
     * getComparison(ReportType,Client,String,Client,String)
     *
     * @param comparisonName
     * @return the comparison file name
     */
    public static String getComparisonFilename(String comparisonName) {

        // output time stamp
        String outputStamp = new Date().format(REPORT_FILE_STAMP);

        // return the file name
        return comparisonFilenameFormat.format([comparisonName,outputStamp] as Object[]);
    }

    /**
     * Generate the file name for the given combination of report type, and report names
     *
     * @param reportType
     * @param reportName1
     * @param reportName2
     */
    public static String getComparisonFilename(ReportType reportType, String reportName1, String reportName2) {

        // get the comparison name
        String comparisonName = getComparisonName(reportType,reportName1,reportName2)

        // output time stamp
        String outputStamp = new Date().format(REPORT_FILE_STAMP);

        // return the file name
        return comparisonFilenameFormat.format([comparisonName,outputStamp] as Object[]);
    }

    /**
     * Generate the file name for the given combination of report type, client ids and tstamp
     *
     * @param reportType
     * @param client1
     * @param reportName1
     * @param client2
     * @param reportName2
     */
    public static String getComparisonName(ReportType reportType,
                                            Client client1, String reportName1,
                                            Client client2, String reportName2) {

        // prefix name based on report type
        String comparisonPrefix;
        String filePrefix;
        switch ( reportType ) {
            case ReportType.ASSESSMENT_COMPARISON:
            comparisonPrefix = ASSESSMENT_COMPARISON_FILENAME_PREFIX;
            filePrefix = ASSESSMENT_FILENAME_PREFIX;
            break;
            case ReportType.BASELINE_COMPARISON:
            comparisonPrefix = BASELINE_COMPARISON_FILENAME_PREFIX;
            filePrefix = BASELINE_FILENAME_PREFIX;
            break;
            default:
            comparisonPrefix = "";
            filePrefix = "";
            break;
        }

        // the timestamp of the first report
        def tstamp1 = reportName1.substring(filePrefix.length(),reportName1.length()-4);
        // the timestamp of the second report
        def tstamp2 = reportName2.substring(filePrefix.length(),reportName2.length()-4);

        // return the file name
        return genericComparisonEnterpriseFormat.format([comparisonPrefix,client1.id,tstamp1,client2.id,tstamp2] as Object[]);
    }

    /**
     * Generate the file name for the given combination of report type, client ids and tstamp
     *
     * @param reportType
     * @param client1
     * @param reportName1
     * @param client2
     * @param reportName2
     */
    public static String getComparisonFilename(ReportType reportType,
                                                Client client1, String reportName1,
                                                Client client2, String reportName2) {

        // prefix name based on report type
        String comparisonName = getComparisonName(reportType,client1,reportName1,client2,reportName2);

        // output time stamp
        String outputStamp = new Date().format(REPORT_FILE_STAMP);

        // return the file name
        return comparisonFilenameFormat.format([comparisonName,outputStamp] as Object[]);
    }

    /**
     * Generate the profile comparison file name for the given combination of profiles
     *
     * @param profile1
     * @param profile2
     */
    public static String getProfileComparisonFilename(Profile profile1, Profile profile2) {
        // output time stamp
        String outputStamp = new Date().format(REPORT_FILE_STAMP);

        // return the file name
        return profileComparisonFilenameFormat.format([profile1.id,profile2.id,outputStamp] as Object[]);
    }

    /**
     * Generate the group asset file name
     */
    public static String getGroupAssetFilename() {
        String outputStamp = new Date().format(REPORT_FILE_STAMP);
        return groupAssetFilenameFormat.format([GROUP_ASSET_FILENAME_PREFIX,outputStamp] as Object[]);
    }


    /**
     * Generate the group assessment file name
     */
    public static String groupGroupAssessmentFilename() {
        String outputStamp = new Date().format(REPORT_FILE_STAMP);
        return groupAssetFilenameFormat.format([GROUP_ASSESSMENT_FILENAME_PREFIX,outputStamp] as Object[]);
    }
}
