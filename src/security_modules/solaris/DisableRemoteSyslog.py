#!/usr/bin/env python

#
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#  Disallow syslog to receive messages from other systems.
#

import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service


class DisableRemoteSyslog:

    def __init__(self):
        self.module_name = "DisableRemoteSyslog"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        cmd = '/usr/bin/svcprop -p config/log_from_remote system-log'
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if results[1].rstrip('\n') == 'true':
            msg = "system-log 'config/log_from_remote' property is set to true"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''

            
    ##########################################################################
    def apply(self, option=None):
        """Apply changes."""

        action_record = ''
        result, reason = self.scan()
        if result == 'Pass':
            return 0, action_record

        # Set Property
        cmd = "/usr/sbin/svccfg -s system-log setprop config/log_from_remote = false"
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = 'Executed %s' % (cmd)
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)

        # Re-read/refresh configuration
        cmd = "/usr/sbin/svcadm refresh system-log"
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = 'Executed %s' % (cmd)
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)

        # Restart Service
        cmd = "/usr/sbin/svcadm restart system-log"
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = 'Executed %s' % (cmd)
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)


        msg = 'Disallowing remote syslog messages'
        return 1, 'yes'

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if change_record == None : 
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 0

        if change_record != 'yes':
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            return 0

        # Set property
        cmd = "/usr/sbin/svccfg -s system-log setprop config/log_from_remote = true"
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = 'Executed %s' % (cmd)
            self.logger.info(self.module_name, 'Undo Performed: ' + msg)

        # Re-read configuration
        cmd = "/usr/sbin/svcadm refresh system-log"
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = 'Executed %s' % (cmd)
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)

        # Restart Service
        cmd = "/usr/sbin/svcadm restart system-log"
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'failed to execute %s: %s' % (cmd, results[2])
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = 'Executed %s' % (cmd)
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)


        msg = 'Allowing remote syslog messages'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
