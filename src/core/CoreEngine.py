#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Parse the provided profile and load security modules which have been correlated
# in the modules configuration file.
#
##############################################################################

MODULE_NAME = "CoreEngine"
MODULE_REV  = "$Rev: 24097 $".strip('$').strip()

import os
import sys
import libxml2
import datetime
import time
import sbProps
import pwd
import platform
import xml.sax.saxutils
import random

os.sys.path.append(sbProps.SB_BASE)
import ModuleInfo
import StateHandler
import sb_utils.file.dac
import sb_utils.file.exclusion
import sb_utils.file.whitelists

try:
    import TCSLogger
except ImportError:
    try:
        from sb_utils.misc import TCSLogger
    except ImportError:
        raise

import sb_utils.os.info
import sb_utils.os.software
import sb_utils.hardware
import tcs_utils
import sb_utils.SELinux

class SkipModule(Exception): pass

# List of available Modules
if os.path.isfile(sbProps.SB_CONFIG_FILE):
    SB_CONFIG_FILE = sbProps.SB_CONFIG_FILE 
else:
    SB_CONFIG_FILE = "../security_modules/cfg/security-modules.xml"


XSD_CONFIG_FILE = sbProps.XSD_CONFIG_FILE  # Schema to validate configuration

# Schema to validate profile
if os.path.isfile(sbProps.XSD_PROFILE):
    XSD_PROFILE  = sbProps.XSD_PROFILE 
else:
    print >> sys.stderr, \
         "ERROR: Unable to locate %s; trying source code location..." % sbProps.XSD_PROFILE
    if os.path.isfile('../security_modules/cfg/schema/SecurityProfile.xsd'):
        XSD_PROFILE = '../security_modules/cfg/schema/SecurityProfile.xsd'
        print >> sys.stderr, "WARNING: Using ../security_modules/cfg/schema/SecurityProfile.xsd"
    else:
        XSD_PROFILE = ""

# Generate these *now* to prevent log from cluttering...
sb_utils.file.exclusion.exlist()
sb_utils.file.whitelists.whlists()

############################################################
### Set perms on file/directory so console can access it ###
### Need to check the log file as well, just in case it  ###
### was rotated                                          ###
############################################################
def allowConsoleAccess(filePath=None):
    """
    If the the console package is installed, allow the sbwebapp 
    user to read 'filePath'
    """
    logger = TCSLogger.TCSLogger.getInstance()

    if filePath == None or not os.path.exists(filePath):
        return 

    if sb_utils.os.info.is_solaris() == True:
        consolepkg = 'TCSoslockdown-console'
    else:
        consolepkg = 'oslockdown-console'

    # Retrieve information about the 'sbwebapp' account 
    try:
        sb_struct = pwd.getpwnam('sbwebapp')
    except KeyError:
        msg = "Console package '%s' is installed but the 'sbweapp' user does not exist" % consolepkg
        logger.critical(MODULE_NAME, msg)
        return

    listToVet = [ sbProps.SB_LOG, filePath ]
    
    # get the parent directory of the reports, and add that to the list of entities to be vetted for ownership/perms
    reportParentDir = os.path.split(filePath)[0]
    if reportParentDir not in listToVet:
        listToVet.append(reportParentDir)
       
    
    for thisfile in listToVet:
    
        msg = "Enforcing ownership/perms on %s..." % (thisfile)
        logger.debug(MODULE_NAME, msg)
        # Change *group* ownership to the 'sbwebapp' account
        try:
#            os.chown(thisfile, int(sb_struct.pw_uid), int(sb_struct.pw_gid))
            os.chown(thisfile, -1 , int(sb_struct.pw_gid))
            sb_utils.SELinux.restoreSecurityContext(thisfile)
        except OSError, err:
            msg = "Unable to set ownership on %s : %s" % (thisfile, err)
            logger.error(MODULE_NAME, msg)

    # Set permissions
        try:
            if os.path.isfile(thisfile):
                os.chmod(thisfile, 0640)
            # don't touch directories, they should be set by RPM
            if os.path.isdir(thisfile):
                os.chmod(thisfile, 03750)

        except OSError, err:
            msg = "Unable to set permssions on %s : %s" % (thisfile, err)
            logger.error(MODULE_NAME, msg)



    return



