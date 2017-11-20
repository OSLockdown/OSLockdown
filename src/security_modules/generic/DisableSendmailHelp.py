#!/usr/bin/env python

##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
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
        self.__file = '/etc/mail/sendmail.cf'

    ##########################################################################
    def validate_input(self, option=None):
        """Validate Input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        if sb_utils.os.info.is_solaris() == True:
            results = sb_utils.os.software.is_installed(pkgname='SUNWsndmr')
        else:
            results = sb_utils.os.software.is_installed(pkgname='sendmail')

        if results == False:
            msg = "sendmail does not appear to be installed on the system"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if not os.path.isfile(self.__file):
            msg = "sendmail is installed but %s is missing" % self.__file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        paramlist = sb_utils.os.config.get_list(configfile='/etc/mail/sendmail.cf', delim='=') 
        if paramlist == None:
            msg = 'Unable to determine Sendmail Help is enabled'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if paramlist.has_key('O HelpFile'):
            reason = "Sendmail Help is enabled; found 'O HelpFile' configured "\
                     "in %s" % (self.__file)
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)

            return 'Fail', reason


        return 'Pass', ''
        

    ##########################################################################
    def apply(self, option=None):
        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        paramlist = sb_utils.os.config.get_list(configfile='/etc/mail/sendmail.cf', delim='=') 
        if paramlist.has_key('O HelpFile'):
            action_record = paramlist['O HelpFile']

        results = sb_utils.os.config.unsetparam(param='O HelpFile', 
                                             configfile='/etc/mail/sendmail.cf')

        if results == False:
            msg = "Unable to remove the 'O HelpFile' option from /etc/mail/sendmail.cf"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0, ''

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        results = sb_utils.os.config.setparam(configfile='/etc/mail/sendmail.cf',
                        param='O HelpFile', value=str(change_record), delim='=')

        if results == False:
            msg = "Unable to reset 'O HelpFile in /etc/mail/sendmail.cf'"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        
        msg = "Reset 'O HelpFile in /etc/mail/sendmail.cf'"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

