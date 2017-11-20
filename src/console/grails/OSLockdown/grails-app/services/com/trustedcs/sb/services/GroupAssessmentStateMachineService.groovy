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

import com.trustedcs.sb.notification.OSLockdownNotificationListener;
import com.trustedcs.sb.notification.OSLockdownNotificationEvent;

import com.trustedcs.sb.web.notifications.Notification;
import com.trustedcs.sb.web.notifications.NotificationTypeEnum;
import com.trustedcs.sb.reports.groupassessment.GroupAssessmentStateMachine;
import com.trustedcs.sb.reports.groupassessment.GroupAssessmentTransaction;

import com.trustedcs.sb.exceptions.DispatcherNotificationException;
import com.trustedcs.sb.exceptions.ReportsException;

import com.trustedcs.sb.reports.util.ReportsHelper;
import com.trustedcs.sb.reports.util.ReportMerger;
import com.trustedcs.sb.reports.util.ReportType;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;

import com.trustedcs.sb.exceptions.ReportsException;

class GroupAssessmentStateMachineService implements OSLockdownNotificationListener {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.GroupAssessmentStateMachineService");
    
    // holds the state machines
    private List<GroupAssessmentStateMachine> stateMachineList = Collections.synchronizedList(new ArrayList<GroupAssessmentStateMachine>());

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def reportsService;
    def dispatcherNotificationService;
    def auditLogService;

    /**
     * Adds the statemachine to the list
     *
     * @param stateMachine
     */
    public void addStateMachine(GroupAssessmentStateMachine stateMachine) {
        // add the state machine
        stateMachineList.add(stateMachine);
    }

    /**
     * Removes the statemachine from the list
     *
     * @param stateMachine
     */
    public void removeStateMachine(GroupAssessmentStateMachine stateMachine) {
        // remove the state machine
        stateMachineList.remove(stateMachine);
    }

    /**
     * Notification recieved
     *
     * @param notificationEvent
     */
    public void notificationReceived (OSLockdownNotificationEvent notificationEvent) {
    	try {
            // if there are any state machines waiting for notifications
            if ( stateMachineList ) {
                // log the event
                m_log.debug(notificationEvent.toString());

                // check transaction id
                String transactionId = notificationEvent.getTransactionId();
                stateMachineList.each { sm ->
                    if ( sm.transactions.containsKey(transactionId) ) {
                        // update the transaction
                        sm.updateTransaction(transactionId,
                            true,
                            notificationEvent.wasSuccessful(),
                            notificationEvent.getInfo());
                    }
                }

                // check for finished statemachines                
                def finishedMachines = stateMachineList.findAll { stateMachine ->
                    stateMachine.hasCompleted();
                }

                // number of completed state machines
                m_log.info("completed count ${finishedMachines.size()}");
                finishedMachines.each { terminatedMachine ->
                    // generate the report for the finished statemachine
                    createReport(terminatedMachine);
                    // remove the statemachine from the list
                    stateMachineList.remove(terminatedMachine);
                }

                // machines left
                m_log.info("state machines left ${stateMachineList.size()}");
            }
            else {
                // no state machines waiting
                m_log.debug("no group assessments in progress, skipping")
            }
    	}
    	catch ( Exception e ) {
            // error processing the notification
            m_log.error("error updating group assessment notification listener",e);
    	}
    }

    /**
     * Method not implemented
     *
     * @param notificationEvent
     */
    public void statusReceived (OSLockdownNotificationEvent notificationEvent) {
        // no operation
    }

    /**
     * Method not implemented
     *
     * @param notificationEvent
     */
    public void infoReceived(OSLockdownNotificationEvent notificationEvent) {
        // no operation
    }

    /**
     * Creates a group assessment report using the completed state machine object
     *
     * Unable to put this method in the GroupAssessmentService since we would end
     * up with a cross injection issue.  The majority of this code is replicated
     * from createReport(Group group, Integer loggingLevel)
     *
     * @param stateMachine
     */
    void createReport(GroupAssessmentStateMachine stateMachine) throws ReportsException {
        try {
            // get the outputfile name
            String reportName = ReportsHelper.groupGroupAssessmentFilename();
            Group groupInstance = Group.get(stateMachine.groupId);
            File directory = reportsService.getReportDirectory(groupInstance,ReportType.GROUP_ASSESSMENT);
            File groupAssessmentFile = new File(directory,reportName);

            // client map
            def clientMap = [:];
            ReportMerger reportMerger = new ReportMerger();

            // invoke report Retrieval            
            m_log.info("group.name ${groupInstance?.name}");

            // get the report
            Client client;
            stateMachine.transactions.each { transactionId, transaction ->
                try {
                    m_log.info("client ID ${transaction.getClientId()}");
                    client = Client.get(transaction.getClientId());
                    m_log.info("client ${client}");
                    if ( transaction.successful ) {
                        try {
                            // pull the latest scan from the client
                            File assessmentFile = reportsService.getLatestReport(client,ReportType.ASSESSMENT,false);
                            clientMap[client.name] = assessmentFile;
                        }
                        catch ( ReportsException reportsException ) {
                            // unable to get the report from the client
                            reportMerger.addMissing(client.name,404,reportsException.message);
                        }
                    }
                    else {
                        // scan failed to be run
                        reportMerger.addMissing(client.name,404,transaction.info);
                    }                    
                }
                catch ( Exception e ) {
                    m_log.error("Unable to get latest assessment from client ${client?.name}",e);
                    if ( client ) {
                        reportMerger.addMissing(client.name,404,"Unable to get latest assessment from client");
                    }
                }
            }

            // client map
            m_log.info("Client Map for Merger: ${clientMap}");
            // generate the report
            reportMerger.merge(groupInstance.name,groupInstance.profile?.name,clientMap,groupAssessmentFile);

            // audit logger
            auditLogService.logReport("add",ReportType.GROUP_ASSESSMENT.displayString,groupAssessmentFile.name);

            // create and save a notification state the group assessment
            // has reached a termination state.
            try {
                // create a date to use the for the notification
                Calendar calendar = Calendar.getInstance();
                Date date = calendar.getTime();

                // create the notification
                Notification notification = new Notification(timeStamp:date,
                    sourceId:stateMachine.groupId,
                    transactionId:"${stateMachine.groupId}:localhost:0:${date.getTime()}",
                    type:NotificationTypeEnum.GROUP_ASSESSMENT.ordinal(),
                    successful:true,
                    info:"Report Completed",
                    dataMap:['fileName':groupAssessmentFile.name,
                             'sourceId':Long.toString(groupInstance.id)]);
                // use the service to save the notification
                dispatcherNotificationService.save(notification);
            }
            catch ( DispatcherNotificationException notificationException ) {
                m_log.error("Unable to persist notification for group assessment");
            }
        }
        catch (Exception e) {
            m_log.error("unable to create group assessment report",e);
            throw new ReportsException(message:e.message);
        }
    }

}