#################################
### Validate Security Profile ###
#################################
def validateProfile(profilePath=None):
    """
    Validate profilePath against profile schema
    """
    logger = TCSLogger.TCSLogger.getInstance()

    if XSD_PROFILE == "":
        return None
    
    try:
        ctxt = libxml2.schemaNewParserCtxt(XSD_PROFILE)
        schema = ctxt.schemaParse()
        validationCtxt = schema.schemaNewValidCtxt()
        doc = libxml2.parseFile(profilePath)
        instance_Err = validationCtxt.schemaValidateDoc(doc)
        doc.freeDoc()
    except Exception, err:
        logger.error(MODULE_NAME, str(err))
        return False

    if instance_Err != 0:
        msg = "%s is invalid according to its schema %s" % (profilePath, XSD_PROFILE) 
        logger.error(MODULE_NAME, msg)
        return False

    msg = "%s has been validated against its schema %s" % (profilePath, XSD_PROFILE) 
    logger.debug(MODULE_NAME, msg)
    return True


######################################################
### Perform reqeusted action: scan, apply, or undo ###
######################################################
def performAction(profilePath=None, action=None, verbose=False, isShim=False, profile_perm=False, modsToDo=[]):
    """
    Perform specified action using profile

    Keyword arguments:
    profilePath -- physical path to security profile
    action -- Either 'scan', 'apply', or 'undo'
    """
    today = datetime.datetime.now()
    logger = TCSLogger.TCSLogger.getInstance()

    logger.notice(MODULE_NAME, "Core Engine (%s): Action request '%s' using '%s'" % (MODULE_REV, str(action), profilePath))
    if action not in ['scan', 'apply', 'undo'] or action == None:
        logger.critical(MODULE_NAME, "'%s' is an unrecognized action." % str(action))
        return False
    
    file_owner = tcs_utils.return_owner_uid(profilePath)
    
    if (not profile_perm and ( not sb_utils.file.dac.isPermOkay(filepath=profilePath, testMode='0600', ignoreExcludes=True) or file_owner != 0)):
        msg = "Invalid permissions for selected profile. " \
              "Fix permissions or use force flag (-f)."
        logger.critical(MODULE_NAME, msg)
        print >> sys.stderr, msg
        return False


    # Update global scan-id file
    tcs_utils.update_sys_scanid()

    # Instantiate instance of StateHandler and record last action request
    stateMgr = StateHandler.StateHandler()
    stateMgr.updateLastAction(action=action)


    # Verify that no 'profile' specific file remain on the system...
    for fileBase in [sbProps.EXCLUSION_DIRS, sbProps.INCLUSION_FSTYPES, sbProps.SUID_WHITELIST, sbProps.SGID_WHITELIST ]:
        fileName = fileBase + ".profile"
        if os.path.exists(fileName):
            msg = "Removing '%s' name, leftover from previous invocation..." % os.path.basename(fileName)
            logger.info (MODULE_NAME, msg)
            os.unlink(fileName)
            
    # Get Report's Timestamp which will be part of its filename
    reportTimestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if action == "scan":  
        rootElementName = "AssessmentReport"
        reportPrefix = "assessment-report"
        reportsPath = sbProps.ASSESSMENT_REPORTS

    if action == "apply": 
        rootElementName = "ApplyReport"
        reportPrefix = "apply-report"
        reportsPath = sbProps.APPLY_REPORTS

    if action == "undo":  
        rootElementName = "UndoReport"
        reportPrefix = "undo-report"
        reportsPath = sbProps.UNDO_REPORTS

