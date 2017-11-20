/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.ClientInfo;
import com.trustedcs.sb.web.pojo.Group;

import com.trustedcs.sb.exceptions.ReportsException;
import com.trustedcs.sb.exceptions.DispatcherCommunicationException;

import com.trustedcs.sb.reports.util.AssetReportCreator;

import com.trustedcs.sb.reports.util.ReportsHelper;
import com.trustedcs.sb.reports.util.ReportType;

class GroupAssetService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.GroupAssetService");

    // Transactional
    boolean transactional = false;

    // injected services
    def messageSource;
    def dispatcherCommunicationService;
    def clientService;
    def reportsService;
    def auditLogService;

    /**
     * Creates an asset report based on the group passed in
     *
     * @param groupInstance
     * @return location of the generated report
     * @throws ReportsException
     */
    File createReport(Group groupInstance, boolean queryClients) throws ReportsException {

        // do we call out to the clients
        if ( queryClients ) {
            // iterate the clients in the group
            groupInstance.clients?.each { clientInstance ->
                try {
                    // host information map
                    def hostInfoMap = [:];
                    // check to see if a client info instance exists
                    if ( !(clientInstance.info) ) {
                        clientInstance.info = new ClientInfo();
                    }
                    // get the host info map
                    // host info map will come back populated - regardless of communications issues
                    // underlying agent call will ensure this
                    
                    hostInfoMap = dispatcherCommunicationService.hostInfo(clientInstance);
                    // update the client info from the map
                    clientService.updateClientInfo(clientInstance,hostInfoMap);
                }
                catch ( DispatcherCommunicationException e ) {
                    // display error message
                    // Update the 'OS' field with the message and save
                    clientService.updateClientInfo(clientInstance,e.message);
                    m_log.error("Group Asset query error: ${e.message}");
                    
                }
            }
        }

        // file name
        def outputFileName = ReportsHelper.getGroupAssetFilename();

        // directory
        File directory = reportsService.getReportDirectory(groupInstance,ReportType.GROUP_ASSET);
        if ( !directory.exists() ) {
            if ( !directory.mkdirs() ) {
                throw new ReportsException("Unable to create directory : ${directory.absolutePath}");
            }
        }

        // output file
        File outputFile = new File(directory,outputFileName);

        // assest report creator
        AssetReportCreator creator = new AssetReportCreator(groupInstance);
        creator.createReport(outputFile);

        // audit logger
        auditLogService.logReport("add",ReportType.GROUP_ASSET.displayString,outputFile.name);

        // return the output file
        return outputFile;
    }
}
