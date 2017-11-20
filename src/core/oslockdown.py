#!/usr/bin/env python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Core Engine
#
###############################################################################
import sys
sys.path.append('/usr/share/oslockdown')
sys.path.append('/usr/share/oslockdown/lib/python')


ALLOW_DISCRETE_MODULES = False
#ALLOW_DISCRETE_MODULES = True
try:
    import warnings
    warnings.simplefilter("ignore", DeprecationWarning)
except:
    pass

try:
    import Diagnostics
    results = Diagnostics.sbDirectories()
    if results != True:
        sys.exit(4)
except ImportError, err:
    print "ERROR: Unable to load 'Diagnostics' module: %s" % err
    sys.exit(1)

###############################################################################
# Don't worry if you've already loaded modules in the Diagnostics phase.
# Python is pretty smart.
import os
import stat
import time
import atexit
import pwd
import signal
import getopt
import re
import libxml2

#### Try to build Python library search path based on OS Lockdown's base
#### directory install.
try:
    import sbProps
except ImportError, err:
    print >> sys.stderr, "ERROR: Unable to load SB Module: %s" % err
    sys.exit(4)

try:
    sys.path.append(sbProps.SB_BASE)
    sys.path.append("%s/lib/python" % sbProps.SB_BASE)
except AttributeError, err:
    print >> sys.stderr, "WARNING: %s" % err
    print >> sys.stderr, "WARNING: Using /usr/share/oslockdown as default base directory"
    sys.path.append('/usr/share/oslockdown')
    sys.path.append('/usr/share/oslockdown/lib/python')

if not os.path.exists(sbProps.SB_BASE):
    print >> sys.stderr, "ERROR: %s does not exist." % sbProps.SB_BASE
    sys.exit(sbProps.EXIT_CONFIG_ERR)

# Import SB Specific Modules
try:
    import TCSLogger
    import ModuleInfo
    import tcs_utils
    import CoreEngine
    import Baseline
    from sb_utils.os.info import *
    from sb_utils import SELinux

except ImportError, err:
    print >> sys.stderr, "ERROR: Unable to load SB Module: %s" % err
    sys.exit(sbProps.EXIT_PYTHON_IMPORT_ERR)


logger = None
# Initialize Logging at the top level....

try:
    logger = TCSLogger.TCSLogger.getInstance(loglevel)
except Exception, err:
    try:
        logger = TCSLogger.TCSLogger.getInstance()
    except Exception, err:          
        print >> sys.stderr, "ERROR: Unable to initialize logging: %s" % str(err)
        sys.exit(sbProps.EXIT_FAILURE)


###############################################################################
def check_pid(verbose=False):
    pid = None

    if verbose == True:
        print >> sys.stdout, "DEBUG: Checking %s" % sbProps.PIDFILE

    if os.path.isfile(sbProps.PIDFILE):
        try:
            infile = open(sbProps.PIDFILE, 'r')
            pid = infile.readline()
            infile.close()
        except (IOError, OSError):
            pass

    if pid != None and pid != '':
        procpath = '/proc/%s' % pid
        if os.path.exists(procpath):
            errmsg = '%s already running.' % sbProps.PRODUCT_NAME
            report_error(errmsg)

    pid = os.getpid()
    if verbose == True:
        print >> sys.stdout, "DEBUG: Recording PID in %s" % sbProps.PIDFILE
    try:
        infile = open(sbProps.PIDFILE, 'w')
        infile.write('%s' % pid)
        infile.close()
    except (OSError, IOError), err:
        errmsg = "Unable to write to %s: %s" % (sbProps.PIDFILE, err)
        report_error(errmsg)
 
    return

###############################################################################
def sigUSR1Handler(signum, frame):
    """
    Handler for USR1 - indicates app should stop whatever it is 'nicely'.
    IE - do start anything new, indicate that anything left as not run and
         that operations were terminated early *** AS REQUESTED ***
    """

    sbProps.ABORT_REQUESTED = True
    try:
        USR1logger = TCSLogger.TCSLogger.getInstance(6)
    except Exception, err:
        try:
            USR1logger = TCSLogger.TCSLogger.getInstance()
        except Exception, err:
            print >> sys.stderr, "ERROR: Unable to initialize logging: %s" % str(err)

    try:
        USR1logger.warning('MAIN', 'SIGUSR1 Abort Request Received')
    except Exception, e:
        pass

    print >> sys.stdout, "SIGUSR1 Abort Request Received"


