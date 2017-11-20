/**
 *
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
 
/*
 *
 * We're going to use CEF format as the upstream notification.  Note that we *expect* to have an upstream 
 * logger that uses the syslog appender.  This may be configured in Config.groovy, or eventually in an 
 * external config so we can alter the 'facility' we're logging as and the location to send the logs to.
 *
 * In summary, a CEF formatted log looks like this:
 *  CEF:<VERSION>|<DEVICE_VENDOR>|<DEVICE_PRODUCT>|<DEVICE_VERSION>|<SIGNATURE>|<NAME>|<SEVERITY>|<EXTENSION>
 * where:
 *   <VERSION> = CEF version (PDF from CEF revision 16 used here.
 *   <DEVICE_VENDOR> = vendor name
 *   <DEVICE_PRODUCT> = product name
 *   <DEVICE_VERSION> = version name
 *   <SIGNATURE> = string/integer representing type of event
 *   <SEVERITY> = severity level in the range 0-10 inclusive, 0 = least severe and 10 = most severe
 *   <NAME>  = human readable 'summary' of what kind of event this is
 *   <EXTENSIONS> = series of tag=value pairs from the CEF data dictionary
 *
 *   Note that there are restrictions on what characters must be escaped, so we'll do that herein and not make
 *   the callers worry about that.  Escaping is different between the 'EXTENSIONS' field and everything else.
 *
 *   VERSION, DEVICE_VENDOR, DEVICE_PEODUCT, and DEVICE VERSION are *FIXED* at build time
 */

package com.trustedcs.sb.services;

// log4j access
import org.apache.log4j.Logger;
import java.text.MessageFormat;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.preferences.UpstreamNotificationPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationFlag;
import com.trustedcs.sb.util.SyslogAppenderLevel;
import com.trustedcs.sb.util.ConsoleTaskPeriodicity;

import grails.util.Environment

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

import org.apache.log4j.Level
import static org.apache.log4j.Level.*

class UpstreamNotificationService {

    // upstream (syslogAppender) logger
    static def upstream = Logger.getLogger("com.trustedcs.services.UpstreamNotificationService");

    // standard application log
    static def m_log = Logger.getLogger("com.trustedcs.sb.services");

    // Transactional
    boolean transactional = false;

    static Boolean syslogIsSet = false;
    // injected services
    def messageSource;
    def grailsApplication;
    def auditLogService;
    
    // message formats

    void setSyslogDestination(String syslogHost, Integer syslogPort)
    {
      def appender = Logger.getLogger("com.trustedcs.services.UpstreamNotificationService").getAppender("upstream")
      appender.setSyslogHost("${syslogHost}:${syslogPort}" as String)
      syslogIsSet = true
      m_log.info("Destination host for syslog messages now ${syslogHost}:${syslogPort}")
    }

        
    /**
     * Generic audit logging statement method
     * @param statement
     */

    // Add the things that are *required* for all of our upstream notifications - 
    // The 'header' fields, and the Consolehost/time data
    
    private def genHeader(sigID, sigName, int severity) {
        def version = grailsApplication.metadata["app.version"].split("-")[0]
        def now = new Date()
        
        def src = "cs1Label=ConsoleHost cs1=${grailsApplication.config.tcs.sb.console.ip}"
        def rt = "rt=${now.getTime()}"
        def fullMsg = "CEF:0|OS Lockdown|OS Lockdown Console|${version}|${sigID}|${sigName}|${severity}|${rt} ${src}"
        return fullMsg as String;
    }

    // Ok, we're using mostly syslog level messages, except or the emergency/alert levels.  
    // Syslog starts has level 0 as the highest priority and 7 as the lowest
    // CEF format has 10 as the highest priority and 0 as the lowest.  Also while we're using
    // syslog for the trigger levels, they don't quite exactly match up with the appender levels.
    // The appender also has an 'OFF' setting to disable it, but we're not using that one.
    // Suppose we could have simply subtracted the syslogappender from 10 to get the CEF level....
    
