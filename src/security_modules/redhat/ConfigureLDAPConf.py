#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.config
import sb_utils.os.linux


class ConfigureLDAPConf:

    def __init__(self):

        self.module_name = "ConfigureLDAPConf"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.__target_file = "/etc/ldap.conf"

        self.__settings = {}

    ##########################################################################
    def validate_options(self, optionDict):
        self.__settings = {}
        
        try:
            items = optionDict['ldapConfs'].splitlines()
            for item in items:
                try:
                    tag, value = item.split(None,1)
                    self.__settings[tag] = value
                except Exception, err:
                    msg = "Unable to parse line '%s' " % item 
                    self.logger.warn(self.module_name, msg)        
            if len(self.__settings) == 0:
                msg = "Empty list of settings for LDAP, aborting module"
                raise tcs_utils.ManualActionReqd("%s %s" % (self.module_name, msg))
            return

        except Exception,err:
            msg = "Unable to parse items from option value  " 
            self.logger.warn(self.module_name, msg)        
            items = []
        
        


    ##########################################################################
    def scan(self, optionDict=None):

        messages = []
        self.validate_options(optionDict)
        failure_flag = False
        
        if not os.path.exists(self.__target_file):
            msg = "'%s' does not exist" % self.__target_file
            messages.append(msg)
            self.logger.notice(self.module_name, msg) 
        else:
            paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                    delim=' ')
            msg = "Checking settings in %s" % (self.__target_file)
            self.logger.info(self.module_name, msg)
        
            for param in  self.__settings.keys():
                if paramlist.has_key(param):
                    if self.__settings[param] != paramlist[param]:
                        msg = "'%s' is set to '%s' in %s; exepcted it to be set to '%s'" % \
                                     (param, paramlist[param], self.__target_file, self.__settings[param])
                        messages.append(msg)
                        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                        failure_flag = True
                    else:
                        msg = "Okay: '%s' is set to '%s' in %s" % (param, self.__settings[param], self.__target_file)
                        self.logger.info(self.module_name, msg)
                else:
                    msg = "'%s' is not set in %s" % (param, self.__target_file)
                    messages.append(msg)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    failure_flag = True
        
                
        if failure_flag == True:
            return False, 'One or more settings are incorrect', {'messages':messages}
        else:
            return True, '', {'messages':messages}
  
    ##########################################################################
    def apply(self, optionDict=None):

        action_record = {}
        messages = []

        self.validate_options(optionDict)

        if not os.path.exists(self.__target_file):
            msg = "'%s' does not exist" % self.__target_file
            messages.append(msg)
            self.logger.notice(self.module_name, msg) 
        else:
            paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                    delim=' ')
            msg = "Checking settings in %s" % (self.__target_file)
            self.logger.info(self.module_name, msg)

            for xparam in self.__settings.keys():
                if paramlist.has_key(xparam):
                    if self.__settings[xparam] == paramlist[xparam]:
                        continue 

                results = sb_utils.os.config.setparam( \
                        configfile=self.__target_file, \
                        param=xparam, value=str(self.__settings[xparam]), delim=' ')
                if results == False:
                    msg = "Unable to set %s in %s" % (xparam, self.__target_file)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    messages.append(msg)
                else:
                    action_record[xparam] = str(results)
                    msg = "Apply Performed: %s set to '%s' in %s" % \
                              (xparam, self.__settings[xparam], self.__target_file)
                    self.logger.notice(self.module_name, msg)

        if action_record == {}:
            return False, '', {'messages':messages}
        else:
            return True, str(action_record), {'messages':messages}
                                                            
            
    ##########################################################################
    def undo(self, change_record=None):

       change_record = tcs_utils.string_to_dictionary(change_record)
        
       msg = "Reverting settings in %s" % (self.__target_file)
       self.logger.info(self.module_name, msg)

       for xparam, xvalue in change_record.iteritems():
           results = ''
           if xvalue == '': 
               results = sb_utils.os.config.unsetparam( \
                   configfile=self.__target_file, param=xparam, delim=' ')
           else:
               results = sb_utils.os.config.setparam( \
                   configfile=self.__target_file, \
                   param=xparam, value=xvalue, delim=' ')

           if results == False:
               msg = "Unable to set %s in %s" % (xparam, self.__target_file)
               self.logger.error(self.module_name, 'Undo Error: ' + msg)
               raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

           else:
               if xvalue == '':
                   msg = "'%s' removed from %s" % (xparam, self.__target_file)
               else:
                   msg = "'%s' set to '%s' in %s" % (xparam, xvalue, self.__target_file)

               self.logger.notice(self.module_name, "Undo Performed: " + msg)


       return 1

if __name__ == "__main__":
    
    myLog = TCSLogger.TCSLogger.getInstance()
    myLog.force_log_level (7)
    myLog._fileobj = sys.stdout
    test = ConfigureLDAPConf()
    print test.scan() 
