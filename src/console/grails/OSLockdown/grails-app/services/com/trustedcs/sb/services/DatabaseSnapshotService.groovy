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

import com.trustedcs.sb.exceptions.*;
import groovy.util.slurpersupport.GPathResult;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Processor;
import com.trustedcs.sb.preferences.AccountPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationFlag;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.scheduler.ScheduledTask;
import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.auth.shiro.ShiroUserRoleRel;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

class DatabaseSnapshotService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.DatabaseSnapshotService");

    // constant for showing success of object load
    static final String SUCCESS = "successful";

    // Transactional
    boolean transactional = false;

    // injected services
    def messageSource;
    def rbacService;
    def securityProfileService;
    def baselineProfileService;
    def processorService;
    def clientService;
    def groupService;
    def scheduledTaskService;
    def accountPreferencesService;
    def upstreamNotificationPreferencesService;
    def upstreamNotificationService;
    def grailsApplication;
        
    /**
     * Exports the contents of the database to an xml file. Both security and
     * baseline profiles that are not write protected and exported as well as,
     * groups, clients and tasks ( as well as their associations together )
     */
    def exportToXml() throws DatabaseSnapshotException {
        
        def dbVersion = grailsApplication.metadata["app.version"];

        // create the export directory if it doesn't exist
        File dbExportDir = SBFileSystemUtil.get(SB_LOCATIONS.DB_EXPORT);
        if ( !dbExportDir.exists() ) {
            if ( !dbExportDir.mkdirs() ) {
                throw new DatabaseSnapshotException(message:"Unable to create directory ${dbExportDir.absolutePath}");
            }
        }

        // create the file and use the current time stamp as a name for it
        int tstamp = System.currentTimeMillis() / 1000;
        File file = new File(dbExportDir,"sbdb-${tstamp}.xml");

        try {
            // print writer for the xml snapshot
            def writer = file.newPrintWriter("UTF-8");

            // create the xml
            writer.println("<sbDB exported='${new Date()}' dbVersion='${dbVersion}'>");

	        // account preferences - we only have one entry, no need to have extra scoping
            writer.println(accountPreferencesService.toXmlString(accountPreferencesService.getAccountPreferences(),false));         

	        // upstreamNotification preferences - we only have one entry, no need to have extra scoping
            writer.println(upstreamNotificationPreferencesService.toXmlString(upstreamNotificationPreferencesService.getUpstreamNotificationPreferences(),false));         

	        // upstreamNotificationFlag preferences - 
            writer.println("  <upstreamNotificationFlags>");
            UpstreamNotificationFlag.list().each { upstreamNotificationFlag -> 
               writer.println(upstreamNotificationService.toXmlString(upstreamNotificationFlag, false));
            }
            writer.println("  </upstreamNotificationFlags>");

            // users
            writer.println("  <users>");
            ShiroUserRoleRel.list().each { userRoleTuple ->
                if ( userRoleTuple.user.username != "admin") {
                    writer.println(rbacService.toXmlString(userRoleTuple,false));
                }
            }
            writer.println("  </users>")

            
            // security profiles
            writer.println("  <profiles>");
            Profile.withCriteria {
                eq('writeProtected',false);
            }.each { securityProfile ->
                writer.println(securityProfileService.toXmlString(securityProfile,false));
            }
            writer.println("  </profiles>");

            // baseline profiles
            writer.println("  <baselineProfiles>");
            BaselineProfile.withCriteria { 
                eq('writeProtected',false);
            }.each { baselineProfile ->
                writer.println(baselineProfileService.toXmlString(baselineProfile,false));
            }
            writer.println("  </baselineProfiles>");

            // processors
            writer.println("  <processors>");
            Processor.listOrderByName().each { processorInstance ->
                writer.println(processorService.toXmlString(processorInstance,false));
            }
            writer.println("  </processors>");


            // clients
            writer.println("  <clients>");
            Client.listOrderByName().each { clientInstance ->
                writer.println(clientService.toXmlString(clientInstance,false));
            }
            writer.println("  </clients>");

            // groups
            writer.println("  <groups>");
            Group.list().each { groupInstance ->
                writer.println(groupService.toXmlString(groupInstance,false));
            }
            writer.println("  </groups>");

            // tasks;
            writer.println("  <tasks>");
            ScheduledTask.list().each { taskInstance ->
                writer.println(scheduledTaskService.toXmlString(taskInstance,false));
            }
            writer.println("  </tasks>");

            // close openning tag
            writer.println("</sbDB>");
            writer.flush();
        }
        catch ( Exception e ) {
            m_log.error("Unable to export DB",e);
            throw new DatabaseSnapshotException(message:e.message);
        }

        // return the created file
        return file;
    }

    /**
     * Import configuration of security|baseline profiles
     * groups, clients and tasks into the console from an xml
     * file
     *
     * @param file
     */
    def importFromXml(File file) throws DatabaseSnapshotException {
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(true);
            def xml = slurper.parse(file);
            return importFromXml(xml);
    	}
    	catch ( Exception e ) {
            m_log.error("Unable to parse database snapshot",e);
            throw new DatabaseSnapshotException(message:e.message);
    	}
    }

    /**
     * Import configuration of security|baseline profiles, groups, clients
     * and taks into the console from an input stream that is an xml document.
     * Used from the upload database snapshot form on in the manage database
     * pages.
     *
     * @param inputStream
     */
    def importFromXml(InputStream inputStream) throws DatabaseSnapshotException {
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(true);
            def xml = slurper.parse(inputStream);
            return importFromXml(xml);
    	}
    	catch ( Exception e ) {
            m_log.error("Unable to parse database snapshot",e);
            throw new DatabaseSnapshotException(message:e.message);
    	}
    }

    def dbVersionNotAcceptable(vers1, vers2) {
        def v1XYZ = vers1.split('\\.');
        def v2XYZ = vers2.split('\\.');
        
        for (iter in 0..2) {
            if (v1XYZ[iter] > v2XYZ[iter]) return true;
        }
        return false;
    }

    /**
     * Import configuration of security|baseline profiles
     * groups, clients and tasks into the console from an xml
     * file that has be parsed already
     *
     * @param xml
     */
    def importFromXml(GPathResult xml) throws DatabaseSnapshotException {

        def results = [ 'user' : [:],
                        'securityProfile' : [:],
                        'baselineProfile' : [:],
                        'processor' : [:],
                        'client' : [:],
                        'group' : [:],
                        'scheduledTask' : [:],
                        'accountPreferences' : [:],
                        'upstreamNotificationPreferences' : [:],
                        'upstreamNotificationFlag' : [:]]

        def currVersion = grailsApplication.metadata["app.version"].split('-')[0];
        def snapVersion = xml.@dbVersion.text().split('-')[0];

        m_log.info("Snapshot import - snapshot from version ${snapVersion}, current application is version ${currVersion}");

        // verify that we're not importing a snapshot from a *newer* x.y.z release - DB format
        // with the x.y.z release should be compatible

        if (snapVersion && dbVersionNotAcceptable(snapVersion, currVersion)) {
            throw new DatabaseSnapshotException (message:"Unable to import - current Console is version ${currVersion} but snapshot is from version ${snapVersion}");
        }               
        
        // users
        ShiroUserRoleRel userRoleRelationship;
        xml.users.user.each { userXml ->
            try {
                userRoleRelationship = rbacService.fromXml(userXml);
                results['user'].put("${userRoleRelationship.user.username}[${userRoleRelationship.role.name}]",SUCCESS);
            }
            catch ( SbRbacException rbacException ) {
                m_log.error("Unable to import user from xml fragment");
                if ( rbacException.message ) {
                    results['user'].put(userXml.@name.text(),rbacException.message);
                }
                else {
                    def errorMessage = "";
                    rbacException.shiroUser.errors.allErrors.each { error ->
                        errorMessage += messageSource.getMessage(error,null);
                        errorMessage += "\n";
                    }
                    results['user'].put(userXml.@name.text(),errorMessage);
                }
            }
        }

	// Account Preferences
        AccountPreferences accountPreferences;
        if (xml.accountPreferences) {
          try {
            accountPreferences = accountPreferencesService.fromXml(xml.accountPreferences);
            results['accountPreferences'].put("AccountPreferences",SUCCESS);
          }
          catch (AccountPreferencesException accountPreferencesException) {
            m_log.error("Unable to import account preferences from xml fragment");
            if ( accountPreferencesException.message ) {
               results['accountPreferences'].put('AccountPreferences',accountPreferencesException.message);
            }
            else {
              def errorMessage = "";
              accountPreferencesException.accountPrefernces.errors.allErrors.each { error ->
                errorMessage += messageSource.getMessage(error,null);
                errorMessage += "\n";
              }
              results['accountPreferences'].put('AccountPreferences',errorMessage);
            }
          }
        }

	// UpstreamNotification Preferences
        UpstreamNotificationPreferences upstreamNotificationPreferences;
        if (xml.upstreamNotificationPreferences) {
          try {
            upstreamNotificationPreferences = upstreamNotificationPreferencesService.fromXml(xml.upstreamNotificationPreferences);
            results['upstreamNotificationPreferences'].put("UpstreamNotificationPreferences",SUCCESS);
          }
          catch (UpstreamNotificationPreferencesException upstreamNotificationPreferencesException) {
            m_log.error("Unable to import upstream notification preferences from xml fragment");
            if ( upstreamNotificationPreferencesException.message ) {
               results['upstreamNotificationPreferences'].put('UpstreamNotificationPreferences',upstreamNotificationPreferencesException.message);
            }
            else {
              def errorMessage = "";
              upstreamNotificationPreferencesException.upstreamNotificationPreferences.errors.allErrors.each { error ->
                errorMessage += messageSource.getMessage(error,null);
                errorMessage += "\n";
              }
              results['upstreamNotificationPreferences'].put('UpstreamNotificationPreferences',errorMessage);
            }
          }
        }

        // upstreamNotificationFlag preferences
        UpstreamNotificationFlag upstreamNotificationFlag;
        xml.upstreamNotificationFlags.upstreamNotificationFlag.each { flagXml ->
            try {
                upstreamNotificationFlag = upstreamNotificationService.fromXml(flagXml);
                results['upstreamNotificationFlag'].put(upstreamNotificationFlag.upstreamNotificationType.quartzJobName,SUCCESS);
            }
            catch ( UpstreamNotificationFlagException upstreamNotificationFlagException ) {
                m_log.error("Unable to import upstream Notification Flag setting from xml fragment");
                if ( upstreamNotificationFlagException.message ) {
                    results['upstreamNotificationFlag'].put(flagXml.@quartzJobName.text(),upstreamNotificationFlagException.message);
                }
                else {
                    def errorMessage = "";
                    upstreamNotificationFlagException.upstreamNotificationFlag.errors.allErrors.each { error ->
                        errorMessage += messageSource.getMessage(error,null);
                        errorMessage += "\n";
                    }
                    results['upstreamNotificationFlag'].put(flagXml.@quartzJobName.text(),errorMessage);
                }
            }
        }



        // security profiles
        Profile securityProfile;
        xml.profiles.profile.each { securityProfileXml ->
            try {
                securityProfile = securityProfileService.fromXml(null,securityProfileXml);
                results['securityProfile'].put(securityProfile.name,SUCCESS);
            }
            catch ( SecurityProfileException securityProfileException ) {
                m_log.error("Unable to import security profile from xml fragment");
                if ( securityProfileException.message ) {
                    results['securityProfile'].put(securityProfileXml.@name.text(),securityProfileException.message);
                }
                else {
                    def errorMessage = "";
                    securityProfileException.securityProfile.errors.allErrors.each { error ->
                        errorMessage += messageSource.getMessage(error,null);
                        errorMessage += "\n";
                    }
                    results['securityProfile'].put(securityProfileXml.@name.text(),errorMessage);
                }
            }
        }

        // baseline profiles
        BaselineProfile baselineProfile;
        xml.baselineProfiles.BaselineProfile.each { baselineProfileXml ->
            try {
                baselineProfile = baselineProfileService.fromXml(baselineProfileXml);
                results['baselineProfile'].put(baselineProfile.name,SUCCESS);
            }
            catch ( BaselineProfileException baselineProfileException ) {
                m_log.error("Unable to import baseline profile from xml fragment");
                if ( baselineProfileException.message ) {
                    results['baselineProfile'].put(baselineProfileXml.@name.text(),baselineProfileException.message);
                }
                else {
                    def errorMessage = "";
                    baselineProfileException.baselineProfileInstance.errors.allErrors.each { error ->
                        errorMessage += messageSource.getMessage(error,null);
                        errorMessage += "\n";
                    }
                    results['baselineProfile'].put(baselineProfileXml.@name.text(),errorMessage);
                }
                
            }
        }

        // processors
        Processor processorInstance;
        xml.processors.processor.each { processorXml ->
            try {
            	processorInstance = processorService.fromXml(processorXml);
                results['processor'].put(processorInstance.name,SUCCESS);
            }
            catch ( ProcessorException processorException ) {
                m_log.error("Unable to import processor from xml fragment",processorException);
                if ( processorException.message ) {
                    results['processor'].put(processorXml.name.text(),processorException.message);
                }
                else {
                    def errorMessage = "";
                    processorException.processorInstance.errors.allErrors.each { error ->
                        errorMessage += messageSource.getMessage(error,null);
                        errorMessage += "\n";
                    }
                    results['processor'].put(processorXml.name.text(),errorMessage);
                }
            }
        }

        // clients
        Client clientInstance;
        def clientIdMap = [:]
        xml.clients.client.each { clientXml ->

            if( lockAndReleaseExpirationDateError ){
                m_log.error( lockAndReleaseExpirationDateError );
                results['client'].put(clientXml.name.text(), lockAndReleaseExpirationDateError );
            }
            else {
                  if (true) {
                    try {
                        clientInstance = clientService.fromXml(clientXml);
                        clientIdMap[clientXml.@id.text()] = clientInstance.id;
                        results['client'].put(clientInstance.name,SUCCESS);
                    }
                    catch ( SbClientException clientException ) {
                        m_log.error("Unable to import client from xml fragement",clientException);
                        if ( clientException.message ) {
                            results['client'].put(clientXml.name.text(),clientException.message);
                        }
                        else {
                            def errorMessage = "";
                            clientException.clientInstance.errors.allErrors.each { error ->
                                errorMessage += messageSource.getMessage(error,null);
                                errorMessage += "\n";
                            }
                            results['client'].put(clientXml.name.text(),errorMessage);
                        }

                    }
                }
                else {
                    String licenseType = SbLicense.instance.isBulk() ? SbLicense.LOCK_AND_RELEASE_LICENSE : SbLicense.ENTERPRISE_LICENSE;
                    String errorMessage = messageSource.getMessage("client.limit.reached", [licenseType] as Object[], null);
                    m_log.error( errorMessage );
                    results['client'].put(clientXml.name.text(), errorMessage );
                }
            }
        }

        // groups
        Group groupInstance;
        def groupIdMap = [:];
        xml.groups.group.each { groupXml ->
            try {
            	groupInstance = groupService.fromXml(groupXml,clientIdMap);
                groupIdMap[groupXml.@id.text()] = groupInstance.id;
                results['group'].put(groupInstance.name,SUCCESS);
            }
            catch ( SbGroupException groupException ) {
                m_log.error("Unable to import group from xml fragment",groupException);
                if ( groupException.message ) {
                    results['group'].put(groupXml.name.text(),groupException.message);
                }
                else {
                    def errorMessage = "";
                    groupException.groupInstance.errors.allErrors.each { error ->
                        errorMessage += messageSource.getMessage(error,null);
                        errorMessage += "\n";
                    }
                    results['group'].put(groupXml.name.text(),errorMessage);
                }
            }
        }

        // Import only Scheduled Task if license is not bulk (aka Lock and Release)
        if( !SbLicense.instance.isBulk() ){

            // scheduled tasks
            ScheduledTask scheduledTaskInstance;
            xml.tasks.task.each { taskXml ->
                try {
                    scheduledTaskInstance = scheduledTaskService.fromXml(taskXml,groupIdMap);
                    results['scheduledTask'].put(scheduledTaskInstance.taskIdentifier,SUCCESS);
                }
                catch ( SbGroupException groupException ) {
                    m_log.error("Unable to import scheduled task from xml fragment",groupException);
                    if ( groupException.message ) {
                        results['scheduledTask'].put(taskXml.@id.text(),groupException.message);
                    }
                    else {
                        def errorMessage = "";
                        groupException.groupInstance.errors.allErrors.each { error ->
                            errorMessage += messageSource.getMessage(error,null);
                            errorMessage += "\n";
                        }
                        results['scheduledTask'].put(taskXml.@id.text(),errorMessage);
                    }
                }
                catch ( SbScheduledTaskException taskException ) {
                    m_log.error("Unable to import scheduled task from xml fragment",taskException);
                    if ( taskException.message ) {
                        results['scheduledTask'].put(taskXml.@id.text(),taskException.message);
                    }
                    else {
                        def errorMessage = "";
                        taskException.scheduledTaskInstance.errors.allErrors.each { error ->
                            errorMessage += messageSource.getMessage(error,null);
                            errorMessage += "\n";
                        }
                        results['scheduledTask'].put(taskXml.@id.text(),errorMessage);
                    }
                }
            }
        }

        m_log.info("IMPORT RESULTS : ${results}");

        // return the results map
        return results;
    }
}
