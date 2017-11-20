#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Baseline System - Master Module
#   - To use the baseline component, THIS directory must be in the Python
#     search path to pick up modules. For example, "<myparent>/Baseline"
#     Modules in the baseline-modules.xml reference modules as 
#     <section>/<component.py>. For example, "Network/ipTables" 
#
#     By default, this module will append the 
#     "/usr/share/oslockdown/Baseline" to the system search path.
#
#   - The baseline-modules.xml defines ALL baseline modules and associated
#     Python module (pyModulePath attribute). For testing purposes, you
#     can override the default baseline-modules.xml file by setting the
#     operating system environment variable BASELINE_CONFIG.
#
#   - This module only has one function which needs to be called: create()
#     Optionally, you can pass it the absolute path to a baseline profile
#     or it will use the default. The baseline profile identifies which
#     modules are to be called in order to collected data. This is done
#     by setting the "enabled" attribute to either 'true' or 'false'.
#
#     NOTE: To help streamline testing during development, try using the
#           <source>/src/core/test-baseline.sh script.
#
##############################################################################
import libxml2
import sys
import platform
import datetime
import os
import pwd
    
sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/Baseline")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sbProps
import sb_utils.os.info
import sb_utils.hardware
from sb_utils.misc.tcs_utils import validateXML
import tcs_utils
import sb_utils.file.dac
import sb_utils.SELinux

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()

MODULE_NAME = "Baseline"
MODULE_REV  = "$Rev: 23917 $".strip('$')
    
DEFAULT_BASELINE_PROFILE = os.path.join(sbProps.BASELINE_PROFILES, 'default.xml')


