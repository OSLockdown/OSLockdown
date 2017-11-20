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

class IPForward:

    def __init__(self):

        self.module_name = "IPForward"
        self.logger = TCSLogger.TCSLogger.getInstance()

        # Identify the configuration file and parameter
        # you want to set here...
        self.__target_file = '/etc/default/ndd'
        self._param       = {  'ip_forward_directed_broadcasts': 0}


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []

        msg = "Using routeadm to test ipv4-forwarding and ipv6-forwarding"
        messages['messages'].append(msg)
        self.logger.debug(self.module_name, msg)

        failure_flag = False
        for param in ['ipv4-forwarding', 'ipv6-forwarding']:
            cmd = '/usr/sbin/routeadm -p %s' % param
            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = 'failed to execute %s: %s' % (cmd, results[2])
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            try:
                param_key = results[1].split(' ')[0].split('=')[0]
                param_val = results[1].split(' ')[0].split('=')[1]
            except IndexError:
                msg = 'Can not determine status of %s' % param
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            if param_val == 'enabled':
                msg = '%s %s is enabled' % (param, param_key)
                messages['messages'].append("Fail: %s" % msg)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                failure_flag = True
            else:
                msg = '%s %s is disabled' % (param, param_key)
                messages['messages'].append("Okay: %s" % msg)
                self.logger.info(self.module_name, msg)

        if not os.path.isfile('/etc/notrouter'):
            msg = '/etc/notrouter file is missing'
            messages['messages'].append("Fail: %s" % msg)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            failure_flag = True
        else:
            msg = '/etc/notrouter file is present'
            messages['messages'].append("Okay: %s" % msg)
            self.logger.debug(self.module_name, msg)

        if failure_flag == True:
            return False, 'IP Forwarding is enabled.', messages
        else:
            return True, '', messages


    ##########################################################################
    def apply(self, option=None):

        messages = {}
        messages['messages'] = []

        action_record = []
        for param in ['ipv4-forwarding', 'ipv6-forwarding']:
            cmd = '/usr/sbin/routeadm -p %s' % param
            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = 'failed to execute %s: %s' % (cmd, results[2])
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            try:
                param_key = results[1].split(' ')[0].split('=')[0]
                param_val = results[1].split(' ')[0].split('=')[1]
            except IndexError:
                msg = 'Can not determine status of %s' % param
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            if param_val == 'enabled':
                cmd = '/usr/sbin/routeadm -d %s' % param
                results = tcs_utils.tcs_run_cmd(cmd, True)
                if results[0] != 0:
                    msg = 'failed to execute %s: %s' % (cmd, results[2])
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    action_record.append('/usr/sbin/routeadm -e %s\n' % param)
                    msg = 'Apply Performed: IP forwarding disabled: %s' % (cmd)
                    self.logger.notice(self.module_name, msg)
                    msg = "Disabled by executing /usr/sbin/routeadm -d %s" % param
                    messages['messages'].append(msg)


        if not os.path.isfile('/etc/notrouter'):
            try:
                out_obj = open('/etc/notrouter', 'w')
                out_obj.write('')
                out_obj.close()
                msg = 'Created /etc/notrouter file'
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                action_record.append('/bin/rm -f /etc/notrouter\n')
            except IOError, err:
                msg = "Unable to create /etc/notrouter: %s" % err
                messages['messages'].append("Error: %s" % msg)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
           
        if action_record == []:
            return False, '', messages
        else:
            return True, ''.join(action_record), messages


    ##########################################################################
    def undo(self, action_record=None):


        if not action_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for cmd in action_record.split('\n'):
            if not cmd:
                continue

            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = 'failed to execute %s: %s' % (cmd, results[2])
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                msg = 'Undo Performed: IP forwarding setting restored: %s' % (cmd)
                self.logger.notice(self.module_name, msg)

        return 1
