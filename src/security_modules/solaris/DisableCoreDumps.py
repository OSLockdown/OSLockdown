#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class DisableCoreDumps:

    def __init__(self):
        self.module_name = "DisableCoreDumps"

        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        cmd = "/usr/bin/coreadm" 
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = 'Unable to execute %s' % cmd
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
 
        found_enabled_line = False
        for line in results[1].split('\n'):
            if 'core dump' in line:
                if 'enabled' in line:
                    self.logger.info(self.module_name, \
                          'Scan Failed: ' + line.lstrip(' '))
                    found_enabled_line = True

        if found_enabled_line == True:
            msg = "Core dumps are not disabled"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        action_record = ''

        result, reason = self.scan()
        if result == 'Pass':
            return 0, action_record

        # Capture contents of /etc/coredadm.conf
        try:
            in_obj = open('/etc/coreadm.conf', 'r')
            action_record = ''.join(in_obj.readlines())
            in_obj.close()
        except IOError:
            pass


        cmds = ['/usr/bin/coreadm -d process', 
                '/usr/bin/coreadm -d global-setid', 
                '/usr/bin/coreadm -d log', 
                '/usr/bin/coreadm -d proc-setid'    ]
                 
        failed_cmd = False 
        for exec_cmd in cmds:
            results = tcs_utils.tcs_run_cmd(exec_cmd, True)
            if results[0] != 0:
                msg = 'Apply Error: Unable to execute %s: %s' % \
                      (exec_cmd, results[2].rstrip('\n'))
                self.logger.error(self.module_name, msg )
                failed_cmd = True
            else:
                msg = 'Apply Performed: Successfully executed %s' % exec_cmd
                self.logger.notice(self.module_name, msg )

        if failed_cmd == True:
            msg = 'Unable to disable core dumps with coreadm utility'
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

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
            tmp_file = open('/etc/coreadm.conf', 'w')
            tmp_file.write(change_record)
        except IOError, err:
            msg = "Unable to write to /etc/coreadm.conf: %s" % str(err).rstrip('\n')
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        tmp_file.close()
        results = tcs_utils.tcs_run_cmd('/usr/bin/coreadm -u', True)
        if results[0] != 0:
            msg = "Unable to undo previous changes (%s): %s" % \
                 (results[1].rstrip('\n'), results[2].rstrip('\n'))
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Core dump configuration restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