def create(baselineProfile=DEFAULT_BASELINE_PROFILE, modVerbose=False, profile_perm=False):

    logger.notice(MODULE_NAME, "---------------- Initiating Baseline -------------------")
    logger.debug(MODULE_NAME, "Baseline Engine - %s" % MODULE_REV )

    if os.environ.has_key('BASELINE_CONFIG'):
        BaselineConfigFile = os.environ['BASELINE_CONFIG'] 
    else:
        BaselineConfigFile = sbProps.BASELINE_CONFIG 

    file_owner = tcs_utils.return_owner_uid(baselineProfile)
    
    if (not profile_perm and ( not sb_utils.file.dac.isPermOkay(filepath=baselineProfile, testMode='0600', ignoreExcludes=True) or file_owner != 0)):
        msg = "Invalid permissions for selected profile. " \
              "Fix permissions or use force flag (-f)."
        logger.critical(MODULE_NAME, msg)
        print >> sys.stderr, msg
        return False


    # Validate baseline configuration file and provided profiel against schema 
    if not os.path.isfile(sbProps.XSD_BASELINE_PROFILE):
        msg = "Skipping validation of baseline profile against its schema -- unable to locate %s" % sbProps.XSD_BASELINE_PROFILE
        logger.warning(MODULE_NAME, msg)
    else: 
        validXML = validateXML(xmlDoc=baselineProfile, xmlSchema=sbProps.XSD_BASELINE_PROFILE)
        if validXML == True:
            logger.debug(MODULE_NAME, "Validated %s against schema definition" % baselineProfile)
        else:
            msg = "%s profile does not validate against schema definition" % baselineProfile
            logger.critical(MODULE_NAME, msg)
            sys.exit(sbProps.EXIT_FAILURE)

    if not os.path.isfile(sbProps.XSD_BASELINE_CONFIG):
        msg = "Skipping validation of baseline module configuration against its schema -- unable to locate %s" % sbProps.XSD_BASELINE_CONFIG
        logger.warning(MODULE_NAME, msg)
    else: 
        validXML = validateXML(xmlDoc=BaselineConfigFile, xmlSchema=sbProps.XSD_BASELINE_CONFIG)
        if validXML == True:
            logger.debug(MODULE_NAME, "Validated %s against schema definition" % BaselineConfigFile)
        else:
            msg = "%s profile does not validate against schema definition" % BaselineConfigFile
            logger.critical(MODULE_NAME, msg)
            sys.exit(sbProps.EXIT_FAILURE)


    # Parse Baseline Profile
    try:
        profileDoc = libxml2.parseFile(baselineProfile)
        logger.info(MODULE_NAME, "Using baseline profile %s" % baselineProfile)
    except libxml2.parserError, err:
        logger.critical(MODULE_NAME, "Exiting: %s - %s" % (str(err), baselineProfile) )
        sys.exit(sbProps.EXIT_FAILURE)

    try:
        configDoc = libxml2.parseFile(BaselineConfigFile)
        logger.info(MODULE_NAME, "Using baseline configuration file %s" % BaselineConfigFile)
    except libxml2.parserError, err:
        logger.critical(MODULE_NAME, "Exiting: %s - %s" % (str(err), BaselineConfigFile) )
        sys.exit(sbProps.EXIT_FAILURE)

        
    namespace = None
    today = datetime.datetime.now()
    creation_timestamp = today.strftime("%Y-%m-%d %T %Z").strip()

    # get the name of the profile from the profile itself, not the filename
    try:
        profileNode = profileDoc.xpathEval("/BaselineProfile")[0]
        profileName = u'%s' % profileNode.prop("name")
    except: 
        profileName = ''


    
    # Create root node, namespace, and appropriate attributes....
    doc = libxml2.newDoc("1.0")
    root = doc.newChild(None,  "BaselineReport", None)
    root.setProp("sbVersion", sbProps.VERSION)

    reportInfo = root.newChild(None, "report", None)
    reportInfo.setNs(namespace)
    
    reportInfo.setProp("profile",     profileName)
    reportInfo.setProp("created",     creation_timestamp)
    reportInfo.setProp("hostname",    platform.node())
    reportInfo.setProp("dist",        sb_utils.os.info.getDistroName())
    reportInfo.setProp("distVersion", sb_utils.os.info.getDistroVersion())
    reportInfo.setProp("cpe",         sb_utils.os.info.getCpeName().replace("cpe:",""))
    reportInfo.setProp("arch",        platform.machine() )
    reportInfo.setProp("totalMemory", "%sMB" % str(sb_utils.hardware.getTotalMemory()))
    
    
    if sb_utils.os.info.is_solaris() == True:
        try:
            reportInfo.setProp("kernel", os.uname()[3])
        except IndexError:
            reportInfo.setProp("kernel", "Unknown")
    else:
        reportInfo.setProp("kernel", platform.release() )
    
    # Get CPU Information
    cpuInfo = sb_utils.hardware.getCpuInfo() 
    if type(cpuInfo) != type({}):
        reportInfo.setProp("cpuInfo",  str(cpuInfo))
        del cpuInfo
    else:
        count = len(cpuInfo.keys())
        for cpuItem in cpuInfo.keys():
            if count > 0:
                msg = "%s x %s" % (str(cpuInfo[cpuItem]), cpuItem)
            else:
                msg = "%s x %s, " % (str(cpuInfo[cpuItem]), cpuItem)
            reportInfo.setProp("cpuInfo",  msg)
            count = count - 1
    del cpuInfo
    
    ##############################################################################
    ## Now Begin collecting data requested in profile
    topOfSections = root.newChild(namespace, "sections", None)
    profileSections = profileDoc.xpathEval("/BaselineProfile/section")
    
    for sectionNode in profileSections:
        section = topOfSections.newChild(namespace, "section", None)
        sectionName =  sectionNode.prop("name")
        section.setNsProp(namespace, "name", sectionName)
    
        for profileSubsection in sectionNode.xpathEval("./module"):
            subsectionName = profileSubsection.prop("name")

            if sbProps.ABORT_REQUESTED == True:
                logger.warn(MODULE_NAME, "Aborted, skipping - %s/%s" % (sectionName, subsectionName))
                continue

            if profileSubsection.prop("enabled") == 'false':
                logger.debug(MODULE_NAME, "Disabled - %s/%s" % (sectionName, subsectionName))
                continue

            if sectionName == 'Software':
                subsection = section
            else:
                subsection = section.newChild(namespace, "subSection", None)

            subsection.setNsProp(namespace, "name", subsectionName)

            try:
                libPath = configDoc.xpathEval("/BaselineConfiguration/section[@name = '%s']/module[@name = '%s']" % (sectionName, subsectionName))[0]
            except IndexError, err:
                print "ERROR: %s" % str(err)
                continue

            libPath = libPath.prop("pyModulePath")

            try:
                baselineModule = __import__(libPath)
                baselineModule = vars(baselineModule)[libPath.split('.')[-1]]

            except (SyntaxError, ImportError), err:
                logger.error(MODULE_NAME, """Unable to import "%s/%s" (%s): %s""" % (sectionName, subsectionName, libPath, str(err)))
                if modVerbose == True: 
                    print >> sys.stderr, "ERROR: %s" % err
                continue

            try:
                logger.info(MODULE_NAME, "INFO: Collecting %s/%s" % (sectionName, subsectionName))
                if modVerbose == True:
                    print >> sys.stdout, "INFO: Collecting %s/%s" % (sectionName, subsectionName)

                # Execute Module to collect data
                try:
                    baselineModule.collect(subsection)
                except Exception, err:
                    logger.error(MODULE_NAME, "ERROR: %s" % err)
                    if modVerbose == True:
                        print >> sys.stdout, "ERROR: %s/%s -- %s" % (sectionName, subsectionName, err)
                

            except ImportError, err:
                msg = "Module %s reported an error: %s" % (libPath, err)
                logger.error(MODULE_NAME, msg)
                if modVerbose == True: 
                    print >> sys.stderr, "ERROR: " + msg
                continue

            except TypeError, err:
                msg = "Module %s reported an error: %s" % (libPath, err)
                logger.error(MODULE_NAME, msg)
                if modVerbose == True: 
                    print >> sys.stderr, "ERROR: " + msg
                continue

            except Exception, err:
                msg = "Module %s reported an error: %s" % (libPath, err)
                logger.error(MODULE_NAME, msg)
                if modVerbose == True: 
                    print >> sys.stderr, "ERROR: " + msg
                continue

    
    ##############################################################################
    # Write report to disk
        
    # Reports will be suffixed with YYYYMMDD_HHMMSS.xml
    reportSuffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.xml")
    FinalBaselineReport = 'baseline-report-%s' % reportSuffix
    FinalBaselineReport = os.path.join(sbProps.BASELINE_REPORTS, FinalBaselineReport)


    # This is primarily used in testing
    if os.environ.has_key('BASELINE_OUTPUT_FILE'):
        FinalBaselineReport = os.environ['BASELINE_OUTPUT_FILE']

    try:
        out_obj = open(FinalBaselineReport, 'w')
        os.chmod(FinalBaselineReport,0750)
        doc.saveTo(out_obj, 'UTF-8', 1)
        out_obj.close()
    except Exception, err:
        logger.error(MODULE_NAME, "Unable to create %s" % FinalBaselineReport)
        if modVerbose == True:
            print >> sys.stderr, "ERROR: %s" % err
        sys.exit(sbProps.EXIT_FAILURE)

    print >> sys.stdout, "CREATED: %s" % FinalBaselineReport

    allowConsoleAccess(filePath=FinalBaselineReport)

    logger.notice(MODULE_NAME, "Wrote baseline report to %s" % FinalBaselineReport)
    if not os.path.isfile(sbProps.XSD_BASELINE_REPORT):
        msg = "Skipping validation of baseline report against its schema -- unable to locate %s" % sbProps.XSD_BASELINE_REPORT
        logger.warning(MODULE_NAME, msg)
    else: 
        validXML = validateXML(xmlDoc=FinalBaselineReport, xmlSchema=sbProps.XSD_BASELINE_REPORT)
        if validXML != True:
            msg = "%s does not validate against its schema" % FinalBaselineReport
            logger.warning(MODULE_NAME, msg)

            if modVerbose == True:
                print >> sys.stderr, "ERROR: " + msg

    try:
        profileDoc.freeDoc()
        configDoc.freeDoc()
        doc.freeDoc()
    except:
        pass


