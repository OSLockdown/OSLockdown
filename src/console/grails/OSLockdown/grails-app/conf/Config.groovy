/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

// locations to search for config files that get merged into the main config
// config files can either be Java properties files or ConfigSlurper scripts

// grails.config.locations = [ "classpath:${appName}-config.properties",
//                             "classpath:${appName}-config.groovy",
//                             "file:${userHome}/.grails/${appName}-config.properties",
//                             "file:${userHome}/.grails/${appName}-config.groovy"]

// if(System.properties["${appName}.config.location"]) {
//    grails.config.locations << "file:" + System.properties["${appName}.config.location"]
// }
grails.project.groupId = appName // change this to alter the default package name and Maven publishing destination
grails.mime.file.extensions = true // enables the parsing of file extensions from URLs into the request format
grails.mime.use.accept.header = false
grails.mime.types = [ 
    all:  	   '*/*',
    atom: 'application/atom+xml',
    css: 'text/css',
    csv: 'text/csv',
    form: 'application/x-www-form-urlencoded',
    html: 	   ['text/html','application/xhtml+xml'],
    js:   	   'text/javascript',
    json: 	   ['application/json','text/json'],
    multipartForm: 'multipart/form-data',
    rss:  	   'application/rss+xml',
    text: 	   'text/plain',
    xml:  	   ['text/xml', 'application/xml']
]

// URL Mapping Cache Max Size, defaults to 5000
//grails.urlmapping.cache.maxsize = 1000

// What URL patterns should be processed by the resources plugin
grails.resources.adhoc.patterns = ['/images/*', '/css/*', '/js/*', '/plugins/*']

// The default codec used to encode data with ${}
grails.views.default.codec="html" // none, html, base64
grails.views.gsp.encoding="UTF-8"
grails.converters.encoding="UTF-8"
// enable Sitemesh preprocessing of GSP pages
grails.views.gsp.sitemesh.preprocess = true
// scaffolding templates configuration
grails.scaffolding.templates.domainSuffix = 'Instance'

// Set to false to use the new Grails 1.2 JSONBuilder in the render method
grails.json.legacy.builder = false
// enabled native2ascii conversion of i18n properties files
grails.enable.native2ascii = true
// packages to include in Spring bean scanning
grails.spring.bean.packages = []
// whether to disable processing of multi part requests
grails.web.disable.multipart=false

// request parameters to mask when logging exceptions
grails.exceptionresolver.params.exclude = ['password']

// configure auto-caching of queries by default (if false you can cache individual queries with 'cache: true')
grails.hibernate.cache.queries = false

// Enforce pre-Grails 2.3 behavior form trimming strings and converting blank strings to null
// we *need* to preserve leading/trailing strings as well as blank strings
grails.databinding.convertEmptyStringsToNull = false
grails.databinding.trimgStrings = false


// set per-environment serverURL stem for creating absolute links
environments {
    production {
//        grails.serverURL = "http://www.trustedcomputersolutions.com"
        grails.logging.jul.usebridge = true
    }
    development {
        grails.dbconsole.enabled = false
        grails.views.gsp.keepgenerateddir='/tmp/GrailsGSP'
        grails.logging.jul.usebridge = false
        // TODO: grails.serverURL = "http://www.changeme.com"

    }
}

grails.config.locations = ["file:/usr/share/oslockdown/console/conf/catalina.properties"]

import org.apache.log4j.net.SyslogAppender

