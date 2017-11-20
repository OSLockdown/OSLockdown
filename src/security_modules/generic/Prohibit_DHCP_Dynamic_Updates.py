#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.config

class InvalidUserID (Exception):
    pass

class Prohibit_DHCP_Dynamic_Updates:

    def __init__(self):
        self.module_name = "Prohibit_DHCP_Dynamic_Updates"

        self.__dhcpfile = '/etc/dhclient.conf'
        self.__param = 'do-forward-updates'
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()




    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        messages = []
        retval = True
        msg = '' 
        cfgFiles = ['/etc/dhclient.conf']
        for configfile in os.listdir('/etc'):
            if configfile != 'dhclient.conf' and configfile.startswith('dhclient') and configfile.endswith('.conf'):
                cfgFiles.append("/etc/%s" % configfile)

        for configfile in cfgFiles:
            try:
                if not os.path.exists(configfile):
                    raise InvalidUserID(configfile)
                oldval = sb_utils.os.config.get_list(configfile=configfile, delim=' ')[self.__param]
                # value could be terminated with a ';', so strip it if so
                if oldval:
                    oldval = oldval.split(';',1)[0].strip()
                if oldval == 'false':
                    msg = "%s has '%s' set to 'false'" % (configfile, self.__param)
                    self.logger.notice(self.module_name, msg)
                else:
                    msg = "%s has '%s' set to '%s' instead of 'false'" % (configfile, self.__param, oldval )
                    messages.append(msg)
                    self.logger.notice(self.module_name, msg)
                    retval = False
                    
            except InvalidUserID, err:
                msg = "%s does not exist, default value for '%s' is true" % (configfile, self.__param)
                messages.append(msg)
                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                retval = False
            except KeyError, err:
                msg = "%s is missing '%s' line" % (configfile, self.__param)
                messages.append(msg)
                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                retval = False
                    
        return retval, msg, {'messages':messages}


    ##########################################################################
    def apply(self, option=None):
        """Create and replace the audit rules configuration."""

        change_record = {}
        messages = []

        cfgFiles = ['/etc/dhclient.conf']
        for configfile in os.listdir('/etc'):
            if configfile != 'dhclient.conf' and configfile.startswith('dhclient') and configfile.endswith('.conf'):
                cfgFiles.append("/etc/%s" % configfile)

        for configfile in cfgFiles:
            isOk = True
            try:
                if not os.path.exists(configfile):
                    open(configfile,"w")
                    raise InvalidUserID(configfile)
                oldval = sb_utils.os.config.get_list(configfile=configfile, delim=' ')[self.__param]
                # value could be terminated with a ';', so strip it if so
                if oldval:
                    oldval = oldval.split(';',1)[0].strip()
                if oldval == 'false':
                    msg = "%s has '%s' set to 'false'" % (configfile, self.__param)
                    self.logger.notice(self.module_name, msg)
                else:
                    msg = "%s has '%s' set to '%s' instead of 'false'" % (configfile, self.__param, oldval )
                    messages.append(msg)
                    self.logger.notice(self.module_name, msg)
                    isOk = False
            except InvalidUserID, err:
                msg = "%s does not exist, default value for '%s' is true" % (configfile, self.__param)
                messages.append(msg)
                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                isOk = False
                    
            except KeyError, err:
                msg = "%s is missing '%s' line" % (configfile, self.__param)
                messages.append(msg)
                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                isOk = False
                    
            if not isOk:
                oldval = sb_utils.os.config.setparam(configfile=configfile, delim=' ', param=self.__param, value='false;')
                change_record[configfile] = [self.__param, oldval]
        
        if not change_record:
           change_record = ''
           retval = False
        else:
            retval = True
        return retval, str(change_record), {'messages':messages}            
                


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        change_record = tcs_utils.string_to_dictionary(change_record)
            
        for configfile in change_record.keys():
            param, val = change_record[configfile]
            if val:
                sb_utils.os.config.setparam(configfile=configfile, delim=' ', param=param, value=val)
            else:
                sb_utils.os.config.unsetparam(configfile=configfile, delim=' ', param=param)
            return True, '', {}
if __name__ == '__main__':
    TEST = Prohibit_DHCP_Dynamic_Updates()
    print TEST.scan()
    
