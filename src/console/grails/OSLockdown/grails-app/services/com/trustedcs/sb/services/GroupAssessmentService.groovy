/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;

import com.trustedcs.sb.reports.groupassessment.GroupAssessmentStateMachine;
import com.trustedcs.sb.reports.groupassessment.GroupAssessmentTransaction;

import com.trustedcs.sb.reports.util.ReportMerger;

import com.trustedcs.sb.exceptions.ReportsException;
import com.trustedcs.sb.exceptions.DispatcherCommunicationException;

import com.trustedcs.sb.ws.client.AgentCommunicator;

import com.trustedcs.sb.reports.util.ReportsHelper;
import com.trustedcs.sb.reports.util.ReportType;

class GroupAssessmentService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.GroupAssessmentService");

    // Transactional
    boolean transactional = false;

    // injected services
    def messageSource;
    def reportsService;
    def dispatcherCommunicationService;
    def groupAssessmentStateMachineService;
    def auditLogService;

    /**
     * Create the report for the group that is passed in.  If fromClient is
     * true then a request out to the client is done, otherwise the latest
     * report from local disk is taken
     *
     * @param groupInstance
     * @param fromClient
     */
    File createReport(Group groupInstance, boolean fromClient) {
        // get the outputfile name
        String reportName = ReportsHelper.groupGroupAssessmentFilename();
        File directory = reportsService.getReportDirectory(groupInstance,ReportType.GROUP_ASSESSMENT);
        File groupAssessmentFile = new File(directory,reportName);

        // create the report merger
        ReportMerger reportMerger = new ReportMerger();
        // the client map used by the report merger
        def clientMap = [:];

        // the client assessment file
        File assessmentFile;
        // iterate the clients
        groupInstance.clients?.each { client ->
            // should the reports be pulled via the dispatcher
            if ( fromClient ) {
                try {
                    // get the latest report from the client
                    assessmentFile = reportsService.getLatestReport(client,ReportType.ASSESSMENT,false);
                    // add the file to the client map
                    clientMap[client.name] = assessmentFile;
                }
                catch ( ReportsException reportsException) {
                    // add the error to the report merger
                    reportMerger.addMissing(client.name,404,reportsException.message);
                }
            }
            else {
                // reports are taken from local disk
                assessmentFile = reportsService.getLatestReport(client,ReportType.ASSESSMENT,true);
                // add the file to the client map
                clientMap[client.name] = assessmentFile;
            }
        }
        // log client map
        m_log.info(clientMap);
        // create the report
        reportMerger.merge(groupInstance.name,groupInstance.profile?.name,clientMap,groupAssessmentFile);
        // audit logger
        auditLogService.logReport("add",ReportType.GROUP_ASSESSMENT.displayString,groupAssessmentFile.name);
        // return the group assessment report location
        return groupAssessmentFile;
    }

    /**
     * Create the report from a newly created set of scans on the group's clients
     *
     * @param groupInstance
     * @param loggingLevel
     */
    void createReport(Group groupInstance, Integer loggingLevel) throws ReportsException {

        // transaction id for the scan
        String transactionId;
        // dispatcher communication client
        AgentCommunicator agent;

        // the state machine for the group assessment
        GroupAssessmentStateMachine stateMachine = new GroupAssessmentStateMachine(groupInstance.clients.size());
        // set the attributes of the statemachine in relation to the group
        stateMachine.groupId = groupInstance.id;
        stateMachine.groupName = groupInstance.name;
        // add the statemachine to the assessment listener
        groupAssessmentStateMachineService.addStateMachine(stateMachine);

        // iterate each client in the group and send the request to scan the client
        groupInstance.clients.each { client ->
            // create the communication agent
            agent = dispatcherCommunicationService.createAgentCommunicator(client);
            // generate a transaction id from the agent since we need it
            // in order to update the statemachine
            transactionId = agent.generateTransactionId();
            // add the transaction id to the state machine
            stateMachine.addTransaction(transactionId);
            // scan the client
            try {
                // communication
                dispatcherCommunicationService.scan(transactionId,agent,loggingLevel,client);
            }
            catch(DispatcherCommunicationException dispatcherException) {
                m_log.error("Unable to start group assessment transaction",dispatcherException);
                // update the statemachine with the failed information
                stateMachine.updateTransaction(transactionId,true,false,dispatcherException.message);
            }
        }

        // the state machine could have completed due to the fact that all clients were offline
        // or returned errors
        if ( stateMachine.hasCompleted() ) {
            groupAssessmentStateMachineService.removeStateMachine(stateMachine);
            groupAssessmentStateMachineService.createReport(stateMachine);
        }
    }
}