###############################################################################
def sigIntHandler(signum, frame):
    """
    Handler for Int - indicates app should stop whatever it is 'nicely'.
    IE - do start anything new, indicate that anything left as not run and
         that operations were terminated early *** AS REQUESTED ***
    """

    sbProps.ABORT_REQUESTED = True
    try:
        Intlogger = TCSLogger.TCSLogger.getInstance(6)
    except Exception, err:
        try:
            Intlogger = TCSLogger.TCSLogger.getInstance()
        except Exception, err:
            print >> sys.stderr, "ERROR: Unable to initialize logging: %s" % str(err)

    try:
        Intlogger.warning('MAIN', 'SIGINT Abort Request Received')
    except Exception, e:
        pass

    print >> sys.stdout, "SIGINT Abort Request Received"

        
    
###############################################################################
def sigHandler(signum, frame):
    """
    Default Signal Handler for **most** signals registered before main()
    was called.
    """
    d = {}
    try:
        for nm in dir(signal):
            if nm.startswith("SIG"):
                v = getattr(signal, nm)
                if type(v) == type(1):
                    d[v] = nm

        msg = "Exiting - %s caught signal: %s(%d)" % (sbProps.PRODUCT_NAME, d[signum], signum)
        del d

    except Exception, err:
        msg = "%s caught signal: %d" % (sbProps.PRODUCT_NAME, signum)

    try:
        logger.critical("MAIN", msg)
    except:
        pass

    print >> sys.stderr, msg
    sys.exit(sbProps.EXIT_ABORT)

###############################################################################
def finalCleanup():
    # cleanup any profile related additions
    try:
        import security_modules.UpdateProfileAdditions
        security_modules.UpdateProfileAdditions.removeFile(sbProps.EXCLUSION_DIRS)
        security_modules.UpdateProfileAdditions.removeFile(sbProps.INCLUSION_FSTYPES)
        security_modules.UpdateProfileAdditions.removeFile(sbProps.SUID_WHITELIST)
        security_modules.UpdateProfileAdditions.removeFile(sbProps.SGID_WHITELIST)
    except ImportError, e:
        # if we can't import the cleanup, don't worry about it, 
        pass

    try:
        os.unlink(sbProps.PIDFILE)
    except OSError:
        pass
    


###############################################################################
def usage_message():
    print >> sys.stdout, "\n%s Version: %s" % (sbProps.PRODUCT_NAME, sbProps.VERSION)
    print >> sys.stdout, "Usage:  oslockdown [OPTIONS] [ACTION]"
    print >> sys.stdout, "        oslockdown [OPTIONS] [TEST]\n"
    print >> sys.stdout, "ACTION:"  
    print >> sys.stdout, "        -a profile      APPLY all applicable changes for <profile>"
    print >> sys.stdout, "        -s profile      SCAN system against <profile>"
    print >> sys.stdout, "        -u profile      UNDO all prior changes for <profile>"
    print >> sys.stdout, "        -b profile      Baseline the system"
    print >> sys.stdout, "        -U              Perform AutoUpdate"
    print >> sys.stdout, " "
    print >> sys.stdout, "        -D              Dump of OS Lockdown configuration"
    print >> sys.stdout, "        -h              Print usage message"
    print >> sys.stdout, "        -L              List all security modules"
    if ALLOW_DISCRETE_MODULES == True:
        print >> sys.stdout, "        -M modulename   Module information" 
    print >> sys.stdout, "        -V              Display OS Lockdown Version"
    print >> sys.stdout, "        -x report       Create text version of <report>"

    print >> sys.stdout, "OPTIONS:"  
    print >> sys.stdout, "        -f              Ignore excessive permissions on profile"
    print >> sys.stdout, "        -l loglevel     Set the log level (1-6)"
    print >> sys.stdout, "        -q              Quick scan"
    print >> sys.stdout, "        -v              Verbose messages"
    print >> sys.stdout, "        -t              Transaction ID for AutoUpdate"
    print >> sys.stdout, "        -n              Notification URL for AutoUpdate"
    print >> sys.stdout, " "
    print >> sys.stdout, " "

    print >> sys.stdout
    print >> sys.stdout, "Note: \"profile\" must be absolute path such as "
    print >> sys.stdout, "        /var/lib/oslockdown/profiles/CISBenchmarks.xml\n"

    return

