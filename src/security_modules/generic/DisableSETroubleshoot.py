#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable SETroubleshoot 
#
# Note:
#   On Red Hat systems, the setroubleshoot service is a facility for notifying 
#   the desktop user of SELinux denials in a user-friendly fashion. SELinux errors 
#   may provide important information about intrusion attempts in progress, or may 
#   give information about SELinux configuration problems which are preventing 
#   correct system operation. In order to maintain a secure and usable SELinux 
#   installation, error logging and notification is necessary.
#
#   On RH4/RH5/F10 setroubleshoot is a true service routine, and is enabled/disabled
#   by 'chkconfig'.  The setroubleshoot service would sends notifications to sealert.
#
#   On RH6, F11+ setroubleshoot is *not* a service, but instead is triggered by sedispatch
#   which is a plugin to the audit daemon.  We can enable/disable this *plugin* by 
#   editting /etc/audisp/plugins.d/sedispatch.conf and changing 'active = yes' to 'active = no'.
#   This plugin listens for AVC issues on dbus and then kicks off setroubleshoot/sealert.
#
#
#
##############################################################################

import sys
import os

sys.path.append('/usr/share/oslockdown')
from ModuleInfo import getServiceList, getPackageList
import TCSLogger
import tcs_utils
import sb_utils.os.info

try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

try:
    import Enable_Disable_Any_Service
except ImportError:
    raise

# Class/methods for disabling the 'setroubleshoot' service
class DisableSETroubleshoot_service:
    def __init__(self, module_name):
        self.module_name = module_name

    def scan(self, option=None):
        return Enable_Disable_Any_Service.scan(self.module_name, enable=False)    

    def apply(self, option=None):
        return Enable_Disable_Any_Service.apply(self.module_name, enable=False)    

    def undo(self, change_record=None):
        return Enable_Disable_Any_Service.undo(self.module_name, change_record=change_record)    
        
# Class/methods for disabling the sedispatch audit plugin
# Note that we don't bother checking for the package, the plugin is sufficient
# Yes, someone could create this plugin w/o installing the package, but we'll still
# disabling it.

class DisableSETroubleshoot_plugin:
    def __init__(self, module_name):
        self.pluginName = '/etc/audisp/plugins.d/sedispatch.conf'
        self.module_name = module_name
        if not os.path.exists(self.pluginName):
            msg = "'%s' does not exist - nothing to check/modify." % self.pluginName
            logger.warning(module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (module_name, msg))
        self.lines = None

    def _readFile(self):
        self.lines = open(self.pluginName,"r").readlines()

    def _writeFile(self):
        open(self.pluginName,"w").writelines(self.lines)
        
    def _tryChange(self, lookFor, changeTo):
        problems=''
        changes=''
        
        for ln in range(len(self.lines)):
            try:
                fields = self.lines[ln].strip().split('=')
                if fields[0].strip() == 'active' and fields[1].strip() == lookFor:
                    problems = "Detected 'active = %s' in %s" % (lookFor, self.pluginName)
                    self.lines[ln] = self.lines[ln].replace(lookFor,changeTo)
                    changes = "Set 'active = %s' in %s'" % (changeTo, self.pluginName)
            except (KeyError,IndexError):
                pass
        return problems, changes                        

    def scan(self, option=None):
    
        
        packageList = getPackageList(libraryName=self.module_name)
        for pkg_item in packageList:
            results = sb_utils.os.software.is_installed(pkgname=pkg_item) 
            if results == False:
                msg = "'%s' package is not installed" % pkg_item
                raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
             
       
        # assume the module passes a scan - we'll change this if we fail
        retval = True
        msg = "Did not find 'active = yes' in %s" % self.pluginName
        messages = {'messages':[]}
        
        self._readFile()
        problems, changes = self._tryChange('yes', 'no')
        if problems:
            retval = False
            msg = problems
            messages['messages'].append(problems)
            logger.warning(self.module_name, msg)
        else:
            logger.notice(self.module_name, msg)
            
        return retval, msg, messages
    def apply(self, option=None):
        # assume the module passes a scan - we'll change this if we fail
        retval, msg, messages = self.scan(option)
        if retval == True:
            return False, msg, messages

        retval = False
            
        msg = "Did not find 'active = yes' in %s" % self.pluginName
        messages = {'messages':[]}
        changerec = ""
        
        self._readFile()
        problems, changes = self._tryChange('yes', 'no')
        if changes:
            retval = True
            msg = changes
            messages['messages'].append(problems)
            self._writeFile()
            changerec = 'yes'
            logger.warning(self.module_name, msg)
        else:
            logger.notice(self.module_name, msg)
        return retval, changerec, messages
        
    def undo(self, change_record=None):

        # assume the module passes a scan - we'll change this if we fail
        retval = False
        msg = "Did not find 'active = no' in %s" % self.pluginName
        
        messages = {'messages':[]}
        
        self._readFile()
        problems, changes = self._tryChange('no', 'yes')
        if problems:
            retval = True
            msg = problems
            messages['messages'].append(problems)
            self._writeFile()
            msg = "Restored 'active = yes' in %s" % self.pluginName
            logger.warning(self.module_name, msg)
        else:
            logger.notice(self.module_name, msg)
        return retval, '',messages

class DisableSETroubleshoot:

    def __init__(self):
        
        # "RedHat" 5 and Fedora 10 behave one way, "RedHat" 6 and Fedora 11+ behave differently
        # determine which we are and set a flag appropriately
        # Note that both methods require the setroubleshoot and setroubleshoot-server packages
        # We will assume a plugin service *unless* we're like RH5 or F10.

        self.module_name = self.__class__.__name__
        isPlugin = True
        
        if sb_utils.os.info.is_LikeRedHat() and sb_utils.os.info.getOSMajorVersion() in ["5"]:
            isPlugin = False
        elif sb_utils.os.info.is_fedora() and sb_utils.os.info.getOSMajorVersion() in ["10"]:
            isPlugin = False

        if isPlugin:
            self.subclass = DisableSETroubleshoot_plugin(self.module_name)
        else:
            self.subclass = DisableSETroubleshoot_plugin(self.module_name)

    def scan(self, option=None):
        return self.subclass.scan(option)    

    def apply(self, option=None):
        return self.subclass.apply(option)    

    def undo(self, change_record=None):
        return self.subclass.undo(change_record)    
        
if __name__ == '__main__':
    TEST = DisableSETroubleshoot()
    print TEST.scan()
    (x, y, z) = TEST.apply()
    print TEST.undo(y)
