#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#  Disable Squid Cache Service

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service


class DisableSquid:
    """
    Disable the squid web caching proxy server.
    """

    def __init__(self):

        self.module_name = 'DisableSquid'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

        #
        # Identify the service and package name here:
        #
        self.__svcname = {'SUNWsquidr': 'squid', 
                          'CSKsquid':   'svc:/network/http:squid-csk' }

        self.__pkgname = ['SUNWsquidr', 'CSKsquid']
        self.__svcdesc = 'Squid Cache server'



    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        foundit = False
        for squid in self.__pkgname:
            results = sb_utils.os.software.is_installed(pkgname=squid)

            if results == None:
                msg = "Unable to determine if %s installed." % squid
                self.logger.error(self.module_name, 'Scan Error: ' + msg)

            if results == False:
                msg = "%s (%s) is not installed on the system" % \
                    (self.__svcdesc, squid)
                self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
                foundit = True
                continue

            msg = '%s is installed' % squid
            self.logger.info(self.module_name, 'Scan: ' + msg)
            results = sb_utils.os.service.is_enabled(svcname=self.__svcname[squid])
            if results == True:
                msg = "svcprop reports %s is on" % self.__svcdesc
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg


        if foundit == False:
            msg = "%s not installed on the system" % self.__svcdesc
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


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

        
        for squid in self.__pkgname:
    
            results = sb_utils.os.software.is_installed(pkgname=squid)
            if results == False or results == None:
                continue

            results = sb_utils.os.service.disable(svcname=self.__svcname[squid])

            if results != True:
                msg = 'Failed to disable %s' % self.__svcname[squid]
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record.append(self.__svcname[squid])
                msg = '%s (%s) disabled' % (self.__svcdesc, self.__svcname[squid])
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
       
        for squid in change_record:
            results = sb_utils.os.service.enable(svcname=squid)
            if results != True:
                msg = 'Failed to enable %s' % squid
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = '%s enabled' % (self.__svcdesc)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

