#!/usr/bin/env python
##########################################################################
# Copyright (c) 2012-2017 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##########################################################################

import sys
import os
import platform
import exceptions
import re
import getopt
import xml.sax.saxutils
import logging
import time
import commands
import zipfile
import StringIO
import AutoupdateCommsShim as Shim 
import DetermineOS

from SB_errors import *


class UpdateClient:
    logFileName = None
    
    def __init__(self, consoleURL=""):
        if not UpdateClient.logFileName:
            UpdateClient.logFileName = self.setupLogging()
        consoleAddr = None
        consolePort = 8443
        consoleSecure = True
        logging.getLogger('AutoUpdate').info("Downloaded content initialization")
        
        consoleRE = re.compile("(https?)?(://)?([^:]*):?([\d]+)?")
        try:
            consoleFields = consoleRE.search(consoleURL)
            consoleAddr = consoleFields.group(3)
            if consoleFields.group(4):
                consolePort = int(consoleFields.group(4))
            if consoleFields.group(1) == "http":
                consoleSecure = False
        except Exception, err:
            logging.getLogger('AutoUpdate').error("Parsing consoleURL : %s" % str(err)) 
            raise AutoUpdateError("Unable to execute autoupdate")

        if consolePort < 1:
            msg = "Console port (%d) must be a positive number - exiting" % consolePort
            logging.getLogger('AutoUpdate').error(msg)
            raise AutoUpdateError("Unable to execute autoupdate")
        self.consoleAddr = consoleAddr
        self.consolePort = consolePort
        self.consoleSecure = consoleSecure              
        self.shim = Shim.Shim( self.consoleAddr, self.consolePort, self.consoleSecure)            
    # Go get the latest updates from the Console

    def getAvailable(self):

        hostname = platform.node()

        pkg_root, short_cpe, major_version, minor_version, arch = DetermineOS.get_os_info() 
        
        # now check to see if we have installed docs that need to be updated - these are done outside the pkg/rpm files
        withDocs = False
        for i in ['security-blanket', 'oslockdown']:
            docsDir = '/usr/share/%s/docs' % i
            if os.path.isdir(docsDir) and len(os.listdir(docsDir)):
                withDocs = True
                break
                          
        logging.getLogger('AutoUpdate').info( "hostname      = %s" % hostname)
        logging.getLogger('AutoUpdate').info( "pkg_root      = %s" % pkg_root )
        logging.getLogger('AutoUpdate').info( "short_cpe     = %s" % short_cpe)
        logging.getLogger('AutoUpdate').info( "major_version = %s" % major_version)
        logging.getLogger('AutoUpdate').info( "minor_version = %s" % minor_version)
        logging.getLogger('AutoUpdate').info( "arch          = %s" % arch)
        logging.getLogger('AutoUpdate').info( "withDocs      = %s" % withDocs)
        
        files = {}
        if hostname != None and short_cpe != None and major_version != None and minor_version != None and arch != None: 
          zipFile = self.shim.listPackages(hostname, pkg_root, short_cpe, major_version, minor_version, arch, withDocs)
          if zipFile:
              logging.getLogger('AutoUpdate').info("zipfile is %d bytes long" % len(zipFile))      
              zipFile = zipfile.ZipFile(StringIO.StringIO(zipFile))
              for entry in zipFile.infolist():
                  files[entry.filename] = zipFile.read(entry.filename)
          else:
              logging.getLogger('AutoUpdate').error( "zipFile is empty")
              raise AutoUpdateError("No updates provided by Console")

        return files
                   
    # Send a notification message to the Console (good/bad/ugly)
    def sendNotification(self, transId, success=True, statusMsg=""):

        info=statusMsg           
        logging.getLogger('AutoUpdate').info( "transId %s " % transId)
        logging.getLogger('AutoUpdate').info( "Info    %s " % info)
        logging.getLogger('AutoUpdate').info( "Success  %s " % success)
        self.shim.sendNotification(transId, info=info, success=success)


    def setupLogging(self):
        fileFormatter = logging.Formatter('%(asctime)-6s: %(name)s - %(levelname)s -%(message)s')
    
        logging.getLogger('AutoUpdate').setLevel(logging.DEBUG)
        consoleLogger = logging.StreamHandler()
        logging.getLogger('AutoUpdate').addHandler(consoleLogger)
    
        prefix = ""
        
        for i in ['security-blanket', 'oslockdown']:
            logDir = "/var/lib/%s/logs" %i 
            if os.path.isdir(logDir):
                prefix = logDir
    
        filename = "%s/AutoUpdate_%d.log" % (prefix, (int(time.time())))
        
        fileLogger = logging.FileHandler(filename=filename)
        fileLogger.setFormatter(fileFormatter)
        logging.getLogger('AutoUpdate').addHandler(fileLogger)
        return filename


def usage_message():     
    print "%s -[u|i] ConsoleURL [-t TaskID] "
    print "\tConsoleURL = URL of Console"
    print "\t             if port not specified 8443 assumed"
    print "\t-u - Update from designated Console"
    print "\t-i - INSTALL from designated Console (SB removed if present)"
    
    sys.exit(1)

