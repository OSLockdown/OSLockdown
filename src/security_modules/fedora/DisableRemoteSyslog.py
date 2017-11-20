#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disallow rsyslog to receive messages from other systems.
#
#

import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class DisableRemoteSyslog:

    def __init__(self):
        self.module_name = "DisableRemoteSyslog"
        self.__target_file = '/etc/init.d/rsyslog'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        found = False
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Checking %s to see if 'SYSLOGD_OPTIONS' as the '-r' option "\
              "specified" % self.__target_file
        self.logger.info(self.module_name, 'Scan Error: ' + msg)

        for line_nr, line in enumerate(in_obj.xreadlines()):
            if line.strip().split("=")[0] == 'SYSLOGD_OPTIONS' and \
             '-r' in line.strip().split("=")[1]:
                msg = "Found: '%s' at line %d" % (line.strip().rstrip('\n'), line_nr)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                found = True
                break

        in_obj.close()

        if found == True: 
            msg = "Syslog configured to accept remote messages."
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

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s file" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        try:
            out_obj = open(self.__target_file + '.new', 'w')
            shutil.copymode(self.__target_file, self.__target_file + '.new')
        except IOError, err:
            msg = "Unable to create temporary %s.new file" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line_nr, line in enumerate(in_obj.xreadlines()):
            if line.strip().split("=")[0] == 'SYSLOGD_OPTIONS' and \
             '-r' in line.strip().split("=")[1]:
                out_obj.write(line.replace('-r',''))
                msg = "Removing '-r' from SYSLOGD_OPTIONS at line %d" % line_nr
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            else:
                out_obj.write(line)

        in_obj.close()
        out_obj.close()

        action_record = tcs_utils.generate_diff_record(self.__target_file + '.new',
                                             self.__target_file)

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Remote rsyslog disabled.'
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

        # Restore file to what it was before the apply
        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = 'Syslog configuration restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

