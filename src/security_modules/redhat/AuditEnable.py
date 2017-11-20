#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Enable the Audit System
#

import sys
import statvfs
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service

class AuditEnable:
    def __init__(self):
        self.module_name = "AuditEnable"
        self.__target_file = '/etc/audit/auditd.conf'
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, option=None):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """
        Determine if the audit service is installed on the system and enabled.
        If the audit is not installed tcs_utils.ScanNotApplicable exception is
        raised.
        """
        if option != None:
            option = None

        results =  sb_utils.os.software.is_installed(pkgname='audit')
        if results != True:
            msg = "audit is not installed on the system"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        ## *ALSO* verify that the /sbin/auditd command exists - early RH4 doesn't have audid as a daemon
        if not os.path.exists('/sbin/auditd'):
            msg = "Required command '/sbin/auditd' does not exist!"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        ## *ALSO* verify that the /sbin/auditd command exists - early RH4 doesn't have audid as a daemon
        if not os.path.exists('/etc/init.d/auditd'):
            msg = "Required service '/etc/init.d/auditd' does not exist!  Is service installed?"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        results = sb_utils.os.service.is_enabled(svcname='auditd')
        if results == None:
            msg = "Unable to determine status of the 'auditd' service"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if results == False:
            msg = "'auditd' service is disabled."
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """Enable Auditing"""

        if option != None:
            option = None

        action_record = ''

        results = sb_utils.os.service.is_enabled(svcname='auditd')
        if results == None:
            msg = "Unable to determine status of the 'auditd' service"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if results == False:
            action_record = 'off'
        else:
            action_record = 'on'

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, reason
        except tcs_utils.ScanNotApplicable, err:
            self.logger.error(self.module_name,'Apply Error: '+ (str(err)))
            return 0, ''
 
        try:
            if not os.path.isfile(self.__target_file):
                in_obj = open('/etc/auditd.conf', 'r')
            else:
                in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = 'Unable to open %s: %s ' % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)

        lines = []
        try:
            lines = in_obj.readlines()
            in_obj.close()
        except Exception:
            pass

        for line in lines:
            if line.startswith('log_file'):
                line = line.strip('\n')
                file_loc = line.split('=')[1]
                file_loc = file_loc.lstrip(' ')
                if not os.path.isfile(file_loc):
                    try:
                        log_file = open(file_loc, 'w')
                        log_file.close()
                    except IOError:
                        msg = 'Unable to create %s' % file_loc
                myst = os.statvfs(file_loc)
                space_leftKB = (myst[statvfs.F_BAVAIL]*myst[statvfs.F_BSIZE])/1024
                if space_leftKB < 32000:
                    msg = "There is less than 32MB of space for %s " % file_loc
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        
        results = sb_utils.os.service.enable(svcname = 'auditd')
        if results != True:
            msg = 'Unable to enable: auditd'
            self.logger.error(self.module_name, 'Apply Failed: ' + msg)
            return 0, ''

        msg = 'auditd service enabled'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        results = sb_utils.os.software.is_installed(pkgname='audit')
        if results != True:
            msg = "audit is not installed on the system"
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0
            
        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        if change_record not in ['off', 'on']:
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0
             
        if change_record == 'on':
            results = sb_utils.os.service.enable(svcname = 'auditd')

        if change_record == 'off':
            results = sb_utils.os.service.disable(svcname = 'auditd')

        if results != True:
            msg = "Unable to set auditd service to '%s' " % change_record
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        msg = "auditd service set to '%s' " % change_record
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1
