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

// log4j access
import org.apache.log4j.Logger;

// security access to get the user
import org.apache.shiro.SecurityUtils;

import java.text.MessageFormat;

class AuditLogService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.audit.AuditLogger");

    // Transactional
    boolean transactional = false;

    // injected services
    def messageSource;

    // message formats

    // log a authentication action
    private static MessageFormat authActionFormat = new MessageFormat("actor[{0}] action[{1}] status[{2}]");

    // log access failure
    private static MessageFormat accessActionFormat = new MessageFormat("actor[{0}] action[{1}] status[{2}] uri[{3}]");

    // log an action "actor[${actor}] action[${action}] ${objectName}[${object}]"
    private static MessageFormat genericActionFormat = new MessageFormat("actor[{0}] action[{1}] {2}[{3}]");

    // log an "actor[${actor}] action[${action}] ${objectName}[${objectIdentifier}] profile[${profileName}]"
    private static MessageFormat profileActionFormat = new MessageFormat("actor[{0}] action[{1}] {2}[{3}] profile[{4}]");

    /**
     * Generic audit logging statement method
     * @param statement
     */
    void log(def statement) {
        m_log.info(statement);
    }

    /**
     * Rbac audit logging method
     * @param action
     * @param userName
     */
    void logRbac(def action, def userName) {
        logGenericAction(action,"user",userName)
    }

    /**
     * Profile audit logging method
     * @param action
     * @param profileName
     */
    void logProfile(def action, def profileName) {
        logGenericAction(action,"profile",profileName);
    }

    /**
     * Baseline Profile audit logging method
     * @param action
     * @param baselineProfileName
     */
    void logBaselineProfile(def action, def baselineProfileName) {
        logGenericAction(action,"baseline profile",baselineProfileName);
    }

    /**
     * Report audit logging method
     * @param action
     * @param reportType
     * @param reportName
     */
    void logReport(def action, def reportType, def reportName) {
        logGenericAction(action,"${reportType} report",reportName)
    }

    /**
     * Client audit logging method
     * @param action
     * @param clientName
     */
    void logClient(def action, def clientName) {
        logGenericAction(action,"client",clientName);
    }

    /**
     * Processor audit logging method
     * @param action
     * @param clientName
     */
    void logProcessor(def action, def processorName) {
        logGenericAction(action,"processor",processorName);
    }

    /**
     * Client action audit logging method
     * @param action
     * @param clientName
     * @param profileName
     */
    void logClientAction(def action, def clientName, def profileName) {
        logProfileAction(action,"client",clientName,profileName);
    }

    /**
     * Group audit logging method
     * @param action
     * @param groupName
     */
    void logGroup(def action, def groupName) {
        logGenericAction(action,"group",groupName);
    }

    /**
     * Group action audit logging method
     * @param action
     * @param groupName
     * @param profileName
     */
    void logGroupAction(def action, def groupName, def profileName) {
        logProfileAction(action,"group",groupName,profileName);        
    }

    /**
     * Task action audit logging method
     * @param action
     * @param taskIdentifier ( '$group($periodType-$time)' )
     */
    void logTask(def action, def taskIdentifier) {
        logGenericAction(action,"task",taskIdentifier);
    }

    /**
     * Generic audit logging function to be called by convience methods
     * 
     * @param action
     * @param objectName
     * @param objectIdentifier
     */
    void logAction(def action, def objectName, def objectIdentifier) {
        if ( SecurityUtils.subject?.principal ) {
            logGenericAction(SecurityUtils.subject.principal,action,objectName,objectIdentifier);
        }
        else {
            logGenericAction("sbwebapp",action,objectName,objectIdentifier);
        }
    }
    
    /**
     * Log the access to a given uri ( only used for failures ) using the Security Utils subject
     *
     * @param action
     * @param status
     * @param uri
     */
    void logAccessAction(def action, def status, def uri) {
        if ( SecurityUtils.subject?.principal ) {
            logAccessAction(SecurityUtils.subject.principal,action,status,uri);
        }
        else {
            logAccessAction("sbwebapp",action,status,uri);
        }        
    }

    /**
     * Log the access to the given uri failure
     *
     * @param actor
     * @param action
     * @param status
     * @param uri
     */
    void logAccessAction(def actor, def action, def status, def uri) {
        m_log.info(accessActionFormat.format([actor,action,status,uri] as Object[]))
    }

    /**
     * Log the authentication action using the security utils actor
     *
     * @param action
     * @param status
     */
    void logAuthAction(def action, def status) {
        try {
            if ( SecurityUtils.subject?.principal ) {
                logAuthAction(SecurityUtils.subject.principal,action,objectName,objectIdentifier);
            }
            else {
                logAuthAction("sbwebapp",action,objectName,objectIdentifier);
            }
        }
        catch ( IllegalStateException exception ) {
            // stupid shiro error
            logAuthAction("sbwebapp",action,objectName,objectIdentifier);
        }
    }

    /**
     * Log the authentication action using the passed actor
     *
     * @param actor
     * @param action
     * @param status
     */
    void logAuthAction(def actor, def action, def status) {
        m_log.info(authActionFormat.format([actor,action,status] as Object[]));
    }

    /**
     * Generic audit logging function to be called by convience methods
     *
     * @param action
     * @param objectName
     * @param objectIdentifier
     */
    void logGenericAction(def action, def objectName, def objectIdentifier) {
        try {
            if ( SecurityUtils.subject?.principal ) {
                logGenericAction(SecurityUtils.subject.principal,action,objectName,objectIdentifier);
            }
            else {
                logGenericAction("sbwebapp",action,objectName,objectIdentifier);
            }
        }
        catch ( IllegalStateException exception) {
            // stupid shiro error
            logGenericAction("sbwebapp",action,objectName,objectIdentifier);
        }
    }

    /**
     * Generic audit logging function to be called by convience methods
     *
     * @param actor
     * @param action
     * @param objectName
     * @param objectIdentifier
     */
    void logGenericAction(def actor, def action, def objectName, def objectIdentifier) {
        m_log.info(genericActionFormat.format([actor,action,objectName,objectIdentifier] as Object[]));
    }

    /**
     * @param action
     * @param objectName
     * @param objectIdentifier
     * @param profileName
     */
    void logProfileAction(def action, def objectName, def objectIdentifier, def profileName) {
        try {
            if ( SecurityUtils.subject?.principal ) {
                logProfileAction(SecurityUtils.subject.principal,action,objectName,objectIdentifier,profileName);
            }
            else {
                logProfileAction("sbwebapp",action,objectName,objectIdentifier,profileName);
            }
        }
        catch ( IllegalStateException exception ) {
            // stupid shiro error
            logProfileAction("sbwebapp",action,objectName,objectIdentifier,profileName);
        }
    }

    /**
     * Logging function for actions that involve profiles
     *
     * @param actor
     * @param action
     * @param objectName
     * @param objectIdentifier
     * @param profileName
     */
    void logProfileAction(def actor, def action, def objectName, def objectIdentifier, def profileName) {
        m_log.info(profileActionFormat.format([actor,action,objectName,objectIdentifier,profileName] as Object[]));
    }

}