###############################################################################
def parse_args():
    # set the default log level
    modsToDo = []
    loglevel = 4
    actions = []
    action = ''
    profile_path = ''
    baseline_profile = ''
    verbose = False
    scan_level = 10
    authtext = None
    modname = None
    reportPath = ''
    rotateDays = ''
    shim_name = ''
    notifyUrl = ''
    transId = ''
    
    cmdArgString = "z:b:d:l:s:u:a:x:R:M:UfhvVLqDcA:t:n:"
    if ALLOW_DISCRETE_MODULES == True:
      cmdArgString = cmdArgString + "m:"
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], cmdArgString )
    except getopt.GetoptError, err:
        print >> sys.stderr, "Error: %s" % err
        usage_message()
        sys.exit(sbProps.EXIT_FAILURE)

    force = False
    
    for o, a in opts:
        if o == '-l':
            try:
                loglevel = int(a)
            except ValueError:
                print >> sys.stderr, "\nError: Missing log level\n"
                usage_message()
                sys.exit(sbProps.EXIT_FAILURE)
        elif o == '-m':
            if a not in modsToDo:
                modsToDo.append(a)
        elif o == '-z':
            shim_name = a
        elif o == '-t':
            transId = a
        elif o == '-n':
            notifyUrl = a
        elif o == '-U':
            actions.append('autoUpdate')
        elif o == '-s':
            actions.append('scan')
            profile_path = a
        elif o == '-a':
            actions.append('apply')
            profile_path = a
        elif o == '-u':
            actions.append('undo')
            profile_path = a
        elif o == '-M':
            actions.append('modinfo')
            modname = a
        elif o == '-R':
            actions.append('rotate')
            rotateDays = a
        elif o == '-L':
            actions.append('modlist')
        elif o == '-x':
            actions.append('transform')
            reportPath = a
        elif o == '-f':
            force = True
        elif o == '-q':
            scan_level = 5
            QUICK_SCAN = True
        elif o == '-b':
            actions.append('baseline')
            baseline_profile = a
        elif o == '-v':
            verbose = True
        elif o == '-c':
            actions.append('check')
        elif o == '-D':
            actions.append('diagnostics')
        elif o == '-V':
            print >> sys.stdout, "%s V%s\n%s\n" % (sbProps.PRODUCT_NAME, sbProps.VERSION, sbProps.COPYRIGHT)
            sys.exit(sbProps.EXIT_SUCCESS)
        elif o == '-A':
            authtext = a
        elif o == '-h':
            usage_message()
            sys.exit(sbProps.EXIT_SUCCESS)

    if len(actions) > 1:
        print >> sys.stderr, "ERROR: Only one action operation may be specified.\n"
        usage_message()
        sys.exit(sbProps.EXIT_FAILURE)
    elif len(actions) == 1:
        action = actions[0]

    return loglevel, action, profile_path, baseline_profile, force, scan_level, verbose, authtext, modname, reportPath, rotateDays, shim_name, modsToDo, notifyUrl, transId

###############################################################################
def report_error(text):
    print >> sys.stderr, text
    sys.exit(sbProps.EXIT_FAILURE)

###############################################################################
def space_free(filesystem):
    """
    Return MB of free space on filesystem, or -1 and an error message
    """
    msgs = []
    disk_free_mb = -1
    OneMeg = 1024*1024
    try:
        diskstats  = os.statvfs(filesystem)
        disk_free_mb = (diskstats.f_bsize*diskstats.f_bavail)/OneMeg
    except Exception, E:
        msg = "Unable to get free disk space."
        msgs.append(msg)
        msg = "Error = %s",str(E)
        msgs.append(msg)
    return disk_free_mb, msgs