// log4j configuration
log4j = {
    // Example of changing the log pattern for the default console
    // appender:
    //
    appenders 
    {
        console name:'stdout', layout:pattern(conversionPattern: '%d{HH:mm:ss} %c{2} %m%n')

        //Keep up to 50 backup files (each ~ 10MB) in size, before the oldest is erased and overwritten.
        rollingFile name:"sbLog", file:"/var/lib/oslockdown/logs/osl-console.log",
            maxFileSize:"10MB", maxBackupIndex:50, layout:pattern(conversionPattern: '%d{MMM dd yyyy HH:mm:ss} %m%n'), append:true

        //Keep up to 50 backup files (each ~ 10MB) in size, before the oldest is erased and overwritten.
        rollingFile name:"sbAudit", file:"/var/lib/oslockdown/logs/oslockdown-audit.log",
            maxFileSize:"10MB", maxBackupIndex:50, layout:pattern(conversionPattern: '%d{MMM dd yyyy HH:mm:ss} %m%n'), append:true

        //Keep up to 50 stacktrace files (each ~10MB) in size, before the oldest is erase and overwritten.
        rollingFile name:"stacktrace", file:"//var/lib/oslockdown/logs/stacktrace.log",
            maxFileSize:"10MB", maxBackupIndex:50, layout:pattern(conversionPattern: '%d{MMM dd yyyy HH:mm:ss} %n'), append:true
     
        appender new SyslogAppender (
            name: 'upstream',
            facility: 'USER',
            syslogHost: 'localhost',
            layout: pattern (conversionPattern: '%m%n'),
            
        )
        
    }

    error  'org.codehaus.groovy.grails.web.servlet',  //  controllers
	       'org.codehaus.groovy.grails.web.pages', //  GSP
	       'org.codehaus.groovy.grails.web.sitemesh', //  layouts
	       'org.codehaus.groovy.grails."web.mapping.filter', // URL mapping
	       'org.codehaus.groovy.grails."web.mapping', // URL mapping
	       'org.codehaus.groovy.grails.commons', // core / classloading
	       'org.codehaus.groovy.grails.plugins', // plugins
	       'org.codehaus.groovy.grails.orm.hibernate', // hibernate integration
	       'org.springframework',
	       'org.hibernate',
               'com.trustedcs.sb.notification' // notification parser exception

    warn   'org.mortbay.log'
    
    info   sbLog:['com.trustedcs.sb.bootstrap',                  
                  'com.trustedcs.sb.metadata',                  
                  'com.trustedcs.sb.web.auth',
                  'com.trustedcs.sb.web.rbac',
                  'com.trustedcs.sb.web.group',
                  'com.trustedcs.sb.web.client',
                  'com.trustedcs.sb.scheduler',
                  'com.trustedcs.sb.web.reports',
                  'com.trustedcs.sb.logging.controller',
                  'com.trustedcs.sb.license.SbLicense',
                  'com.trustedcs.sb.reports.web.controller',
                  'com.trustedcs.sb.migration',
                  'com.trustedcs.sb.validator',
                  'com.trustedcs.sb.taglib',
                  'com.trustedcs.sb.reports.util',
                  'com.trustedcs.sb.notificationHandler',
                  'com.trustedcs.sb.web.notification',
                  'com.trustedcs.sb.ws.client',
                  'com.trustedcs.sb.reports.groupassessment',
                  'com.trustedcs.sb.scheduledtask',
                  'com.trustedcs.sb.xsl',
                  'com.trustedcs.sb.xml',
                  'com.trustedcs.sb.help.OnlineHelp',
                  'com.trustedcs.sb.clientregistration.controller',
                  'com.trustedcs.sb.metadata.baseline',
                  'com.trustedcs.sb.updatesb',
                  'com.trustedcs.sb.services',
		  'com.trustedcs.sb.UpdateSBEngine']
    debug  sbLog:[/*'com.trustedcs.sb.services.communication', */
                  'grails.app.task',
                  'grails.app.jobs']
    info   sbAudit:['com.trustedcs.audit.AuditLogger']

    debug  upstream:['com.trustedcs.services.UpstreamNotificationService'], additivity:false
           
}


     

// Uncomment and edit the following lines to start using Grails encoding & escaping improvements

/* remove this line 
// GSP settings
grails {
    views {
        gsp {
            encoding = 'UTF-8'
            htmlcodec = 'xml' // use xml escaping instead of HTML4 escaping
            codecs {
                expression = 'html' // escapes values inside null
                scriptlet = 'none' // escapes output from scriptlets in GSPs
                taglib = 'none' // escapes output from taglibs
                staticparts = 'none' // escapes output from static template parts
            }
        }
        // escapes all not-encoded output at final stage of outputting
        filteringCodecForContentType {
            //'text/html' = 'html'
        }
    }
}
remove this line */
