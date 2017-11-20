/*
 * Copyright 2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.trustedcs.sb.util

import org.apache.shiro.SecurityUtils

import com.trustedcs.sb.web.pojo.Client

/**
 *
 * @author kloyevsky
 */
class SBDetachmentUtil {

    // Possible values for the detachmentOperationState
    static final int NOT_RUNNING        = 0 // not running (also set to this state after detachment complete request)
    static final int STARTED            = 1
    static final int STOPPING           = 2

    private static String   detachmentOperationUserId
    private static Date     detachmentOperationStartDate
    private static int      detachmentOperationState = NOT_RUNNING

    // Detachment states and their display names
    static final int    DETACH_PHASE_ZERO_PREPARE_FOR_DETACHMENT_ID                                   = 0
    static final String DETACH_PHASE_ZERO_PREPARE_FOR_DETACHMENT_NAME                                 = "Preparing for a detachment (step 1 of 6)"
    static final int    DETACH_PHASE_ONE_SANITY_CHECKS_AND_HOST_INFO_FETCH_ID                         = 1
    static final String DETACH_PHASE_ONE_SANITY_CHECKS_AND_HOST_INFO_FETCH_NAME                       = "Running validation and comms check with a client (step 2 of 6)"
    // Note: that this phase 2 includes a case of successfully invoking Baseline action as well as Baseline action finishing with an error
    // (ie. when the Baseline Notification has ( !baselineNotification.successful || !baselineNotification.dataMap || !baselineNotification.dataMap[ "fileName" ] )
    static final int    DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_ID               = 2
    static final String DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_NAME             = "Running Baseline action (step 3 of 6)"
    // Note: that this phase 3 includes a case of successfully invoking Assessment action as well as Assessment action finishing with an error
    // (ie. when the Assessment Notification has ( !assessmentNotification.successful || !assessmentNotification.dataMap || !assessmentNotification.dataMap[ "fileName" ] )
    static final int    DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_ID               = 3
    static final String DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_NAME             = "Running Assessment action (step 4 of 6)"
    static final int    DETACH_PHASE_FOUR_FETCH_BASELINE_ASSESS_REPORTS_AND_SB_CLIENT_APP_LOG_ID      = 4
    static final String DETACH_PHASE_FOUR_FETCH_BASELINE_ASSESS_REPORTS_AND_SB_CLIENT_APP_LOG_NAME    = "Fetching reports and client log (step 5 of 6)"
    static final int    DETACH_PHASE_FIVE_RETAIN_PROFILES_AND_COMPLETE_DETACHMENT_ID                  = 5
    static final String DETACH_PHASE_FIVE_RETAIN_PROFILES_AND_COMPLETE_DETACHMENT_NAME                = "Retaining profiles and finalizing detachment (step 6 of 6)"
    // Aborting steps are considered separate "phases" (note that Aborting can only happen while in step 2 or 3; if already reached step 4 abort is not done)
    static final int    DETACH_PHASE_ABORT_BASELINE_ACTION_ID                                         = 6
    static final String DETACH_PHASE_ABORT_BASELINE_ACTION_NAME                                       = "Aborting Baseline action"
    static final int    DETACH_PHASE_ABORT_ASSESS_ACTION_ID                                           = 7
    static final String DETACH_PHASE_ABORT_ASSESS_ACTION_NAME                                         = "Aborting Assessment action"


    static final String SB_LOG_MAXIMUM_5MB_SIZE_EXCEEDED_ERROR  = "which is larger than the maximum allowed transfer size of 5 MB"
    static final String DETACHMENT_STATUS_UNAVAILABLE           = "Detachment status unavailable."
    static final String DETACHMENT_OPERATION_STOPPED_ERROR      = "detachment operation was stopped"

    // singleton instance
    private static instance;

    public static SBDetachmentUtil getInstance(){
        if( !instance ){
            instance = new SBDetachmentUtil()
        }
        return instance
    }

    /**
     * Called when a detachment operation is started.
     * 
     * If this is the very first detach operation sets the detachmentOperationState=STARTED, detachmentOperationUserId and detachmentOperationStartDate
     * Otherwise (there is already detachment operation in the system) throws an exception.
     */
    public void startDetachment(){

        boolean isAlreadyRunning = false

        // Allow only one thread in critical section which is update to instance properties
        synchronized ( instance ){

            if( instance.detachmentOperationState == NOT_RUNNING ){
                // detachment operation is NOT running
                instance.detachmentOperationState = STARTED
                instance.detachmentOperationStartDate   = new Date()
                String loggedInUserId
                try
                {
                    loggedInUserId = SecurityUtils.subject?.principal
                }
                catch( Exception e )
                {
                    loggedInUserId = "unknown"
                }
                instance.detachmentOperationUserId  = loggedInUserId
            }
            else {
                // detachment operation is already running (either STARTED or STOPPING)
                isAlreadyRunning = true
            }
        }

        if( isAlreadyRunning ){
            // If a detachment was already running then throw exception as only one detachment
            // operation can run in the entire system at a time       
            throw new RuntimeException( "Detachment operation started on ${instance.detachmentOperationStartDate} by user ${instance.detachmentOperationUserId} is currently running. Only one detachment operation is allowed at a time." )
        }
    }

    // Called when a detachment operation stop is requested. Assumes, operation was already started.
    // Otherwise, throws an exception.
    public void stopDetachment(){

        boolean isStarted = true
        int currentState  = NOT_RUNNING

        // Allow only one thread in critical section which is update to instance properties
        synchronized ( instance ){

            if( instance.detachmentOperationState == STARTED ){
                instance.detachmentOperationState  = STOPPING
            }
            else {
                isStarted = false
            }
        }

        if( !isStarted ){
            // If a detachment was NOT started then throw exception as only started detachment can be stopped
            String message
            if( currentState == STOPPING ){
                message = "there is already such a request."
            }
            else { // NOT_RUNNING
                message = "no detachment operation is running."
            }
            throw new RuntimeException( "Detachment stop request cannot be processed since ${message}" )
        }
    }

