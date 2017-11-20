#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module check's root's shell to make sure it is on the 
# root filesystem. If it is not, it will set the shell
# to the OS default.
#

import os
import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info

class RootShell:

    def __init__(self):
        """Constructor"""
        self.module_name = "RootShell"
        self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.info.is_solaris() == True:
            self.__root_sh_path = '/sbin/sh'
        else:
            self.__root_sh_path = '/bin/bash'
   
    ##########################################################################
    def scan(self, option=None):
        """
        Check to see if root's shell is on the root (/) filesystem
        """
        if option != None:
            option = None

        # Get root accounts login information
        userinfo = pwd.getpwnam('root')        

        # Perform an file stat on root's shell
        try: 
            root_sh = os.stat(userinfo[6])
        except Exception, err: 
            msg = 'Unable to stat %s: %s' % (userinfo[6], err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
         
        # Perform a stat on the root filesystem 
        try:
            root_fs = os.stat('/')
        except Exception, err: 
            msg = 'Unable to stat root filesystem: %s' % (err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        # Compare the device numbers between root and where
        # root's shell sits. If they are differen't numbers,
        # then they are on two different filesystems

        if root_fs.st_dev != root_sh.st_dev:
            msg = "Root's shell %s is not on the root partition" % userinfo[6]
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', 'Root\'s shell is not on the / partition'

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        action_record = ""
        if option != None:
            option = None
        results, msg = self.scan()
        if results == 'Pass':
            return 0, ''

        if msg != None:
            msg = None

        # Let's make sure the default shell (/bin/bash) is okay
        # and some idiot didn't make make /bin a different filesystem
        try:
            root_fs = os.stat('/')
        except Exception, err:
            msg = 'Unable to stat root filesystem: %s' % (err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            bash_fs = os.stat(self.__root_sh_path)
        except Exception, err:
            msg = 'Unable to stat %s:  %s' % (self.__root_sh_path, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if root_fs.st_dev != bash_fs.st_dev:
            msg = '%s is not on the / filesystem either' % self.__root_sh_path
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Now set root's shell to /bin/shell
        action_record = pwd.getpwnam('root')[6]
        cmd = '/usr/sbin/usermod -s %s root' % (self.__root_sh_path)
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = "Unable to set root's shell to %s: %s" % (self.__root_sh_path, results[2])
            self.logger.error(self.module_name, 'Scan Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Root\'s shell changed to the default %s' % self.__root_sh_path
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, 'fixed'

    ##########################################################################
    def undo(self, change_record=None):
        """Reset root's shell"""

        if not os.path.isfile(change_record):
            msg = '%s is not a file; unable to change shell' % change_record
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, msg
        
        cmd = '/usr/sbin/usermod -s %s root' % (change_record)
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = "Unable to set root's shell to %s: %s" % (change_record, results[2])
            self.logger.error(self.module_name, 'Undo Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Root\'s shell reset to %s' % change_record
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

    ##########################################################################
    def validate_input(self, option=None):
        """
        Validate option which is blank
        """
        if option != None:
            option = None

        return 0
