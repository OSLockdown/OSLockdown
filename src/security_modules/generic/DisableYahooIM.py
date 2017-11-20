#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
"""
DisableYahooIM

 If ymessenger rpm is installed, remove file permissions from it's
 executable.
"""

import sys
import os
import stat

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms

class DisableYahooIM:
    """
    Disable the ymessenger client binary
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'DisableYahooIM'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Check for rpm and file permissions"""
        if option != None:
            option = None


        if sb_utils.os.info.is_solaris() == True:
            msg = "Yahoo IM client is not part of the standard Solaris distribution."
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        results =  sb_utils.os.software.is_installed(pkgname='ymessenger')
        if results != True:
            msg = "ymessenger is not installed on the system"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        try:
            statinfo = os.stat('/usr/bin/ymessenger')
        except (OSError, IOError), err: 
            reason = "Unable to stat /usr/bin/ymessenger: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + reason)
            raise tcs_utils.ScanError("%s %s" % (self.module_name, reason))

        # We want the permissions to 000 so it can not be executed or read
        if statinfo.st_mode & 0777 ^ 0000 != 0:
            reason = \
            '/usr/bin/ymessenger has permissions of %o instead of 000' % \
                     stat.S_IMODE(statinfo.st_mode)
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        elif statinfo.st_uid != 0:
            reason = '/usr/bin/ymessenger has owner %d instead of 0 (root)' % \
                    statinfo.st_uid
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason


        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):

        if sb_utils.os.info.is_solaris() == True:
            msg = "Yahoo IM client is not part of the standard Solaris distribution."
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, msg

        changes_to_make = {'owner':'root',
                           'group':'root',
                           'dacs':0}
        change_record = sb_utils.file.fileperms.change_file_attributes('/usr/bin/ymessenger', changes_to_make)

        msg = \
        '/usr/bin/ymessenger permissions set to 0000 and ownership to root'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        
        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        if sb_utils.os.info.is_solaris() == True:
            msg = "Yahoo IM client is not part of the standard Solaris distribution."
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        # if we ever see an empty change record, then blindly  reset perms...
        if change_record == "":
            change_record = {'owner':'root',
                             'group':'root',
                             'dacs':755}

        sb_utils.file.fileperms.change_file_attributes('/usr/bin/ymessenger', change_record)
        
        msg = '/usr/bin/ymessenger permissions restored'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

