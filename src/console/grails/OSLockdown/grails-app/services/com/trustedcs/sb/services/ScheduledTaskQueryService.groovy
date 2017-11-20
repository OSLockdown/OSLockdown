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

// web service classes
import com.trustedcs.sb.taskverification.QueryHandlerInterface;
import com.trustedcs.sb.services.sei.DispatcherTask;
import com.trustedcs.sb.services.sei.TaskVerificationQuery;
import com.trustedcs.sb.services.sei.TaskVerificationResponse;

// domain object classes
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.scheduler.ScheduledTask;

// OS Lockdown Utils
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.FingerprintHelper;
import com.trustedcs.sb.license.SbLicense;

class ScheduledTaskQueryService implements QueryHandlerInterface {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ScheduledTaskQueryService");

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def securityProfileService;
    def baselineProfileService;

    /**
     * Scheduled Task Query handler for the console
     *
     * This method is called from the web service implementation in order to find
     * out if a scheduled task is still valid and if not then return the new
     * profiles that are associated with the task.
     *
     * @param query
     * @return the verification response
     */
    public TaskVerificationResponse query(TaskVerificationQuery query) {

        // create the SEI response
        TaskVerificationResponse response = new TaskVerificationResponse();

        // response information
        response.code = 200;
        response.reasonPhrase = "Okay";

        // query result information
        response.queryResultCode = 0;
        response.queryResultInfo = "Okay";

        try {
            // check for license
            if ( !(SbLicense.instance.isValid()) ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Console license expired.";
                return response;
            }

            // ids
            def ids;

            // parse out the ids;
            // ids[0] = task.id
            // ids[1] = client.id
            // ids[2] = group.id
            String[] idStrings = query.getId().split(":");
            if ( idStrings.size() != 3 ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Query does not follow the correct id format.";
                return response;
            }

            try {
                ids = idStrings.collect { val ->
                    val.toLong();
                }
            }
            catch ( Exception nfe ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Query does not follow the correct id format.";
                return response;
            }

            // check to see if the scheduled task exists
            ScheduledTask task = ScheduledTask.get(ids[0]);
            if ( !task ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Task no longer exists";
                return response;
            }

            // check to see if the client exists
            Client client = Client.get(ids[1]);
            if ( !client ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Client no longer exists";
                return response;
            }

            // check to see if the group exists
            def groupResult = Group.withCriteria {
                eq('id',ids[2])
                join 'profile'
            }
            if ( !groupResult ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Group no longer exists";
                return response;
            }

            // task's group and group listing match
            def result = ScheduledTask.withCriteria {
                eq('group',groupResult[0])
                eq('id',task.id)
            }
            if ( !result ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Task no longer associated with the specified group";
                return response;
            }

            // set the task on the response
            response.task = createSeiDispatcherTask(task);
            // set the dispatcher task id
            response.task.id = "${task.id}:${client.id}:${groupResult[0].id}";

            // finger print matching
            String profileFingerprint;
            // check to see if the action requires a security profile
            if ( task.actions.contains('s') || task.actions.contains('a') ) {
                // scan or apply
                // find the security profile
                Profile securityProfile = groupResult[0].profile;
                // does the group have a profile anymore
                if (securityProfile) {
                    // find the xml file location
                    File file = securityProfileService.getXmlLocation(securityProfile);
                    // security profile fingerprint
                    profileFingerprint = FingerprintHelper.getSHA1String(file);
                    // compare the dispatcher security profile fingerprint and the one on the console
                    if ( profileFingerprint != query.getSecurityProfileFingerprint() ) {
                        response.queryResultCode = 3;
                        response.queryResultInfo = "Security Profile Changed";
                        response.task.securityProfile = file.getText();
                    }                    
                }
                else {
                    // the profile not longer exists
                    response.queryResultCode = 1;
                    response.queryResultInfo = "Security Profile no longer specified";                    
                }
            }
            if ( task.actions.contains('b') ) {
                // baseline
                // find the baseline profile
                BaselineProfile baselineProfile = groupResult[0].baselineProfile;
                // does the group have a profile anymore
                if (baselineProfile) {
                    // find the xml file location
                    File file = baselineProfileService.getXmlLocation(baselineProfile);
                    // security profile fingerprint
                    profileFingerprint = FingerprintHelper.getSHA1String(file);
                    // compare the dispatcher security profile fingerprint and the one on the console
                    if ( profileFingerprint != query.getBaselineProfileFingerprint() ) {
                        response.queryResultCode = 3;
                        response.queryResultInfo = "Baseline Profile Changed";
                        response.task.baselineProfile = file.getText();
                    }                    
                }
                else {
                    // the profile not longer exists
                    response.queryResultCode = 1;
                    response.queryResultInfo = "Baseline Profile no longer specified";                    
                }
            }
        }
        catch (Exception e) {
            m_log.error("Unable to verify task",e);
            // internal error, do what you were going to do
            response.queryResultCode = 0;
            response.queryResultInfo = e.message;
            return response;
        }

        return response;
    }

    /**
     * Creates a dispatcher task with the attributes of the domain object
     * This sei object can't be generated by the service due to the fact that it's
     * a different type of dispatcher task.  This task is server based, the service's
     * is client based.
     *
     * @param scheduledTask the domain object
     * @return the sei interface object for webservices
     */
    private DispatcherTask createSeiDispatcherTask(ScheduledTask scheduledTaskInstance) {
        def dispatcherTask = new DispatcherTask();
        dispatcherTask.actions = scheduledTaskInstance.actions;
        dispatcherTask.loggingLevel = scheduledTaskInstance.loggingLevel;
        dispatcherTask.periodType = scheduledTaskInstance.periodType;
        dispatcherTask.periodIncrement = scheduledTaskInstance.periodIncrement;
        dispatcherTask.hour = scheduledTaskInstance.hour;
        dispatcherTask.minute = scheduledTaskInstance.minute;
        return dispatcherTask;
    }
}
