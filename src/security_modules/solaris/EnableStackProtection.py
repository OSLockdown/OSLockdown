#!/usr/bin/env python
#
# Copyright (c) 2009 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
import sys
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.solaris
import sb_utils.os.config

class EnableStackProtection:

    def __init__(self):
        self.module_name = "EnableStackProtection"
        self.__target_file = '/etc/system'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
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

       
        machinetype = sb_utils.os.info.is_x86()
        if machinetype == True:
            msg = "module not applicable to Solaris x86"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)

        try:
            in_obj = open('/etc/system')
        except IOError, err:
            msg = 'Unable to read /etc/system (%s)' % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        foundit = 0

        patterns = ['^set noexec_user_stack(\s*)=(\s*)1', 
                    '^set noexec_user_stack_log(\s*)=(\s*)1' ]

        for search_pattern in patterns:
            msg = "Looking for %s in /etc/system" % search_pattern
            self.logger.info(self.module_name, msg)
            audit_pattern = re.compile(search_pattern)
            in_obj.seek(0)
            for line in in_obj.readlines():
                if audit_pattern.search(line):
                    foundit = foundit + 1

        in_obj.close()

        if foundit != 2:
            msg = "/etc/system does not have the noexec_user_stack entries"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        if option != None:
            option = None

        action_record = [] 

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

        for xparam in ['set noexec_user_stack', 'set noexec_user_stack_log']:
            results = sb_utils.os.config.setparam( \
                        configfile='/etc/system', \
                        param=xparam, value='1', delim='=')

            if results == False:
                msg = "Unable to set %s in /etc/system" % (xparam)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record.append(xparam + '=' + results + '\n')
                msg = '%s set to 1 in /etc/system' % (xparam)
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "module not applicable in non-global Solaris zones"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))


        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        failure_flag = False
        for xparam in change_record.split('\n'):
            if not xparam:
                continue

            if '=' not in xparam:
                msg = 'Malformed change record: %s' % (xparam)
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            param_key = xparam.split('=')[0]
            param_val = xparam.split('=')[1]

            if not param_val:
                results = sb_utils.os.config.unsetparam( param=param_key,
                             configfile=self.__target_file)
                msg = 'Removing %s from %s' % (param_key, self.__target_file)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            else:
                results = sb_utils.os.config.setparam( param=param_key,
                                                   delim='=',
                                                   value=param_val,
                                                   configfile=self.__target_file)

                msg = 'Resetting %s to %s from %s' % \
                       (param_key, param_val, self.__target_file)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            

            if results == False:
                msg = "Unable to restore settings in %s" % (self.__target_file)
                self.logger.error(self.module_name, 'Undo Failed: ' + msg)
                failure_flag = True

       
        if failure_flag == True:
            return 0
        else:
            return 1

