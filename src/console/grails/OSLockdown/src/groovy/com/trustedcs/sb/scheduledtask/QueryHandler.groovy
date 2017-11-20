/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.scheduledtask;

// web service classes
import com.trustedcs.sb.taskverification.QueryHandlerInterface;
import com.trustedcs.sb.services.sei.DispatcherTask;
import com.trustedcs.sb.services.sei.TaskVerificationQuery;
import com.trustedcs.sb.services.sei.TaskVerificationResponse;
import com.trustedcs.sb.services.sei.TaskVerificationResponse;

// domain object classes
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.scheduler.ScheduledTask;

// OS Lockdown Utils
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.FingerprintHelper;
import com.trustedcs.sb.license.SbLicense;

import org.apache.log4j.Logger;

/**
 * @author amcgrath
 * Result codes come from com.trustedcs.sb.services.sei.TaskVerificationResponse
 * 
 */
public class QueryHandler implements QueryHandlerInterface {
	
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.scheduledtask.QueryHandler");

    public TaskVerificationResponse query(TaskVerificationQuery query) {
		
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
			
            // parse out the ids;
            // ids[0] = task.id
            // ids[1] = client.id
            // ids[2] = group.id
            def idStrings = query.getId().split(":");
            if ( idStrings.size() != 3 ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Query does not follow the correct id format.";
                return response;
            }
            def ids = idStrings.collect { val ->
            	Long.parseLong(val);
            }
			
            // task exists
            def task = ScheduledTask.get(ids[0]);
            if ( !task ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Task no longer exists";
                return response;
            }
			
            // set the task on the response
            response.task = createDispatcherTask(task);
            // client exists
            def client = Client.get(ids[1]);
            if ( !client ) {
                response.queryResultCode = 2;
                response.queryResultInfo = "Client no longer exists";
                return response;
            }
			
            // group exists
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
			
            // set the dispatcher task id
            response.task.id = "${task.id}:${client.id}:${groupResult[0].id}";
			
            // check to see if the action requires a profile
            if ( task.actions.contains('s') || task.actions.contains('a') ) {
                // finger print matching
                def profilePrint;
                def profile = groupResult[0].profile;
                if (profile) {
                    def file = SBFileSystemUtil.getProfile(profile.fileName);
                    profilePrint = FingerprintHelper.getSHA1String(file);
                    if ( profilePrint != query.getProfileFingerprint() ) {
                        response.queryResultCode = 3;
                        response.queryResultInfo = "Profile Changed";
                        response.profile = file.getText();
                    }
                    return response;
                }
                else {
                    response.queryResultCode = 1;
                    response.queryResultInfo = "Profile no longer specified";
                    return response;
                }
            }
        }
        catch (NumberFormatException nfe) {
            response.queryResultCode = 2;
            response.queryResultInfo = "Query does not follow the correct id format.";
            return response;
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
    private DispatcherTask createDispatcherTask(def scheduledTaskInstance) {
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
