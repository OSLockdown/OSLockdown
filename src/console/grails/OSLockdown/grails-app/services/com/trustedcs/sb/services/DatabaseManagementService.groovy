/*
 * Original file generated in 2011 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2011-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services

import org.apache.log4j.Logger;
import com.trustedcs.sb.preferences.AppDBPreferences;
import com.trustedcs.sb.exceptions.AppDBPreferencesException;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult

class DatabaseManagementService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.");

    // Transactional
    boolean transactional = true

    // Reference to Grails application.
    def grailsApplication

    // AppDBPreferences related methods
    AppDBPreferences getAppDBPreferences()
    {
        // Don't log it, hidden application domain object

        boolean found = false
        AppDBPreferences appDBPreferences = AppDBPreferences.get( 1 )
        if( appDBPreferences ) {
            found = true
        }
        else{
            //
            // Create AppDBPreferences with dbApplicationVersion=app.version
            //
            String appVersion = grailsApplication.metadata["app.version"]
            appDBPreferences = new AppDBPreferences( dbApplicationVersion:appVersion )
            if( appDBPreferences.save( flush: true ) )
            {
                found = true
            }
        }

        if( found ){
            return appDBPreferences
        }
        else {
            AppDBPreferencesException appDBPreferencesException = new AppDBPreferencesException( appDBPreferences:appDBPreferences )
            throw appDBPreferencesException
        }
    }

    AppDBPreferences updateAppDBPreferences( String dbApplicationVersion, Date dbLastUpgradedOn, String prevDbApplicationVersion )
    {
        AppDBPreferences appDBPreferences = AppDBPreferences.get( 1 )
        if( appDBPreferences ){
            appDBPreferences.dbApplicationVersion = dbApplicationVersion
            appDBPreferences.dbLastUpgradedOn = dbLastUpgradedOn
            appDBPreferences.prevDbApplicationVersion = prevDbApplicationVersion
            if( appDBPreferences.save(flush: true) )
            {
                return appDBPreferences
            }
        }

        AppDBPreferencesException appDBPreferencesException = new AppDBPreferencesException( appDBPreferences:appDBPreferences )
        throw appDBPreferencesException
    }

}