def parse_args():
    consoleURL = None
    transId = None
    pretend = False
    forceFlag = False
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "fzt:c:")
        for o, a in opts:    
            if o == "-c":
                consoleURL = a
            elif o == "-t":
                transId = a
            elif o == "-z":
                pretend = True
            elif o == "-f":
                forceFlag = True
    
    except getopt.GetoptError, err:
        logging.getLogger('AutoUpdate').error("Error: %s" % err)
        usage_message()
        
    if not consoleURL and not pretend:
        msg = "The name or IP address of a Console must be provided for upgrades- exiting"
        raise AutoUpdateError(msg)
    
    
    return consoleURL, transId, pretend, forceFlag

    
def _getUpgradesFromConsole(consoleURL):
    updateClient = UpdateClient(consoleURL)
    
    return updateClient.getAvailable()
    

def _autoUpdate(consoleURL, pretend, forceFlag):
            
    # we'll get the list of available files to install from the Console
    fileList = _getUpgradesFromConsole(consoleURL)

    if platform.uname()[0] == "Linux":
        from SB_Updaters import Linux_Updater as Updater
    elif platform.uname()[0] == "SunOS":
        from SB_Updaters import Solaris_Updater as Updater
    #elif platform.uname()[0] == "AIX":
    #    from SB_Updaters import AIX_Updater as Updater
    else:
        raise AutoUpdateError("Unable to load OS specific installation module for %s." % platform.uname()[0])
    
    updater = Updater(fileList, pretend, forceFlag)
       
    try:
        updater.applyUpdate() 
    except AutoUpdateExit, e:
        print "Raising AutoUpdateExit"
        raise 
    except AutoUpdateError, e:
        print "Raising AutoUpdateError"
        raise
    except Exception, e:
        raise 
    return updater
    

def _notify(consoleURL, transId, isOk, statusMsg):
    updateClient = UpdateClient(consoleURL)
    updateClient.sendNotification(transId, isOk, statusMsg)

def doAutoUpdate(consoleURL, transId, pretend, forceFlag):
    
# IMPORTANT NOTES - at most a single line starting with AUTOUPDATE: should be returned.  
#                 - any fatal errors should be written to STDERR
    
    pkg_root, short_cpe, major_version, minor_version, arch = DetermineOS.get_os_info()      
#    if short_cpe == "redhat" and major_version == "4":
#        statusMsg = "AutoUpdate not supported on RHEL/CentOS/Oracle Enterprise Linux V4 platforms.  Manual update from full tarball is required."
#        logging.getLogger('AutoUpdate').error("AUTOUPDATE -> %s" % statusMsg)
#        return 1

    # Assume failure
    isOk = False
    retval = 1
    statusMsg = "Something failed"

    # NOTE - AutoUpdateExit is a shortcut exception indicating successful return, no further processing required.
    updater = None
    try:
        if consoleURL:
            updater = _autoUpdate(consoleURL, pretend, forceFlag)
            isOk = True
            statusMsg = "Autoupdate successful"
        else:
            raise AutoUpdateError("No Console URL provided to contact for updates.")
        logging.getLogger('AutoUpdate').info(statusMsg)
    except AutoUpdateExit, e:
        logging.getLogger('AutoUpdate').info(e)
        isOk = True
        statusMsg = str(e)
        sys.stdout = open("/dev/stdout","w")
        print >> sys.stdout, "CREATED: %s" % UpdateClient.logFileName
        sys.stdout = open("/dev/null","w")
        sys.stderr = open("/dev/null", "w")
    except AutoUpdateError, e:
        sys.stderr = open("/dev/stderr","w")
        print >> sys.stderr, "ERROR: %s" % e
        logging.getLogger('AutoUpdate').error("ERROR: %s" %e)
        statusMsg = str(e)
        sys.stderr = open("/dev/null", "w")
        sys.exit(1)
    except Exception, e:
        raise
    
            
    # Ok, so how did we finish?
    logging.getLogger('AutoUpdate').info(statusMsg)
    
    # 

    # Send a notification if we were given a Console address
    if consoleURL:
        if not transId:
            transId = "0:%s:0:0" % platform.node()
        try:
            _notify(consoleURL, transId, isOk, statusMsg)
        except Exception, e:
            logging.getLogger('AutoUpdate').error("AUTOUPDATE: unable to send notification of - %s " % statusMsg)
            logging.getLogger('AutoUpdate').error("AUTOUPDATE: notification error - %s " % str(e))
    
    if isOk:
        logging.getLogger('AutoUpdate').info("AUTOUPDATE: %s " % statusMsg)
        retval = 0
        # ONLY if we're done go any final cleanup 
        if updater :
            logging.getLogger('AutoUpdate').info("AUTOUPDATE: performing final cleanup after successful update - no further logging " )
            updater.successfulInstallCleanup(UpdateClient.logFileName)
    else:
        logging.getLogger('AutoUpdate').error(statusMsg)
            

if __name__ == "__main__":
    
    consoleURL, transId, pretend, forceFlag = parse_args()
    doAutoUpdate(consoleURL, transId, pretend, forceFlag)
