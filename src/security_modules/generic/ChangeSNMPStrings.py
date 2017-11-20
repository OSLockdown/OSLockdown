#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import re

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info


class ChangeSNMPStrings:
    """
    Change SNMP Default 'public' string
    """

    def __init__(self):

        self.module_name = 'ChangeSNMPStrings'

        if sb_utils.os.info.is_solaris() == True:
            self.__target_file = '/etc/snmp/conf/snmpd.conf'
        else:
            self.__target_file = '/etc/snmp/snmpd.conf'

        self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.info.is_solaris() == True:
            self.__pkgname = "SUNWsacom"
            self.__svcname = 'svc:/application/management/snmpdx:default'
        else:
            self.__pkgname = "net-snmp"
            self.__svcname = 'snmpd'

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []

        results = sb_utils.os.software.is_installed(pkgname=self.__pkgname)

        if results == False:
            msg = "%s package is not installed on the system" % self.__pkgname
            self.logger.info(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % 
                                              (self.module_name, msg))

        if not os.path.isfile(self.__target_file):
            msg = "%s package is installed but %s is missing" % self.__target_file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__target_file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to read %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % 
                                              (self.module_name, msg))
        msg = "Checking %s for regular expression: " \
             "^(com2sec|system-group-read-community|read-community|rocommunity)+" % self.__target_file
        self.logger.info(self.module_name, msg)

        foundit = False
        regexp = re.compile('^(com2sec|system-group-read-community|read-community|rocommunity)+')
        for line_nr, line in enumerate(in_obj.xreadlines()):
            if regexp.search(line):
                fields = line.strip('\n').split()
                if 'public' in fields:
                    msg = "Found 'public' set on line %d of "\
                        "%s: %s" % (line_nr, self.__target_file, line.lstrip())
                    messages['messages'].append(msg)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    foundit = True

        in_obj.close()
        retval = True
        if foundit == True:
            if not sb_utils.os.service.is_enabled(svcname=self.__svcname):
                msg = "%s package is installed on the system with 'public' community strings, but the service is not enabled" % self.__pkgname
                messages['messages'].append(msg)
                self.logger.info(self.module_name, 'Scan Passed: ' + msg)
                retval = True
            else:
                msg = "If you apply this module it will only disable the "\
                      "SNMP service. Manual action by the System Administrator is required " \
                      "to change the 'public' community string.  While OS Lockdown will pass this module " \
                      "after it has been applied, other scanning tools may still complain about the " \
                      "SNMP configuration until these string are altered." 
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                retval = False
        else:
            msg = "Did not find 'public' community strings in %s" % (self.__target_file)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            retval = True
        return retval, '', messages


    ##########################################################################
    def apply(self, option=None):

        messages = {}
        messages['messages'] = []
        try:
            result, reason, messages = self.scan()
            if result == True:
                return False, '', messages

        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            messages['messages'].append(msg)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return False, '', messages

        messages['messages'] = []    # reset the message field, we know we've found a problem
        results = sb_utils.os.service.disable(svcname=self.__svcname)

        if results != True:
            msg = 'Failed to disable snmpd'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'snmp service disabled'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        msg = "The %s service has been disabled.  Manual action by the System Administrator is required " \
              "to change the 'public' community string.  While OS Lockdown will pass this module " \
              "since the %s service has been disabled, other scanning tools may still complain about the " \
              "SNMP configuration until these string are altered." % (self.__svcname, self.__svcname)
        messages['messages'].append(msg)
        return True, 'disabled', messages


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        messages = {}
        messages['messages'] = []
        try:
            result, reason, messages = self.scan()
            if result == False:
                return result, reason, messages

        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            messages['messages'].append(msg)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, msg, messages

        if not change_record or change_record != 'disabled':
            msg = 'Unable to undo without valid change record'
            messages['messages'].append(msg)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, msg, messages
            
        results = sb_utils.os.service.enable(svcname=self.__svcname)

        if results != True:
            msg = 'Failed to enable snmp'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'snmp service enabled'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', messages
