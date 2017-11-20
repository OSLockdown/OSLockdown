#!/usr/bin/env python

#  Disable Inetd (Xinetd)
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service

class DisableInetd:
    """
    Disable the internet super-server daemon
    """

    def __init__(self):

        self.module_name = 'DisableInetd'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

        self._pkgname = "xinetd"
        self._svcname = "xinetd"
        self._svcdesc = "xinetd"

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        retVal = True # assume pass
        messages = {'messages':[]} 
        msg = ''
         
        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed on the system" % self._pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        results = sb_utils.os.service.is_enabled(svcname=self._svcname)
        if results == True:
            msg = '%s service is on' % self._svcdesc
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            messages['messages'].append(msg)
            retVal = False

        return retVal, msg, messages
        

    ##########################################################################
    def apply(self, option=None):


        result, reason, messages = self.scan()
        if result == True:
            return False, reason, messages
            
        messages={'messages':[]}
        
        retVal = True
        action_record = ''
        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed on the system" % self._pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            messages['messages'].append(msg)
            return False, msg, messages

        results = sb_utils.os.service.is_enabled(svcname=self._svcname)
        if results == None:
            msg = "Unable to determine status of the '%s' service" % self._svcname
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if results == False:
            action_record = 'off'
        else:
            action_record = 'on'

        results = sb_utils.os.service.disable(svcname=self._svcname)
        if results != True:
            msg = 'Unable to disable: %s' % self._svcname
            self.logger.error(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = '%s service is disabled.' % self._svcname
        messages['messages'].append(msg)
        
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, action_record, messages
        


    ##########################################################################
    def undo(self, change_record=None):
        """
        Undo the previous action.
        """

        results = sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "%s is not installed on the system" % self._svcname
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {'messages':[msg]}
            
        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {'messages':[msg]}

        if change_record not in ['off', 'on']:
            msg = "Skipping Undo: Uknown change record in state file: '%s'" % change_record
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {'messages':[msg]}
             
        if change_record == 'on':
            results = sb_utils.os.service.enable(svcname = self._svcname )

        if change_record == 'off':
            results = sb_utils.os.service.disable(svcname = self._svcname )

        if results != True:
            msg = "Unable to set %s (%s) service to '%s' " % (self._svcdesc, self._svcname)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        msg = "%s (%s) service set to '%s' " % (self._svcdesc, self._svcname, change_record)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return True, '', ''
