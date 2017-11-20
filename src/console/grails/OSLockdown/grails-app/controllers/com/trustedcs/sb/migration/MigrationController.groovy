/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.migration;

import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.exceptions.BaselineProfileException;
import com.trustedcs.sb.exceptions.DatabaseSnapshotException;
import com.trustedcs.sb.scheduler.ScheduledTask;

import com.trustedcs.sb.license.SbLicense;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.auth.shiro.*;

import org.apache.log4j.Logger;

class MigrationController {
	
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.migration.MigrationController");

    // service injection
    def messageSource;
    def databaseSnapshotService;
    def baselineProfileService;    

    /**
     * Display a summary page for what can be done for migration.
     */
    def index = {
		
        def snapshots = new TreeMap();
        def pattern = ~/.*\.xml/;
        def snapshotsDir = SBFileSystemUtil.get(SB_LOCATIONS.DB_EXPORT);
        def tstamp;
        def date;
        if ( snapshotsDir.exists() ) {
            snapshotsDir.eachFileMatch(pattern) { file ->
                if ( file.exists() ) {
                    try {
                        tstamp = file.name.substring(5,file.name.length()-4).toLong() * 1000;
                        date = new Date(tstamp);
                        snapshots[file.name] = date.format("E MMM dd HH:mm:ss z yyyy");
                    }
                    catch (Exception e ) {
                        m_log.error("Unable to parse filename for date format: ${file.name}");
                        snapshots[file.name] = file.name;
                    }
                }
            }
        }	
        
        [snapshots:snapshots]
    }
	
    def importDBLocal = {
        clearFlash();

        // if no snapshot was selected
        if ( !(params.snapshot) ) {
            flash.error = "No snapshot was specified .";
            redirect(action:'index');
            return;
        }

        // find the snapshot file
        File snapshotFile = new File(SBFileSystemUtil.get(SB_LOCATIONS.DB_EXPORT),params.snapshot);

        // provide default empty results if import aborts
        def results = [ 'user' : [:],
                        'securityProfile' : [:],
                        'baselineProfile' : [:],
                        'processor' : [:],
                        'client' : [:],
                        'group' : [:],
                        'scheduledTask' : [:],
                        'accountPreferences' : [:],
                        'upstreamNotificationPreferences' : [:]]
        try {
            // service call
            results = databaseSnapshotService.importFromXml(snapshotFile);
        }
        catch ( DatabaseSnapshotException snapshotException ) {
            flash.error = snapshotException.message;
        }

        // render the results
    	render(view:"importResults",model:[results:results]);
    }
	
    /**
     * Load an existing database into the web application
     */
    def importDB = {
        clearFlash();

        // get the file from the request
    	def file = request.getFile('dbFile');
    	
        // check to see if a file was uploaded
    	if ( file.isEmpty() ) {
            flash.error = "No file was specified or the file was empty.";
            redirect(action:'index');
            return;
    	}

        // provide default empty results if import aborts
        def results = [ 'user' : [:],
                        'securityProfile' : [:],
                        'baselineProfile' : [:],
                        'processor' : [:],
                        'client' : [:],
                        'group' : [:],
                        'scheduledTask' : [:],
                        'accountPreferences' : [:],
                        'upstreamNotificationPreferences' : [:]]
        try {
            // service call
            results = databaseSnapshotService.importFromXml(file.getInputStream());
        }
        catch ( DatabaseSnapshotException snapshotException ) {
            flash.error = snapshotException.message;
        }
    	// render the results
    	render(view:"importResults",model:[results:results]);
    }   
    
    /**
     * Persist the current database contents to an xml file
     */
    def exportDB = {
        clearFlash();
       try {
           File snapshotFile = databaseSnapshotService.exportToXml();
           flash.message = messageSource.getMessage("database.snapshot.exported",[snapshotFile.absolutePath] as Object[],null);
       }
       catch ( DatabaseSnapshotException snapshotException ) {
           flash.error = "Unable to export database snapshot : ${snapshotException.message}";
       }

       redirect(action:'index');
    }
	
    /**
     * Clear flash scope of messages
     */
    private clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }	 
}
