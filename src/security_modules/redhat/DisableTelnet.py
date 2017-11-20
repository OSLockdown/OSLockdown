#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable Telnet Service

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger

import sb_utils.os.software
import sb_utils.os.xinetd

class DisableTelnet:

    ##########################################################################
    def __init__(self):

        self.module_name = 'DisableTelnet'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        results =  sb_utils.os.software.is_installed(pkgname='telnet-server')
        if results != True:
            msg = "'telnet-server' package is not installed."
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        results =  sb_utils.os.xinetd.is_enabled(svcname='telnet')
        if results == None:
            msg = "Unable to determine status of the 'telnet' service"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if results == True:
            msg = "'telnet' service is enabled."
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        results =  sb_utils.os.xinetd.disable(svcname='telnet')
        if results != True:
            msg = "Unable to disable the 'telnet' service"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "'telnet' service disabled"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, 'disabled'

    ##########################################################################
    def undo(self, change_record=None):

        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        if not change_record or change_record != 'disabled':
            msg = 'unable to undo without valid change record'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0
        
        results =  sb_utils.os.xinetd.enable(svcname='telnet')
        if results != True:
            msg = "Unable to enable the 'telnet' service"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "'telnet' service enabled"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

