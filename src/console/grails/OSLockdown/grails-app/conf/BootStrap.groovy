/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
// logging
import org.apache.log4j.Logger;

// grails imports
import grails.util.GrailsUtil;
import grails.util.Environment;
import grails.util.BuildSettingsHolder;
import org.codehaus.groovy.grails.commons.ApplicationHolder;
import org.codehaus.groovy.grails.commons.GrailsApplication;
import org.codehaus.groovy.grails.commons.ConfigurationHolder;

// profile related classes
import com.trustedcs.sb.validator.ProfileOptionsValidator;

// notification handler related classes
import com.trustedcs.sb.web.notifications.Notification;
import com.trustedcs.sb.notification.OSLockdownNotifier;
import com.trustedcs.sb.clientregistration.ClientRegistrationNotifier;
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;

// client registration
import com.trustedcs.sb.clientregistration.ClientRegistrationEngine;

// scheduled tasks
import com.trustedcs.sb.scheduler.ScheduledTask;
import com.trustedcs.sb.taskverification.TaskVerificationEngine;

// software updates
import com.trustedcs.sb.updatesb.UpdateSBEngine;

// groups and clients 
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.metadata.Profile;

// clientTypes
import com.trustedcs.sb.util.ClientType;

// file system
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

// Security Module
import com.trustedcs.sb.metadata.SecurityModule;

// database snapshot
import com.trustedcs.sb.exceptions.DatabaseSnapshotException;
import com.trustedcs.sb.exceptions.SbRbacException;
import com.trustedcs.sb.exceptions.SbGroupException;
import com.trustedcs.sb.exceptions.SbClientException;
import com.trustedcs.sb.exceptions.SecurityMetadataException;
import com.trustedcs.sb.exceptions.BaselineMetadataException;

// security 
import org.apache.shiro.crypto.hash.Sha1Hash;
import org.apache.shiro.authz.UnauthorizedException;
import org.apache.shiro.mgt.DefaultSecurityManager;
import org.apache.shiro.subject.SimplePrincipalCollection;
import org.apache.shiro.subject.Subject;


// license file
import com.trustedcs.sb.license.SbLicense;

import groovy.util.ConfigObject;

import javax.net.ssl.HttpsURLConnection;
import com.trustedcs.sb.ssl.IgnoreHostnameVerifier;

// rbac
import com.trustedcs.sb.auth.shiro.*;

import groovy.sql.Sql;
import groovy.sql.GroovyRowResult;

// AppDBPreferences
import com.trustedcs.sb.preferences.AppDBPreferences;
import com.trustedcs.sb.preferences.AccountPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationFlag;


import com.trustedcs.sb.util.SyslogAppenderLevel;

/**
 * Bootstrap class run everytime the application starts.
 */
class BootStrap {

    // logger
    static def bootLog = Logger.getLogger("com.trustedcs.sb.bootstrap");
    
    // injected services
    def messageSource;
    def baselineProfileService;
    def securityProfileService;
    def databaseSnapshotService;
    def scheduledTaskQueryService;
    def dispatcherNotificationService;
    def rbacService;
    def clientRegistrationService;
    def clientService;
    def groupService;
    def groupAssessmentStateMachineService;
    def securityMetadataService;
    def baselineMetadataService;
    def databaseManagementService;
    def updateSBService;
    def upstreamNotificationService;
    def upstreamNotificationPreferencesService;
    def periodicService;
    def dataSource;

    def task;
    // Environment Variables

    // displays the in memory database as a swing gui
    private static final String SB_SHOW_DB_MANAGER = "SB_SHOW_DB_MANAGER";
    // resets the password of the application back to Admin123
    private static final String SB_CONSOLE_PASSWORD_RESET = "SB_CONSOLE_PASSWORD_RESET";
    // loads the snapshot at the set location ( must be absolute path )
    private static final String SB_LOAD_SNAPSHOT = "SB_LOAD_SNAPSHOT";
    // bypasses authorization login page only in development mode
    private static final String SB_BYPASS_AUTH = "SB_BYPASS_AUTH";
    // loads the security profile metadata
    private static final String SB_CONSOLE_LOAD_SECURITY_METADATA = "SB_CONSOLE_LOAD_SECURITY_METADATA";
    // loads the security profiles from the file system
    private static final String SB_CONSOLE_LOAD_SECURITY_PROFILES = "SB_CONSOLE_LOAD_SECURITY_PROFILES";
    // loads the baseline profile metadata
    private static final String SB_CONSOLE_LOAD_BASELINE_METADATA = "SB_CONSOLE_LOAD_BASELINE_METADATA";
    // loads the baseline profiles from the file system
    private static final String SB_CONSOLE_LOAD_BASELINE_PROFILES = "SB_CONSOLE_LOAD_BASELINE_PROFILES";

    private static final String SINGLE_QUOTE = "'";

    // Table names
    private static final String COMMON_PLATFORM_ENUMERATION_MODULES_TABLE = "COMMON_PLATFORM_ENUMERATION_MODULES";
    private static final String COMMON_PLATFORM_ENUMERATION_TABLE         = "COMMON_PLATFORM_ENUMERATION";
    private static final String COMPLIANCY_MODULES_TABLE                  = "COMPLIANCY_MODULES";
    private static final String COMPLIANCY_TABLE                          = "COMPLIANCY";
    private static final String MODULE_TAG_MODULES_TABLE                  = "MODULE_TAG_MODULES";
    private static final String MODULE_TAG_TABLE                          = "MODULE_TAG";
    // Sql commands
    private static final String DELETE_FROM                               = "delete from";
    private static final String DROP_TABLE                                = "drop table";
    private static final String SELECT_COUNT_ALL_FROM                     = "select count(*) from";
    // Table-specific sql commands
    private static final String OLD_TABLE_EXISTS_QUERY =
        "${SELECT_COUNT_ALL_FROM} INFORMATION_SCHEMA.SYSTEM_TABLES where table_schem=\'PUBLIC\' ";
    private static final String OLD_TABLE_CPE_MODULES_EXISTS_QUERY =
        "${OLD_TABLE_EXISTS_QUERY} and table_name=\'${COMMON_PLATFORM_ENUMERATION_MODULES_TABLE}\'";
    private static final String OLD_TABLE_COMPLIANCY_MODULES_EXISTS_QUERY =
        "${OLD_TABLE_EXISTS_QUERY} and table_name=\'${COMPLIANCY_MODULES_TABLE}\'";
    private static final String OLD_TABLE_MODULE_TAG_MODULES_EXISTS_QUERY =
        "${OLD_TABLE_EXISTS_QUERY} and table_name=\'${MODULE_TAG_MODULES_TABLE}\'";
    private static final String OLD_TABLE_AUTOBASE_EXISTS_QUERY =
        "${OLD_TABLE_EXISTS_QUERY} and (table_name=\'DATABASECHANGELOG\' or table_name=\'DATABASECHANGELOGLOCK\')"
    private static final String OLD_TABLE_NOTIFICATIONS_NULLABLE =
        "select * from INFORMATION_SCHEMA.SYSTEM_COLUMNS where TABLE_SCHEM=\'PUBLIC\' and TABLE_NAME=\'NOTIFICATION\' and COLUMN_NAME=\'ABORTED\' AND NULLABLE=false;"
    private static final String OLD_TABLE_SCHEDULED_TASK_HAS_GEN_DELTA =
        "select * from INFORMATION_SCHEMA.SYSTEM_COLUMNS where TABLE_SCHEM=\'PUBLIC\' and TABLE_NAME=\'SCHEDULED_TASK\' and COLUMN_NAME=\'GEN_DELTA\' ;"



