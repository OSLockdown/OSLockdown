#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger

import sb_utils.errors.codes

import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.solaris

class DisableApmd:

    def __init__(self):
        self.module_name = 'DisableApmd'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

        #
        # Identify the service and package name here:
        #
        self.__svcname = 'svc:/system/power:default'
        self.__svcdesc = 'power management'
        self.__pkgname = 'SUNWpmu'

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))


        results = sb_utils.os.software.is_installed(pkgname=self.__pkgname)

        if results == None:
            msg = "Unable to determine if %s installed." % self.__pkgname
            self.logger.error(self.module_name, 'Scan Error: ' + msg)

        if results == False:
            msg = "%s (%s) is not installed on the system" % \
                (self.__svcdesc, self.__pkgname)
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        results = sb_utils.os.service.is_enabled(svcname=self.__svcname)
        if results == True:
            msg = "svcprop reports %s is on" % self.__svcdesc
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = "module is not applicable for this system"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        action_record = ''
        results = sb_utils.os.service.is_enabled(svcname=self.__svcname)
        if results == None:
            msg = "Unable to determine status of the '%s' service" % self.__svcname
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if results == False:
            action_record = 'off'
        else:
            action_record = 'on'
        
        results = sb_utils.os.service.disable(svcname=self.__svcname)
        if results != True:
            msg = 'Failed to disable %s' % self.__svcname
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = '%s (%s) disabled' % (self.__svcdesc, self.__svcname)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))


        results = sb_utils.os.software.is_installed(pkgname=self.__pkgname)
        if results != True:
            msg = "%s is not installed on the system" % self.__svcname
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
            results = sb_utils.os.service.enable(svcname = self.__svcname)

        if change_record == 'off':
            results = sb_utils.os.service.disable(svcname = self.__svcname)

        if results != True:
            msg = "Unable to set %s (%s) service to '%s' " % (self.__svcdesc, self.__svcname, change_record)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "%s (%s) service set to '%s' " % (self.__svcdesc, self.__svcname, change_record)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1

