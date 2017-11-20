#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

"""
  DisablePAMConsole
  PAM grants sole access to admin privileges to the first 
  user who logs into the console.

"""

import sys
import os
import shutil
import glob
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class DisablePAMConsole:
    """
    Class to disable PAM from granting sole access to admin privileges 
    to the first user who logs into the console.
    """

    def __init__(self):
        """Constructor"""
        self.module_name = "DisablePAMConsole"
        self.__target_file = '/etc/pam.d/'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Find any lines in /etc/pam.d/* that contains pam_console.so"""
        found = False

        file_list = glob.glob(self.__target_file+'*')

        search_pattern = re.compile('pam_console.so')
        for pamfile in file_list:
            msg = "Looking for pam_console.so in %s" % pamfile
            self.logger.info(self.module_name, 'Scan: ' + msg)
            try:
                in_obj = open(pamfile, 'r')
            except IOError, err:
                msg = "Unable to open %s: %s" % (pamfile, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            for line in in_obj:
                linelist = line.split()
                # ignore comments and other lines
                if len(linelist) < 3 or linelist[0].startswith('#'):
                    continue

                if search_pattern.search(linelist[2]):
                    msg = "Found pam_console.so in %s" % pamfile
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    found = True

            in_obj.close()


        if found: 
            msg = "pam_console is not disabled"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        else:
            return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """Apply changes."""

        action_record = ''
        result, reason = self.scan()
        if result == 'Pass':
            return 0, action_record

        file_list = glob.glob(self.__target_file+'*')

        search_pattern = re.compile('pam_console.so')
        for pamfile in file_list:
            try:
                in_obj = open(pamfile, 'r')
            except IOError, err:
                msg = "Unable to open %s: %s" % (pamfile, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            found = False
            for line in in_obj:
                linelist = line.split()
                # ignore comments and other lines
                if len(linelist) < 3 or linelist[0].startswith('#'):
                    continue

                if search_pattern.search(linelist[2]):
                    found = True

            if not found:
                in_obj.close()
                continue

            in_obj.seek(0)

            msg = "Removing pam_console.so from %s" % pamfile
            self.logger.notice(self.module_name, 'Apply: ' + msg)
            try:
                out_obj = open(pamfile + '.new', 'w')
                shutil.copymode(pamfile, pamfile + '.new')
                sb_utils.SELinux.restoreSecurityContext(pamfile)
            except (OSError, IOError), err:
                msg = "Unable to create temporary %s.new file" % pamfile
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            for line in in_obj:
                linelist = line.split()
                if len(linelist) > 2 and search_pattern.search(linelist[2]):
                    continue
                out_obj.write(line)

            in_obj.close()
            out_obj.close()

            action_record += tcs_utils.generate_diff_record(pamfile + '.new',
                                             pamfile)

            try:
                shutil.copymode(pamfile, pamfile + '.new')
                shutil.copy2(pamfile + '.new', pamfile)
                sb_utils.SELinux.restoreSecurityContext(pamfile)
                os.unlink(pamfile + '.new')
            except (OSError, IOError):
                msg = "Unable to replace %s with new version" % pamfile
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Disabled pam_console support.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'The pam_console configuration has been restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