    //   Syslog     SysLogAppenders       CEF
    //   EMERG(0)    ------                10   <HIGHEST>
    //   ALERT(1)    ------                 9
    //   CRIT(2)     FATAL(2)               8
    //   ERR(3)      ERROR(3)               7
    //   WARN(4)     WARN(4)                6
    //   NOTICE(5)   ------                 5
    //   INFO(6)     INFO(5)                4
    //   DEBUG(7)    DEBUG(6)               3
    //   -----       TRACE(7)               2
    //   -----       ALL(8)                 1
    //   -----       ------                 0  <LOWEST>
    //
    //

    void log(SyslogAppenderLevel level, UpstreamNotificationTypeEnum notif, String notifText,  List extensionsList)
    {
        def prefs = UpstreamNotificationPreferences.get(1);
        def extensions = extensionsList.join(" ")

        if (!syslogIsSet && prefs) 
        {
          setSyslogDestination(prefs.syslogHost, prefs.syslogPort)
        }
        
        if (prefs) {

//            def whatNotif = UpstreamNotificationFlag.findByUpstreamNotificationType(notif)
//            def enabled = whatNotif.enabled
//            println "prefs.logTriggerLevel.rank()=${prefs.logTriggerLevel.rank()}"
//            println "    level.rank()=${level.rank()} "
//            println "    enabled=${UpstreamNotificationFlag.findByUpstreamNotificationType(notif).enabled}"
            if (prefs.syslogEnabled && UpstreamNotificationFlag.findByUpstreamNotificationType(notif).enabled)
            {
                def header = genHeader(notif.ordinal(), notif.getLogString(), 8)
                switch (level)
                {
                    case (SyslogAppenderLevel.FATAL):
                        upstream.fatal("${genHeader(notif.ordinal(), notifText, 8)} ${extensions}");
                        break;
                    case (SyslogAppenderLevel.ERROR):
                        upstream.error("${genHeader(notif.ordinal(), notifText, 7)} ${extensions}");
                        break;
                    case (SyslogAppenderLevel.WARN):
                        upstream.warn ("${genHeader(notif.ordinal(), notifText, 6)} ${extensions}");
                        break;
                    case (SyslogAppenderLevel.INFO):
                        upstream.info ("${genHeader(notif.ordinal(), notifText, 4)} ${extensions}");
                        break;
                    case (SyslogAppenderLevel.DEBUG):
                        upstream.debug("${genHeader(notif.ordinal(), notifText, 3)} ${extensions}");
                        break;
                    default:
                        println "NO MATCHING LEVEL"
                }
            }
        }
       
    }

    def fromXml(GPathResult xmlFragment) {
        // scheduled task
        def jobName = xmlFragment.upstreamNotificationType.text()
        def flagEnum = UpstreamNotificationTypeEnum.byQuartzJobName(jobName)
        def flagId = flagEnum.ordinal()
        def enabledFlag = xmlFragment.enabled.text().toBoolean();
        def periodicitySetting = ConsoleTaskPeriodicity.byDisplayName(xmlFragment.periodicity.text());
        
        UpstreamNotificationFlag upstreamNotificationFlag = UpstreamNotificationFlag.findByUpstreamNotificationType(flagEnum) ?: new UpstreamNotificationFlag(upstreamNotificationType:flagEnum);
        
        upstreamNotificationFlag.clearErrors()
        upstreamNotificationFlag.upstreamNotificationType = flagEnum;
        upstreamNotificationFlag.enabled = enabledFlag;
        upstreamNotificationFlag.periodicity = periodicitySetting
        
        upstreamNotificationFlag.save(failOnError:true)
        auditLogService.log("import Upstream Notification Flag - ${flagEnum.quartzJobName}");
        return upstreamNotificationFlag;
    }
    
    /**
     * Convert the client instance to xml
     *
     * @param clientInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(UpstreamNotificationFlag upstreamNotificationFlagInstance,boolean includePreamble,Writer writer) throws Exception {    	

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            upstreamNotificationFlag() {
                upstreamNotificationType(upstreamNotificationFlagInstance.upstreamNotificationType.quartzJobName)
                enabled(upstreamNotificationFlagInstance.enabled)
                periodicity(upstreamNotificationFlagInstance.periodicity)
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
    String toXmlString(UpstreamNotificationFlag upstreamNotificationFlagInstance, boolean includePreamble)
    throws Exception {
        StringWriter prefWriter = new StringWriter();
        toXml(upstreamNotificationFlagInstance,false,prefWriter);
        return prefWriter.toString();
    }
}
