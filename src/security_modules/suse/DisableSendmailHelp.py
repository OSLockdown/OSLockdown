#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.config


class DisableSendmailHelp:

    def __init__(self):
        self.module_name = "DisableSendmailHelp"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__file = '/etc/sendmail.cf'


    ##########################################################################
    def scan(self, option=None):
    
        messages = {'messages': []}
        results = sb_utils.os.software.is_installed(pkgname='sendmail')
        if results == False:
            msg = "'sendmail' package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "'sendmail' package is installed"
            messages['messages'].append(msg)
            self.logger.info(self.module_name, msg)
            
        if not os.path.isfile(self.__file):
            msg = "sendmail is installed but %s is missing" % self.__file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        else:
            msg = "Examining %s" % (self.__file)
            messages['messages'].append(msg)
            self.logger.info(self.module_name, msg)

        paramlist = sb_utils.os.config.get_list(configfile='/etc/sendmail.cf', delim='=') 
        if paramlist == None:
            msg = 'Unable to determine Sendmail Help is enabled'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if paramlist.has_key('O HelpFile'):
            msg = "Sendmail Help is enabled; found 'O HelpFile' configured "\
                     "in %s" % (self.__file)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, messages

        msg = "'O HelpFile' not set"
        return True, msg, messages
        

    ##########################################################################
    def apply(self, option=None):

        (result, reason, messages) = self.scan()
        if result == True:
            return False, reason, messages

        messages = {'messages': []}
        paramlist = sb_utils.os.config.get_list(configfile='/etc/sendmail.cf', delim='=') 
        if paramlist.has_key('O HelpFile'):
            action_record = paramlist['O HelpFile']

        msg = "Removing 'O HelpFile' from %s" % (self.__file)
        messages['messages'].append(msg)
        results = sb_utils.os.config.unsetparam(param='O HelpFile', 
                                             configfile='/etc/sendmail.cf')

        if results == False:
            msg = "Unable to remove the 'O HelpFile' option from /etc/sendmail.cf"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return True, action_record, messages


    ##########################################################################
    def undo(self, change_record=None):

        messages = {'messages': []}
        try:
            (result, reason, messages) = self.scan()
            if result == False:
                return False, reason, messages
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, str(err), {}

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        results = sb_utils.os.config.setparam(configfile='/etc/sendmail.cf',
                        param='O HelpFile', value=str(change_record), delim='=')

        if results == False:
            msg = "Unable to reset 'O HelpFile in /etc/sendmail.cf'"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        
        msg = "Reset 'O HelpFile in /etc/sendmail.cf'"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, messages

