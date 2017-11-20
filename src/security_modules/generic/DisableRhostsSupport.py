#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
#  Disable Rhosts Support from PAM
#

import sys
import os
import shutil
import glob
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info 
import sb_utils.SELinux

class DisableRhostsSupport:

    def __init__(self):
        self.module_name = "DisableRhostsSupport"
        self.__target_file = '/etc/pam.d/'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        found = False

        if sb_utils.os.info.is_solaris() == True:
            file_list = ['/etc/pam.conf']
        else:
            file_list = glob.glob(self.__target_file + '*')

        search_pattern = re.compile('pam_rhosts')
        for pamfile in file_list:
            file_found = False
            msg = "Looking for pam_rhosts in %s" % pamfile
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
                if sb_utils.os.info.is_solaris() == True:
                    if search_pattern.search(linelist[3]):
                        found = True
                        file_found = True
                else:
                    if search_pattern.search(linelist[2]):
                        found = True
                        file_found = True

            in_obj.close()

            if file_found:
                msg = "Found pam_rhosts in %s" % (pamfile)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        if found: 
            msg = "rhosts is not disabled"
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

        if sb_utils.os.info.is_solaris() == True:
            file_list = ['/etc/pam.conf']
        else:
            file_list = glob.glob(self.__target_file + '*')

        search_pattern = re.compile('pam_rhosts')
        for pamfile in file_list:
            try:
                in_obj = open(pamfile, 'r')
            except IOError, err:
                msg = "Unable to open %s: %s" % (pamfile, err)
                self.logger.error(self.module_name, 'Appy Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            found = False
            for line in in_obj:
                linelist = line.split()
                # ignore comments and other lines
                if len(linelist) < 3 or linelist[0].startswith('#'):
                    continue
                if sb_utils.os.info.is_solaris() == True:
                    if search_pattern.search(linelist[3]):
                        found = True
                else:
                    if search_pattern.search(linelist[2]):
                        found = True

            if not found:
                in_obj.close()
                continue

            in_obj.seek(0)

            msg = "Removing pam_rhosts from %s" % (pamfile)
            self.logger.notice(self.module_name, 'Appy: ' + msg)

            try:
                out_obj = open(pamfile + '.new', 'w')
                shutil.copymode(pamfile, pamfile + '.new')
            except IOError, err:
                msg = "Unable to create temporary %s.new file" % pamfile
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            for line in in_obj:
                linelist = line.split()
                try: 
                    if search_pattern.search(linelist[2]):
                        continue
                    if search_pattern.search(linelist[3]):
                        continue
                except IndexError:
                    pass

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
            except (IOError, OSError):
                msg = "Unable to replace %s with new version" % pamfile
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Disabled rhosts support.'
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
            tcs_utils.apply_patch(change_record.lstrip())
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'The rhosts configuration has been restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

