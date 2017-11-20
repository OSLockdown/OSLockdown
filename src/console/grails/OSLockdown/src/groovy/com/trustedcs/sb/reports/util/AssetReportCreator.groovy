/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

import org.codehaus.groovy.grails.commons.ApplicationHolder;
import com.trustedcs.sb.web.pojo.*;
import org.apache.log4j.Logger;

/**
 * @author amcgrath
 *
 */
public class AssetReportCreator {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.reports.util.AssetReportCreator");

    // variables
    Group group;
	
    /**
     * Group Asset Report Creator
     * @param g
     */
    AssetReportCreator( Group g ) {
        group = g;
    }
	
    /**
     * Create the report from the group
     * @param outputFile
     */
    public void createReport(File outputFile) {
        def writer = new BufferedWriter(new FileWriter(outputFile));
        def builder = new groovy.xml.MarkupBuilder(writer);
        builder.AssetReport(
            name:group.name,
            profile:group.profile?.name,
            created:new Date().format(ReportsHelper.CREATED_DATE_FORMAT),
            sbVersion:ApplicationHolder.application.metadata['app.version']) {
            
            // description
            description(group.description);

            // clients
            group.clients?.each { c ->
            	def info = c.info;
            	if (c.info) 
                {
                  client(name:c.name,
                      hostAddress:c.hostAddress,
                      port:c.port,
                      location:c.location,
                      contact:c.contact,
                      clientVersion:info.clientVersion,
                      distribution:info.distribution,
                      kernel:info.kernel,
                      uptime:info.uptime,
                      architecture:info.architecture,
                      loadAverage:info.loadAverage,
                      memory:info.memory,
                      errorMsg:info.errorMsg);
                }
                else
                { 
                  ClientInfo defInfo = new ClientInfo(); 
                  client(name:c.name,
                      hostAddress:c.hostAddress,
                      port:c.port,
                      location:c.location,
                      contact:c.contact,
                      clientVersion:defInfo.clientVersion,
                      distribution:defInfo.distribution,
                      kernel:defInfo.kernel,
                      uptime:defInfo.uptime,
                      architecture:defInfo.architecture,
                      loadAverage:defInfo.loadAverage,
                      memory:defInfo.memory,
                      errorMsg:"Never Contacted");
                 }
            }       	
        }
        m_log.info("Report Complete");
    }
}