###############################################################################
def main():
    """
    Main Controlling function of OS Lockdown 
    """
    ABORT_REQUESTED = False
    # Establish functions to run when application ends
    # - Always remove pid file when the application ends
    atexit.register(finalCleanup) 

    # How do we handle signals the process may encounter?
    signal.signal(signal.SIGALRM, sigHandler)
    signal.signal(signal.SIGHUP, sigHandler)
    signal.signal(signal.SIGINT, sigIntHandler)
    signal.signal(signal.SIGUSR1, sigUSR1Handler)
    
    # The application must be ran as root
    if os.getuid() != 0:
        print >> sys.stderr, "You must have root privileges to run %s" % sbProps.PRODUCT_NAME
        sys.exit(sbProps.EXIT_FAILURE) 

    # Parse the command line options
    # - Function returns action in the 'action' variable
    loglevel, action, profile_path, baseline_profile, profile_perm, scan_level, verbose, authtext, modname, reportPath, rotateDays, shim_name, modsToDo, notifyUrl, transId = parse_args()

    if not action:
        usage_message()
        sys.exit(sbProps.EXIT_SUCCESS) 

    if verbose == True:
        print >> sys.stdout, "DEBUG: Verbose on"


    # If we're asked to be anything except the default log level, then force the reset here.
    if loglevel != 4:
        logger.force_log_level(loglevel)
        
    if verbose == True:
        print >> sys.stdout, "DEBUG: Initializing global logger (level=%d)" % int(loglevel)
        print >> sys.stdout, "DEBUG: Logging to %s" % sbProps.SB_LOG

    logger.notice("MAIN", "="*60)
    msg = ".:: Starting %s (%s) ::." % (sbProps.PRODUCT_NAME, sbProps.VERSION)
    logger.notice("MAIN", msg.center(60)) 
    logger.notice("MAIN", "="*60)

    # if we're doing something that may generate anything besides a trivial amount of data, verify that
    # we have enough room.  Eventually this will be configurable, but for now assume we need at least 20MB
    # of free space on whatever filesystem holds /var/lib/oslockdown (where we write to) before
    # proceeding

    if action in ['transform', 'scan', 'apply', 'undo', 'baseline', 'autoUpdate' ] :
        # How much space do we have on SB_VAR_BASE?
        disk_free_mb,msgs = space_free(sbProps.SB_VAR_BASE)
        if disk_free_mb < 0:
            for msg in msgs:
                print >> sys.stderr, msg
                logger.critical("MAIN",msg)
            sys.exit(sbProps.EXIT_FAILURE)
        if disk_free_mb < sbProps.DISK_SPACE_REQUIRED:
            msg = "ERROR: %s does not have at least %d MB free space (found %d MB), unable to proceed." %  (sbProps.SB_VAR_BASE, sbProps.DISK_SPACE_REQUIRED, disk_free_mb)
            print >> sys.stderr, msg
            logger.critical("MAIN",msg)
            sys.exit(sbProps.EXIT_FAILURE)

    #--------------------------------------------------------------------------
    # Kick off an autoupdate action - note that by design, the autoupdate action *will not return* unless there was
    # an exception that wasn't caught.
    
    if action == 'autoUpdate':
        try:
            import AutoUpdate
            pretend = False
            forceFlag = False    # Note that we're overloading profile_perm to indicate a 'forced' option
            if shim_name:
                pretend = True
            if profile_perm == True:
                forceFlag = True
            AutoUpdate.AutoUpdate().autoUpdate(notifyUrl, transId, pretend, forceFlag)
            msg = "Autoupdate not required - no update performed"
            
        except ImportError, e:
            msg = "Unable to import AutoUpdate module - autoupdate failure - %s" % e
        
        print >>sys.stdout,"ERROR: %s" % msg
        logger.error(sbProps.PRODUCT_NAME, msg)
        sys.exit(sbProps.EXIT_FAILURE)

    #--------------------------------------------------------------------------
    # Check license key - now a plain stub to say 'unlicensed'...
    if action == 'check':
        is_valid = 1
        try:
          licType = open('/var/lib/oslockdown/files/ConsoleType.txt').read().strip()
          if licType not in ['Enterprise', 'Standalone']:
            licString = "Unable to process license type from '/var/lib/oslockdown/files/ConsoleType.txt'"
          else:
            licString = "%s license detected" % licType
            is_valid = 0          
        except IOError, e:
            licString = "%s %s" %(e.strerror, e.filename)
        if is_valid == 0:
            print "OS Lockdown: %s" % licString
        else:
            print >> sys.stderr, "OS Lockdown: %s" % licString
            print >> sys.stderr, "A license file is no longer required to run the 'oslockdown' actions,"
            print >> sys.stderr, "and a Console (if installed) will default to an Enterprise installation."
            print >> sys.stderr, "If a Standalone installation is desired, please execute"
            print >> sys.stderr, "      /usr/share/oslockdown/tools/SB_Setup -l"
	    print >> sys.stderr, "to select an installation types."
        sys.exit(is_valid)   
    #--------------------------------------------------------------------------
    # Run Diagnostics - Dump Configuration, too
    if action == 'diagnostics':
        logger.notice("MAIN", "Running diagnostics and dumping configuration")
        Diagnostics.dumpConfiguration()
        print >> sys.stdout, "==================="

        sys.exit(sbProps.EXIT_SUCCESS) 
 
    #--------------------------------------------------------------------------
    # Module Information
    if action == 'modinfo':
        logger.notice("MAIN", "Retrieving module information for '%s'" % modname)
        if modname == None:
            usage_message()
            sys.exit(sbProps.EXIT_SUCCESS) 
           
        ModuleInfo.dumpModuleInfo(moduleName=modname)
        sys.exit(sbProps.EXIT_SUCCESS) 

    #--------------------------------------------------------------------------
    # Module List
    if action == 'modlist':
        logger.notice("MAIN", "Retrieving list of modules")
        ModuleInfo.dumpModuleList()
        sys.exit(sbProps.EXIT_SUCCESS) 


    #--------------------------------------------------------------------------
    # Transform report from XML to Text
    if action == 'transform':
        logger.notice("MAIN", "Creating text report from %s" % reportPath )
        strPattern = re.compile( '\.xml$')
        targetFile = strPattern.sub( '.txt', reportPath)
        # Open Report and determine report type by examining root element
        try:
            xmldoc = libxml2.parseFile(reportPath)
            root =  xmldoc.children
            reportType = root.name
            xmldoc.freeDoc()
        except Exception, err:
            logger.error("MAIN", "Unable to open %s: %s" % (reportPath, str(err)))
            sys.exit(sbProps.EXIT_FAILURE)

        if verbose == True:
            print >> sys.stdout, "DEBUG: Identified '%s' as '%s'" % (os.path.basename(reportPath), reportType)
        logger.debug("MAIN", "Identified '%s' as '%s'" % (os.path.basename(reportPath), reportType))

        # Now select appropriate stylesheet (XSL)
        if reportType == 'BaselineReport':
            styleSheet = os.path.join(sbProps.XSL_DIR, "txt/all-in-one-generic.xsl")
        elif reportType == 'AssessmentReport':
            styleSheet = os.path.join(sbProps.XSL_DIR, "txt/all-in-one-generic.xsl")
        elif reportType == 'ApplyReport':
            styleSheet = os.path.join(sbProps.XSL_DIR, "txt/all-in-one-generic.xsl")
        elif reportType == 'UndoReport':
            styleSheet = os.path.join(sbProps.XSL_DIR, "txt/all-in-one-generic.xsl")
        else:
            if verbose == True:
                print >> sys.stderr, "ERROR: Unable to determine appropriate XSL for report type '%s'" % reportType
            logger.error("MAIN", "Unable to create report")
            sys.exit(sbProps.EXIT_FAILURE)

        logger.debug("MAIN", "Using %s" % styleSheet)
        if verbose == True:
            print >> sys.stdout, "DEBUG: Using %s" % styleSheet

        # Transform the report
        try:
            results = tcs_utils.transformXML(xmlDoc=reportPath, output=targetFile, xslFile=styleSheet)
        except Exception, err:
            logger.error("MAIN", "Unable to create report: %s" % str(err))
            print >> sys.stderr, "ERROR: Unable to create report: %s" % str(err)
            if is_solaris() == False:
                print >> sys.stderr, "NOTICE: Try installing the 'libxslt-python' package"
            sys.exit(sbProps.EXIT_FAILURE)
        
        if results == False:
            print >> sys.stderr, "ERROR: Unable to create report"
            logger.error("MAIN", "Unable to create report")
            sys.exit(sbProps.EXIT_FAILURE)

        print >> sys.stdout, "NOTICE: Created %s" % targetFile

        logger.notice("MAIN", "Created %s" % targetFile)
        sys.exit(sbProps.EXIT_SUCCESS) 

    #-- If shim_name was provided, alter the contents of sbProps (verifying that required directories are present)
    #-- as well as disallow undo/baseline ops
    if shim_name != '':
        isShim = True
        if action in ['undo', 'baseline']:
            msg = "SHIM MODE - undo and baseline actions not possible - aborting"
            logger.error("MAIN", msg)
            print >> sys.stderr, msg
            sys.exit(sbProps.EXIT_ABORT)
        else:
            sbProps.ASSESSMENT_REPORTS = sbProps.ASSESSMENT_REPORTS.replace('/standalone/', '/shim/%s/'%shim_name)
            sbProps.APPLY_REPORTS      = sbProps.APPLY_REPORTS.replace('/standalone/', '/shim/%s/'%shim_name)
            sbProps.SB_STATE_FILE      = sbProps.SB_STATE_FILE.replace('/lib/oslockdown/', '/lib/oslockdown/reports/shim/%s/'%shim_name)
            # verify directories exists..
            sbbasedir = sbProps.SB_DIR_REPORTS
            for component in [ 'shim', shim_name ]:
                sbbasedir = os.path.join(sbbasedir, component)
                if not os.path.isdir(sbbasedir):
                    os.mkdir(sbbasedir, 777)
            
    else:
        isShim = False
        