    // Called after the completion of the stop detachment request. Assumes, operation was already requested to be stopped.
    // Otherwise, throws an exception.
    public void detachmentComplete(){

        boolean isStopping = true
        int currentState  = NOT_RUNNING

        // Allow only one thread in critical section which is update to instance properties
        synchronized ( instance ){

            if( instance.detachmentOperationState == STOPPING ){
                instance.detachmentOperationState       = NOT_RUNNING
                // clear userId and detachment start date
                instance.detachmentOperationUserId      = null
                instance.detachmentOperationStartDate   = null
            }
            else {
                isStopping = false

                currentState = instance.detachmentOperationState
            }
        }

        if( !isStopping ){
            // If a detachment was NOT stopping then throw exception as only stopping detachment can be completed
            String message
            if( currentState == STARTED ){
                message = "detachment operation was started and is in progress, but there is no detachment stop request for it."
            }
            else { // NOT_RUNNING
                message = "no detachment operation is running."
            }
            throw new RuntimeException( "Detachment complete request cannot be processed since ${message}" )
        }
    }

    // Returns true if detachment was requested to be stopped (or aborted).
    public boolean stopDetachmentRequested(){
        return instance.detachmentOperationState == STOPPING
    }

    // Returns true if the detachment process is currently STARTED or STOPPING, which BOTH are considered as running.
    public boolean isDetachmentInProgress(){
        return instance.detachmentOperationState != NOT_RUNNING
    }

    /**
    * Returns user formatted status message (including the name of the currently executing detachment phase given
    * the persisted phase from status, which is persisted after each "action" is done)
    *
    * @param String lastPersistedStatus - the persisted detach status
    * @return detachment phase name
    */
    static public String getUserFormattedStatusMessage( String lastPersistedStatus ){

        // Extract the last persisted phase from status
        int lastPersistedPhaseFromStatus = -1

        // There was an error, lastPersistedStatus has format "lastPersistedPhaseFromStatus:{actual error message}"
        int indexOfErrorSeparator = lastPersistedStatus.indexOf( ":" )
        String lastPersistedPhaseFromStatusAsString
        if( indexOfErrorSeparator > 0 ){ // can't be == 0
            lastPersistedPhaseFromStatusAsString = lastPersistedStatus.substring( 0, indexOfErrorSeparator)
        }
        else { // no : assume entire lastPersistedStatus is lastPersistedPhaseFromStatusAsString
            lastPersistedPhaseFromStatusAsString = lastPersistedStatus
        }
        // Try to parse to int
        try {
            lastPersistedPhaseFromStatus = lastPersistedPhaseFromStatusAsString.toInteger()
        }
        catch( Exception e ){
            lastPersistedPhaseFromStatus = -1
        }

        // currentPhaseName is the next phase name *after* lastPersistedPhaseFromStatus
        String currentPhaseName = "Unknown"
        if( lastPersistedPhaseFromStatus == DETACH_PHASE_ZERO_PREPARE_FOR_DETACHMENT_ID ){
            currentPhaseName = DETACH_PHASE_ZERO_PREPARE_FOR_DETACHMENT_NAME
        }
        else if( lastPersistedPhaseFromStatus == DETACH_PHASE_ONE_SANITY_CHECKS_AND_HOST_INFO_FETCH_ID ){
            currentPhaseName = DETACH_PHASE_ONE_SANITY_CHECKS_AND_HOST_INFO_FETCH_NAME
        }
        else if( lastPersistedPhaseFromStatus == DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_ID ){
            currentPhaseName = DETACH_PHASE_TWO_INVOKE_BASELINE_AND_WAIT_FOR_ITS_COMPLETION_NAME
        }
        else if( lastPersistedPhaseFromStatus == DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_ID ){
            currentPhaseName = DETACH_PHASE_THREE_INVOKE_ASSESS_AND_WAIT_FOR_ITS_COMPLETION_NAME
        }
        else if( lastPersistedPhaseFromStatus == DETACH_PHASE_FOUR_FETCH_BASELINE_ASSESS_REPORTS_AND_SB_CLIENT_APP_LOG_ID ){
            currentPhaseName = DETACH_PHASE_FOUR_FETCH_BASELINE_ASSESS_REPORTS_AND_SB_CLIENT_APP_LOG_NAME
        }
        else if ( lastPersistedPhaseFromStatus == DETACH_PHASE_FIVE_RETAIN_PROFILES_AND_COMPLETE_DETACHMENT_ID ){
            currentPhaseName = DETACH_PHASE_FIVE_RETAIN_PROFILES_AND_COMPLETE_DETACHMENT_NAME
        }
        else if ( lastPersistedPhaseFromStatus == DETACH_PHASE_ABORT_BASELINE_ACTION_ID ){
            currentPhaseName = DETACH_PHASE_ABORT_BASELINE_ACTION_NAME
        }
        else if ( lastPersistedPhaseFromStatus == DETACH_PHASE_ABORT_ASSESS_ACTION_ID ){
            currentPhaseName = DETACH_PHASE_ABORT_ASSESS_ACTION_NAME
        }

        // There was an error
        if( indexOfErrorSeparator > 0 ){
            // Extract actual error, which is whatever follows after ":" within lastPersistedStatus
            String actualErrorMessage = lastPersistedStatus.substring( indexOfErrorSeparator + 1 )

            return "${currentPhaseName} had an error [${actualErrorMessage}]"
        }
        // no error, return current phase name
        else { 
            return currentPhaseName
        }
    }
}

