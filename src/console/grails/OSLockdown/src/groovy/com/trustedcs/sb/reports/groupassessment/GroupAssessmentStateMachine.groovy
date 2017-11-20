/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.reports.groupassessment;

import org.apache.log4j.Logger;

/**
 * @author amcgrath
 *
 */
public class GroupAssessmentStateMachine {
	
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.reports.groupassessment.statemachine");
    // map <String(transactionId),GroupAssessmentTransaction>
    def transactions = [:];
    Long groupId;
    String groupName;
    boolean finished = false;
    int totalClients = 0;

    /**
     * Constructor
     *
     * @param clients the total number of clients that exist for this state machine
     */
    GroupAssessmentStateMachine(int clients) {
        totalClients = clients;
    }
	
    /**
     * Add a transaction to the statemachine
     * @param transaction
     */
    void addTransaction(GroupAssessmentTransaction transaction) {
        transactions[transaction.id] = transaction;
    }
	
    /**
     * Add a transaction to the statemachine
     * convience method for not having to create the object
     * @param transactionId
     */
    void addTransaction(String transactionId) {
        GroupAssessmentTransaction transaction = new GroupAssessmentTransaction();
        transaction.id = transactionId;
        addTransaction(transaction);
    }
	
    /**
     * update the transaction
     * @param id
     */
    synchronized void updateTransaction(String id, boolean finished, boolean success, String information) {
        if ( transactions[id] ) {
            transactions[id].terminatedState = finished;
            transactions[id].successful = success;
            transactions[id].info = information;    
        }
        else {
            GroupAssessmentTransaction transaction = 
            GroupAssessmentTransaction(id:id,terminatedState:finished,successful:success,info:information);
            transactions[id] = transaction;
        }
        m_log.info("transaction state ${transactions[id]}");
        m_log.info("stateMachine\n ${this}");
        checkState();
    }
	
    /**
     * Checks to see if all the transactions have reached a completed state
     * if they have then create the report
     */
    void checkState() {
        if ( hasCompleted() ) {
            m_log.info("all scans completed");
        }
    } 
	
    /**
     * Checks to see if the statemachine has reached the termination
     * state.
     *
     * @return returns if all of the transactions have reached their
     *         completed state.
     */
    boolean hasCompleted() {
        if ( finished ) {
            return true;
        }

        // check all the transactions in the state machine to see if they are completed
        boolean transactionsFinished = true;
        transactions.each { transactionId , transaction ->
            if ( !(transaction.terminatedState) ) {
                transactionsFinished = false;
            }
        }

        // if all the transactions are finished and the transaction size is the total
        // number of clients
        if ( transactionsFinished && transactions.size() == totalClients ) {
            finished = true;
        }
        return finished;
    }
	
    /**
     * Check if the transaction is in the statemachine
     * @return if the transaction id exists in the statemachine
     */
    boolean hasTransaction(String id) {
        return transactions.containsKey(id);
    }

    /**
     *
     * @return string represenation of the state machine
     */
    public String toString() {
        StringBuffer buffer = new StringBuffer();
        buffer.append("group[${groupName}]\n");
        transactions.each {
            buffer.append("${it}\n");
        }
        return buffer.toString();
    }
}