    // Reference to Grails application.
    def grailsApplication
    def shiroSecurityManager;
    

    // Init the application
    def init = { servletContext ->
        def startupMsg

        // We'll need any upstream notification/flag values fairly early, so create them if they do not already exist
        upstreamNotificationPreferencesService.appInit()
        
        // ----------- File System Setup for fixed paths  -----------
        SBFileSystemUtil.setFixed();

        // ----------- License Check -----------
        licenseCheck();        

        // ----------- File System Setup for dynamic paths  -----------
        SBFileSystemUtil.setDynamic(SbLicense.instance.isStandAlone());

        
        // Change host name verification for SSL TLS connections        
        if ( Environment.current != Environment.DEVELOPMENT ) {
            IgnoreHostnameVerifier myHv = new IgnoreHostnameVerifier();
            HttpsURLConnection.setDefaultHostnameVerifier(myHv);
        }

        // See http://act.ualise.com/blogs/continuous-innovation/2009/07/viewing-grails-in-memory-hsqldb/
        if(System.getenv(SB_SHOW_DB_MANAGER)) {
            String[] databaseManagerOptions = new String[3];
            databaseManagerOptions[0] = '--url';
            databaseManagerOptions[2] = '--noexit';
            switch (Environment.current) {
                case Environment.DEVELOPMENT :
                    databaseManagerOptions[1] = 'jdbc:hsqldb:file:instance;shutdown=true';
                    org.hsqldb.util.DatabaseManagerSwing.main( databaseManagerOptions );
                    break;
                case Environment.TEST :
                    databaseManagerOptions[1] = 'jdbc:hsqldb:file:/var/lib/oslockdown/console/dbtest/instance';
                    break;
                case Environment.PRODUCTION :
                    databaseManagerOptions[1] = 'jdbc:hsqldb:file:/var/lib/oslockdown/console/db/instance';
                    break;
                default :
                break;
            }
        }
        
        // read the configuration of the application
        readSbConfiguration();

        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            startupMsg = "OS Lockdown Enterprise Console Startup" ;        
        }
        else if ( SbLicense.instance.isBulk()) {
            startupMsg = "OS Lockdown Lock and Release Console Startup" ;        
        } 
        else {
            startupMsg = "OS Lockdown Standalone Console Startup" ;        
        }
        def extensionsList = []
        extensionsList << "cs5Label=Result"
        extensionsList << "cs5=Console startup"
        upstreamNotificationService.log(SyslogAppenderLevel.INFO,UpstreamNotificationTypeEnum.APP_START_STOP, "App Status", extensionsList);        

    
        // ----------- Is this the first time the application has been run?
        // ----------- By this we really mean - do we have a database?  If so, we can expect to see 
        // ----------- at least the Admin user.  Otherwise we need to create one before continuing

        boolean isFirstRun;
        isFirstRun = initialApplicationEvocation();

        if (isFirstRun == true) {
            // Ok, no existing DB, so create default user(s) so we can load them next
            establishSecurity();
        }

        // Load our *admin* context to continue - this will let any initial DB work proceed as though the Admin user
        // had logged in to do them. 
        // Took this (including the 'runAs' method) from the following post by Goran Ehrsson with a few modifications
        // http://grails.1312388.n4.nabble.com/Shiro-SecurityManager-and-BootStrap-groovy-td4630989.html

