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

/**
 * Seperate service from the reports service based on the idea that we could
 * change the web service interface for the console to get console logs to be
 * a different service entirely as well as add other methods including the
 * listing of different logs to the dispatcher.  Causes some code to be
 * replicated in the mean time though.  This is acceptable for groundwork.
 */
class LoggingCommunicationService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.communication.LoggingCommunicationService");

    // transactional service
    boolean transactional = false;

    /**
     * Retrieves the oslockdown application log from
     * /var/lib/oslockdown/logs/oslockdown.log
     *
     * @param clientInstance
     */
    def getApplicationLog(Client clientInstance) throws ReportsCommunicationException {

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
            reportsResponse = communicator.getSbAppLog();
        }
        catch(Exception e) {
            m_log.error("Unable to get OS Lockdown log",e)
            errorMessage = messageSource.getMessage("logging.retrieve.error",
                [clientInstance.name,e.message] as Object[],null);
            m_log.error(errorMessage);
            throw new ReportsCommunicationException(message:errorMessage);
        }

        // response may or may not have been returned
        m_log.info("reports[sblog] response code[${reportsResponse?.code}] reason[${reportsResponse?.reasonPhrase}]");

        // check to see if there was an error
        if ( !(reportsResponse) || reportsResponse.code >= 400 ) {
            m_log.error("Client ${clientInstance.name} unable to retrieve log ${reportsResponse?.reasonPhrase}");
            // there was a response
            if ( reportsResponse ) {
                // check the reason for the error
                errorMessage = messageSource.getMessage("logging.retrieve.error",
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
            File directory = SBFileSystemUtil.getClientLogsDirectory(client.id);

            // check to see the directory exists
            if ( !directory.exists() ) {
                // create the directory if it doesn't
                if ( !directory.mkdirs() ) {
                    throw new ReportsCommunicationException(message:messageSource.getMessage("reports.directory.error",
                        [directory.absolutePath] as Object[],null));
                }
            }

            // Location that the log will exist on disk
            File logFile = new File(directory,"oslockdown.log");

            // persist the content to the output file location
            try {
                // use the file's output stream
                logFile.withOutputStream { outStream ->
                    outStream << new ByteArrayInputStream(reportsResponse.content.getBytes());
                }
            }
            catch ( Exception e ) {
                m_log.error("Unable to persist: ${e.message}");
                throw new ReportsCommunicationException(message:messageSource.getMessage("logging.persist.error",
                        [clientInstance.name,reportFile.absolutePath,e.message] as Object[],null));
            }

            // return the persisted file
            return logFile;
        }
        else {
            // no response content
            throw new ReportsCommunicationException(message:messageSource.getMessage("logging.response.content.null",
                    [clientInstance.name] as Object[],null));
        }
    }

    /**
     * Creates a web services client proxy object of the given client
     *
     * @param client the client to create the webservice proxy agent from
     */
    ReportsCommunicator createReportsCommunicator(Client client) {
    	boolean useHttps = false;
    	if ( Environment.current == Environment.PRODUCTION ) {
            useHttps = true;
    	}
        return new ReportsCommunicator(client.id,
            client.hostAddress,
            client.port,
            useHttps);
    }
}
