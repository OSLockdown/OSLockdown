#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable the Finger Service Daemon
#
# This is an xinetd-based service. Solaris has a separate module
# which shuts down the service via the SMF.
#
##############################################################################

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

import sb_utils.os.software
import sb_utils.os.xinetd


class DisableFinger:

    def __init__(self):
        self.module_name = "DisableFinger"
  
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []

        results =  sb_utils.os.software.is_installed(pkgname='finger-server')
        if results != True:
            msg = "'finger-server' package is not installed."
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "'finger-server' package is installed."
            messages['messages'].append(msg)
            self.logger.info(self.module_name, msg)

        results =  sb_utils.os.xinetd.is_enabled(svcname='finger')
        if results == None:
            msg = "Unable to determine status of the 'finger' service"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if results == True:
            msg = "'finger' service is enabled."
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, messages

        msg = "'finger' service is disabled"
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, 'Scan Passed: ' + msg)
        return True, msg, messages

    ##########################################################################
    def apply(self, option=None):

        try:
            (result, reason, messages) = self.scan()
            if result == True:
                return False, reason, messages

        except tcs_utils.ScanNotApplicable, err:
            msg = 'Not applicable for this system'
            self.logger.info(self.module_name, msg)
            return False, "Not applicable", {'messages': [str(err)]}

        messages = {}
        messages['messages'] = []
        results =  sb_utils.os.xinetd.disable(svcname='finger')
        if results != True:
            msg = "Unable to disable the 'finger' service"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "'finger' service is now configured to not start during "\
              "next system boot"
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        # We return "enabled" as the change record to indicate what its status
        # was before OS Lockdown
        return True, 'enabled', messages

    ##########################################################################
    def undo(self, change_record=None):

        try:
            (result, reason, messages) = self.scan()
            if result == False:
                return False, reason, messages

        except tcs_utils.ScanNotApplicable, err:
            msg = 'Not applicable for this system'
            self.logger.info(self.module_name, msg)
            return False, "Not applicable", {'messages': [str(err)]}

        if not change_record or change_record != 'enabled':
            msg = 'Unable to undo without valid change record'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, msg, {'messages': ["Error: %s" % msg]}
            
        results =  sb_utils.os.xinetd.enable(svcname='finger')
        if results != True:
            msg = "Unable to enable the 'finger' service"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "'finger' service enabled"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, {'messages': ["'finger' service has been re-enabled"]}

