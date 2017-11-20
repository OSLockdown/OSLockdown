#!/usr/bin/env python
##############################################################################
# Copyright (c) 2009-2015 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Invoked to take apart the provided 'updater' file from the Console and
# trigger an autoupdate action#
##############################################################################

MODULE_NAME = "AutoUpdate"
MODULE_REV  = "$Rev: 17889 $".strip('$').strip()

import os
import sys
import logging
import zipfile
import sbProps
import shutil
import StringIO
import tarfile
import exceptions

os.sys.path.append(sbProps.SB_BASE)

try:
    import TCSLogger
except ImportError:
    try:
        from sb_utils.misc import TCSLogger
    except ImportError:
        raise
logger = TCSLogger.TCSLogger.getInstance()
                    

class AutoUpdate:

    def __init__(self):
        self.updaterRoot = '/var/lib/oslockdown/profiles/.enterprise'
        self.updaterName = '%s/autoupdate.tgz' % self.updaterRoot
        logger.info("AutoUpdate", " CORE AUTOUPDATE INITIALIZED")

    def autoUpdate(self, notifyUrl=None, transId=None, pretend = False, forceFlag = False):
        # The file *should* have been saved as /var/lib/oslockdown/profiles/.enterprise/autoupdate.tgz
        # To autoupdate python code is designed to be more or less 'self-contained', not relying on any other
        # OS Lockdown code.  So scrub the current system path to remove any 'oslockdown' references
        # *IF* the self.updaterZipName file exists, than append that path to our import path, then the path to 
        # the standard autoupdate files.  This will ensure that the SB_Updaters.py file from the Console is chosen
        # over the one from whatever files are currently loaded.
        # The SB_Updaters.py file will hold the current 'how do I update Linux/Solaris' code.
        
        newpath = [ elem for elem in sys.path if not 'oslockdown' in elem ]
        
        
        if os.path.exists(self.updaterName):
            newpath.append(self.updaterRoot)
        
            try:
            	tarball = tarfile.open(self.updaterName)
            	for entry in tarball:
               	    if entry != None:
                        tarball.extract(entry.name, self.updaterRoot)
            	newpath.append(self.updaterRoot + "/autoupdate")
                sys.path = newpath
        
            	import InstallUpdate
        
            	# the notifyUrl is substantially longer than what the update really needs, but there is code
            	# in those routines to strip off only what is required, so just give it the full string
            	# we need to redirect stdin/stdout/stderr to keep the autoupdate going when we kill the dispatcher...
            	sys.stdin = open("/dev/null")
            	sys.stdout = open("/dev/null","w")
            	sys.stderr = open("/dev/null","w")
                InstallUpdate.doAutoUpdate(notifyUrl, transId, pretend, forceFlag)
                if os.path.exists(self.updaterName) :
                    os.unlink(self.updaterName) 
                if os.path.exists(self.updaterRoot + "/autoupdate"):
                    shutil.rmtree(self.updaterRoot + "/autoupdate")
            except ImportError, e:
                sys.stderr = open("/dev/stderr","w") 
                print >> sys.stderr , "ERROR: Unable to import downloaded installer package",e
                logger.error("AutoUpdate", " unable to extract Updater files successfully - %s" % str(e))
                sys.exit(1)
             
            except Exception, e:
                #sys.stderr = open("/dev/stderr","w") 
                print >> sys.stderr , "ERROR: ",e
                logger.error("AutoUpdate", e)
                sys.exit(1)
                   
        else:
           logger.error("AutoUpdate", " %s does not exist" % self.updaterName)
           sys.exit(1)
        
        # if we ever get to here (IE - the Updater.zip provided code fell through -
        # assume it was because nothing neede to be done.  
        sys.exit(sbProps.EXIT_SUCCESS)
        
        
if __name__ == "__main__":
    try:
        AutoUpdate().autoUpdate()
    except Exception, e:
         logger.error("AutoUpdate", " unable to extract Updater files successfully - %s" % str(e))
         sys.exit(sbProps.EXIT_FAILURE)
    
