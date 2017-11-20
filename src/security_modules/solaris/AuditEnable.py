#!/usr/bin/env python
#
# Copyright (c) 2008 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
import sys
import os
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.solaris

class AuditEnable:
    """
    Enable Audit System
    """
    ##########################################################################
    def __init__(self, hmac_msg=None):
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
        if option != None:
            option = None

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        try:
            in_obj = open('/etc/system')
        except IOError, err:
            msg = 'Unable to read /etc/system (%s)' % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        foundit = False
        audit_pattern = re.compile('^set c2audit:audit_load(.*)=(.*)1')
        for line in in_obj.readlines():
            if audit_pattern.search(line):
                foundit = True
                break

        in_obj.close()

        if foundit == False:
            msg = "/etc/system does not have the 'c2audit:audit_load' entry"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        msg = "/etc/system has a 'c2audit:audit_load' entry"
        return 'Pass', msg 


    ##########################################################################
    def apply(self, option=None):
        if option != None:
            option = None


        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, reason
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            return 0, err
 
        if not os.path.isfile('/etc/security/bsmconv') or \
                                       not os.path.isfile('/usr/bin/echo'):  
            msg = "Failed to enable auditing (/etc/security/bsmconv)"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        cmd = "/usr/bin/echo y | /etc/security/bsmconv"
        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] != 0:
            msg = "Failed to enable auditing: %s" % output[2]
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Auditing enabled (/etc/security/bsmconv executed)'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, 'enabled'


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        if not change_record or change_record != 'enabled':
            msg = "unable to undo without valid change record"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0
            
        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system.'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        if not os.path.isfile('/etc/security/bsmunconv') or \
                                     not os.path.isfile('/usr/bin/printf'):
            msg = "Failed to disable auditing (/etc/security/bsmunconv)"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        cmd = """/usr/bin/printf "y\ny\n" | /etc/security/bsmunconv"""
        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] != 0:
            msg = "Failed to disable auditing: %s" % output[2]
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Auditing disabled (/etc/security/bsmunconv executed)'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1, ''