#    if not os.path.isdir(reportsPath):
#        os.mkdir(reportsPath)
#        allowConsoleAccess(reportsPath)

    outputReport = os.path.join(reportsPath, "%s-%s.xml" % (reportPrefix, reportTimestamp))

    # Get Dictionary of module metadata
    logger.debug(MODULE_NAME, "Reading %s" % SB_CONFIG_FILE)

    ModuleConfigs  = ModuleInfo.sbModule(configFile=SB_CONFIG_FILE)
    logger.debug(MODULE_NAME, "Loaded metadata for %d modules" % len(ModuleConfigs))

    LibraryMapping = ModuleInfo. getModuleToLibraryMap(configFile=SB_CONFIG_FILE)
    logger.debug(MODULE_NAME, "Mapped %d modules to their libraries" % len(LibraryMapping))

    sysCpeName =  sb_utils.os.info.getCpeName()
    logger.notice(MODULE_NAME, "Identified this platform as %s" % sysCpeName)

    # Step 1:  Open Profile and configuration file
    profileDoc = libxml2.parseFile(profilePath)

    ##########################################################################
    # Step 2: Create Empty document which can be populated during 
    #         module actions
    #
    finalReport = libxml2.newDoc("1.0")
    root = finalReport.newChild(None,  rootElementName, None)
    root.setProp("sbVersion", sbProps.VERSION)

    reportInfoNode = root.newChild(None, "report", None)
    moduleResultsNode = root.newChild(None, "modules", None)

    today = datetime.datetime.now()
    creation_timestamp = today.strftime("%Y-%m-%d %T %Z").strip()


    # Grab profile Description
    profileName = 'Undefined'
    try:
        profileNode = profileDoc.xpathEval("/profile")[0]
        profileName = profileNode.prop("name")
    except: 
        pass
    reportInfoNode.setProp("profile",  u'%s' % profileName)
    msg = "PROFILE: %s" % (profileName)

    print >> sys.stdout, msg

    # Grab profile Description
    try:
        profileNode = profileDoc.xpathEval("/profile/info/description/verbose")[0]
        reportInfoNode.newChild(None, "description", profileNode.getContent() )
    except: 
        reportInfoNode.newChild(None, "description", None)


    # Populate info node stuff
    reportInfoNode.setProp("created",     creation_timestamp)
    reportInfoNode.setProp("hostname",    platform.node())
    reportInfoNode.setProp("dist",        sb_utils.os.info.getDistroName())
    reportInfoNode.setProp("distVersion", sb_utils.os.info.getDistroVersion())
    reportInfoNode.setProp("cpe",         sb_utils.os.info.getCpeName())
    reportInfoNode.setProp("arch",        platform.machine() )
    reportInfoNode.setProp("totalMemory", "%sMB" % str(sb_utils.hardware.getTotalMemory()))
    
    if sb_utils.os.info.is_solaris() == True:
        try:
            reportInfoNode.setProp("kernel", os.uname()[3])
        except IndexError:
            reportInfoNode.setProp("kernel", "Unknown")
    else:
        reportInfoNode.setProp("kernel", platform.release() )
    
    # Get CPU Information
    cpuInfo = sb_utils.hardware.getCpuInfo() 
    if type(cpuInfo) != type({}):
        reportInfoNode.setProp("cpuInfo",  str(cpuInfo))
        del cpuInfo
    else:
        count = len(cpuInfo.keys())
        for cpuItem in cpuInfo.keys():
            if count > 0:
                msg = "%s x %s" % (str(cpuInfo[cpuItem]), cpuItem)
            else:
                msg = "%s x %s, " % (str(cpuInfo[cpuItem]), cpuItem)
            reportInfoNode.setProp("cpuInfo",  msg)
            count = count - 1
    del cpuInfo


    ##########################################################################
    ## Iterate through each module and perform action
    ##
    os.sys.path.append(os.path.join(sbProps.SB_BASE, 'security_modules'))

    # First, build a dictionary modules in the profile keyed by the sortKey
    # attribute so, we can perform a lexical sort and execute them accordingly.
    #
    # Secondly, grab any option values provided in the profile for each
    # module.
    #
    executionList = {}
    optionValueList = {}
    for moduleNode in profileDoc.xpathEval("/profile/security_module"):
        moduleName = moduleNode.prop("name")

        # We must do a composite key to eliminate duplicate sortKey attributes
        # sortKey should be treated as a number, and we'll turn that into a 4 character 
        # string with leading zeros 
        try:
            libraryName  =  LibraryMapping[moduleName]  
            sortKey      = ModuleConfigs[libraryName]['sortKey'].rjust(4).replace(' ','0') 
        except KeyError:
            continue

        if not (modsToDo == [] or moduleName in modsToDo or libraryName in modsToDo):
            continue
        compositeKey = "%s:%s" % (sortKey, moduleName)
        executionList[compositeKey] = moduleName

        #
        # Get module's option value if provided
        #
        # This is where we grab the option value from the profile
        # so, if any character scrubbing is needed -- this is where to do it
        #

        # Important:
        # Historically all option(s) for a module have been in one big string (comma separated).
        # After 4.0.10 (but not in that release) all profiles are written with each profile having 
        # a separate 'option' element for each option.  However, we could be handed an oldstyle profile, 
        # so we need to be able to process it.  SO......
        # NOTE: as of 6/15/2012 there are only 3 modules with multiple options
        #  'Set Password Aging..' has 4, 'Crontab Perms' has 2, and 'Create Pre-Session...' has 4
        #
        #
        # ALL options for scan/apply will be sent by dictionary.  ALL dictionaries will be examined to make sure that all 
        # entries (as defined in security-modules.xml) are present, and if not, the default value used
        # So our processing will be:
        #
        # get modules 'option' elements.  If opt[0] has a name attribute - newstyle profile, else oldstyle profile
        # if oldstyle *and* more than one option allowed , split option on commas and assign to positional arguments (if more options than args, yell)
        # if oldstyle and only one option, treat entire string as single value
        # if newstyle, assign using option name
        #
        # AFTERWARD - compare number of arguments in dictionary with expected args - comment appropriately and fill missing args w/defaults
        
        optionValueList[moduleName] = None
        moduleOptions = {}

        possibleOptions = ModuleConfigs[libraryName]['options']
        optionNodes = moduleNode.xpathEval('./option')
        
        if optionNodes and not possibleOptions:
            # oops - module in profile claims options, but none listed for module in spec
            logger.warning(MODULE_NAME, "Module '%s' claims option value(s) but none expected" % moduleName)
        elif optionNodes:
            if optionNodes[0].prop('name') == None:
                logger.warning(MODULE_NAME, "Module '%s' has oldstyle option list, converting on the fly..." % moduleName)
                
                # ok, old profile, multiple possible options. split on the comma, but only upto the number of expected options minus one 
                profileOptions = xml.sax.saxutils.unescape(optionNodes[0].getContent()).split(",",len(possibleOptions)-1)       
                # now pack non-empty options into possible ones
                print "%s ProfileOptions = %d  , possible options = %d" % (moduleName, len(profileOptions), len(possibleOptions)) 
                for optIndex in range(len(profileOptions)):
                    moduleOptions[possibleOptions[optIndex]] = profileOptions[optIndex]             
            else:
                # New style profile, walk options and assign
                for opt in optionNodes:
                    moduleOptions[opt.prop('name')] = xml.sax.saxutils.unescape(opt.getContent())

        # Check number of options...
        if len(moduleOptions) < len(possibleOptions):
            logger.warning(MODULE_NAME, "Module '%s' has fewer options than expected." % (moduleName))
        elif len(moduleOptions) > len(possibleOptions):
            logger.warning(MODULE_NAME, "Module '%s' has more options than expected." % (moduleName))
        
        # Ok, now walk possibleOptions, making sure everything has a value
        for opt in possibleOptions:
            if opt not in moduleOptions:
                logger.warning(MODULE_NAME, "Module '%s' missing option for '%s', using default value." % (moduleName, opt))
                moduleOptions[opt] = ModuleConfigs[libraryName]['optionsDefaults'][opt]

        optionValueList[moduleName] = moduleOptions
    #
    # Now, operate on each module from the sorted executionList dictionary
    #  - There are better ways to sort dictionary keys in newer versions of
    #    Python but we must support versions 2.3 to 2.6
    #
    moduleKeylist = executionList.keys()
    moduleKeylist.sort()
    if action == 'undo':
        moduleKeylist.reverse()

    total_time   = 0
    totalPass    = 0
    totalApply   = 0
    totalUndone  = 0
    totalNotReqd = 0
    totalFail    = 0
    totalNA      = 0
    totalManual  = 0
    totalError   = 0
    totalCount   = 0
    totalOther   = 0
    totalAborted = 0
    
    for moduleKey in moduleKeylist:
        results = ''
        statusMsg = ''
        moduleResults = ()
        delta = 0

        #### OK, check the abort flag, and if 'True', log the results as 'Abort requested'.  Don't 
        #### Need to do anything further....
        
        
        try:
            moduleName  =  executionList[moduleKey]
            libraryName =  LibraryMapping[moduleName]
            sortKey     = ModuleConfigs[libraryName]['sortKey'].rjust(4).replace(' ','0')
        except KeyError,e:
            print e
            totalOther += 1
            results = "Other"
            logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
            continue

        optionValue = optionValueList[moduleName]
        reportModuleNode = moduleResultsNode.newChild(None, "module", None)
        reportModuleNode.setProp("name", moduleName)
        reportModuleNode.setProp("severityLevel", ModuleConfigs[libraryName]['severity_level'])
        severity_value = int( ModuleConfigs[libraryName]['severity_level'] )
        if severity_value <= 1:
            reportModuleNode.setProp("severity", "Low")
        elif severity_value <= 5:
            reportModuleNode.setProp("severity", "Medium")
        elif severity_value <= 10:
            reportModuleNode.setProp("severity", "High")


        reportModuleNode.newChild(None, "description", ModuleConfigs[libraryName]['description'])

        # Add views
        viewNode = reportModuleNode.newChild(None, "views", None)
        for view in ModuleConfigs[libraryName]['views']:
            try:
                vNode = viewNode.newChild(None, "view", view)
            except:
                pass

        compliancyNode = reportModuleNode.newChild(None, "compliancy", None)
        for comp in ModuleConfigs[libraryName]['compliancy']:
            try:
                vNode = compliancyNode.newChild(None, "line-item", None)
                cProps = comp.split('|')
                vNode.setProp("source", cProps[0])
                vNode.setProp("name", cProps[1])
                vNode.setProp("version", cProps[2])
                vNode.setProp("item", cProps[3])
            except Exception,e:
                print e
                pass


        detailsNode = reportModuleNode.newChild(None, "details", None)

        # Make a log entry with a BIG line to indicate 
        # the begining of a "new" module
        logStartMessage = "%s %s %s" % ("="*20, action.upper().center(10), "="*20)
        logger.notice(libraryName, logStartMessage)

        # Determine if module is supported on current platform by comparing 
        # this system CPE name with the module's supported platform list
        platformList = ModuleConfigs[libraryName]['platforms']
        if sysCpeName in platformList:
            supportedCpe = True
            msg = "Current system CPE '%s' exactly matches one of the module's entries." % (sysCpeName)
            logger.debug(MODULE_NAME, msg)
            supportedCpe = True
        else:
            supportedCpe = False
            for cpeItem in platformList:
                if sysCpeName.startswith(cpeItem):
                    msg = "Current system CPE '%s' starts with (partial match) module's '%s' entry." % (sysCpeName, cpeItem)
                    logger.debug(MODULE_NAME, msg)
                    supportedCpe = True
                    break

        if supportedCpe == False:
            msg = """"%s" (%s) is not applicable to this operating system.""" % (moduleName, libraryName)
            logger.notice(MODULE_NAME, msg)
            reportModuleNode.setProp("results", 'OS NA')
            results = "OS NA"
            delta = 0
            if verbose == True:
                msg = "MODULE: %-50s %-15s %10.3f ms" % ( moduleName, results, delta)
                print >> sys.stdout, msg
            totalNA += 1
            logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
            continue

        if sbProps.ABORT_REQUESTED == True:
            msg = "Skipping %s of '%s', ABORT signal noticed" % (action, libraryName)
            logger.warn(MODULE_NAME, msg)
            reportModuleNode.setProp("results", 'Aborted')
            results = 'Aborted'
            moduleResults = ('Aborted',"", {'messages':["Abort requested"]})
            if verbose == True:
                msg = "MODULE: %-50s %-15s %10.3f ms" % ( moduleName, results, delta)
                print >> sys.stdout, msg
                if sbProps.DEVELOPMENT_MODE == True:
                    print >> sys.stdout, "    --> %s" % statusMsg
                    print >> sys.stdout, "    --> %s" % str(moduleResults) 
            totalAborted += 1
            logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
            continue

            
        try:
            importedModule = __import__(libraryName)
