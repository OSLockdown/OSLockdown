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

class PasswordInvalidate:
    """
    Once the password expired, the account will be locked out after X days (-I 7).
    """
    def __init__(self):
        self.module_name = "PasswordInvalidate"
        self.__target_file = '/etc/shadow'
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.name_map = {}
        self.setup_uids()

    ##########################################################################
    def setup_uids(self):
        """
        Get a list of usernames and ids for later use
        """
        try:
            in_obj = open('/etc/passwd', 'r')
        except IOError, err:
            msg = "Unable to open password file file: %s" % err
            self.logger.error(self.module_name, 'Init Failed: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        # map the user names to their ids
        for line in lines:
            if line.startswith('+'):
                msg = "/etc/passwd - Skipping %s entry" % line.rstrip('\n')
                self.logger.debug(self.module_name, 'Init Error: ' + msg)
                continue

            fields = line.split(':')
            if len(fields) < 7:
                continue
            try:
                self.name_map[fields[0]] = int(fields[2])
            except Exception:
                pass
 
    ##########################################################################
    def validate_input(self, option=None):
        """Validate Input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Scan System"""
        # Just to keep pylint quiet
        if option != None:
            option = None

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError:
            msg = "Unable to open shadow file"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            return 'Fail', msg

        original_content = in_obj.readlines()
        in_obj.close()

        user = None
        for line in original_content:
            fields = line.split(':')
            if len(fields) < 7:
                continue

            # skip system users
            if self.name_map.has_key(fields[0]) and \
                self.name_map[fields[0]] < 500:
                continue

            if len(fields[6]) == 0:
                user = fields[0]

        if user: 
            msg = "User %s has no password invalidation interval set" % user
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        # Just to keep pylint quiet
        if option != None:
            option = None

        action_record = ''
        result, reason = self.scan()
        if result == 'Pass':
            return 0, action_record

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open shadow file"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        user = ''
        action_record = []
        for line in lines:
            fields = line.split(':')
            if len(fields) < 7:
                continue

            # skip system users
            if self.name_map.has_key(fields[0]) and \
                self.name_map[fields[0]] < 500:
                continue

            if len(fields[6]) == 0:
                user = fields[0]
                cmd = '/usr/bin/chage -I 7 %s' % user
                output_tuple = tcs_utils.tcs_run_cmd(cmd)
                if output_tuple[0] != 0:
                    msg = "Unexpected return value (%s)" % output_tuple[0]
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                action_record.append(user)

        msg = 'Password invalidation interval set.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, ' '.join(action_record)

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

        for user in change_record.split():
            cmd = '/usr/bin/chage -I "-1" %s' % user
            output_tuple = tcs_utils.tcs_run_cmd(cmd)
            if output_tuple[0] != 0:
                msg = "Unexpected return value (%s)" % output_tuple[0]
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Password invalidation interval removed.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

