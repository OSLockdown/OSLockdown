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
import sb_utils.os.config
import sb_utils.os.solaris


class TcpStrongISS:

    def __init__(self):

        self.module_name = "TcpStrongISS"
        self.logger = TCSLogger.TCSLogger.getInstance()

        # Identify the configuration file and parameter
        # you want to set here...
        self.__target_file = '/etc/default/inetinit'
        self.__param       = 'TCP_STRONG_ISS'


    ##########################################################################
    def validate_input(self, option_str):
        if not option_str:
            return 1
        try:
            value = int(option_str)
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        zonename = sb_utils.os.solaris.zonename()                                                                                       
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): Unable to set %s" % (zonename, self.__param)
            self.logger.notice(self.module_name, 'Scan: ' + msg)                                                                    
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))   

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
        if int(value) != 2:
            reason = "%s is set to '%s' instead of 2 in %s" % (self.__param, value, self.__target_file)

            self.logger.info(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):


        action_record = ''

        result, reason = self.scan(option)
        if result == 'Pass':
            return 0, ''

        results = sb_utils.os.config.setparam(configfile=self.__target_file,
                                                param=self.__param,
                                                value='2',
                                                delim='=')

        if results == False:
            msg = "Unable to set %s in %s" % (self.__param, self.__target_file)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            action_record = results
      
        msg = "%s set to '2' in %s" % (self.__param, self.__target_file)

        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record

    ##########################################################################
    def undo(self, change_record):
        """Undo the previous action."""


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

