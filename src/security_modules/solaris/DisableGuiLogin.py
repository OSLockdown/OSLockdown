#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

import sb_utils.os.service
import sb_utils.os.software


class DisableGuiLogin:

    def __init__(self):
        self.module_name = "DisableGuiLogin"
        self.logger = TCSLogger.TCSLogger.getInstance()

        #
        # Identify the service and package name here:
        #
        self.__svcname = [ 'svc:/application/graphical-login/cde-login:default',
                           'svc:/application/gdm2-login:default' ]

        self.__svcdesc = 'Graphical (CDE and GDM2) login'


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        fail_flag = False
        for chksvc in self.__svcname:
            results = sb_utils.os.service.is_enabled(svcname=chksvc)
            if results == True:
                msg = "svcprop reports %s is on" % chksvc
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                fail_flag = True

        if fail_flag == True:
            return 'Fail', msg
      
        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        action_record = []

        for chksvc in self.__svcname:
            results = sb_utils.os.service.is_enabled(svcname=chksvc)
            if results == True:
                action_record.append("on|%s\n" % chksvc) 

                results = sb_utils.os.service.disable(svcname=chksvc)
                if results != True:
                    msg = 'Failed to disable %s' % chksvc
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    msg = '%s (%s) disabled' % (self.__svcdesc, chksvc)
                    self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        if action_record == []:
            return 0, ''
        else:
            return 1, ''.join(action_record) 

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if change_record == None:
            msg = 'No change record provided; unable to perform undo.'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        for chksvc in change_record.split('\n'):
            if chksvc == "":
                continue
            fields = chksvc.split('|')
            if len(fields) != 2:
                msg = "Malformed change record: \"%s\"" % chksvc
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                continue
            if fields[0] == 'on':
                results = sb_utils.os.service.enable(svcname=fields[1])
                if results != True:
                    msg = 'Failed to enable %s' % fields[1]
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    msg = '%s (%s) enabled' % (self.__svcdesc, fields[1])
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1