############################################################
### Set perms on file/directory so console can access it ###
############################################################
def allowConsoleAccess(filePath=None):
    """
    If the the console package is installed, allow the sbwebapp 
    user to read 'filePath'
    """
    print "Resetting access on %s" % filePath

    if filePath == None or not os.path.exists(filePath):
        return

    if sb_utils.os.info.is_solaris() == True:
        consolepkg = 'TCSsbconsole'
    else:
        consolepkg = 'oslockdown-console'

    if not sb_utils.os.software.is_installed(pkgname=consolepkg):
        return

    msg = "'%s' package is installed; adjusting access controls for %s..." % (consolepkg, filePath)
    logger.debug(MODULE_NAME, msg)

    # Retrieve information about the 'sbwebapp' account 
    try:
        sb_struct = pwd.getpwnam('sbwebapp')
    except KeyError:
        msg = "Console package '%s' is installed but the 'sbweapp' user does not exist" % consolepkg
        logger.critical(MODULE_NAME, msg)
        return

    # Change ownership to the 'sbwebapp' account
    try:
        os.chown(filePath, int(sb_struct.pw_uid), int(sb_struct.pw_gid))
        sb_utils.SELinux.restoreSecurityContext(filePath)
    except OSError, err:
        msg = "Unable to set ownership on %s : %s" % (filePath, err)
        logger.error(MODULE_NAME, msg)

    # Set permissions
    try:
        if os.path.isfile(filePath):
            os.chmod(filePath, 0640)

        if os.path.isdir(filePath):
            os.chmod(filePath, 0750)

    except OSError, err:
        msg = "Unable to set permssions on %s : %s" % (filePath, err)
        logger.error(MODULE_NAME, msg)


    return

