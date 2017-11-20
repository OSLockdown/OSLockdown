/**
 *
 * Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 *
 *
 *
 * Note - this is the stub for the 'open source' variant of OS Lockdown
 *      - it defaults to an unlimited count license for the the 'Enterprise'
 *      - variant, and as such most of the guts herein have been replaced by
 *      - stubs that return a consistent value, rather than do the more 
 *      - extensive ripping out of calls through out the remainder of the code
 *      - base.  
 *
 */
package com.trustedcs.sb.license;

import com.trustedcs.sb.util.ClientType;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import grails.util.Environment;

import org.apache.log4j.Logger;

class SbLicense {


    // license properties and some well known values
    public static final String PRODUCT = "product";
    public static final String TYPE = "type";
    public static final String STANDALONE = "STANDALONE";
    public static final String ENTERPRISE = "ENTERPRISE";
    public static final String MINITRIAL = "TryMe";
    public static final String CLIENT_LIMIT = "clientCountLimit";
    public static final String PROCESSOR_LIMIT = "processorCountLimit";
    public static final String VERSION = "version";
    public static final String VALID_TILL = "validTill";
    public static final String PERMANENT = "PERMANENT";
    public static final String BULK = "BULK";
    public static final String TRIAL = "TRIAL";
    public static final String SUBSCRIPTION = "SUBSCRIPTION";

    // Display names of the 3 licensing models
    public static final String ENTERPRISE_LICENSE       = "Enterprise";
    public static final String LOCK_AND_RELEASE_LICENSE = "Lock and Release";
    public static final String STANDALONE_LICENSE       = "Standalone";

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.license.SbLicense");

    // singleton instance
    private static instance;
    private static currentLicenseText;
    private static isLoaded = false;
    private static consoleIsEnterprise = false;
    private static consoleIsStandalone = false;
    private static consoleTypeString = ""
    /**
     * Private singleton constructor
     * @param properties
     */

    /**
     * Private constructor
     */
    private SbLicense() {
    }

    /**
     *  Note for isEnterprise and isStandalone
     *  The previous commercial release had 2 license files, one for Enterprise
     *  and one for Standalone.  The opensource release has a single file whose
     *  text will be 'Enterprise' or 'Standalone', if nothing is found assume
     *  an Enterprise Console.
     *  It is possible to change a 'Standalone' into an 'Enterprise' Console by 
     *  editing the textof this file.  However, converting from Enterprise to 
     *  Standalone is *NOT* recommended.  The database structure is the same 
     *  between them, and the basic 'under-the-hood' ops are the same.  A 
     *  Standalone can be considered an Enterprise of size one, but the names 
     *  of the single Client and single Group are hardcoded for Standalone installation. 
     */
     

    static private void readAndProcessLicense()
    {
      def firstRead = false;
      if (!instance) {
        instance = new SbLicense()
        instance.consoleIsEnterprise = false;
        instance.consoleIsStandalone = false;
        instance.consoleTypeString = "";
      }
      def consoleType = new File('/var/lib/oslockdown/files/ConsoleType.txt')   
      if (consoleType.exists())
      {       
        def txt = consoleType.text.trim()
        if (txt != instance.consoleTypeString) 
        {
          m_log.info("Console detecting change in license type")
          firstRead = true
          instance.consoleIsEnterprise = false;
          instance.consoleIsStandalone = false;
        }
        if (txt == 'Enterprise')
        {
            if (firstRead) 
            {
              m_log.info("Console start up - detected Enterprise installation")
            }
            instance.consoleIsEnterprise = true;
            instance.consoleTypeString = txt
        }
        else if (txt == 'Standalone')
        {
            if (firstRead) 
            {
              m_log.info("Console start up - detected Standalone installation")
            }
            instance.consoleIsStandalone = true;
            instance.consoleTypeString = txt
        }
        else 
        {
            if (firstRead) 
            {
              m_log.warn("Console start up - unable to determine Enterprise/Standalone - assuming Enterprise")
            }
            instance.consoleIsEnterprise = true;
            instance.consoleTypeString = ""
        }
      }
      else
      {
        if (firstRead) 
        {
          m_log.warn("Console start up - unable to determine Enterprise/Standalone - assuming Enterprise")
        }
        instance.consoleIsEnterprise = true;
      }
    }
    
    static synchronized void reloadLicense() {
    }
    
    /**
     * Get the singleton instance
     */
    static synchronized SbLicense getInstance() {
        readAndProcessLicense();
        return instance;
    }


    /**
     * Checks to see if there is a valid license line
     * @return if the license is valid
     */
    public boolean isValid() {
        return true;
    }

    /**
     * Returns when the latest license for the latest version is valid till.
     */
    public Date validTill() {
        return getUnexpiringDate();
    }


    /**
     * @return a date that has the end time of 2037
     */
    private Date getUnexpiringDate() {
        def date=new Date();
        date.time=2147483647000L   // 32 bit maximum *signed* value in *milliseconds*
        return  date;

    }

    /**
     * Returns the latest version that the license is validated for
     * @returns get the latest version
     */
    public int getVersion() {
        int latestVersion = 4;
        return latestVersion;
    }


     
    /**
     * Returns if the license is enterprise
     * @returns if the license is for the enterprise mode
     */
    public boolean isEnterprise() {
        return instance.consoleIsEnterprise;
    }

    /**
     * Returns if the license is bulk
     * @returns if the license is for bulk mode
     */
    public boolean isBulk() {
        boolean isBulk = false;
        return isBulk;
    }

    /**
     * Returns if the license is standalone - if both licenses found - ENTERPRISE trumps Standalone
     * @returns if the license is for standalone mode
     */
    public boolean isStandAlone() {
        return instance.consoleIsStandalone;
    }

    /**
     * Returns if the license is standalone
     * @returns if the license is for standalone mode
     */
    public boolean allowProcessors() {
        boolean allowProcessors = true;
        return allowProcessors;
    }

    public String timeBombType() {
        String timeBombType="";
        return timeBombType;
    }

    
    public boolean isFullTrial() {
        return false;
    }

    public String licenseSynopsis() {
        String synopsis = "OpenSourced Enterprise License - unlimited client count ";
        
        return synopsis;
    }
}
