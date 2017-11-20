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

class RequireGrubPassword:

    def __init__(self):
        #CONSTANTS
        self.MISSING   = 1
        self.TOO_SHORT = 2
        self.IS_NULL_LITERAL = 3
        
        self.module_name = "RequireGrubPassword"
        
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

        messages = {'messages':[]}
        retval = True

        # leave quickly if we are N/A due to architecture.
        test_arch = platform.machine()
        if test_arch == 's390x':
            msg = "GRand Unified Bootloader (GRUB) not used on S390 hardware"
            self.logger.notice(self.module_name, "Not Applicable: " + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        elif sb_utils.os.info.is_solaris() == True and sb_utils.os.info.is_x86() == False:
            msg = "GRand Unified Bootloader (GRUB) not used on SPARC hardware"
            self.logger.notice(self.module_name, "Not Applicable: " + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        # Ok, quickly test the permissions on the grub file.  It should be owned by root and perms no greater than 0600:
        # This module won't fix the problems, but so only indicate any issues with a warning.  Permission problems do not
        # Constitute a failure case, as the 'System Configuration File Permissions' module will fix (if that module is enabled).
        
        msg = "Checking access controls on %s" % self.__target_file
        self.logger.info(self.module_name, 'Scan: ' + msg)

        try:
            statinfo = os.stat(self.__target_file)
        except OSError, err:
            msg = "Unable to stat %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if statinfo.st_uid != 0:
            msg = '%s is not owned by root' % self.__target_file
            messages['messages'].append("Warning:%s" % msg)
            self.logger.warning(self.module_name, 'Warning: ' + msg)

        if (statinfo.st_mode & 0177):
            msg = '%s has permissions of %o but expected 0600' % \
                         (self.__target_file,stat.S_IMODE(statinfo.st_mode))
            messages['messages'].append("Warning:%s" % msg)
            self.logger.warning(self.module_name, 'Warning: ' + msg)

        if messages['messages'] != []:
            msg = "Ownership/permissions issues on '%s' can be fixed by 'System Configuration File Permissions' (but only if that module is part of this profile)" % self.__target_file
            messages['messages'].append("Warning:%s" % msg)
            self.logger.warning(self.module_name, 'Warning: ' + msg)
                
        
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to  open %s: %s" % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        msg = "Checking %s for 'password --md5' line" % (self.__target_file)
        self.logger.info(self.module_name, msg)
        password = re.compile('^password\s+--md5\s+\S+')

        for line_nr, line in enumerate(lines):
            if password.search(line.strip()):
                msg = "Found 'password --md5' option at line "\
                      "%d of %s" % (line_nr+1, self.__target_file)
                self.logger.info(self.module_name, 'Scan Passed: ' + msg)
                return True ,'', messages

        msg = "%s is missing 'password --md5' option" % (self.__target_file)
        messages['messages'].append('Error:%s' % msg)
        self.logger.info(self.module_name, 'Scan Failed: ' + msg)
        return False ,'', messages

    ##########################################################################
    def apply(self, option=None):

        reason = ""
        messages = {'messages':[]}

        result, reason, messages = self.scan()
        if result == True:
            return False, '', messages
        reason = ""
        
        msg = "Administrator must set grub password manually on each machine."
        raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        return False, reason, msg

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action.  Note that this is only a legacy to allow removall of a password that
           OS Lockdown set in versions 4.0.7 and earlier.  SB4.0.8+ will not set grub passwords"""

        msg = "Skipping Undo: No change record in state file."
        self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
        return False, msg, {}