#        except ImportError, err:
        except tcs_utils.AbortProfile, err:
            # raise if we need to *stop* right here, and do not processes any more modules
            msg = "Unable to import '%s' library : %s" % (libraryName, str(err))
            reportModuleNode.setProp("results", 'Module Unavailable')
            logger.critical(MODULE_NAME, msg)
            if verbose == True:
                print >> sys.stdout,"Abort Processing exception received" , "< %s >" % str(err)
            sbProps.ABORT_REQUESTED = True
            results = 'Aborted'
            continue
        except Exception, err:
            msg = "Unable to import '%s' library : %s" % (libraryName, str(err))
            reportModuleNode.setProp("results", 'Module Unavailable')
            logger.critical(MODULE_NAME, msg)
            results = 'Error'
            if verbose == True:
                msg = "MODULE: %-50s %-15s %10.3f ms" % ( moduleName, results, delta)
                print >> sys.stdout, msg
            totalOther += 1
            logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
            continue

        msg = "Imported library '%s', sortKey='%s', requesting '%s' action" % (libraryName, int(sortKey), action)
        if action in ['scan', 'apply'] and optionValue != None:
            msg = "%s, and profile has provided an option value" % msg
        logger.debug(MODULE_NAME, msg)
        
        # Instantiate one class inside the module which has the same name and verify we have a match
        methodlist = [method for method in dir(importedModule) if callable(getattr(importedModule, method)) and method == libraryName]
        if not methodlist:
        
            msg = "Unable to find the '%s' class in the module file" % (libraryName)
            logger.critical(MODULE_NAME, msg)
            reportModuleNode.setProp("results", 'Error')
            results = 'Error'
            if verbose == True:
                msg = "MODULE: %-50s %-15s %10.3f ms" % ( moduleName, results, delta)
                print >> sys.stdout, msg
            totalError += 1
            logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
            continue


        # Verify that the executable instance of the module/class has the appropriate
        # method to handle reqeusted action: scan, apply, or undo.
        #
        # If needed, the availableMethods list/array could be used in identifying
        # modules/classes which may be missing methods. Or it could be used to 
        # document each module/class methods
        #
        execInstance = vars(importedModule)[methodlist[0]]
        availableMethods = dir(execInstance)
        if action not in availableMethods:
            msg = "'%s' does not have the '%s()' method" % (libraryName, action)
            logger.critical(MODULE_NAME, msg)
            reportModuleNode.setProp("results", 'Invalid Action')
            results = 'Error'
            if verbose == True:
                msg = "MODULE: %-50s %-15s %10.3f ms" % ( moduleName, results, delta)
                print >> sys.stdout, msg
            totalError += 1
            logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
            continue


                
        #######################################
        ##### Scan, Apply, or Undo action #####
        #######################################
        #### OK, check the abort flag, and if 'True', log the results as 'Abort requested'.
               
        # Ok, indicate that from here on, we're *in* a Module... eventually this will move into module super class....
        # note the nested try, we need to do this to *ensure* that we back out of the module even if don't wind up 
        # handing a raised exception.  Would be nice to just use try/except.../finally, but the older versions of python
        # don't support that.
        
        logger.inModule(libraryName)
        try:
            try:
                # if results is not empty then something was detected where we should *not* execute.  So raise
                # an exception to skip everything below....
                
                if results:  
                    raise SkipModule(results)
                t1 = time.time()

                # If we are a shim, we would only have gotten here for an scan/apply action, so 'pretend' to 
                # do the action.  Each module has a small change of failing (just to provide some variability in
                # the results.  For applys that work, the change record is simply "CHANGED".  Remember that we're
                # expeting a tuple as the response (TRUE|FALSE, "CHANGED"|"", "SIMULATED FAILURE"|"SIMULATED PASS") as the reply
                
                if isShim == True:
                    if action == 'scan':
                        if random.randint(1, 10) % 2 == 0:   # 50% of modules fail scan
                            moduleResults = ("Pass", "", {'messages':["SIMULATED SCAN PASSED"]})
                        else:
                            moduleResults = ("Fail", "", {'messages':["SIMULATED SCAN FAILURE"]})
                    else:
                        results = "Applied"
                        if random.randint(1, 10) != 1 :   # 10% of modules fail apply
                            moduleResults = (True, "CHANGED", {'messages':["SIMULATED APPLY OK"]})
                        else:
                            moduleResults = (False, "", {'messages':["SIMULATED APPLY FAILURE"]})
                    # random int between 0 and 1, cubed to give nonlinear sleep time
                    sleeptime = random.randint(1, 10) / 10.0
                    time.sleep(sleeptime*sleeptime*sleeptime)  
                else:
                    if action == 'scan':
                        moduleResults = execInstance().scan(optionValue)

                    if action == 'apply':
                        results = "Applied"
                        moduleResults = execInstance().apply(optionValue)

                    if action == 'undo':
                        results = "Undone"
                        change_record = stateMgr.getLibraryLastChangeRecord(libraryName=libraryName)
                        if change_record:
                            moduleResults = execInstance().undo(change_record)
                        else:
                            moduleResults = (False, 'Not Required', 
                                {'messages': ['No change record; no action taken']})
                            results = "Not Required"

                t2 = time.time()
                delta = ( (t2-t1)*1000)
                total_time = total_time + delta

            except tcs_utils.ScanNotApplicable, err: 
                results = 'NA'
                statusMsg = str(err)
                # Omit library name from beginning of message
                if statusMsg.split()[0] == libraryName:
                    try:
                        statusMsg = ' '.join(statusMsg.split()[1:])
                    except:
                        pass 

            except tcs_utils.ManualActionReqd, err: 
                results = 'Manual Action'
                statusMsg = str(err)
                # Omit library name from beginning of message
                if statusMsg.split()[0] == libraryName:
                    try:
                        statusMsg = ' '.join(statusMsg.split()[1:])
                    except:
                        pass 

            except tcs_utils.OSNotApplicable,   err: results = 'OS NA'
            except tcs_utils.ZoneNotApplicable, err: results = 'Zone NA'
            except tcs_utils.ModuleNotAvail,    err: results = 'NAVAIL'
            except tcs_utils.ScanError,         err: results = 'Error'
            except tcs_utils.ActionError,       err: results = 'Error'
            except tcs_utils.ModuleUnsupported, err: results = 'Module Unsupported'
            except (OSError, IOError),          err: results = 'Error'
            except SkipModule,        err: 
                # raised if some preprocessing detects a reason to skip the module, evertything *should* be set
                # already, so just quietly continue from here
                print >> sys.stdout, "SKIPMODULE" , "< %s >" % str(err)
                results = str(err)
            
            except tcs_utils.AbortProfile, err:
                # raise if we need to *stop* right here, and do not processes any more modules
                print >> sys.stdout,"Abort Processing exception received" , "< %s >" % str(err)
                sbProps.ABORT_REQUESTED = True
                results = 'Aborted'
            ##
            ## Catch all of the garbage exceptions from the module such as
            ## SyntaxError, IndexError, TypeError, NameError, and general
            ## Exception. But we also what the line number and source
            ## code file so we can fix it!
            ##
             
            except Exception, err: 
                results = 'Error'
                try:
                    import traceback
                    ei1, ei2, ei3 = sys.exc_info()
                    d = traceback.format_exception( ei1, ei2, ei3 )
                    what_err = d[-1].strip()
                    where_err = d[-2].splitlines()[0].split(',')
                    errfile = where_err[0]
                    errline = where_err[1]
                    statusMsg = "%s : %s at %s" % (what_err, errfile, errline)
                except ImportError:
                    statusMsg = str(err)

        finally:
            logger.inModule("")

        # If we got an error and status message is alread set
        # just use the error string returned by the exception
        if results == 'Error' and statusMsg == '':
            statusMsg = str(err)

        if results in ['NA', 'OS NA', 'Zone NA', 'Manual Action']:
            logger.notice(MODULE_NAME, statusMsg)
        elif results in ['NAVAIL' ]:
            logger.warn(MODULE_NAME, statusMsg)
        elif results in [ 'Error']:
            logger.error(MODULE_NAME, statusMsg)
        
        
        # For scan action
        if results == '' and action == 'scan': 
            results = moduleResults[0]
            if moduleResults[1] != '':
                statusMsg = moduleResults[1]
            else:
                statusMsg = "None"

        if type(results) == type(True) and action == 'scan':
            if results == True:
                results = "Pass"
            if results == False:
                results = "Fail"

        if type(results) == type(True) and action == 'undo':
            if results == True:
                results = "Undone"
            if results == False:
                results = "-"


        # If the first item in the tuple moduleResults[0] is 1 or True
        # then we we will set the change record
        updateChangeRecord = False
        if action == 'apply' and results == "Applied":
            if type(moduleResults) == type(()):
                if len(moduleResults) > 1:
                    if type(moduleResults[0]) == type(1):
                        msg = "'%s' library apply method still returning integer" % libraryName
                        logger.debug(MODULE_NAME, msg)
                        if moduleResults[0] == 1:
                            updateChangeRecord = True
                        else:
                            results = "Not Required"
        
                    if type(moduleResults[0]) == type(True):
                        if moduleResults[0] == True:
                            updateChangeRecord = True
                        else:
                            results = "Not Required"
                    
            # Update change records
            if updateChangeRecord == True:
                if len(moduleResults) < 2:
                    msg = "'%s' library module performed an apply but did not return a change record" % libraryName
                    logger.critical(MODULE_NAME, msg)
                else:
                    if type(moduleResults[1]) != type('abc'):
                        msg = "'%s' did not return a string data type for a change record" % (libraryName)
                        logger.critical(MODULE_NAME, msg)
                    else:
                        msg = "'%s' returned a %d byte change record" % (libraryName, len(moduleResults[1]))
                        logger.debug(MODULE_NAME, msg)
                        if moduleResults[1] == '':
                            msg = "'%s' library module performed an apply but returned '' as the change record" % libraryName
                            logger.critical(MODULE_NAME, msg)
                        else:
                            stateMgr.setLibraryChangeRecord(libraryName=libraryName, changeRecord=moduleResults[1] )

        updateChangeRecord = False
        if action == 'undo' and results == "Undone":
            if type(moduleResults) == type(()):
                if len(moduleResults) > 1:
                    if type(moduleResults[0]) == type(1):
                        msg = "'%s' library undo method still returning integer" % libraryName
                        logger.debug(MODULE_NAME, msg)
                        if moduleResults[0] == 1:
                            updateChangeRecord = True
                        else:
                            results = "Not Required"
        
                    if type(moduleResults[0]) == type(True):
                        if moduleResults[0] == True:
                            updateChangeRecord = True
                        else:
                            results = "Not Required"