#    print sbProps.ASSESSMENT_REPORTS
#    print sbProps.APPLY_REPORTS
#    print sbProps.SB_STATE_FILE
    
    #--------------------------------------------------------------------------
    # Perform action: scan, apply, undo, or baseline
    # If NOT baseline, check the profile that was provided
    if action in ['scan', 'apply', 'undo'] and isShim == False:
        check_pid(verbose)
        if not os.path.isfile(profile_path):
            print >> sys.stderr, "%s does not exist" % profile_path
            sys.exit(sbProps.EXIT_CONFIG_ERR)

    # Verify report output directory exists, *and* has correct permissions.
    if action == "scan":  
        reportsPath = sbProps.ASSESSMENT_REPORTS

    elif action == "apply": 
        reportsPath = sbProps.APPLY_REPORTS

    elif action == "undo":  
        reportsPath = sbProps.UNDO_REPORTS

    elif action == "baseline":  
        reportsPath = sbProps.BASELINE_REPORTS

    AllowConsoleAccess(reportsPath)
        
    if action != 'baseline':
        CoreEngine.performAction(profilePath=profile_path, action=action, verbose=verbose, isShim=isShim, profile_perm=profile_perm, modsToDo=modsToDo)
    else:
        Baseline.create(baselineProfile=baseline_profile, modVerbose=verbose, profile_perm=profile_perm)

    return

