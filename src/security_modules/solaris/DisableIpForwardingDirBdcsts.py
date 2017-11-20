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



class DisableIpForwardingDirBdcsts:
    ##########################################################################
    def __init__(self):

        self.module_name = "DisableIpForwardingDirBdcsts"

        self.logger = TCSLogger.TCSLogger.getInstance()

        # Identify the configuration file and parameter
        # you want to set here...
        self.__target_file = '/etc/default/ndd'
        self.__desc        = 'IP forwarding of directed broadcasts'
        self.__param       = {  'ip_forward_directed_broadcasts': 0 }


    ##########################################################################
    def scan(self, option=None):
            
        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                delim='=') 

        zonename = sb_utils.os.solaris.zonename()

        messages = {'messages': []}

        if zonename != 'global' and not os.path.islink('/dev/ip'):
            msg = "Non-global Solaris zone (%s): /dev/ip is unavailable" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))


        failure_flag = False
        if paramlist == None:
            msg = 'Scan Error: Unable to determine parameter setting'
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        for param in self.__param.keys():
            if param.startswith('ip'):
                thedriver = 'ip'

            if param.startswith('icmp'):
                thedriver = 'icmp'

            if param.startswith('tcp'):
                thedriver = 'tcp'

            if param.startswith('udp'):
                thedriver = 'udp'

            curvalue = sb_utils.os.solaris.ndd_get(param=param, driver=thedriver)
            if int(curvalue) != int(self.__param[param]):
                reason = "%s is set to '%s' instead of %d" % (param, curvalue, self.__param[param])
                messages['messages'].append(reason)
                self.logger.notice(self.module_name, "Scan Failed: %s" % reason)
                failure_flag = True
                continue

            # Module ONLY applies to global Solaris zones
            if zonename != 'global':
                msg = "Non-global Solaris zone (%s): Skipping check of "\
                      "/etc/default/ndd" % (zonename) 
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                messages['messages'].append(msg)
                continue
            
            # Is parameter implicility set in /etc/default/ndd?
            if not paramlist.has_key(param):
                msg = "%s option is NOT set in %s" % (param, self.__target_file)
                self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                messages['messages'].append(msg)
                failure_flag = True
                continue

            # If parameter is set, does it match desired value?
            value = paramlist[param]
            if int(value) != int(self.__param[param]):
                msg = "%s is set to '%s' instead of %d" % (param, value, self.__param[param])
                self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                messages['messages'].append(msg)
                failure_flag = True
            else:
                msg = "%s is set to '%d' in %s" % (param, self.__param[param], self.__target_file)
                self.logger.info(self.module_name, msg)
                messages['messages'].append(msg)


        if failure_flag == True:
            msg = "%s not disabled" % (self.__desc)
            self.logger.notice(self.module_name, msg)
            return False, msg, messages
        else:
            return True, '', messages


    ##########################################################################
    def apply(self, option=None):

        result, reason, messages = self.scan()
        if result == True:
            return False, '', {}
                                                                
        messages = {'messages': [] }

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to perform module apply or undo action to a "\
                  "non-global Solaris zone (%s)" % zonename
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        action_record = []

        for xparam in self.__param.keys():
            results = sb_utils.os.config.setparam( \
                        configfile=self.__target_file, \
                        param=xparam, value=str(self.__param[xparam]), delim='=')

            if results == False:
                msg = "Unable to set %s in %s" % (xparam, self.__target_file)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record.append(xparam + '=' + results + '\n')
                msg = "%s set to '%d' in %s" % (xparam, self.__param[xparam], self.__target_file)
                self.logger.notice(self.module_name, "Apply Performed: %s" % msg)
                messages['messages'].append(msg)

            # Set in memory settings ...
            if xparam.startswith('ip'):
                thedrvr = 'ip'

            if xparam.startswith('icmp'):
                thedrvr = 'icmp'

            if xparam.startswith('tcp'):
                thedrvr = 'tcp'

            if xparam.startswith('udp'):
                thedrvr = 'udp'

            #curvalue = sb_utils.os.solaris.ndd_get(param=xparam, driver=thedriver)

            results = sb_utils.os.solaris.ndd_set(param=xparam,
                       paramValue=str(self.__param[xparam]), driver=thedrvr)
            if results == False:
                msg = "Unable to set %s to %s in current running kernel" % (xparam, str(self.__param[xparam]))
                messages['messages'].append("Error: %s" % msg)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
            else:
                msg = "Set %s to %s in current running kernel" % (xparam, str(self.__param[xparam]))
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return True, ''.join(action_record), messages 


    ##########################################################################            
    def undo(self, change_record=None):

        messages = {'messages': [] }
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
                messages['messages'].append(msg)
            else:
                results = sb_utils.os.config.setparam( param=param_key,
                                                   delim='=',
                                                   value=param_val,
                                                   configfile=self.__target_file)

                msg = 'Resetting %s to %s from %s' % \
                       (param_key, param_val, self.__target_file)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                messages['messages'].append(msg)
            
            if results == False:
                msg = "Unable to restore %s in %s" % (param_key, self.__target_file)
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
                messages['messages'].append("Error: %s" % msg)
            else:
                msg = "Reset %s to %s in current running kernel" % (param_key, param_key)
                self.logger.notice(self.module_name, 'Undo Error: ' + msg)
                messages['messages'].append(msg)

       
        if failure_flag == True:
            return False, '', messages
        else:
            return True, '', messages
