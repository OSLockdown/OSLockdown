#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.config

class CreateLoginFTPBanner:

    def __init__(self):
        self.module_name = "CreateLoginFTPBanner"
        if sb_utils.os.info.is_LikeSUSE() == True:
            self.__config_file = '/etc/vsftpd.conf'
        else:
            self.__config_file = '/etc/vsftpd/vsftpd.conf'

        self.logger = TCSLogger.TCSLogger.getInstance() 



    ##########################################################################
    def scan(self, optionDict=None):

        if optionDict == None or not 'ftpLoginBanner' in optionDict:
            msg = 'Missing option: No warning banner provided'                                                                       
            self.logger.error(self.module_name, 'Scan Error: ' + msg)                                                      
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))   
        option = optionDict['ftpLoginBanner']
        replacePat = re.compile('\n')
        option = replacePat.sub(' ', option)
        option = option.strip("\"")

        results =  sb_utils.os.software.is_installed(pkgname='vsftpd')
        if results != True:
            msg = "'vsftpd' package is not installed."
            self.logger.info(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        msg = "Checking %s for 'ftpd_banner' setting" % self.__config_file
        self.logger.debug(self.module_name, msg)

        paramlist = sb_utils.os.config.get_list(configfile=self.__config_file,
                                                delim='=') 
        if paramlist == None:
            msg = "Unable to determine settings from %s" % self.__config_file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if not paramlist.has_key('ftpd_banner'):
            msg = "ftpd_banner parameter not set in %s " % self.__config_file
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            del paramlist
            return 'Fail', 'ftpd_banner parameter not set'

        if str(paramlist['ftpd_banner']).strip("\"") != str(option):
            msg = "ftpd_banner parameter not set to '%s'" % str(option)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            del paramlist
            return 'Fail', msg

        del paramlist
        return 'Pass', ''

    ##########################################################################
    def apply(self, optionDict=None):
        """Apply changes."""

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''

        option = optionDict['ftpLoginBanner']
        
        replacePat = re.compile('\n')
        option = replacePat.sub(' ', option)
        option = option.strip("\"")

        results =  sb_utils.os.software.is_installed(pkgname='vsftpd')
        if results != True:
            msg = "'vsftpd' package is not installed."
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''

        msg = "Checking %s for 'ftpd_banner' setting" % self.__config_file
        self.logger.debug(self.module_name, msg)

        paramlist = sb_utils.os.config.get_list(configfile=self.__config_file,
                                                delim='=') 

        if paramlist == None:
            msg = "Unable to determine settings from %s" % self.__config_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        action_record = ''
        if paramlist.has_key('ftpd_banner'):
            action_record = str(paramlist['ftpd_banner'])
            if str(paramlist['ftpd_banner']) == str(option):
                msg = "ftpd_banner parameter correctly set" 
                self.logger.notice(self.module_name, msg)
                return 0, ''
        else:
            action_record = '{}'
        results = sb_utils.os.config.setparam(configfile=self.__config_file, 
                param='ftpd_banner', value="\"%s\"" % str(option), delim='=')

        if results == False:
            msg = "Unable to set 'ftpd_banner' in %s" % (self.__config_file)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        results =  sb_utils.os.software.is_installed(pkgname='vsftpd')
        if results != True:
            msg = "'vsftpd' package is not installed."
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            return 0

        if change_record == None:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record != '{}':
            results = sb_utils.os.config.setparam(configfile=self.__config_file, 
                param='ftpd_banner', value=str(change_record), delim='=')
        else:
            results = sb_utils.os.config.unsetparam(configfile=self.__config_file, 
                param='ftpd_banner', delim='=')

        if results == False:
            msg = "Unable to set 'ftpd_banner' in %s" % (self.__config_file)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            if change_record == '':
                msg = "'ftpd_banner' removed from %s" % (self.__config_file)
            else:
                msg = "'ftpd_banner' set to '%s' in %s" % (change_record, self.__config_file)
            self.logger.notice(self.module_name, "Undo Performed: " + msg)

        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
