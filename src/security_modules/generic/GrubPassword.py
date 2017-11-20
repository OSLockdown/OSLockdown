#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

"""
GrubPassword module provides the GrubPassword class which is capable of
handling the security guidelines regarding the requirement for a grub password.
"""

import re
import os
import stat
import sys


import crypt
import shutil
import platform

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info

class GrubPassword:

    def __init__(self):
        #CONSTANTS
        self.MISSING   = 1
        self.TOO_SHORT = 2
        self.IS_NULL_LITERAL = 3
        
        self.module_name = "GrubPassword"
        
        # What file should we be looking for?
        # Currently Solaris/SUSE/openSUSE use /boot/grub/menu.lst, everyone else uses /boot/grub/grub.conf
        # TODO:  should we not hardcode but look intelligently at the file(s) to determine the right one?
        
        if sb_utils.os.info.is_solaris() == True or sb_utils.os.info.is_LikeSUSE() == True:
            self.__target_file = '/boot/grub/menu.lst'
        else:
            self.__target_file = '/boot/grub/grub.conf'
            
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

    def scan(self, option=None):

        msg = "This module has been retired.  Please replace 'Password Protect Grub' with 'Require Grub Password' in all profiles"
        self.logger.warning(self.module_name, msg)
        raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
        return False ,'',{}

    ##########################################################################
    def apply(self, option=None):

        reason = ""
        messages = {'messages':[]}

        result, reason, messages = self.scan()
        if result == True:
            return False, '', messages
        reason = ""
        
        msg = "This module has been retired.  Please replace 'Password Protect Grub' with 'Require Grub Password' in all profiles"
        self.logger.warning(self.module_name, msg)
        messages['messages'].append('Retire:%s' % msg)

        msg = "Administrator must set grub password manually on each machine."
        messages['messages'].append('Warning:%s' % msg)
        raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        return False, reason, messages

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action.  Note that this is only a legacy to allow removall of a password that
           OS Lockdown set in versions 4.0.7 and earlier.  SB4.0.8+ will not set grub passwords"""

        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Restore file to what it was before the apply
        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Password removed from grub's %s." % (self.__target_file)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

