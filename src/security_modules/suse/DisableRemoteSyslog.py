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
#

import sys
import os

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.config
import tcs_utils

class DisableRemoteSyslog:

    def __init__(self):
        self.module_name = "DisableRemoteSyslog"
        self.__sysconfig = '/etc/sysconfig/syslog'
        self.logger = TCSLogger.TCSLogger.getInstance()
        
        if not os.path.exists(self.__sysconfig):
            msg = "'%s' does not exist!" % self.__sysconfig
            self.logger.warning(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        messages = {'messages': [] }

        msg = "Checking %s to make sure 'SYSLOGD_PARAMS' does not have '-r'" % self.__sysconfig
        messages['messages'].append(msg)
        self.logger.debug(self.module_name, msg)

        paramlist = sb_utils.os.config.get_list(self.__sysconfig, '=')
        if not paramlist.has_key('SYSLOGD_PARAMS'):
            msg = "'SYSLOGD_PARAMS' is not set in %s"  % self.__sysconfig
            messages['messages'].append("Okay: %s" % msg)
            self.logger.notice(self.module_name, "Scan Passed: %s" % msg)
            return True, '', messages
            
        syslogd_params = paramlist['SYSLOGD_PARAMS'].strip('"')
        if syslogd_params == '':
            msg = "'SYSLOGD_PARAMS' is set to '' in %s"  % self.__sysconfig
            messages['messages'].append("Okay: %s" % msg)
            self.logger.notice(self.module_name, "Scan Passed: %s" % msg)
            return True, '', messages

        syslogd_params = syslogd_params.split()
        if '-r' in syslogd_params:
            msg = "'SYSLOGD_PARAMS' contains '-r' in %s" % self.__sysconfig
            messages['messages'].append("Fail: %s" % msg)
            self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
            return False, '', messages

        return True, '', messages


    ##########################################################################
    def apply(self, option=None):

        action_record = ''
        messages = {'messages': [] }

        msg = "Checking %s to make sure 'SYSLOGD_PARAMS' does not have '-r'" % self.__sysconfig
        messages['messages'].append(msg)
        self.logger.debug(self.module_name, msg)

        paramlist = sb_utils.os.config.get_list(self.__sysconfig, '=')
        if not paramlist.has_key('SYSLOGD_PARAMS'):
            msg = "'SYSLOGD_PARAMS' is not set in %s"  % self.__sysconfig
            messages['messages'].append("Okay: %s" % msg)
            self.logger.notice(self.module_name, msg)
            return False, '', messages
            
        syslogd_params = paramlist['SYSLOGD_PARAMS'].strip('"')
        if syslogd_params == '':
            msg = "'SYSLOGD_PARAMS' is set to '' in %s"  % self.__sysconfig
            messages['messages'].append("Okay: %s" % msg)
            self.logger.notice(self.module_name, msg)
            return False, '', messages

        
        action_record = syslogd_params
        if not '-r' in syslogd_params.split():
            msg = "'SYSLOGD_PARAMS' does not contain '-r' in %s" % self.__sysconfig
            messages['messages'].append("Okay: %s" % msg)
            self.logger.notice(self.module_name, msg)
            return False, '', messages

        syslogd_params = "\"%s\"" % syslogd_params.replace('-r', '').strip()

        # A change is required
        results = sb_utils.os.config.setparam(configfile=self.__sysconfig, param='SYSLOGD_PARAMS', value=syslogd_params, delim='=')
        msg = "Removed '-r' from 'SYSLOGD_PARAMS' in %s" % self.__sysconfig
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, "Apply Performed: %s" % msg)
        msg = 'Remote syslog disabled.'
        return True, action_record, messages


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        messages = {'messages': []}
        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {}

        change_record = "\"%s\"" % change_record
        results = sb_utils.os.config.setparam(configfile=self.__sysconfig, param='SYSLOGD_PARAMS', value=change_record, delim='=')
        if results == False:
            msg = "Unable to restore SYSLOGD_PARAMS to %s in %s" % (change_record, self.__sysconfig)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            messages['messages'].append(msg)
            return False, '', messages

        msg = "Reset SYSLOGD_PARAMS to %s in %s" % (change_record, self.__sysconfig)
        self.logger.info(self.module_name, 'Undo Performed: ' + msg)
        messages['messages'].append(msg)
        msg = 'Syslog configuration restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, messages

