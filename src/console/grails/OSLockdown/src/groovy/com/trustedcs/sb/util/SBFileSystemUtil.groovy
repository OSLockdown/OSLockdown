/*
 * Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.util;

import org.apache.log4j.Logger;

/**
 * <p>This class is used to be an intermediary that will allow the application
 * to use convention over configuration for the location of data files.</p>
 * 
 * <p>/usr/share/oslockdown/profiles</p>
 * <p>/var/log/oslockdown.log</p>
 * <p>/var/lib/oslockdown/profiles</p>
 * <p>/var/lib/oslockdown/baselines</p>
 * <p>/var/lib/oslockdown/assessment</p>
 * <p>/var/lib/oslockdown/cce</p> 
 * @author amcgrath
 */
public class SBFileSystemUtil {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.util.FileSystem");
	 
    // enum of file locations
    public static enum SB_LOCATIONS {
        USR_SHARE_SB,
        VAR_LIB_SB,
        DB_EXPORT,
        CFG,
        PROFILES,
        PROFILE_COMPARISONS,
        BASELINE_PROFILES,
        REPORTS,
        BASELINES,
        BASELINE_COMPARISONS,
        ASSESSMENTS,
        ASSESSMENT_COMPARISONS,
        GROUP_ASSESSMENTS,
        ARCHIVE,
        ARCHIVE_GROUPS,
        ARCHIVE_CLIENTS,
        MODULES_METADATA,
        BASELINE_METADATA,
        OPTION_TYPES,
        AUDIT_LOG_FILE,
        LOG_FILE,
        LICENSE_FILE,
        BANNER,
        SCHEMA,
        MODULE_HELP_FILE,
        ADMIN_HELP_FILE,
        APPLIES,
        UNDOS};
	
    // [String:File]
    private static def fileMap = [:];
	
