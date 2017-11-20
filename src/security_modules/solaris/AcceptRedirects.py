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
import sb_utils.os.solaris



class AcceptRedirects:
    ##########################################################################
    def __init__(self, hmac_msg=None):

        self.module_name = "AcceptRedirects"

        self.logger = TCSLogger.TCSLogger.getInstance()

        # Identify the configuration file and parameter
        # you want to set here...
        self.__target_file = '/etc/default/ndd'
        self.__desc        = 'Accept ICMP redirects'

        self.__param       = [ 'ip_ignore_redirect',
                               'ip6_ignore_redirect' ]

    ##########################################################################
    def validate_input(self, option=None):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
            
        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                delim='=') 

        zonename = sb_utils.os.solaris.zonename()

        if zonename != 'global' and not os.path.islink('/dev/ip'):
            msg = "Non-global Solaris zone (%s): /dev/ip is unavailable" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        failure_flag = False
        if paramlist == None:
            msg = 'Unable to determine parameter setting'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))


        for param in self.__param:
            curvalue = sb_utils.os.solaris.ndd_get(param=param, driver='ip')

            if int(curvalue) != 1:
                reason = "%s is set to '%s' instead of 1" % (param, curvalue)
                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                failure_flag = True
                continue

            if not paramlist.has_key(param):
                reason = "%s option is NOT set in %s" % (param, 
                                                      self.__target_file)

                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                failure_flag = True
                continue

            value = paramlist[param]
            if int(value) != 1:
                reason = "%s is set to '%s' instead of 1" % (param, value)
                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                failure_flag = True
            else:
                msg = "%s is set to 1 in %s" % (param, self.__target_file)
                self.logger.info(self.module_name, msg)


        if failure_flag == True:
            msg = "%s not disabled" % (self.__desc)
            self.logger.notice(self.module_name, msg)
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
                                                            
        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to perform module apply or undo action to a "\
                  "non-global Solaris zone (%s)" % zonename
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        action_record = []

        for xparam in self.__param:
            results = sb_utils.os.config.setparam( \
                        configfile=self.__target_file, \
                        param=xparam, value='1', delim='=')

            if results == False:
                msg = "Unable to set %s in %s" % (xparam, self.__target_file)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record.append(xparam + '=' + results + '\n')
                msg = '%s set to 1 in %s' % (xparam, self.__target_file)
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

            # Set in memory settings ...
            if xparam.startswith('ip'):
                thedrvr = 'ip'

            if xparam.startswith('icmp'):
                thedrvr = 'icmp'

            if xparam.startswith('tcp'):
                thedrvr = 'tcp'

            if xparam.startswith('udp'):
                thedrvr = 'udp'

            results = sb_utils.os.solaris.ndd_set(param=xparam,
                       paramValue='1', driver=thedrvr)
            if results == False:
                msg = "Unable to set %s to 1 in current running kernel" % (xparam)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)


        return 1, ''.join(action_record) 


    ##########################################################################            
    def undo(self, change_record=None):

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to perform module undo or apply action to a "\
                  "non-global Solaris zone (%s)" % zonename
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        failure_flag = False
        for xparam in change_record.split('\n'):
            if not xparam:
                continue

            if '=' not in xparam:
                msg = 'Malformed change record: %s' % (xparam)
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            param_key = xparam.split('=')[0]
            param_val = xparam.split('=')[1]

            if not param_val:
                results = sb_utils.os.config.unsetparam( param=param_key,
                             configfile=self.__target_file)
                msg = 'Removing %s from %s' % (param_key, self.__target_file)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            else:
                results = sb_utils.os.config.setparam( param=param_key,
                                                   delim='=',
                                                   value=param_val,
                                                   configfile=self.__target_file)

                msg = 'Resetting %s to %s from %s' % \
                       (param_key, param_val, self.__target_file)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            

            if results == False:
                msg = "Unable to restore %s in %s" % (self.__param, self.__target_file)
                self.logger.error(self.module_name, 'Undo Failed: ' + msg)
                failure_flag = True

            # Set in memory settings ...
            if param_key.startswith('ip'):
                thedrvr = 'ip'

            if param_key.startswith('icmp'):
                thedrvr = 'icmp'

            if param_key.startswith('tcp'):
                thedrvr = 'tcp'

            if param_key.startswith('udp'):
                thedrvr = 'udp'

            results = sb_utils.os.solaris.ndd_set(param=param_key,
                       paramValue=param_val, driver=thedrvr)
            if results == False:
                msg = "Unable to set %s to %s in current running kernel" % (param_key, param_key)
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                failure_flag = True


       
        if failure_flag == True:
            return 0
        else:
            return 1