#Below section is a proposed bugfix (for #11619) 
#patch start 
            elif type(moduleResults) == type(True) or type(1):
                msg = "'%s' library undo method still returning single integer/boolean " % libraryName
                logger.debug(MODULE_NAME, msg)
                if moduleResults == 1 or moduleResults == True:
                    updateChangeRecord = True
                else:
                    results = "Not Required"
#patch ends
                
             
                    
            # Update change records
            if updateChangeRecord == True:
                stateMgr.clearLastChangeRecord(libraryName=libraryName )

        # Update report
        reportModuleNode.setProp("results", results)
        detailsNode.newChild(None, "statusMessage", statusMsg)
        messagesNode = detailsNode.newChild(None, "messages", None)

        #
        # Parse the third element of the tuple for detailed messages
        #   - introduced in v4.0.3+
        #
        if type(moduleResults) != type(()):
            msg = "'%s' module library is not returning a data type tuple after %s" % (libraryName, action)
            logger.debug(MODULE_NAME, msg)
        else:    
            if len(moduleResults) > 2:
                if type(moduleResults[2]) == type({}):
                    if moduleResults[2].has_key('messages'):  
                        if type(moduleResults[2]['messages']) == type([]) and moduleResults[2]['messages'] != [None]:
                            for msgEntry in moduleResults[2]['messages']:
                                if type(msgEntry) == type(""):
                                    messagesNode.newChild(None, "message", xml.sax.saxutils.escape(msgEntry))

        ##
        ## Update Module State file through State Handler
        ##
        ## Method Key is: (libraryName, action, results, execTimeMs)
        stateMgr.setActionStatus(libraryName, action, results, str(int(round(float(delta)))))

        # Record timing informaton in report
        reportModuleNode.setProp("execTimeMs",  str(int(round(float(delta)))) )
 
        logger.notice(MODULE_NAME, "'%s' results is '%s'" %  (libraryName, results))
        totalCount += 1
        if results == "Pass":
            totalPass += 1
        elif results == "Fail":
            totalFail += 1
        elif results == "Applied":
            totalApply += 1
        elif results == "Undone":
            totalUndone += 1
        elif results == "Not Required":
            totalNotReqd += 1
        elif results in ["OS NA", "Zone NA", "NA" ]:
            totalNA += 1 
        elif results == "Manual Action":
            totalManual += 1
        elif results in [ "Error", "NAVAIL" ]: 
            totalError += 1
        else:
            totalOther += 1
            
        if verbose == True:
            msg = "MODULE: %-50s %-15s %10.3f ms" % ( moduleName, results, delta)
            print >> sys.stdout, msg
            if sbProps.DEVELOPMENT_MODE == True:
                if results == 'Error':
                    print >> sys.stdout, "    --> %s" % statusMsg
                    print >> sys.stdout, "    --> %s" % str(moduleResults) 

    ##
    ##
    ##########################################################################
    if verbose == True:
        print >> sys.stdout, "\n"
        print >> sys.stdout, "STATS: MODULES %d " % totalCount
        print >> sys.stdout, "STATS: PASS    %d " % totalPass
        print >> sys.stdout, "STATS: APPLY   %d " % totalApply
        print >> sys.stdout, "STATS: Undone  %d " % totalUndone
        print >> sys.stdout, "STATS: NotReqd %d " % totalNotReqd
        print >> sys.stdout, "STATS: FAIL    %d " % totalFail
        print >> sys.stdout, "STATS: N/A     %d " % totalNA
        print >> sys.stdout, "STATS: ERROR   %d " % totalError
        print >> sys.stdout, "STATS: Aborted %d " % totalAborted
        print >> sys.stdout, "STATS: MANUAL  %d " % totalManual
        print >> sys.stdout, "STATS: OTHER   %d " % totalOther
    
        print >> sys.stdout, "STATS: TIME    %s " %  str(int(round(float(total_time))))
    reportInfoNode.setProp("execTimeMs", str(int(round(float(total_time)))))
    
    msg = "Module actions have completed. Finishing up...." 
    logger.notice(MODULE_NAME, msg)

    if stateMgr:
        msg = "Closing State Handler..."
        logger.debug(MODULE_NAME, msg)
        del stateMgr


    
    ##
    ## Write Final report to disk
    ##
    try:
        out_obj = open(outputReport, 'w')
        os.chmod(outputReport,0750)
        finalReport.saveTo(out_obj, sbProps.XML_ENCODING, 1)
        out_obj.close()
        finalReport.freeDoc()
    except IOError, err:
        msg = "Unable to write report %s : %s" % (outputReport, str(err))
        logger.critical(MODULE_NAME, msg)
        raise

    msg = "Wrote report to %s" % outputReport
    logger.notice(MODULE_NAME, msg)
    print >> sys.stdout, 'CREATED: ', outputReport
    allowConsoleAccess(filePath=outputReport)

    return 



if __name__ == '__main__':
    #validateProfile(profilePath='../security_modules/profiles/DISAUNIXSTIG.xml')
    #performAction(profilePath='../security_modules/profiles/DISAUNIXSTIG.xml', action='apply', verbose=True)
    #performAction(profilePath='../security_modules/profiles/DISAUNIXSTIG.xml', action='scan', verbose=True)
    #performAction(profilePath='../security_modules/profiles/DISAUNIXSTIG.xml', action='undo', verbose=True)
    msg = "Direct execution of %s is not permitted." % sys.argv[0]
    print >> sys.stdout , "ERROR: ", msg

