#!/usr/bin/env python
#########################################################################
# Copyright (c) 2007-2017 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##########################################################################
#
# Notes:  This is a shim to fit between the UpdateClient code and whatever SOAP client library
# is being used.  The initial part of this file just unpacks the SUDS library code (if not
# already done) and sets up the python environment to use it.
#
#
#
#


import sys
import os
import exceptions
import tarfile
import shutil
import getopt
import logging
import commands
import DetermineOS

from SB_errors import *

#
#

#

try:
    pkg_root, short_cpe, major_version, minor_version, arch = DetermineOS.get_os_info()      
    candidatedir = "%s/autoupdaters/%s-%s-%s" % (os.path.dirname(os.path.realpath(__file__)), short_cpe, major_version, arch) 
    candidate1 = "%s/AutoupdateComms.pyo" % candidatedir
    candidate2 = "%s/_AutoupdateComms.so" % candidatedir

    try :
        import selinux
        selinuxIsEnabled = selinux.is_selinux_enabled()
    except ImportError:
        selinuxIsEnabled = False
        pass
        
    for candidate in [candidate1, candidate2]:
        if not os.path.exists(candidate):
            msg = "Unable to locate required file '%s'" % candidate
            logging.getLogger('AutoUpdate').error(msg)
            raise AutoUpdateError(msg)
        if not os.access(candidate,os.R_OK):
            msg = "Unable to read required file '%s'" % candidate
            logging.getLogger('AutoUpdate').error(msg)
            raise AutoUpdateError(msg)

    # Ok, we need to try and fix the SELinux context of the relevant files.  We'll
    # copy the existing context of known libraries, since we know we can
    # call them from the current context already.
    # If any call here fails, silently skip the rest and keep running.
    
    if selinuxIsEnabled:
    
        try:
            # not sure at this point if we're updating Security Blanket or OS Lockdown, so
            # do a quick check...
            # If upgrading Security Blanket start with *that* contexts, otherwise use OS Lockdown context.
            if os.path.isfile('/usr/share/security-blanket/sb_utils/auth/Affirm.pyo'):
                startingContext = selinux.getfilecon("/usr/share/security-blanket")[1]
            else:
                startingContext = selinux.getfilecon("/usr/share/oslockdown")[1]
            
	    selinux.setfilecon(candidate1, startingContext.replace("_rw_t", "_py_t"))
            selinux.setfilecon(candidate2, startingContext.replace("_rw_t", "_licso_t"))
	    
	    os.chmod(candidate1,0700)     
            os.chmod(candidate2,0700)     
        except (NameError,AttributeError), e:    
            logging.getLogger('AutoUpdate').error(e)
	    

    sys.path.append(candidatedir)
    import AutoupdateComms                                                                                                                  
except Exception,e:
    raise AutoUpdateError(e)
    
class Shim:
    def __init__(self, consoleAddr="", consolePort=8443, consoleSecure = True):
        """Instantiate class with initial values for communication."""
        self.Client = None
        self.pkg_root, self.short_cpe, self.major_version, self.minor_version, self.arch = DetermineOS.get_os_info()      
        
        self.consoleAddr = consoleAddr
        self.consolePort = consolePort
        self.consoleSecure = consoleSecure
        
        self.baseURL = "http"
        if self.consoleSecure:
            self.baseURL += "s"
        self.baseURL += "://%s:%d/OSLockdown/services/" % (self.consoleAddr, self.consolePort)
        
        self.updateURL = self.baseURL + "updatesb?wsdl"
        self.notifyURL = self.baseURL + "console?wsdl"

               
    def listPackages(self, hostname="", pkg_root="", short_cpe="", major_version="", minor_version="", arch="", withDocs=True):
        """Report these parameters to the Console and request a zipFile with appropriate files to install/update.
           Returns a string with the base64 encoded zipfile containing all required files.
           For now *ignore* all fields other than hostname and withDocs
           
        """
        
        AutoupdateComms.getRemoteFile(self.updateURL, hostname, self.pkg_root, self.short_cpe, self.major_version, self.minor_version, self.arch, withDocs)
        status = AutoupdateComms.getReturnCode()
        data = AutoupdateComms.getData()
        print "Returned status of %d" % status
        print "Returned %d bytes" % len(data)
        if status != 0:
            raise AutoUpdateError(data)
        return data
    
    # Send a notification message to the Console (good/bad/ugly)
    def sendNotification(self, transId, info="", body="", success=False):
        """Send a notification the Console on the results of the update - only sent by UpdateClient if a transId was supplied.  
        """
        
        AutoupdateComms.sendNotification(self.notifyURL,info, transId, success)
        status = AutoupdateComms.getReturnCode()
        data = AutoupdateComms.getData()
        print "Returned status of %d" % status
        print "Returned %d bytes" % len(data)
        if status != 0:
            raise AutoUpdateError(data)
        return data

        
                
        
def usage_messages():     
    print "%s -c ConsoleADDR [-p ConsolePORT] [-s] [-t TaskID] "
    print "   -c ConsoleADDR = hostname/IP of console to update/intall from"
    print "   -p ConsolePORT = Console's port number [default is 8443]"
    print "   -t TaskID      = task id if update requested by Console - send notification with results"
    print "   -s             = use non-secure mode (testing only)"
    sys.exit(1)
    
def main():
    
    consoleAddr = ""
    consolePort = 8443
    consoleSecure = True
    retVal = 0
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "i:sc:p:")
        for o, a in opts:    
            if o == "-c":
                consoleAddr = a
            if o == "-s":
                consoleSecure = False
            elif o == "-p":
                consolePort = int(a)
                    
    
    except getopt.GetoptError, err:
        logging.getLogger('AutoUpdate').error(err)
        usage_messages()

    if consolePort < 1:
        msg = "Console port must be a positive number - exiting"
        logging.getLogger('AutoUpdate').error( msg)
        sys.exit(1)
    elif not consoleAddr:
        msg = "The name or IP address of a Console must be provided - exiting"
        logging.getLogger('AutoUpdate').error( msg)
        sys.exit(1)
    
    shim = Shim(consoleAddr, consolePort, consoleSecure)
    data = shim.listPackages(hostname='hostname', withDocs=False)
    data = shim.sendNotification(transId='0:0:0:0', info = "Autoupdate Splendid")
    data = shim.sendNotification(transId='0:0:0:0', info = "Autoupdate Splendid", success=True)
     
    
    
if __name__ == "__main__":
    main()  
    
