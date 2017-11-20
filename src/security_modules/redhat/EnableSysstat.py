#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Enable System Accounting
#
# Notes:
#     The main difference between Red Hat and SUSE is that the service
#     name is slightly different in SUSE 11. Solaris modules must be
#     different becuase we must make crone ntries for Solaris systems.
#
#
##############################################################################

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger

import sb_utils.os.software
import sb_utils.os.service

class EnableSysstat:

    def __init__(self):

        self.module_name = 'EnableSysstat'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        self._pkgname = "sysstat"
        self._svcname = "sysstat"
        self._svcdesc = "System Accounting"


    ##########################################################################
    def scan(self, option=None):

        results_flag = True
        messages = {}
        messages['messages'] = []
        msg_string = ''

        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed on the system" % self._pkgname
            self.logger.warning(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "'%s' package is installed." % (self._pkgname)
            messages['messages'].append(msg)
            self.logger.info(self.module_name, msg)

        results = sb_utils.os.service.is_enabled(svcname=self._svcname)
        if results == False:
            msg = "Fail: '%s' service is disabled" % (self._svcname)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            results_flag = False 
            msg_string = msg
        else:
            msg = "'%s' service is enabled" % (self._svcname)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, 'Scan Passed: ' + msg)
            results_flag = True 

        return results_flag, msg_string, messages


    ##########################################################################
    def apply(self, option=None):

        update_flag = True
        messages = {}
        messages['messages'] = []

        action_record = ''
        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed" % self._pkgname
            self.logger.warning(self.module_name, 'Not Applicable: ' + msg)
            messages['messages'].append(msg)
            msg = "Manual: You must install the '%s' package" % self._pkgname
            messages['messages'].append(msg)
            return False, 'Required package is not installed', messages
        else:
            msg = "'%s' package is installed" % self._pkgname
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)

        results = sb_utils.os.service.is_enabled(svcname=self._svcname)
        if results == False:
            action_record = 'off'

        else:
            msg = "'%s' is already enabled" % self._svcname
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, msg)
            return False, 'empty', messages
            
        # Enable the service
        results = sb_utils.os.service.enable(svcname=self._svcname)
        if results != True:
            msg = 'Fail: Unable to enable: %s' % self._svcname
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            messages['messages'].append(msg)
            update_flag = False
        else:
            msg = '%s service is enabled.' % self._svcname
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            messages['messages'].append(msg)
            update_flag = True
            msg = "Manual: Either reboot or manually start by "\
                      "executing: service %s start" % self._svcname
            messages['messages'].append(msg)
            

        return update_flag, action_record, messages


    ##########################################################################
    def undo(self, change_record=None):

        messages = {}
        messages['messages'] = []

        results = sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed" % self._pkgname
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, msg, messages
        else:
            msg = "'%s' package is installed" % self._pkgname
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)

        if not change_record:
            msg = "No change record provided"
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            messages['messages'].append(msg)
            return False, msg, messages

        if change_record not in ['off', 'on']:
            msg = "Error: Malformed change record"
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            messages['messages'].append(msg)
            return False, msg, messages
             
        if change_record == 'on':
            results = sb_utils.os.service.enable(svcname = self._svcname )
        else:
            results = sb_utils.os.service.disable(svcname = self._svcname )

        msg = ''
        if results != True:
            msg = "Unable to set %s (%s) service to '%s' " % (self._svcdesc, self._svcname)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            msg = "Set '%s' service to %s" % (self._svcname, change_record)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

            
        return True, msg, messages


if __name__ == '__main__':
    Test = EnableSysstat()
    #print Test.scan()
    print Test.apply()
    print Test.undo('off')