#################################################################
### Set perms ondirectory so console can access files therein ###
################################################################
def AllowConsoleAccess(dirPath=None):
    """
    All directories that the Console *should* be able to read files shall:
        be owned by root:sbwebapp
        have perms 750 + SETGID + STICKY = 03750
                     SETGID says all *files* will be group owned by same group as the parent directory, this is what lets us
                         give sbwebapp read permissions (based on group ownership)
                     STICKY says only owner of file can delete it
    """

    dirPermissions = 0750 + stat.S_ISGID + stat.S_ISVTX
    if dirPath == None :
        return
    # Retrieve information about the 'sbwebapp' account 
    try:
        sb_struct = pwd.getpwnam('sbwebapp')
    except KeyError:
        msg = "The 'sbweapp' user does not exist" 
        logger.critical(MODULE_NAME, msg)
        return

    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
    elif not os.path.isdir(dirPath):
        msg = "The '%s' path isn't a DIRECTORY" %dirPath
        logger.critical(MODULE_NAME, msg)
        return
        
    statbuf = os.stat(dirPath)
    if statbuf.st_uid != 0 or statbuf.st_gid != sb_struct.pw_gid:
        # Change *group* ownership to the 'sbwebapp' account  - have to set ownership
        # first because chown-ing a file *removes* setuig/setgid bits
        try:
            os.chown(dirPath, 0, int(sb_struct.pw_gid))
            sb_utils.SELinux.restoreSecurityContext(dirPath)
        except OSError, err:
            msg = "Unable to set ownership on %s to root:sbwebapp: %s" % (dirPath, err)
            logger.error(MODULE_NAME, msg)
    
    
    if statbuf.st_mode != dirPermissions:
        # Set permissions
        try:
            os.chmod(dirPath, dirPermissions)
    
        except OSError, err:
            msg = "Unable to set permssions on %s : %s" % (dirPath, err)
            logger.error(MODULE_NAME, msg)

    return



##############################################################################
if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:  
        print >> sys.stderr, "%s: Aborted" % sbProps.PRODUCT_NAME
        sys.exit(sbProps.EXIT_ABORT)

    sys.exit(sbProps.EXIT_SUCCESS)

