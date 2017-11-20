/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services.communication;

import org.apache.log4j.Logger;

import com.trustedcs.sb.ws.client.ReportsCommunicator;
import com.trustedcs.sb.services.client.reports.ReportsResponse;

import com.trustedcs.sb.web.pojo.Client;

import com.trustedcs.sb.exceptions.ReportsCommunicationException;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import grails.util.Environment;

class ReportsCommunicationService {

    def grailsApplication

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.communication.ReportsCommunicationService");

    // transactional service
    boolean transactional = false;

    // injected services
    def messageSource;

    /**
     * Returns the the list of baselines that exist on the given client
     *
     * @param clientInstance
     * @return List<String> xml file listing
     */
    def listBaselines(Client clientInstance) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // list of baslines that are available
        def reportList = [];

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getBaselineList();
        }
        catch(Exception e) {
            m_log.error("Unable to list baselines",e)
            errorMessage = messageSource.getMessage("reports.list.baselines.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[listBaselines] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to list baselines ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.list.baselines.error",
                    [clientInstance.name, reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is a body to the response try to parse it
        if ( reportsResponse.body ) {
            try {
                // parse the response body
                XmlSlurper slurper = new XmlSlurper();
                def xml = slurper.parseText(reportsResponse.body);
                // add each file to the list
                xml.file.each { file ->
                    reportList << file.@name.text();
                }
                // return the created list
                return reportList;
            }
            catch ( Exception e ) {
                m_log.error("Unable to parse : ${reportsResponse.body}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.parse.error",
                        [clientInstance.name] as Object[],null));
            }
        }
        else {
            // no respnse body
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns the the list of assessments that exist on the given client
     *
     * @param clientInstance
     * @return List<String> xml file listing
     */
    def listAssessments(Client clientInstance) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // list of baslines that are available
        def reportList = [];

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getAssessmentList();
        }
        catch(Exception e) {
            m_log.error("Unable to list assessments",e)
            errorMessage = messageSource.getMessage("reports.list.assessments.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[listAssessments] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to list assessments ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.list.assessments.error",
                    [clientInstance.name, reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is a body to the response try to parse it
        if ( reportsResponse.body ) {            
            try {
                // parse the response body
                XmlSlurper slurper = new XmlSlurper();
                def xml = slurper.parseText(reportsResponse.body);
                // add each file to the list
                xml.file.each { file ->
                    reportList << file.@name.text();
                }
                // return the created list
                return reportList;
            }
            catch ( Exception e ) {
                m_log.error("Unable to parse : ${reportsResponse.body}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.parse.error",
                        [clientInstance.name] as Object[],null));
            }
        }
        else {
            // no respnse body
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns the requested assessment report
     *
     * @param clientInstance
     * @param reportFileName
     */
    def getAssessment(Client clientInstance, String reportFileName) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;        

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getAssessment(reportFileName);
        }
        catch(Exception e) {
            m_log.error("Unable to retrieve assessment ${reportFileName}",e)
            errorMessage = messageSource.getMessage("reports.retrieve.assessment.error",
                [clientInstance.name,reportFileName,e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[assessment] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to retrieve assessment ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.retrieve.assessment.error",
                    [clientInstance.name,reportFileName,reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is content persist it to disk
        if ( reportsResponse.content ) {
            // locate the directory
            File directory = SBFileSystemUtil.getClientAssessmentDirectory(clientInstance.id);

            // check to see the directory exists
            if ( !directory.exists() ) {
                // create the directory if it doesn't
                if ( !directory.mkdirs() ) {
                    throw new ReportsCommunicationException(message:messageSource.getMessage("reports.directory.error",
                        [directory.absolutePath] as Object[],null));
                }
            }

            // Location that the report will exist on disk
            File reportFile = new File(directory,reportFileName);

            // persist the content to the output file location
            try {
                // use the file's output stream
                reportFile.withOutputStream { outStream ->
                    outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                }
            }
            catch ( Exception e ) {
                m_log.error("Unable to presist: ${e.message}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.persist.error",
                        [clientInstance.name,reportFileName,reportFile.absolutePath,e.message] as Object[],null));
            }

            // return the persisted file
            return reportFile;
        }
        else {
            // no response content
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.content.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns the requested baseline report
     *
     * @param clientInstance
     * @param reportFileName
     */
    def getBaseline(Client clientInstance, String reportFileName) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getBaseline(reportFileName);
        }
        catch(Exception e) {
            m_log.error("Unable to retrieve baseline ${reportFileName}",e)
            errorMessage = messageSource.getMessage("reports.retrieve.baseline.error",
                [clientInstance.name,reportFileName,e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[baseline] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to retrieve baseline ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.retrieve.baseline.error",
                    [clientInstance.name,reportFileName,reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is content persist it to disk
        if ( reportsResponse.content ) {
            // locate the directory
            File directory = SBFileSystemUtil.getClientBaselineDirectory(clientInstance.id);

            // check to see the directory exists
            if ( !directory.exists() ) {
                // create the directory if it doesn't
                if ( !directory.mkdirs() ) {
                    throw new ReportsCommunicationException(message:messageSource.getMessage("reports.directory.error",
                        [directory.absolutePath] as Object[],null));
                }
            }

            // Location that the report will exist on disk
            File reportFile = new File(directory,reportFileName);

            // persist the content to the output file location
            try {
                // use the file's output stream
                reportFile.withOutputStream { outStream ->
                    outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                }
            }
            catch ( Exception e ) {
                m_log.error("Unable to presist: ${e.message}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.persist.error",
                        [clientInstance.name,reportFileName,reportFile.absolutePath,e.message] as Object[],null));
            }

            // return the persisted file
            return reportFile;
        }
        else {
            // no response content
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.content.null",
                    [clientInstance.name] as Object[],null));
        }
    }    

    /**
     * Returns the the list of applies that exist on the given client
     *
     * @param clientInstance
     * @return List<String> xml file listing
     */
    def listApplies(Client clientInstance) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // list of baslines that are available
        def reportList = [];

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getApplyList();
        }
        catch(Exception e) {
            m_log.error("Unable to list applies",e)
            errorMessage = messageSource.getMessage("reports.list.applies.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[listApplies] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to list applies ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.list.applies.error",
                    [clientInstance.name, reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is a body to the response try to parse it
        if ( reportsResponse.body ) {
            try {
                // parse the response body
                XmlSlurper slurper = new XmlSlurper();
                def xml = slurper.parseText(reportsResponse.body);
                // add each file to the list
                xml.file.each { file ->
                    reportList << file.@name.text();
                }
                // return the created list
                return reportList;
            }
            catch ( Exception e ) {
                m_log.error("Unable to parse : ${reportsResponse.body}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.parse.error",
                        [clientInstance.name] as Object[],null));
            }
        }
        else {
            // no respnse body
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns the requested apply report
     *
     * @param clientInstance
     * @param reportFileName
     */
    def getApply(Client clientInstance, String reportFileName) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getApply(reportFileName);
        }
        catch(Exception e) {
            m_log.error("Unable to retrieve apply ${reportFileName}",e)
            errorMessage = messageSource.getMessage("reports.retrieve.apply.error",
                [clientInstance.name,reportFileName,e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[apply] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to retrieve apply ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.retrieve.apply.error",
                    [clientInstance.name,reportFileName,reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is content persist it to disk
        if ( reportsResponse.content ) {
            // locate the directory
                                                    //TODO : implement
            File directory = SBFileSystemUtil.getClientApplyDirectory(clientInstance.id);

            // check to see the directory exists
            if ( !directory.exists() ) {
                // create the directory if it doesn't
                if ( !directory.mkdirs() ) {
                    throw new ReportsCommunicationException(message:messageSource.getMessage("reports.directory.error",
                        [directory.absolutePath] as Object[],null));
                }
            }

            // Location that the report will exist on disk
            File reportFile = new File(directory,reportFileName);

            // persist the content to the output file location
            try {
                // use the file's output stream
                reportFile.withOutputStream { outStream ->
                    outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                }
            }
            catch ( Exception e ) {
                m_log.error("Unable to presist: ${e.message}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.persist.error",
                        [clientInstance.name,reportFileName,reportFile.absolutePath,e.message] as Object[],null));
            }

            // return the persisted file
            return reportFile;
        }
        else {
            // no response content
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.content.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns the the list of undos that exist on the given client
     *
     * @param clientInstance
     * @return List<String> xml file listing
     */
    def listUndos(Client clientInstance) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // list of baslines that are available
        def reportList = [];

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getUndoList();
        }
        catch(Exception e) {
            m_log.error("Unable to list undoes",e)
            errorMessage = messageSource.getMessage("reports.list.undos.error",
                [clientInstance.name, e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[listUndos] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to list undos ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.list.undos.error",
                    [clientInstance.name, reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is a body to the response try to parse it
        if ( reportsResponse.body ) {
            try {
                // parse the response body
                XmlSlurper slurper = new XmlSlurper();
                def xml = slurper.parseText(reportsResponse.body);
                // add each file to the list
                xml.file.each { file ->
                    reportList << file.@name.text();
                }
                // return the created list
                return reportList;
            }
            catch ( Exception e ) {
                m_log.error("Unable to parse : ${reportsResponse.body}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.parse.error",
                        [clientInstance.name] as Object[],null));
            }
        }
        else {
            // no respnse body
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.body.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Returns the requested undo report
     *
     * @param clientInstance
     * @param reportFileName
     */
    def getUndo(Client clientInstance, String reportFileName) throws ReportsCommunicationException {

        // the client response
        ReportsResponse reportsResponse;

        // the ws client proxy
        ReportsCommunicator communicator;

        // error message for the exception
        def errorMessage;
        try {
            // create the communicator
            communicator = createReportsCommunicator(clientInstance);
            // make the call out to the client
            reportsResponse = communicator.getUndo(reportFileName);
        }
        catch(Exception e) {
            m_log.error("Unable to retrieve undo ${reportFileName}",e)
            errorMessage = messageSource.getMessage("reports.retrieve.undo.error",
                [clientInstance.name,reportFileName,e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[undo] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to retrieve undo ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("reports.retrieve.undo.error",
                    [clientInstance.name,reportFileName,reportsResponse.reasonPhrase] as Object[],null);
            }
            else {
                // not response recieved
                errorMessage = messageSource.getMessage("reports.response.null",
                    [clientInstance.name] as Object[],null);
            }
            // throw an exception with the error message
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // if there is content persist it to disk
        if ( reportsResponse.content ) {
            // locate the directory
            File directory = SBFileSystemUtil.getClientUndoDirectory(clientInstance.id);

            // check to see the directory exists
            if ( !directory.exists() ) {
                // create the directory if it doesn't
                if ( !directory.mkdirs() ) {
                    throw new ReportsCommunicationException(message:messageSource.getMessage("reports.directory.error",
                        [directory.absolutePath] as Object[],null));
                }
            }

            // Location that the report will exist on disk
            File reportFile = new File(directory,reportFileName);

            // persist the content to the output file location
            try {
                // use the file's output stream
                reportFile.withOutputStream { outStream ->
                    outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                }
            }
            catch ( Exception e ) {
                m_log.error("Unable to presist: ${e.message}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("reports.persist.error",
                        [clientInstance.name,reportFileName,reportFile.absolutePath,e.message] as Object[],null));
            }

            // return the persisted file
            return reportFile;
        }
        else {
            // no response content
            throw new ReportsCommunicationException(message:messageSource.getMessage("reports.response.content.null",
                    [clientInstance.name] as Object[],null));
        }
    }


    /**
     * Creates a web services client proxy object of the given client
     *
     * @param client the client to create the webservice proxy agent from
     */
    ReportsCommunicator createReportsCommunicator(Client client) {
    	boolean useHttps = grailsApplication.config.tcs.sb.console.secure.toBoolean();
        return new ReportsCommunicator(client.id,
            client.hostAddress,
            client.port,
            useHttps);
    }
}
