#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info

class NoEmptyPasswords:
    def __init__(self):
        self.module_name = "NoEmptyPasswords"
        self.__target_file = '/etc/shadow'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open shadow file: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        original_content = in_obj.readlines()
        in_obj.close()

        user = ''
        for line in original_content:
            fields = line.split(':')
            if len(fields) < 7:
                continue
            if len(line.split(":")[1]) == 0:
                user = line.split(":")[0]

        if user: 
            msg = "User %s has an empty password" % user
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """Create and replace the audit rules configuration."""

        action_record = ''
        result, reason = self.scan()
        if result == 'Pass':
            return 0, action_record

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open shadow file: %s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        user = ''
        action_record = ''
        for line in in_obj:
            fields = line.split(':')
            if len(fields) < 7:
                continue
            if len(line.split(":")[1]) == 0:
                user = line.split(":")[0]
                cmd = '/usr/bin/passwd -l %s' % user
                output_tuple = tcs_utils.tcs_run_cmd(cmd)
                if output_tuple[0] != 0:
                    msg = "Unexpected return value (%s)" % output_tuple[0]
                    self.logger.info(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    msg = "Successfully executed: %s" % cmd
                    self.logger.debug(self.module_name, 'Apply Performed: ' + msg)

                    msg = "User (%s) has been locked because it has an empty password" % user
                    self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

                action_record += user+'\n'

        in_obj.close()

        msg = 'Empty passwords removed.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        force_flag = ""
        if sb_utils.os.info.is_solaris() == False:
            force_flag = "-f"

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        for user in change_record.split('\n'):
            if not user:
                break
            cmd = '/usr/bin/passwd %s -u %s' % (force_flag, user)
            output_tuple = tcs_utils.tcs_run_cmd(cmd)
            if output_tuple[0] != 0:
                msg = "Unexpected return value (%s)" % output_tuple[0]
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                msg = "Successfully executed: %s" % cmd
                self.logger.debug(self.module_name, 'Undo Performed: ' + msg)

                msg = "User (%s) unlocked" % user
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        msg = 'User accounts with empty passwords have been unlocked.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

