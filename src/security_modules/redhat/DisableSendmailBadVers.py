#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

# 
# Disable Sendmail Service if running a vulnerable version
#

import sys

from distutils import version


sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service

class DisableSendmailBadVers:

    def __init__(self):

        self.module_name = 'DisableSendmailBadVers'
        self.logger = TCSLogger.TCSLogger.getInstance()

        # This is the minimum version.. must be >= value below to pass
        self.__badversion = "8.13.8"


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        results =  sb_utils.os.software.is_installed(pkgname='sendmail')
        if results != True:
            msg = "'sendmail' package is not installed."
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
 
        (swVer, swRel) = sb_utils.os.software.version(pkgname='sendmail')

        a = version.LooseVersion("None:%s" % swVer)
        b = version.LooseVersion("None:%s" % self.__badversion)

        if a < b:          
            msg = "Vulnerable version of sendmail found: %s (expected >= %s)" % \
                    (swVer, self.__badversion)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        else:          
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

        results = sb_utils.os.service.is_enabled(svcname='sendmail')
        if results == None:
            msg = "Unable to determine status of the 'sendmail' service"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if results == False:
            action_record = 'off'
        else:
            action_record = 'on'

        results = sb_utils.os.service.disable(svcname = 'sendmail')
        if results != True:
            msg = 'Unable to disable: sendmail'
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return 0, msg

        msg = 'sendmail service disabled.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record

    ##########################################################################
    def undo(self, change_record=None):

        results = sb_utils.os.software.is_installed(pkgname='sendmail')
        if results != True:
            msg = "sendmail is not installed on the system"
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0
            
        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        if change_record not in ['off', 'on']:
            msg = "Skipping Undo: Uknown change record in state file: '%s'" % change_record
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0
             
        if change_record == 'on':
            results = sb_utils.os.service.enable(svcname = 'sendmail')

        if change_record == 'off':
            results = sb_utils.os.service.disable(svcname = 'sendmail')

        if results != True:
            msg = "Unable to set sendmail service to '%s' " % change_record
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        msg = "sendmail service set to '%s' " % change_record
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1

