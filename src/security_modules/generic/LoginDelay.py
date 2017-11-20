#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Solaris: set SLEEPTIME=4 in /etc/default/login
# Linux:   set FAIL_DELAY=4 in /etc/login.defs 
#

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.config

class LoginDelay:

    def __init__(self):
        self.module_name = "LoginDelay"

        if  sb_utils.os.info.is_solaris() == True:
            self._config_file = '/etc/default/login'
            self.keyname = 'SLEEPTIME'
            self.delim = ['=']
        else:
            self._config_file = '/etc/login.defs'
            self.keyname = 'FAIL_DELAY'
            self.delim = [' ', '\t']

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'loginDelay' in optionDict:
            return 1
        try:
            value = int(optionDict['loginDelay'])
        except ValueError:
            return 1
        if value < 1:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict=None):

        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['loginDelay']
        option = int(option)
       
        msg = "Looking for '%s' in %s" % (self.keyname, self._config_file)
        self.logger.info(self.module_name, msg)

        # Grab parameters separated by the OS's specific delimeter(s)
        paramlist = {} 
        paramlist.update(sb_utils.os.config.get_list(configfile=self._config_file, delim=self.delim)) 

        if not paramlist.has_key(self.keyname):
            msg = "Could not find '%s' in %s" % (self.keyname, self._config_file)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            del paramlist
            return 'Fail', msg
        else:
            if int(paramlist[self.keyname]) != option:
                msg = "'%s' is set to %d but expected it to be %d" % \
                           (self.keyname, int(paramlist[self.keyname]), option)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                del paramlist
                return 'Fail', msg
        
        return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict=None):

        action_record = ''

        if self.validate_input(optionDict): 
            msg = "Invalid option value."
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        option = optionDict['loginDelay']
        option = int(option)

        # Grab parameters separated by the OS's specific delimeter(s)
        paramlist = {} 
        paramlist.update(sb_utils.os.config.get_list(configfile=self._config_file, delim=self.delim)) 

        if not paramlist.has_key(self.keyname):
            action_record = 'unset'
            results = sb_utils.os.config.setparam(configfile=self._config_file,
                        param=self.keyname, value=str(option), delim=self.delim)
            msg = "Apply Performed: Set %s to %d in %s" % (self.keyname, option, self._config_file)
            self.logger.notice(self.module_name, msg)
            del paramlist
            return 1, action_record

        else:
            if int(paramlist[self.keyname]) == option:
                return 0, ''
            else:
                results = sb_utils.os.config.setparam(configfile=self._config_file,
                        param=self.keyname, value=str(option), delim=self.delim)
                if results == False:
                    return 0, ''

                msg = "Apply Performed: Set %s to %d in %s" % (self.keyname, option, self._config_file)
                self.logger.notice(self.module_name, msg)
                return 1, str(paramlist[self.keyname])



    ##########################################################################
    def undo(self, change_record):


        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record == '':
            msg = "Skipping Undo: No change record or empty change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0
            
        if change_record == 'unset':
            results = sb_utils.os.config.unsetparam(param=self.keyname, delim=self.delim, configfile=self._config_file)
            if results == False:
                msg = "Unable to remove %s from %s" % (self.keyname, self._config_file)
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                msg = "Removed %s from %s" % (self.keyname, self._config_file)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                return 1
         
        results = sb_utils.os.config.setparam(configfile=self._config_file,
                        param=self.keyname, value=str(change_record), delim=self.delim)

        msg = "%s set to %s in %s" % (self.keyname, str(change_record), self._config_file)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