        runAs("admin") {
            databaseBootStrap(isFirstRun);
        }
        
        
    }   
        
    def runAs(String username, Closure closure) {
      def user = ShiroUser.findByUsername(username, [cache: true])
      if (!user) {
          throw new UnauthorizedException("[$username] is not a valid user")
      }
      def realm = shiroSecurityManager.realms.find{it}
      def bootstrapSecurityManager = new DefaultSecurityManager(realm)
      def principals = new SimplePrincipalCollection(username, realm.name)
      def subject = new Subject.Builder(bootstrapSecurityManager).principals(principals).buildSubject()
      subject.execute(closure)
    }
  
    private setDefaultAccountPreferences() 
    {
      if (AccountPreferences.list().size() == 0)
      {
        bootLog.info("Creating default preferences for Account settings");
        AccountPreferences accountPreferences = new AccountPreferences().save();
      }
    }
      
    private void databaseBootStrap(boolean isFirstRun)
    {
        if (isFirstRun) {
          setDefaultAccountPreferences();
          loadFilesFromDiskToDB();
        }
        if ( !isFirstRun) {
          // ----------- Remove the UNIQUE constraint on the CLIENT.NAME column for upgrade to 4.0.4
          upgradeClientTo404Fix();
          
          // reset the module metadata
          if ( System.getenv(SB_CONSOLE_LOAD_SECURITY_METADATA)) {
            bootLog.info("Resetting Console Security Metadata");
            upgradeSecurityMetadataTo403Fix();
            loadSecurityModules( true );
          }

          // load the baseline profiles
          if ( System.getenv(SB_CONSOLE_LOAD_SECURITY_PROFILES) ) {
              loadSecurityProfiles( true );
          }

          // load the baseline metadata
          if ( System.getenv(SB_CONSOLE_LOAD_BASELINE_METADATA) ) {
              loadBaselineModules( true );
          }

          // load the baseline profiles
          if ( System.getenv(SB_CONSOLE_LOAD_BASELINE_PROFILES) ) {
              loadBaselineProfiles( true );
          }
        }
        // Ok, *database* should be loaded, do an integrity check
        dbCheckIntegrity();

    // ----------- Notifications Initialization -----------  
        initializeNotificationHandlers();    
    
        // setup enterprise handlers
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            TaskVerificationEngine.getInstance().setQueryHandler(scheduledTaskQueryService);
            bootLog.info("Scheduled Task Query Handler Set");

            // client registration listener
            ClientRegistrationEngine.getInstance().setClientRegistrationHandler(clientRegistrationService);
            bootLog.info("Client Auto Registration Engine Handler Set");

            ClientRegistrationNotifier.getInstance().registerListener(clientRegistrationService);
            bootLog.info("Client Auto Registration Listener Registered");

        }
     
        // grab the optionTypes.xml
        try {
            if ( SBFileSystemUtil.get(SB_LOCATIONS.OPTION_TYPES).exists() ) {
                ProfileOptionsValidator.getInstance().loadConfiguration(SBFileSystemUtil.get(SB_LOCATIONS.OPTION_TYPES));
                bootLog.info("Profile options validator initialized");
            }
            else {
                bootLog.fatal("${SBFileSystemUtil.get(SB_LOCATIONS.OPTION_TYPES).absolutePath} missing");
            }
        }
        catch ( Exception e ) {
            bootLog.error("Unable to load optionTypes",e);
        }
     
        // reset the password if asked for
        if ( System.getenv(SB_CONSOLE_PASSWORD_RESET) ) {
            try {
                bootLog.info("RESETTING ADMIN PASSWORD");
                rbacService.resetAdminPassword();
            }
            catch ( SbRbacException e ) {
                bootLog.error("Unable to reset admin password");
            }
        }

        // load a database snapshot if asked for
        if ( System.getenv(SB_LOAD_SNAPSHOT) && ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) ) {
            try {
                File snapshotFile = new File(System.getenv(SB_LOAD_SNAPSHOT));
                databaseSnapshotService.importFromXml(snapshotFile);
                bootLog.info("Loaded database snapshot from location : ${snapshotFile.absolutePath}");
            }
            catch ( DatabaseSnapshotException snapshotException ) {
                bootLog.error("Unable to load requested database snapshot : ${snapshotException.message}");
            }
        }

        // Store the current SB version number (from application.properties file, app.version property) into the DB.
        // The Console's app.version is set during Console's building, see src/console/Makefile and specifically the line containing
        //      (cd grails/OSLockdown/; $(GRAILS) set-version $(SB_VERSION)-${SB_RELEASE} )
        // The app.version contains major version, followed by dash and release version.
        AppDBPreferences appDBPreferences = databaseManagementService.getAppDBPreferences()

        String applicationVersion = grailsApplication.metadata["app.version"]
        String dbApplicationVersion = appDBPreferences.dbApplicationVersion
        Date dbLastUpgradedOn

        //
        // Upgrade DB based on DB and current SB version. Note that for New SB installs dbApplicationVersion=applicationVersion so
        // make sure the below logic is not kicked in for new installs.
        //
        if( dbApplicationVersion ){

            // 4.0.6->4.0.7 Upgrade
            if( dbApplicationVersion.startsWith( "4.0.6" ) && applicationVersion.startsWith( "4.0.7" ) ){

//println "---->>> doing a 4.0.6 to 4.0.7 DB upgrade"

                upgrade_4_0_6_to_4_0_7()

                // Set last upgraded timestamp
                dbLastUpgradedOn = new Date()
            }
        }
        
        // Ok, now make sure the columns are expanded for the Client name/address fields.  They were 50 and 30 respectively, until SB4.1.0
        // Now they need to be 100 chars each to allow for a long FQDN that a customer hit
        
        fixClientNameLengths()
        
        // Ok, we're updating the NOTIFICATION table *here* rather than in the upgrade_4_0_6_to_4_0_7() routine
        // to make sure the table is built correctly regardless of where this database came from.  
        
        fixNotificationsAbortedColumn()

        // update database structure for version 4.1.2
        updateDbTo412()

        // Ok, now make sure the columns are expanded for the Profile NAME fields.  The '-M' option to OS Lockdown 
        // allows for creating a Profile from a Module by name, and the name of the Profile will be "TEST-$MODUELNAME".
        // We've got several Modules whose name is long enough to overflow this created length, so we'll bump the size up a bit 
        // here.  
        
        fixProfileNameLengths()

        // update database structure for version 4.1.4 
        updateDbTo414()
        
        // No changes need to be made for the 4.1.4 upgrade - all new tables are 'in-memory' and created on the fly each time
        
        
        verifyLastPasswordChangeDate()
        
        if(System.getenv("RESET_NOTIF")) {
          fixNotificationsDataMapping()
        }
              
        // write the applicationVersion (and optionally in case of a DB upgrade the dbLastUpgradedOn, but notice don't
        // null it out in case it was non-null) to the DB.
        databaseManagementService.updateAppDBPreferences( applicationVersion, dbLastUpgradedOn ?: appDBPreferences.dbLastUpgradedOn, dbApplicationVersion )

        bootLog.info("OS Lockdown Console Version ${applicationVersion} Initialization Complete");
        bootLog.info("URL http${ConfigurationHolder.config?.tcs?.sb?.console?.secure == "true" ? "s":""}://${ConfigurationHolder.config?.tcs?.sb?.console?.ip}:${ConfigurationHolder.config?.tcs?.sb?.console?.port}/OSLockdown");
    } // init

    

    private void upgrade_4_0_6_to_4_0_7()
    {
        def sqlObject
        try {
            sqlObject = new Sql( dataSource )
            
            // select count(*) from INFORMATION_SCHEMA.SYSTEM_TABLES where table_schem='PUBLIC' and
            // (table_name='DATABASECHANGELOG' or table_name='DATABASECHANGELOGLOCK')
            def rows = sqlObject.rows( OLD_TABLE_AUTOBASE_EXISTS_QUERY )
            if( rows.size() == 1 && rows[0].getAt( 0 ) == 2 ) // the returned count=2 as they are 2 autobase columns
            {
                sqlObject.execute ( ( String ) ("${DROP_TABLE} DATABASECHANGELOG") );
                sqlObject.execute ( ( String ) ("${DROP_TABLE} DATABASECHANGELOGLOCK") );
            }


            bootLog.info( "4.0.6->4.0.7 DB Upgrade succeeded" )
        }
        catch( Exception e ){
            bootLog.error( "4.0.6->4.0.7 DB Upgrade failed.", e)
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
    }
    private void fixClientNameLengths()
    {
        def sqlObject
        bootLog.info( "Checking to see if Client name/address column lengths has been upgraded to 100 characters" )
        try
        {
            sqlObject = new Sql( dataSource )
            String query = "select count(*) from INFORMATION_SCHEMA.SYSTEM_COLUMNS where TABLE_NAME=\'CLIENT\' and " +
                           "COLUMN_NAME=\'HOST_ADDRESS\' and COLUMN_SIZE=100 "
//            println "Query is ${query}"
            def rows = sqlObject.rows( query )
//            println "Found ${rows.size()}"
//            println "Found ${rows[0].getAt(0)}"
            if( rows.size() == 1 && rows[0].getAt(0) != 1  ) //         
            {
              bootLog.info( "Upgrading Client name/address column lengths to 100 characters" )
              sqlObject.execute ( "ALTER TABLE CLIENT ALTER COLUMN HOST_ADDRESS VARCHAR(100) " )
              sqlObject.execute ( "ALTER TABLE CLIENT ALTER COLUMN NAME VARCHAR(100) " )
              sqlObject.execute ( "ALTER TABLE CLIENT_REGISTRATION_REQUEST ALTER COLUMN HOST_ADDRESS VARCHAR(100) " )
              sqlObject.execute ( "ALTER TABLE CLIENT_REGISTRATION_REQUEST ALTER COLUMN NAME VARCHAR(100) " )
            }
            else
            {
              bootLog.info( "Upgrading Client name/address column lengths not required" )
            }
        }
        catch( Exception e ){
            bootLog.error( "Upgrade of Client name/address column lengths failed.", e)
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
    }

    private void fixProfileNameLengths()
    {
        def sqlObject
        bootLog.info( "Checking to see if Profile name column lengths has been upgraded to 50 characters" )
        try
        {
            sqlObject = new Sql( dataSource )
            String query = "select count(*) from INFORMATION_SCHEMA.SYSTEM_COLUMNS where TABLE_NAME=\'PROFILE\' and " +
                           "COLUMN_NAME=\'NAME\' and COLUMN_SIZE=30 "
//            println "Query is ${query}"
            def rows = sqlObject.rows( query )
//            println "Found ${rows.size()}"
//            println "Found ${rows[0].getAt(0)}"
            if( rows.size() == 1 && rows[0].getAt(0) == 1  ) //         
            {
              bootLog.info( "Upgrading Profile name column lengths to 50 characters" )
              sqlObject.execute ( "ALTER TABLE PROFILE ALTER COLUMN NAME VARCHAR(50) " )
            }
            else
            {
              bootLog.info( "Upgrading Profile name column lengths not required" )
            }
        }
        catch( Exception e ){
            bootLog.error( "Upgrade of Profile name column lengths failed.", e)
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
    }

    // This should be a fairly simple march through the Notifications, so just do it each time...
    private void fixNotificationsDataMapping()
    {
        Notification.findAll().each {notif ->
          int sourceId
          boolean hasFileName
          print "BEFORE"
          print notif
//          if (notif.sourceId == null) {
              print "${notif.transactionId} -> ${notif.sourceId}"
              sourceId = notif.dataMap['sourceId'].toInteger()
              notif.sourceId = sourceId
              notif.client = Client.get(sourceId)
              notif.hasFileName = 'fileName' in notif.dataMap.keySet()
              print "AFTER"
              print notif
              notif.save()          
//          }

        }  
    }

    // The Processor table will be added for us, we just need to add some
    // update the 'client_type' field for existing Clients *IF* NULL, depending on the license type:
    // If isEnterprise -> CLIENT_ENTERPRISE
    // If isBulk       -> CLIENT_BULK
    // Else            -> CLIENT_STANDALONE
    // We also need to drop a constraint where a Notification ClientID *must* exist - this has been marked
    // so that a Notification 'belongsTo' a specific Client, and the deletions of the Client will cascade to the
    // appropriate notifications 

    private void updateDbTo412 ()
    {
        String sqlStr
        
        // First fix ClientType for current Clients
        if (SbLicense.instance.isEnterprise()) {
            sqlStr = "update CLIENT set CLIENT_TYPE='CLIENT_ENTERPRISE' where CLIENT_TYPE is NULL"
        }
        else if (SbLicense.instance.isBulk()) {
            sqlStr = "update CLIENT set CLIENT_TYPE='CLIENT_BULK' where CLIENT_TYPE is NULL"
        }
        else {
            sqlStr = "update CLIENT set CLIENT_TYPE='CLIENT_STANDALONE' where CLIENT_TYPE is NULL"
        }
        // look for the 'client_type' field in the Client table, if it isn't there, then the database is pre-412
        
        def sqlObject
        
        try
        {       
            sqlObject = new Sql( dataSource )
            sqlObject.execute ( sqlStr )
             bootLog.info("Client Types updated for current Clients");
        
        }
        finally
        {
          if (sqlObject) 
          {
            sqlObject.close()
          }
        } 
        // Ok, now fix the constraint
        try
        {
            sqlObject = new Sql( dataSource )

            // look to see if the CLIENT_ID columns is there, and if so kill it and the associated constraint
            String query = "select count(*) from INFORMATION_SCHEMA.SYSTEM_COLUMNS where TABLE_NAME=\'NOTIFICATION\' and " +
                           "COLUMN_NAME=\'CLIENT_ID\'  "
            def rows = sqlObject.rows( query )
            if( rows.size() == 1 && rows[0].getAt( 0 ) == 1 )
            {
                sqlObject.execute ( "alter table NOTIFICATION drop constraint FK237A88EB83D89D5F" )
                sqlObject.execute ( "alter table NOTIFICATION drop column CLIENT_ID")
                bootLog.info("CLIENT_ID column and constraint in NOTIFICATION table dropped");
            }
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }

    }

    private void updateDbTo414 ()
    {
        def sqlObject
        bootLog.info( "'Scheduled Task' table being upgraded" )
        try {
            sqlObject = new Sql( dataSource )
            
            // <sigh> Grails won't add our new flag, so we have to do this the hard way
            // See if the flag is there.  If not, add it, otherwise assume it is correct.
            def rows = sqlObject.rows( OLD_TABLE_SCHEDULED_TASK_HAS_GEN_DELTA )
            if( rows.size() == 0  )
            {
                sqlObject.execute ("alter table SCHEDULED_TASK add column GEN_DELTA boolean")
                sqlObject.execute ( "update SCHEDULED_TASK set GEN_DELTA=FALSE where GEN_DELTA is NULL" )
                sqlObject.execute ( "alter table SCHEDULED_TASK alter column GEN_DELTA SET NOT NULL" )

                bootLog.info( "'Scheduled_Task' table DB Upgrade succeeded" )
            }
            else
            {
                bootLog.info( "'Scheduled_Task' table DB upgrade not required" )
            }
        }
        catch( Exception e ){
            bootLog.error( "'Scheduled_Tasks' table Upgrade failed.", e)
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
        bootLog.info( "'Scheduled_Tasks' table update check done" )
    }
    
    
    private void verifyLastPasswordChangeDate ()
    {
        String sqlStr
        
        sqlStr = "update shiro_user set last_change=now() where last_change is NULL"
        def sqlObject
        
        try
        {       
            sqlObject = new Sql( dataSource )
            sqlObject.execute ( sqlStr )
             bootLog.info("Verifying all users have a 'lastChange' field");
        
        }
        finally
        {
          if (sqlObject) 
          {
            sqlObject.close()
          }
        } 
}
    
    private void fixNotificationsAbortedColumn()
    {
        def sqlObject
        bootLog.info( "'Notifications' table being upgraded" )
        try {
            sqlObject = new Sql( dataSource )
            
            // In 4.0.6 (commit 14982) we added the ABORTED column, but it initially was allowed to be NULL.
            // The 4.0.7 upgrade altered this on upgrade from 4.0.6 to a 'not null' field, but only on the
            // 4.0.6 to 4.0.7 upgrade.  We're changing this to make this change regardless of the current version
            // if the field is still marked 'nullable', or if the field doesn't exist at all.

            // Grails has added NOTIFICATION.ABORTED column for us, however it's still NULLABLE
            // even though we said aborted(nullable:false) in Notification.constraints closure.

            // select * from INFORMATION_SCHEMA.SYSTEM_COLUMNS where TABLE_SCHEM='PUBLIC' and TABLE_NAME='NOTIFICATION' 
            // and COLUMN_NAME='ABORTED' and NULLABLE=false  ;

            // if we're ok, don't bother doing the rest.  Otherwise make our changes....
            def rows = sqlObject.rows( OLD_TABLE_NOTIFICATIONS_NULLABLE )
            if( rows.size() == 0  )
            {
            // 1. First of all set ABORTED=FALSE for all NOTIFICATIONs (default)
//                bootLog.info( "'Notifications' table getting all records with NULL abort fixed" )
                sqlObject.execute ( "update NOTIFICATION set ABORTED=FALSE where ABORTED is NULL" )

            // 2. Once we have a FALSE (non-null) value change ABORTED into a non-nullable column
//                bootLog.info( "'Notifications' table ABORTED field set to NOT NULL" )
                sqlObject.execute ( "alter table NOTIFICATION alter column ABORTED SET NOT NULL" )

                bootLog.info( "'Notifications' table DB Upgrade succeeded" )
            }
            else
            {
                bootLog.info( "'Notifications' table DB upgrade not required" )
            }
        }
        catch( Exception e ){
            bootLog.error( "'Notifications' table Upgrade failed.", e)
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
        bootLog.info( "'Notifications' table update check done" )
    }

    /**
     * Read the configuration of the OS Lockdown console from
     * /usr/share/oslockdown/console/conf/catalina.properties
     */
    void readSbConfiguration() {
        // configuration from catalina.properties
        def port = ConfigurationHolder.config?.tcs?.sb?.console?.port;
        def ip = ConfigurationHolder.config?.tcs?.sb?.console?.ip;
        def secureComms = ConfigurationHolder.config?.tcs?.sb?.console?.secure;
        // force the setting of secure comms on the mini trial so it can't be circumnavigated
        
        // check to see if there is missing configuration
        if ( !port || !ip || !secureComms ) {
//            bootLog.error("Missing console configuration.");
            def newConfig = new ConfigObject();            
            def tcsConfig = new ConfigObject();            
            def sbConfig = new ConfigObject();             
            def consoleConfig = new ConfigObject();
            
            // ip check
            if ( !ip ) {
               bootLog.error("catalina.properties 'tcs.sb.console.ip' was not set");
                consoleConfig["ip"] = "localhost";
            }
            
            // port check
            if ( !port ) {
                bootLog.error("catalina.properties 'tcs.sb.console.port' was not set");
                switch (Environment.current) {
                    case Environment.DEVELOPMENT:
                    case Environment.TEST:
                    consoleConfig["port"] = "8080";
                    break;
                    case Environment.PRODUCTION:
                    consoleConfig["port"] = "8443";
                    break;
                }             
            }
            
            // secure communication check
            if ( !secureComms ) {
//                bootLog.error("catalina.properties 'tcs.sb.console.secure' was not set");
                switch (Environment.current) {
                    case Environment.DEVELOPMENT:
                    case Environment.TEST:
                    consoleConfig["secure"] = "false";
                    break;
                    case Environment.PRODUCTION:
                    consoleConfig["secure"] = "true";
                    break;
                }
            }
            
            // merge the configuration
            sbConfig["console"] = consoleConfig;
            tcsConfig["sb"] = sbConfig;
            newConfig["tcs"] = tcsConfig;
            ConfigurationHolder.config.merge(newConfig);            
        }                   
        // log notification address
        bootLog.info("Console Notification Address - ${ConfigurationHolder.config?.tcs?.sb?.console?.ip}:${ConfigurationHolder.config?.tcs?.sb?.console?.port}");
        
        // set ssl properties        
        def consoleConfig = ConfigurationHolder?.config?.tcs?.sb?.console;      
        if ( consoleConfig ) {
            // secure communication configuration
            if ( consoleConfig.get("secure").toBoolean() ) {
                bootLog.info("Secured communications enabled");
                // keystore
                if ( consoleConfig.get('keystore')) {
                    System.setProperty("javax.net.ssl.keyStore",consoleConfig.get('keystore'));
                }
                else {
                    bootLog.error("catalina.properties 'keystore' property missing");
                }
        
                // keypass
                if ( consoleConfig.get('keypass') ) {
                    System.setProperty("javax.net.ssl.keyStorePassword",   consoleConfig.get('keypass'));
                }
                else {
                    bootLog.error("catalina.properties 'keypass' property missing");
                }
        
                // truststore
                if ( consoleConfig.get('truststore') ) {
                    System.setProperty("javax.net.ssl.trustStore",         consoleConfig.get('truststore'));
                }
                else {
                    bootLog.error("catalina.properties 'truststore' property missing");
                }
        
                // trustpass
                if ( consoleConfig.get('trustpass') ) {
                    System.setProperty("javax.net.ssl.trustStorePassword", consoleConfig.get('trustpass'));
                }
                else {
                    bootLog.error("catalina.properties 'trustpass' property missing");
                }
            }
            else {
                bootLog.info("Secured communications not enabled");
            }
        }
        else {
            bootLog.error("Unable to locate tcs.sb.console configuration properties");
        }
    }
    
    /**
     * Does the license check
     */
    void licenseCheck() {
        // even though we are calling this method in the resource.groovy
        // double check to make sure the license code is executed.
        SbLicense.getInstance();
    }
    
    /**
     * Checks to see what environment the application is if development
     * or this is the first run of production the database is populated with
     * the initial setup objects. ( users, roles, metadata, profiles )
     */
    boolean initialApplicationEvocation() {
        // should run?
        boolean runFirstStartActions = false;
    
        bootLog.info ("Checking for existing DB -> SecurityModule.list().size() = ${SecurityModule.list().size()}")
	
	// test
        switch (Environment.current) {
            case Environment.DEVELOPMENT:
                if ( SecurityModule.list().size() == 0 ) {
                    bootLog.info("Development: first run of OS Lockdown");
                    runFirstStartActions = true;
                }
                break;
            case Environment.TEST:
                if ( SecurityModule.list().size() == 0 ) {
                    bootLog.info("Test: first run of OS Lockdown");
                    runFirstStartActions = true;
                }
                break;
            case Environment.PRODUCTION:
                if ( SecurityModule.list().size() == 0 ) {
                    bootLog.info("Production: first run of OS Lockdown");
                    runFirstStartActions = true;
                }
                break;
        }
    
        return runFirstStartActions;
    }

    /**
     * Ok, go do a default load of the files from *disk* - we don't have an existing database yet
     */
    private void loadFilesFromDiskToDB() {
        // invoke the actions
            
        // ----------- Security Module Metadata Setup -----------
        loadSecurityModules( false );

        // ----------- Security Profiles Setup -----------
        loadSecurityProfiles( false );

        // ----------- Baseline Module Metadata Setup -----------
        loadBaselineModules( false );

        // ----------- Baseline Profiles Setup -----------
        loadBaselineProfiles( false );
            
        // if the product is stand-alone then a dummy group and client
        // must be added
        if ( SbLicense.instance.isStandAlone() ) {    
            createStandalone();
        }    
        
    }
     
    /**
     * Role based access control setup
     */
    private void establishSecurity() {
        bootLog.info("Establishing Security");
        // admin role
        // -can configure SB application
        // -can run scan, apply, baseline, undo, reports
        def adminRole = new ShiroRole(name: "Administrator").save() ;
        def adminUser;
        def now = new Date()
        adminUser = new ShiroUser(username: "admin", passwordHash: new Sha1Hash("Admin123").toHex(), lastChange:now).save();
         
        new ShiroUserRoleRel(user: adminUser, role: adminRole).save();
        bootLog.info("Administrator Role Established");
         
        // create the other roles other roles
        def userRole = new ShiroRole(name: "User").save();
        def secOfficerRole = new ShiroRole(name:"Security Officer").save();
        def mgmtRole = new ShiroRole(name:"Management").save();
         
        // setting up non-production preloads
        if ( Environment.current != Environment.PRODUCTION ) {
            // user role
            // -can run scan, apply, baseline, undo, reports
            def normalUser = new ShiroUser(username: "user", passwordHash: new Sha1Hash("asdf").toHex(), lastChange:now).save();
            new ShiroUserRoleRel(user: normalUser, role: userRole).save();
            bootLog.info("User Role Established");
             
            // security officer role
            // -can run/view scan, baseline, reports
            def secOfficerUser = new ShiroUser(username: "securityOfficer", passwordHash: new Sha1Hash("asdf").toHex(), lastChange:now).save();
            new ShiroUserRoleRel(user: secOfficerUser, role: secOfficerRole).save();
            bootLog.info("Security Officer Role Established");
             
            // management role
            // can view reports
            def mgmtUser = new ShiroUser(username: "mgmt", passwordHash: new Sha1Hash("asdf").toHex(), lastChange:now).save();
            new ShiroUserRoleRel(user: mgmtUser, role: mgmtRole).save();
            bootLog.info("Management Role Established");
        }
    }

    /**
     * Setup dispatcher notification listeners
     */
    void initializeNotificationHandlers() {
         
        // enterprise specific handlers
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            // group assessment report listener
            OSLockdownNotifier.getInstance().registerListener(groupAssessmentStateMachineService);
            bootLog.info("Group Assessment Listener Registered");
        }
         
        // persistence listener
        OSLockdownNotifier.getInstance().registerListener(dispatcherNotificationService);
        bootLog.info("Notification Persistence Listener Registered");
    }
     
    /**
     * Load the security modules into the database from
     * /usr/share/oslockdown/cfg/security-modules.xml
     *
     * @param resetMetadata
     */
    private void loadSecurityModules(boolean resetMetadata) {

        try {
            if ( resetMetadata ) {
                securityMetadataService.removeAll();
            }
            securityMetadataService.fromXml();
        }
        catch ( SecurityMetadataException securityMetadataException ) {
            bootLog.error("Unable to load the security metadata",securityMetadataException);
        }
    }

    /**
     * Load the baseline modules into the database from
     * /usr/share/oslockdown/baseline-modules.xml
     *
     * @param resetMetadata
     */
    private void loadBaselineModules(boolean resetMetadata) {

        try {
            if ( resetMetadata ) {
                baselineMetadataService.removeAll();
            }
            baselineMetadataService.fromXml();
        }
        catch ( BaselineMetadataException baselineMetadataException ) {
            bootLog.error("Unable to load the baseline metadata",baselineMetadataException);
        }
    }
     
    /**
     * Creates the profiles from the profiles directory and stores them in the
     * database.
     */
    void loadSecurityProfiles( boolean isUpgrade ) {
        // security profiles
        def securityProfile;
        
        // *.xml file pattern
        def pattern = ~/.*\.xml/;
        bootLog.info("Loading Security Profiles");
        SBFileSystemUtil.get(SB_LOCATIONS.PROFILES).eachFileMatch(pattern) { file ->
            bootLog.info("Checking on disk profile :${file}")
            try {
                securityProfile = securityProfileService.fromXml(file, isUpgrade );
                bootLog.info("Security Profile: ${securityProfile.name} Loaded");
            }
            catch ( Exception e ) {
                bootLog.error("Unable to load security profile: ${file.getAbsolutePath()}",e);
            }
        }
    }

    /**
     * Creates the baseline profiles from the baseline profiles directory and stores
     * them in the database
     */
    void loadBaselineProfiles( boolean isUpgrade ) {
        // baseline profiles
        def baselineProfile;

        // *.xml file pattern
        def pattern = ~/.*\.xml/;

        // load baseline profiles
        bootLog.info("Loading Baseline Profiles");
        SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_PROFILES).eachFileMatch(pattern) { file ->
            try {
                baselineProfile = baselineProfileService.fromXml(file, isUpgrade );
                bootLog.info("Baseline Profile: ${baselineProfile.name} Loaded");
            }
            catch ( Exception e ) {
                bootLog.error("Unable to load baseline profile: ${file.getAbsolutePath()}",e);
            }
        }
    }


    /**
     * Basic integrity check on Security Profiles and Baseline Profiles
     * For every Profile the Console sees in the database, there had better be a flat
     * file representing it on disk.  If not, edit any Group using it and set that entry
     * to 'None', along with a warning on disk
     */
     
    private void dbCheckIntegrity() {
    
        boolean exists;
        bootLog.info("Performing basic Console DB integrity checks...");
        bootLog.info("Verifying Security Profiles in Console DB actually exist...")
        def file;
        
        Profile.findAll().each { securityProfile -> 
            file = SBFileSystemUtil.getProfile(securityProfile.fileName)
            if ( file.exists() ) {
                bootLog.info( "  Security Profile '${securityProfile.name}' : file ${file.getAbsoluteFile()} exists.")
                exists = true;
            }
            else {
                bootLog.error( "  Security Profile '${securityProfile.name}' : file ${file.getAbsoluteFile()} does not exist!")
                exists = false;
            }
            Group.withCriteria {
                eq("profile",securityProfile);
            }.each { group ->
                bootLog.info( "    Found in Group '${group.name}'")
                if (! exists) {
                    bootLog.warn( "        Removing SecurityProfile '${securityProfile.name}' from '${group.name}'")
                    group.profile = null
                }
            }
            if (! exists) {
                securityProfile.delete()

                if (securityProfile.hasErrors()) {
                    m_log.error("Unable to delete Security Profile");
                    securityProfile.errors.allErrors.each { error ->
                        m_log.error(messageSource.getMessage(error,null));
                    }
                }

            }
        }

        bootLog.info("Verifying Baseline Profiles in Console DB actually exist...")

        BaselineProfile.findAll().each { baselineProfile -> 
            file = SBFileSystemUtil.getBaselineProfile(baselineProfile.fileName)
            if ( file.exists() ) {
                bootLog.info( "  Baseline Profile '${baselineProfile.name}' : file ${file.getAbsoluteFile()} exists.")
                exists = true;
            }
            else {
                bootLog.error( "  Baseline Profile '${baselineProfile.name}' : file ${file.getAbsoluteFile()} does not exist!")
                exists = false;
            }
            Group.withCriteria {
                eq("baselineProfile",baselineProfile);
            }.each { group ->
                bootLog.info( "    Found in Group '${group.name}'")
                if (! exists) {
                    bootLog.warn( "        Removing BaselineProfile '${BaselineProfile.name}' from Group '${group.name}'")
                    group.baselineProfile = null
                }
            }
            if (! exists) {
                baselineProfile.delete();
                if (baselineProfile.hasErrors()) {
                    m_log.error("Unable to delete Baseline Profile");
                    baselineProfile.errors.allErrors.each { error ->
                        m_log.error(messageSource.getMessage(error,null));
                    }
                }

            }
        }
    }     

    /**
     * Create the required standalone group and client
     */
    void createStandalone() {
        // domain objects
        Client standaloneClient;
        Group standaloneGroup;
        // successful setup
        boolean setupSuccessful = true;

        // stand alone client creation
        try {
            standaloneClient = new Client(name:"Standalone Client",hostAddress:"127.0.0.1",
                location:"localhost",contact:"Standalone Administrator", clientType:ClientType.CLIENT_STANDALONE);
            clientService.save(standaloneClient);
            bootLog.info("Created Standalone Client");
        }
        catch ( SbClientException clientException ) {
            bootLog.error("Unable to create stand-alone client");
            setupSuccessful = false;
        }

        // stand alone group creation
        try {
            standaloneGroup = new Group(name:"Standalone Group",description:"Standalone Group with a single client");
            standaloneGroup.addToClients(standaloneClient);
            groupService.save(standaloneGroup);
            bootLog.info("Created Standalone Group");
        }
        catch (SbGroupException groupException) {
            bootLog.error("Unable to create stand-alone client");
            setupSuccessful = false;
        }

        // check to see if the setup was completely successful
        if ( setupSuccessful ) {
            bootLog.info("Standalone Configuration Established");
        }
        else {
            bootLog.error("Unable to create stand-alone client");
        }
    }

    private void upgradeSecurityMetadataTo403Fix(){

        // Manual stuff for the upgrade to 4.0.3. The below code should run once to "fix" the problem,
        // but thereafter if it runs it won't break anything.
        
        //
        // 1. Remove single quotes around the library name for 'RemoveGamesAccount' and 'RemoveNewsAccount'
        //
        SecurityModule.findAll().each { module ->

            String libraryName = module.library
            if( libraryName.startsWith( SINGLE_QUOTE ) && libraryName.endsWith( SINGLE_QUOTE ) )
            {
                // Eat up enclosing single quotes. Leave for possibility of a single quote inside of the library name.
                // This is to handle 'RemoveGamesAccount' and 'RemoveNewsAccount'
                libraryName = libraryName.substring( 1, libraryName.length() - 1 )

                bootLog.info(" Stripping single quotes from library names. Original library [${module.library}] changed one [${libraryName}]");

                module.library = libraryName
            }
        }

        //
        // 2. Remove the Old "join" tables for the SecurityModule Many-to-Many relationships in the opposite direction
        // a. COMMON_PLATFORM_ENUMERATION_MODULES with CPE being the owning side,
        // b. COMPLIANCY_MODULES (with Compliancy being the owning side, and
        // c. MODULE_TAG_MODULES (with ModuleTag being the owning side)
        // (these 3 were fixed so now SecurityModule is the owning side) and delete all data from the Many-side table
        // (they will be re-populated with fresh data in loadSecurityModules(true) method).
        // The original 1-to-Many relationship tables (SECURITY_MODULE_MODULE_LIBRARY_DEPENDENCY and
        // SECURITY_MODULE_MODULE_OPTION) will be cleaned up in securityMetadataService.removeAll() from inside
        // loadSecurityModules(true) method as well, and re-populated with fresh data there as well.
        //
        def sqlObject
        try
        {
            sqlObject = new Sql( dataSource )

            //
            // "SELECT count(*) FROM INFORMATION_SCHEMA.SYSTEM_TABLES where table_schem=\'PUBLIC\' and
            //      table_name=\'COMMON_PLATFORM_ENUMERATION_MODULES\'"
            def rows = sqlObject.rows( OLD_TABLE_CPE_MODULES_EXISTS_QUERY )
            if( rows.size() == 1 && rows[0].getAt( 0 ) == 1 )
            {
                // table COMMON_PLATFORM_ENUMERATION_MODULES exists in the DB. This should *ONLY* be the case
                // on upgrade to 4.0.3. Drop the COMMON_PLATFORM_ENUMERATION_MODULES table.
                // Also delete all entries from COMMON_PLATFORM_ENUMERATION table (it will be re-initialized
                // from the metadata in loadSecurityModules(true);

                // Log the number of entries (it should match the number after the table from the other side
                // is re-initialized).
                //  rows = sqlObject.rows( ( String ) ( "${SELECT_COUNT_ALL_FROM} ${COMMON_PLATFORM_ENUMERATION_MODULES_TABLE}") );
                //  bootLog.info("${COMMON_PLATFORM_ENUMERATION_MODULES_TABLE} table contains [${rows[0].getAt( 0 ) }] rows");

                // WTF this does not work sqlObject.execute ( "delete from ${COMMON_PLATFORM_ENUMERATION_MODULES_TABLE}" );
                // so have to explicitly cast to String which sucks.
                sqlObject.execute ( ( String ) ("${DROP_TABLE} ${COMMON_PLATFORM_ENUMERATION_MODULES_TABLE}") );
                sqlObject.execute ( ( String ) ("${DELETE_FROM} ${COMMON_PLATFORM_ENUMERATION_TABLE}") );

                bootLog.info("cpe tables are upgraded to 4.0.3");
            }

            //
            // "SELECT count(*) FROM INFORMATION_SCHEMA.SYSTEM_TABLES where table_schem=\'PUBLIC\' and
            //      table_name=\'COMPLIANCY_MODULES\'"
            rows = sqlObject.rows( OLD_TABLE_COMPLIANCY_MODULES_EXISTS_QUERY )
            if( rows.size() == 1 && rows[0].getAt( 0 ) == 1 )
            {
                // table COMPLIANCY_MODULES exists in the DB. This should *ONLY* be the case
                // on upgrade to 4.0.3. Drop the COMPLIANCY_MODULES table.
                // Also delete all entries from COMPLIANCY table (it will be re-initialized
                // from the metadata in loadSecurityModules(true);

                // Log the number of entries (it should match the number after the table from the other side
                // is re-initialized).
                //  rows = sqlObject.rows( ( String ) ( "${SELECT_COUNT_ALL_FROM} ${COMPLIANCY_MODULES_TABLE}") );
                //  bootLog.info("${COMPLIANCY_MODULES_TABLE} table contains [${rows[0].getAt( 0 ) }] rows");

                sqlObject.execute ( ( String ) ("${DROP_TABLE} ${COMPLIANCY_MODULES_TABLE}") );
                sqlObject.execute ( ( String ) ("${DELETE_FROM} ${COMPLIANCY_TABLE}") );

                bootLog.info("compliancy tables are upgraded to 4.0.3");
            }

            //
            // "SELECT count(*) FROM INFORMATION_SCHEMA.SYSTEM_TABLES where table_schem=\'PUBLIC\' and
            //      table_name=\'MODULE_TAG_MODULES\'"
            rows = sqlObject.rows( OLD_TABLE_MODULE_TAG_MODULES_EXISTS_QUERY )
            if( rows.size() == 1 && rows[0].getAt( 0 ) == 1 )
            {
                // table MODULE_TAG_MODULES exists in the DB. This should *ONLY* be the case
                // on upgrade to 4.0.3. Drop the MODULE_TAG_MODULES table.
                // Also delete all entries from MODULE_TAG table (it will be re-initialized
                // from the metadata in loadSecurityModules(true);

                // Log the number of entries (it should match the number after the table from the other side
                // is re-initialized).
                //  rows = sqlObject.rows( ( String ) ( "${SELECT_COUNT_ALL_FROM} ${MODULE_TAG_MODULES_TABLE}") );
                //  bootLog.info("${MODULE_TAG_MODULES_TABLE} table contains [${rows[0].getAt( 0 ) }] rows");

                sqlObject.execute ( ( String ) ("${DROP_TABLE} ${MODULE_TAG_MODULES_TABLE}") );
                sqlObject.execute ( ( String ) ("${DELETE_FROM} ${MODULE_TAG_TABLE}") );

                bootLog.info("module tag tables are upgraded to 4.0.3");
            }
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
    }

    // Remove the UNIQUE constraint on CLIENT.NAME column. 
    // a. For new 4.0.4 installs this constraint is not in the DB so this method removes nothing
    // b. For upgrades from versions earlier than 4.0.4 to version 4.0.4, this method will drop this constraint
    private void upgradeClientTo404Fix(){

        def sqlObject
        try
        {
            sqlObject = new Sql( dataSource )

            String query = "select count(*) from INFORMATION_SCHEMA.SYSTEM_TABLE_CONSTRAINTS where TABLE_SCHEMA=\'PUBLIC\' and " +
                           "TABLE_NAME=\'CLIENT\' and CONSTRAINT_TYPE=\'UNIQUE\' and CONSTRAINT_NAME=\'SYS_CT_64\' "
            def rows = sqlObject.rows( query )
            if( rows.size() == 1 && rows[0].getAt( 0 ) == 1 )
            {
                // so have to explicitly cast to String which sucks.
                //sqlObject.execute ( ( String ) ("${DROP_TABLE} ${COMMON_PLATFORM_ENUMERATION_MODULES_TABLE}") );
                //sqlObject.execute ( ( String ) ("${DELETE_FROM} ${COMMON_PLATFORM_ENUMERATION_TABLE}") );

                sqlObject.execute ( "alter table CLIENT drop constraint SYS_CT_64" )

                bootLog.info("CLIENT table is upgraded to 4.0.4");
            }
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }
    }

    /**
     * Application Teardown
     */
    def destroy = {
        def shutdown
        if ( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            shutdown = "OS Lockdown Enterprise Console Shutdown" ;        
        }
        else if ( SbLicense.instance.isBulk()) {
            shutdown = "OS Lockdown Lock and Release Console Shutdown" ;        
        } 
        else {
            shutdown = "OS Lockdown Standalone Console Shutdown" ;        
        }
        def extensionsList = []
        extensionsList << "cs5Label=Result"        
        extensionsList << "cs5=Console shutdown"
        upstreamNotificationService.log(SyslogAppenderLevel.INFO,UpstreamNotificationTypeEnum.APP_START_STOP, ,"App Status", extensionsList);        
    }     

} 
