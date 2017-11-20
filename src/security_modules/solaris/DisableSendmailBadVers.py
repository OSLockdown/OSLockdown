#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service

#
class DisableSendmailBadVers:
    """
    Disable Sendmail Service if running vulnerable version
    """

    def __init__(self):

        self.module_name = 'DisableSendmailBadVers'
        self.logger = TCSLogger.TCSLogger.getInstance()

        # This is the minimum version.. must be >= value below to pass
        self.__goodversion = "8.13.8"

        #
        # Identify the service and package name here:
        #
        self.__svcname = {'SUNWsndmr': 'svc:/network/smtp:sendmail'} 
        self.__pkgname = ['SUNWsndmr']
        self.__svcdesc = 'Sendmail service'

    ##########################################################################
    def __isbadversion(self, pkg=None):

        if pkg == None:
            return None

        sendmail_version = sb_utils.os.software.version(pkgname=pkg)

        if sendmail_version == None:
            return None

        installed_ver = sendmail_version[0].split('.')
        required_ver  = self.__goodversion.split('.')

        msg = 'Found %s version %s' % (pkg, ''.join(sendmail_version))

        self.logger.debug(self.module_name, msg)
        badvers = False

        if int(installed_ver[0]) > int(required_ver[0]):
            return False
        else:
            if int(installed_ver[1]) < int(required_ver[1]):
                badvers = True
            else:
                if int(installed_ver[2]) < int(required_ver[2]):
                    badvers = True

        return badvers

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        foundit = False
        for sendmail in self.__pkgname:
            results = sb_utils.os.software.is_installed(pkgname=sendmail)

            if results == None:
                msg = "Unable to determine if %s installed." % sendmail
                self.logger.error(self.module_name, 'Scan Error: ' + msg)

            if results == False:
                msg = "%s (%s) is not installed on the system" % \
                    (self.__svcdesc, sendmail)
                self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
                foundit = True
                continue

            msg = '%s is installed' % sendmail
            self.logger.info(self.module_name, 'Scan: ' + msg)

            # Is package a good version?
            check = self.__isbadversion(pkg=sendmail)
            if check == False:
                continue

            results = sb_utils.os.service.is_enabled(svcname=self.__svcname[sendmail])
            if results == True:
                msg = "svcprop reports %s is on" % self.__svcdesc
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        action_record = []
        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = "module is not applicable for this system"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        
        for sendmail in self.__pkgname:
    
            results = sb_utils.os.software.is_installed(pkgname=sendmail)
            if results == False or results == None:
                continue

            check = self.__isbadversion(pkg=sendmail)
            if check == False:
                continue

            results = sb_utils.os.service.disable(svcname=self.__svcname[sendmail])

            if results != True:
                msg = 'Failed to disable %s' % self.__svcname[sendmail]
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record.append(self.__svcname[sendmail])
                msg = '%s (%s) disabled' % (self.__svcdesc, self.__svcname[sendmail])
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, action_record

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
       
        results = sb_utils.os.service.enable(svcname=self.__svcname)
        if results != True:
            msg = 'Failed to enable %s' % self.__svcname
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = '%s enabled' % (self.__svcdesc)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