    /**
     * Method initializes the helper library so that the directories
     * and files can be referenced to the correct locations depending
     * on what file system the application/script is deployed on.
     * Note that the 'init' method sets *fixed* paths
     */
    public static void setFixed() {
        // placeholders
        def usrShareSb;
        def varLibSb;
		
        if ( File.separator.equals("/") ) {
            // unix
            usrShareSb = new File("/usr/share/oslockdown");
            varLibSb = new File("/var/lib/oslockdown");
        }
        else {
            // windows
            usrShareSb = new File("c:/sb/usr/share/oslockdown");
            varLibSb = new File("c:/sb/var/lib/oslockdown");            
        }
		fileMap[SB_LOCATIONS.USR_SHARE_SB] = usrShareSb;
        fileMap[SB_LOCATIONS.VAR_LIB_SB] = varLibSb;
        	
        // directories
        fileMap[SB_LOCATIONS.PROFILES] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"profiles");
        fileMap[SB_LOCATIONS.BASELINE_PROFILES] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"baseline-profiles");
        fileMap[SB_LOCATIONS.CFG] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"cfg");
        fileMap[SB_LOCATIONS.SCHEMA] = new File(fileMap[SB_LOCATIONS.CFG],"schema");
        fileMap[SB_LOCATIONS.DB_EXPORT] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"console/dbexport");

        // files
        fileMap[SB_LOCATIONS.LOG_FILE] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"logs/oslockdown.log");
        fileMap[SB_LOCATIONS.AUDIT_LOG_FILE] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"logs/oslockdown-audit.log");
        fileMap[SB_LOCATIONS.MODULES_METADATA] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"cfg/security-modules.xml");
        fileMap[SB_LOCATIONS.BASELINE_METADATA] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"cfg/baseline-modules.xml");
        fileMap[SB_LOCATIONS.OPTION_TYPES] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"cfg/optionTypes.xml");
        fileMap[SB_LOCATIONS.LICENSE_FILE] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"files/sb.license");
        fileMap[SB_LOCATIONS.BANNER] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"cfg/ConsoleWarningBanner.txt");
		
        // help files
        fileMap[SB_LOCATIONS.MODULE_HELP_FILE] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"console/webapps/OSLockdown/sbhelp/modules/jhelpmap.jhm");
        fileMap[SB_LOCATIONS.ADMIN_HELP_FILE] = new File(fileMap[SB_LOCATIONS.USR_SHARE_SB],"console/webapps/OSLockdown/sbhelp/admin/jhelpmap.jhm");


    }

    /**
     * Sets paths that depend on license type
     * 
     */
    public static void setDynamic(boolean isStandalone) {
        // report directories

        if ( isStandalone ) {
            fileMap[SB_LOCATIONS.REPORTS] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"reports/standalone");
        }
        else {
            fileMap[SB_LOCATIONS.REPORTS] = new File(fileMap[SB_LOCATIONS.VAR_LIB_SB],"reports/ec");
        }

        if ( !(fileMap[SB_LOCATIONS.REPORTS].exists()) )  {
            if ( !(fileMap[SB_LOCATIONS.REPORTS].mkdirs()) ) {
                m_log.error("Unable to create: ${fileMap[SB_LOCATIONS.REPORTS]}");
            }
        }
        
        fileMap[SB_LOCATIONS.ASSESSMENTS] = new File(fileMap[SB_LOCATIONS.REPORTS],"assessments");
        fileMap[SB_LOCATIONS.BASELINES] = new File(fileMap[SB_LOCATIONS.REPORTS],"baselines");
        fileMap[SB_LOCATIONS.APPLIES] = new File(fileMap[SB_LOCATIONS.REPORTS],"apply-reports");
        fileMap[SB_LOCATIONS.UNDOS] = new File(fileMap[SB_LOCATIONS.REPORTS],"undo-reports");

        // archive locations
        fileMap[SB_LOCATIONS.ARCHIVE] = new File(fileMap[SB_LOCATIONS.REPORTS],"archive");
        fileMap[SB_LOCATIONS.ARCHIVE_GROUPS] = new File(fileMap[SB_LOCATIONS.ARCHIVE],"groups");
        fileMap[SB_LOCATIONS.ARCHIVE_CLIENTS] = new File(fileMap[SB_LOCATIONS.ARCHIVE],"clients");

        // comparison locations
        fileMap[SB_LOCATIONS.BASELINE_COMPARISONS] = new File(fileMap[SB_LOCATIONS.REPORTS],"baseline-comparisons");
        if ( !(fileMap[SB_LOCATIONS.BASELINE_COMPARISONS].exists()) )  {
            if ( !(fileMap[SB_LOCATIONS.BASELINE_COMPARISONS].mkdirs()) ) {
                m_log.error("Unable to create: ${fileMap[SB_LOCATIONS.BASELINE_COMPARISONS]}");
            }
        }
        fileMap[SB_LOCATIONS.ASSESSMENT_COMPARISONS] = new File(fileMap[SB_LOCATIONS.REPORTS],"assessment-comparisons");
        if ( !(fileMap[SB_LOCATIONS.ASSESSMENT_COMPARISONS].exists()) )  {
            if ( !(fileMap[SB_LOCATIONS.ASSESSMENT_COMPARISONS].mkdirs()) ) {
                m_log.error("Unable to create: ${fileMap[SB_LOCATIONS.ASSESSMENT_COMPARISONS]}");
            }
        }
        fileMap[SB_LOCATIONS.PROFILE_COMPARISONS] = new File(fileMap[SB_LOCATIONS.REPORTS],"profile-comparisons");
        if ( !(fileMap[SB_LOCATIONS.PROFILE_COMPARISONS].exists()) )  {
            if ( !(fileMap[SB_LOCATIONS.PROFILE_COMPARISONS].mkdirs()) ) {
                m_log.error("Unable to create: ${fileMap[SB_LOCATIONS.PROFILE_COMPARISONS]}");
            }
        }
		
	}
    
    /**
     * Returns the directory for the group's reports
     * @param id
     */
    public static File getGroupDirectory(def id) {
        return new File(fileMap[SB_LOCATIONS.REPORTS],"groups/${id}"); 
    }
    
    /**
     * Returns the directory for the group's assessments
     * @param id
     */
    public static File getGroupAssessmentDirectory(def id) {
        return new File(getGroupDirectory(id),"assessments");
    }
    
    /**
     * Returns the directory for the group's assets
     * @param id
     */
    public static File getGroupAssetDirectory(def id) {
        return new File(getGroupDirectory(id),"assets");
    }  
    
    /**
     * Returns the directory for the client's reports
     * @param id
     */
    public static File getClientDirectory(def id) {
        return new File(fileMap[SB_LOCATIONS.REPORTS],"clients/${id}");
    }
    
    /**
     * Returns the directory for the client's assessments
     * @param id
     */
    public static File getClientAssessmentDirectory(def id) {
        return new File(getClientDirectory(id),"assessments");
    }
    
    /**
     * Returns the directory for the client's baselines
     */
    public static File getClientBaselineDirectory(def id) {
        return new File(getClientDirectory(id),"baselines");        
    }

    /**
     * Returns the directory for the client's applies
     * @param id
     */
    public static File getClientApplyDirectory(def id) {
        return new File(getClientDirectory(id),"apply-reports");
    }

    /**
     * Returns the directory for the client's undoes
     * @param id
     */
    public static File getClientUndoDirectory(def id) {
        return new File(getClientDirectory(id),"undo-reports");
    }
    
    /**
     * Returns the directory for the client's baselines
     */
    public static File getClientLogsDirectory(def id) {
        return new File(getClientDirectory(id),"logs");        
    }
    
    /**
     * Returns the Profile's file object for the given name
     * @param profileName
     */
    public static File getProfile(def profileName) {
    	return new File(fileMap[SB_LOCATIONS.PROFILES],profileName);
    }

    /**
     * Returns the Baseline Profile's file object for the given name
     * @param profileName
     */
    public static File getBaselineProfile(def profileName) {
    	return new File(fileMap[SB_LOCATIONS.BASELINE_PROFILES],profileName);
    }
	
    public static String toString() {
        def returnString = "\n";
        fileMap.each { key, value ->
            returnString += "$key $value\n";
        }
        return returnString;
    }
	
    public static def get(SB_LOCATIONS location) {
        return fileMap[location];
    }
}
