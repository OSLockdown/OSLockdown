#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Set Password History - Users can use any of X number of previous passwords
# 
# Set HISTORY in /etc/default/passwd
#

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.config


class PasswordReuse:

    def __init__(self):

        self.module_name = "PasswordReuse"
        self.logger = TCSLogger.TCSLogger.getInstance()

        # Identify the configuration file and parameter
        # you want to set here...
        self.__target_file = '/etc/default/passwd'
        self.__param       = 'HISTORY'


    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'passwordReuse' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordReuse'])
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict):


        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordReuse']
        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                delim='=') 

        if paramlist == None:
            msg = 'Unable to determine parameter setting'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if not paramlist.has_key(self.__param):
            reason = "%s  option is NOT set in %s" % (self.__param, 
                                                      self.__target_file)

            self.logger.info(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        value = paramlist[self.__param]
        if value != option:
            reason = "%s is set to '%s' instead of '%s'" % (self.__param, 
                                                        value, option)

            self.logger.info(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict):

        action_record = ''

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''
        option = optionDict['passwordReuse']

        results = sb_utils.os.config.setparam(configfile=self.__target_file,
                                                param=self.__param,
                                                value=option,
                                                delim='=')

        if results == False:
            msg = "Unable to set %s in %s" % (self.__param, self.__target_file)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            action_record = results
      
        msg = '%s set to %s in %s' % (self.__param, 
                                      str(option), 
                                      self.__target_file)

        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, str([action_record])  # return a list, so we can return an 'empty' for an unset entity

    ##########################################################################
    def undo(self, change_record):
        """Undo the previous action."""

        
        if change_record[0:11].strip().startswith('['):  # new style...
            change_record = tcs_utils.string_to_dictionary(change_record)[0]
            if change_record == []:
                change_record = None
                
        if not change_record:
            msg = "No previous value provided for %s; "\
                 "removing entry from %s" % (self.__param, self.__target_file)
            self.logger.info(self.module_name, 'Undo: ' + msg)
            results = sb_utils.os.config.unsetparam(param=self.__param, 
                             configfile=self.__target_file)
        else:
            results = sb_utils.os.config.setparam( param=self.__param,
                                                   delim='=',
                                                   value=change_record,
                                                   configfile=self.__target_file)
            

        if results == False:
            msg = "Unable to restore %s in %s" % (self.__param, self.__target_file)
            self.logger.error(self.module_name, 'Undo Failed: ' + msg)
            return 0

        msg = "Restored %s in %s" % (self.__param, self.__target_file)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
