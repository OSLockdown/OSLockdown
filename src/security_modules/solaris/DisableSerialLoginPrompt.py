#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.solaris


class DisableSerialLoginPrompt:

    def __init__(self):

        self.module_name = "DisableSerialLoginPrompt"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option_str):
        if not option_str:
            return 1
        try:
            value = int(option_str)
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        zonename = sb_utils.os.solaris.zonename()                                                                                       
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): Unable to use pmadm command" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)                                                                    
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))   

        if not os.path.isfile('/usr/sbin/pmadm'):
            msg = "Unable to find /usr/sbin/pmadm command"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)                                                                    
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))   

        failure_flag = False
        cmd = "/usr/sbin/pmadm -L -p zsmon"
        results = tcs_utils.tcs_run_cmd(cmd, True)  
        if results[0] != 0:
            msg = "Unable to execute: %s (%s)" % (cmd, results[2])
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, '', {'messages':[msg]}

        for line in results[1].split('\n'):
            fields = line.split(':')
            if len(fields) == 1:
                continue

            if len(fields) < 4:
                msg = "Ignoring malformed line: %s" % line
                self.logger.debug(self.module_name, msg)
                continue

            test = fields[3].find('x')
            if test < 0:
                msg = "%s is NOT disabled through port monitor %s" % (fields[2], fields[0])
                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                failure_flag = True
            else:
                msg = "%s is disabled through port monitor %s" % (fields[2], fields[0])
                self.logger.info(self.module_name, msg)

        if failure_flag == True:
            return False, 'Some services are not disabled through the zsmon port monitor', {'messages':[msg]}
        else:
            return True, '', {}


    ##########################################################################
    def apply(self, option=None):

        result, reason, messages = self.scan()
        if result == True:
            return False, '', {}

        action_record = []

        zonename = sb_utils.os.solaris.zonename()                                                                                       
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): Unable to use the pmadm command" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)                                                                    
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))   

        if not os.path.isfile('/usr/sbin/pmadm'):
            msg = "Unable to find /usr/sbin/pmadm command"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)                                                                    
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))   

        failure_flag = False
        cmd = "/usr/sbin/pmadm -L -p zsmon"
        results = tcs_utils.tcs_run_cmd(cmd, True)  
        if results[0] != 0:
            msg = "Unable to execute: %s (%s)" % (cmd, results[2])
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return False, '', {}

        for line in results[1].split('\n'):
            fields = line.split(':')
            if len(fields) == 1:
                continue

            if len(fields) < 4:
                msg = "Ignoring malformed line: %s" % line
                self.logger.debug(self.module_name, msg)
                continue

            test = fields[3].find('x')
            if test < 0:
                cmd = "/usr/sbin/pmadm -d -p zsmon -s %s" % str(fields[2])
                results = tcs_utils.tcs_run_cmd(cmd, True)  
                if results[0] != 0:
                    msg = "Unable to disable %s: %s" % (fields[2], str(results[2]).rstrip())
                    self.logger.notice(self.module_name, "Apply Failed: " + msg)
                else:
                    msg = "Disabled %s" % (fields[2])
                    self.logger.notice(self.module_name, "Apply Performed: " + msg)
                    action_record.append(fields[2])

        return True, ' '.join(action_record), {}

    ##########################################################################
    def undo(self, change_record):
        """Undo the previous action."""

        if change_record == None:
            msg = 'No change record provided; unable to perform undo.'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, '',{}

        for svctag in change_record.split(' '):
            cmd = "/usr/sbin/pmadm -e -p zsmon -s %s" % svctag
            results = tcs_utils.tcs_run_cmd(cmd, True)  
            if results[0] != 0:
                msg = "Unable to enable %s: %s" % (svctag, str(results[2]).rstrip())
                self.logger.notice(self.module_name, "Undo Failed: " + msg)
            else:
                msg = "Enabled %s" % (svctag)
                self.logger.notice(self.module_name, "Undo Performed: " + msg)

        return True, '', {}

