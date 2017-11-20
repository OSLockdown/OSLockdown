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



class TCPMaxSynBacklog:
    ##########################################################################
    def __init__(self):

        self.module_name = "TCPMaxSynBacklog"

        self.logger = TCSLogger.TCSLogger.getInstance()

        # Identify the configuration file and parameter
        # you want to set here...
        self.__target_file = '/etc/default/ndd'
        self._param       = {  'tcp_conn_req_max_q': 1024, 
                               'tcp_conn_req_max_q0': 4096  }


    ##########################################################################
    def validate_input(self, option=None):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict=None):
            

        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                delim='=') 

        zonename = sb_utils.os.solaris.zonename()

        failure_flag = False
        if paramlist == None:
            msg = 'Scan Error: Unable to determine parameter setting'
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if optionDict != None and 'tcpMaxSynBacklog' in optionDict:
            option = optionDict['tcpMaxSynBacklog']
            option = int(option)
            if option < 1024:
                msg = "Specified option value %d < 1024 is not recommended "\
                      "for tcp_conn_req_max_q0 therefore, using 4096 instead." \
                          % (option)
                self.logger.warn(self.module_name, msg)
                option = 4096
                self._param['tcp_conn_req_max_q0'] = 4096
            if option > 4096:
                msg = "Specified option %d > 4096; not recommended for "\
                      "tcp_conn_req_max_q0 however, still using value" % (option)
                self.logger.warn(self.module_name, msg)
        else:
            msg = "No specified option value for tcp_conn_req_max_q0 "\
                  "therefore, defaulting to 4096"
            self.logger.warn(self.module_name, msg)
            option = 1024
            self._param['tcp_conn_req_max_q0'] = 4096
                
        for param in self._param.keys():

            if param.startswith('ip'):
                thedrvr = 'ip'

            if param.startswith('icmp'):
                thedrvr = 'icmp'

            if param.startswith('tcp'):
                thedrvr = 'tcp'

            if param.startswith('udp'):
                thedrvr = 'udp'

            curvalue = sb_utils.os.solaris.ndd_get(param=param, driver=thedrvr)

            if int(curvalue) != int(self._param[param]):
                reason = "Scan Failed: %s is set to '%s' instead of %d" % \
                                     (param, curvalue, self._param[param])
                self.logger.notice(self.module_name, reason)
                if zonename != 'global':
                    reason = 'This parameter can only be set (applied) from the global zone'
                    self.logger.info(self.module_name, reason)

                failure_flag = True
                continue

            # Module ONLY applies to global Solaris zones
            if zonename != 'global':
                msg = "Non-global Solaris zone (%s): Skipping check of "\
                      "/etc/default/ndd" % (zonename) 
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue
            
            # Is parameter implicility set in /etc/default/ndd?
            if not paramlist.has_key(param):
                msg = "Scan Failed: %s option is NOT set in %s" % \
                               (param, self.__target_file)
                self.logger.notice(self.module_name, msg)
                failure_flag = True
                continue

            # If parameter is set, does it match desired value?
            value = paramlist[param]
            if int(value) != int(self._param[param]):
                msg = "Scan Failed: %s is set to '%s' instead of %d" % \
                            (param, value, self._param[param])
                self.logger.notice(self.module_name, msg)
                failure_flag = True
            else:
                msg = "%s is set to '%d' in %s" % \
                        (param, self._param[param], self.__target_file)
                self.logger.info(self.module_name, msg)


        if failure_flag == True:
            msg = "Pending TCP connections queues not tuned"
            self.logger.notice(self.module_name, msg)
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict=None):
        
        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''
                                                                
        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to perform module apply or undo action to a "\
                  "non-global Solaris zone (%s)" % zonename
            self.logger.notice(self.module_name, msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        action_record = []

        if optionDict != None and 'tcpMaxSynBacklog' in optionDict:
            option = optionDict['tcpMaxSynBacklog']
            option = int(option)
            if option < 1024:
                msg = "Specified option value %d < 1024 is not recommended "\
                      "for tcp_conn_req_max_q0 therefore, using 4096 instead." \
                          % (option)
                self.logger.warn(self.module_name, msg)
                option = 4096
                self._param['tcp_conn_req_max_q0'] = 4096
            if option > 4096:
                msg = "Specified option %d > 4096; not recommended for "\
                      "tcp_conn_req_max_q0 however, still using value" % (option)
                self.logger.warn(self.module_name, msg)
        else:
            msg = "No specified option value for tcp_conn_req_max_q0 "\
                  "therefore, defaulting to 4096"
            self.logger.warn(self.module_name, msg)
            option = 1024
            self._param['tcp_conn_req_max_q0'] = 4096


        for xparam in self._param.keys():
            results = sb_utils.os.config.setparam( \
                        configfile=self.__target_file, \
                        param=xparam, value=str(self._param[xparam]), delim='=')

            if results == False:
                msg = "Unable to set %s in %s" % (xparam, self.__target_file)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record.append(xparam + '=' + results + '\n')
                msg = "Apply Performed: %s set to '%d' in %s" % \
                              (xparam, self._param[xparam], self.__target_file)
                self.logger.notice(self.module_name, msg)

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
                       paramValue=str(self._param[xparam]), driver=thedrvr)
            if results == False:
                msg = "Unable to set %s to %s in current running kernel" % (xparam, str(self._param[xparam]))
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
                failure_flag = True

       
        if failure_flag == True:
            return 0
        else:
            return 1
