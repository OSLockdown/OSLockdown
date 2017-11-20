/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services

import org.apache.log4j.Logger;

import com.trustedcs.sb.preferences.UpstreamNotificationPreferences;
import com.trustedcs.sb.util.LoggingLevel;
import com.trustedcs.sb.util.SyslogFacility;
import com.trustedcs.sb.util.SyslogAppenderLevel;
import com.trustedcs.sb.exceptions.UpstreamNotificationPreferencesException;
import com.trustedcs.sb.preferences.UpstreamNotificationFlag;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.util.ConsoleTaskPeriodicity;
import com.trustedcs.sb.license.SbLicense;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

class UpstreamNotificationPreferencesService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services");

    static final String DATE_FORMAT_FOR_DB_EXPORT_IMPORT = "yyyy-MM-dd HH:mm:ss.S";


    // Transactional
    boolean transactional = true

    // Reference to Grails application.
    def grailsApplication
    def auditLogService;
    def messageSource;
    def periodicService;
    def upstreamNotificationService
    
    // UpstreamNotificationPreferences related methods
    UpstreamNotificationPreferences getUpstreamNotificationPreferences()
    {
        // Don't log it, hidden application domain object
        boolean found = false
        UpstreamNotificationPreferences upstreamNotificationPreferences = UpstreamNotificationPreferences.get( 1 )
        if( upstreamNotificationPreferences != null ) {
            found = true
        }
        else{
            //
            // Create UpstreamNotificationPreferences 
            //
            upstreamNotificationPreferences = new UpstreamNotificationPreferences( )
            if( upstreamNotificationPreferences.save( flush: true ) )
            {
                found = true
            }
        }

        if( found ){
            return upstreamNotificationPreferences
        }
        else {
            UpstreamNotificationPreferencesException upstreamNotificationPreferencesException = new UpstreamNotificationPreferencesException( upstreamNotificationPreferences:upstreamNotificationPreferences )
            throw upstreamNotificationPreferencesException
        }
        upstreamNotificationPreferences.clearErrors()
    }

    // Trigger flags are those where the user can change the timing.
    def getUpstreamNotificationFlags()
    {
       def isEnterprise = SbLicense.instance.isEnterprise()
       def (displayable, undisplayable) = UpstreamNotificationFlag.list().split { it -> 
         ((isEnterprise == true) || (it.upstreamNotificationType.enterpriseOnly == false))
       }
       return displayable.split { it ->
        it.upstreamNotificationType.userCanChangeTiming == false
       }
    }



    /**
     * Saves the UpstreamNotification preferences
     *
     * @param user
     */
    def save(UpstreamNotificationPreferences upstreamNotificationPreferences) {
        // save group to the database
        upstreamNotificationPreferences.clearErrors()
        if (upstreamNotificationPreferences.validate() && !upstreamNotificationPreferences.hasErrors() && upstreamNotificationPreferences.save()) {
            m_log.info("Upstream Notification Preferences Saved");           
            alterAppenderSettings(upstreamNotificationPreferences)
            m_log.info("Upstream Notification details updated.");           
        }
        else {
            m_log.error("Unable to save Upstream Notification Preferences");
            upstreamNotificationPreferences.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new UpstreamNotificationPreferencesException(upstreamNotificationPreferences:upstreamNotificationPreferences);
        }
    }


    def alterAppenderSettings(UpstreamNotificationPreferences upstreamNotificationPreferences) {
       def upstreamLogger = Logger.getLogger("com.trustedcs.services.UpstreamNotificationService")
       def upstreamAppender = upstreamLogger.getAppender('upstream')
       upstreamAppender.facility = upstreamNotificationPreferences.syslogFacility.toString();
       upstreamAppender.activateOptions()
       m_log.info("Upstream Notification details updated.");           
    }



    def updateUpstreamNotificationPreferences(params )
    {

        def dirtyNames = [];

        // Ok, first save changes to the preferences
        
        UpstreamNotificationPreferences upstreamNotificationPreferences = UpstreamNotificationPreferences.get( 1 )
        try {
          upstreamNotificationPreferences.properties = params
          upstreamNotificationPreferences.lastChanged = Calendar.getInstance().getTime();
          if (upstreamNotificationPreferences.validate()) {
            dirtyNames = upstreamNotificationPreferences.dirtyPropertyNames
            if (dirtyNames)
            {
              def resetSyslogDestination = false
              m_log.info("Updating Upstream Notification Preferences")
              upstreamNotificationPreferences.save(flush: true)
              dirtyNames.each { it ->
                if (it != "lastChanged") 
                {
                  m_log.info("Updated Upstream Notification Preferences for ${it} ->  ${upstreamNotificationPreferences.getPersistentValue(it)}");           
                  if (it == "syslogHost" || it == "syslogPort")
                  {
                    resetSyslogDestination = true
                  }
                }
                
              }
              if (resetSyslogDestination)
              {
                def syslogHost = upstreamNotificationPreferences.getPersistentValue("syslogHost")
                def syslogPort = upstreamNotificationPreferences.getPersistentValue("syslogPort")                  
                upstreamNotificationService.setSyslogDestination(syslogHost,syslogPort)
              }
              // Ok, some explicit checks to see if we've changed the loghost/port for syslogappender....
              
            }
          }
        }         
        catch (Exception e) {
          print e
          UpstreamNotificationPreferencesException upstreamNotificationPreferencesException = new UpstreamNotificationPreferencesException( upstreamNotificationPreferences:upstreamNotificationPreferences )
          throw upstreamNotificationPreferencesException
        }
        

        // Ok, not sure if there is a better way to do this.  Iterate over indexes and see if we have required settings.
        UpstreamNotificationFlag.list().each { it ->
            // quickly check to see if the user asked for the default timing for this flag/notif
            if (params["flagList_${it.id}.periodicity"])
            {
              it.periodicity = params["flagList_${it.id}.periodicity"]
              if (it.periodicity == ConsoleTaskPeriodicity.DEFAULT)
              {                                                                                
                it.periodicity = it.upstreamNotificationType.defaultPeriodicity                
              }                                                                                
            }

            it.enabled = params["flagList_${it.id}.enabled"]?:false

            if ( it.isDirty() ) {
              if ( it.validate() && it.save() ) {
                // if the user can *not* change the timing, our changes are a simple enabled/disabled
                def newStatusStr = it.enabled ? 'enabled' : 'disabled'
                def newPeriodStr = "@ ${it.periodicity}"
                
                if (it.upstreamNotificationType.userCanChangeTiming == false)
                {
                  m_log.info("Updated Upstream Notification Preferences for '${it.upstreamNotificationType.displayString}' -> ${newStatusStr}" )
                }
                else
                {                     
                  m_log.info("Updated Upstream Notification Preferences for '${it.upstreamNotificationType.displayString}' -> ${newStatusStr} ${newPeriodStr}")
                }                
              }
              else {
                m_log.info ("validate returned false ${it.errors}")
              }
              if (it.periodicity.valid)
              {
                periodicService.updateTasking(it.upstreamNotificationType.quartzJobName, it.periodicity.cronexpr, it.enabled?:false)
              }
            }     
        }
        if (dirtyNames) {
          alterAppenderSettings(upstreamNotificationPreferences)
        }
        return upstreamNotificationPreferences
    }



    /**
     * Creates a client from an xml fragment
     *
     * @param xmlFragment
     */
    def fromXml(GPathResult xmlFragment) {
        // create the client

    	UpstreamNotificationPreferences upstreamNotificationPreferences = getUpstreamNotificationPreferences();

        upstreamNotificationPreferences.syslogHost                   = xmlFragment.syslogHost.text();
        upstreamNotificationPreferences.syslogPort                   = xmlFragment.syslogPort.text().toInteger();
        upstreamNotificationPreferences.syslogFacility               = SyslogFacility.byFacility(xmlFragment.syslogFacility.text());
        upstreamNotificationPreferences.syslogEnabled                = xmlFragment.syslogEnabled.text().toBoolean();
        upstreamNotificationPreferences.lastChanged                  = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, xmlFragment.lastChanged.text())

        // save the preferences
        upstreamNotificationPreferences.clearErrors()
        save(upstreamNotificationPreferences)
        auditLogService.log("import UpstreamNotificationPreferences");

    	return upstreamNotificationPreferences;
    }

    
    /**
     * Convert the client instance to xml
     *
     * @param clientInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(UpstreamNotificationPreferences upstreamNotificationPreferencesInstance,boolean includePreamble,Writer writer) throws Exception {    	

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            upstreamNotificationPreferences() {
                syslogEnabled(upstreamNotificationPreferencesInstance.syslogEnabled)
                syslogHost(upstreamNotificationPreferencesInstance.syslogHost)
                syslogPort(upstreamNotificationPreferencesInstance.syslogPort)
                syslogFacility(upstreamNotificationPreferencesInstance.syslogFacility)
                lastChanged(upstreamNotificationPreferencesInstance.lastChanged.format(DATE_FORMAT_FOR_DB_EXPORT_IMPORT))
            }
        }

        // create the transformer
        Transformer transformer = TransformerFactory.newInstance().newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, 'yes');
        transformer.setOutputProperty('{http://xml.apache.org/xslt}indent-amount', '4');
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, includePreamble ? "no" : "yes");

        // create the output stream
        Result result = new StreamResult(writer);

        // transform
        transformer.transform(new StreamSource(new StringReader(createdXml.toString())), result);
    }

    /**
     * Convert the client to be xml
     *
     * @param client
     * @param includePreamble
     * @return returns a String representation of the client's xml
     */
    String toXmlString(UpstreamNotificationPreferences upstreamNotificationPreferencesInstance, boolean includePreamble)
    throws Exception {
        StringWriter prefWriter = new StringWriter();
        toXml(upstreamNotificationPreferencesInstance,false,prefWriter);
        return prefWriter.toString();
    }


    
    void appInit() {
      // verify base notification setting sexist
      getUpstreamNotificationPreferences()
      
      // might not be the grooviest way, but use validate to try and catch duplicates
      UpstreamNotificationTypeEnum.each { it ->
        def flag = new UpstreamNotificationFlag(upstreamNotificationType:it, enabled:false, periodicity:it.defaultPeriodicity)
        if (flag.validate()) {
            m_log.info "Adding Upstream Notification '${it.displayString}' action with default enablement of 'False'"
            flag.save()
        }
      }
    }
    
}
