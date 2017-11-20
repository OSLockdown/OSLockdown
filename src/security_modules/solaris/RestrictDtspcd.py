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
import sb_utils.os.solaris



class RestrictDtspcd:
    ##########################################################################
    def __init__(self):

        self.module_name = "RestrictDtspcd"

        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__ndd_file = '/etc/default/ndd'
        self.__desc     = 'Lock down dtspcd'
        self.__param    = {  'arp_cleanup_interval': 60000 }


    ##########################################################################
    def validate_input(self, option=None):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
            
        messages = {'messages': [] }
        failure_flag = False

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global' and not os.path.islink('/dev/tcp'):
            msg = "Non-global Solaris zone (%s): /dev/tcp is unavailable" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        ##############
        ## Check value in running kernel
        curvalues = sb_utils.os.solaris.ndd_get(param='tcp_extra_priv_ports', driver='tcp').split('\n')
        port_list = []
        for port in curvalues:
            port_list.append(int(port))

        if 6112 not in port_list:
            msg = "Port tcp/6112 is not a privileged port in the running kernel"
            self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
            messages['messages'].append("Fail: %s" % msg)
            failure_flag = True
        else:
            msg = "Port tcp/6112 is a privileged port in the running kernel"
            messages['messages'].append("Okay: %s" % msg)

        ##################
        ## Check the ndd configuration file 
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): Skipping check of %s" % (zonename, self.__ndd_file) 
            self.logger.debug(self.module_name, 'Scan: ' + msg)
            messages['messages'].append("Fail: %s" % msg)
        else:    
            foundit = False
            try:
                in_obj = open(self.__ndd_file, 'r')
                for line in in_obj.readlines():
                    if not line.startswith('tcp_extra_priv_ports_add'):
                        continue
                    else:
                        (keyname, keyvalue) = line.rstrip().split('=')
                        if int(keyvalue) == 6112:
                            foundit = True
                            break
                            
                in_obj.close()
                if foundit == False:
                    msg = "Could not find 'tcp_extra_priv_ports_add=6112' in %s" % self.__ndd_file
                    messages['messages'].append("Fail: %s" % msg)
                    failure_flag = True
                else:
                    msg = "Found 'tcp_extra_priv_ports_add=6112' in %s" % self.__ndd_file
                    messages['messages'].append("Okay: %s" % msg)

            except (IndexError,IOError), err:
                msg = 'Unable to read %s: %s' % (self.__ndd_file, err)
                self.logger.error(self.module_name, msg)
                messages['messages'].append("Error: %s" % msg)

        if failure_flag == True:
            msg = "dtspcd port tcp/6112 is not marked as privileged"
            self.logger.notice(self.module_name, msg)
            return False, msg, messages
        else:
            msg = "dtspcd port tcp/6112 is marked as privileged"
            return True, msg, messages


    ##########################################################################
    def apply(self, option=None):

        result, msg, messages = self.scan(option)
        if result == True:
            msg = "dtspcd port tcp/6112 is already marked as privileged"
            return False, '', msg
                                                                
        messages = {'messages': []}
        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to perform module apply or undo action to a "\
                  "non-global Solaris zone (%s)" % zonename
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        action_record = []
        try:
            out_obj = open(self.__ndd_file, 'a')
            out_obj.write("tcp_extra_priv_ports_add=6112\n") 
            out_obj.close()
            action_record.append('applied')
            msg = "Appended 'tcp_extra_priv_ports_add=6112' to %s" % self.__ndd_file
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            messages['messages'].append(msg)
        except IOError, err:
            msg = "Unable to append 'tcp_extra_priv_ports_add=6112' to %s" % self.__ndd_file
            self.logger.error(self.module_name, 'Error: ' + msg)
            messages['messages'].append("Error: %s" % msg)
             
        curvalues = sb_utils.os.solaris.ndd_get(param='tcp_extra_priv_ports', driver='tcp').split('\n')
        port_list = []
        for port in curvalues:
            port_list.append(int(port))

        if 6112 not in port_list:
           results = sb_utils.os.solaris.ndd_set(param='tcp_extra_priv_ports_add', paramValue='6112', driver='tcp')
           if results == False:
               msg = "Unable to set 'tcp_extra_priv_ports_add' 6112 in running kernel"
               self.logger.error(self.module_name, 'Apply Error: ' + msg)
               messages['messages'].append("Error: %s" % msg)
           else:
               msg = "Set 'tcp_extra_priv_ports_add' 6112 in running kernel"
               messages['messages'].append(msg)

        return True, ''.join(action_record), messages 


    ##########################################################################            
    def undo(self, change_record=None):

        messages = {'messages': []}
        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to perform module undo or apply action to a "\
                  "non-global Solaris zone (%s)" % zonename
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        if change_record != 'applied':
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        ##########################
        ## Current running Kernel
        curvalues = sb_utils.os.solaris.ndd_get(param='tcp_extra_priv_ports', driver='tcp').split('\n')
        port_list = []
        for port in curvalues:
            port_list.append(int(port))

        if 6112 in port_list:
           results = sb_utils.os.solaris.ndd_set(param='tcp_extra_priv_ports_del', paramValue='6112', driver='tcp')
           if results == False:
               msg = "Unable to 'tcp_extra_priv_ports_del' 6112 in running kernel"
               self.logger.error(self.module_name, 'Undo Error: ' + msg)
               messages['messages'].append("Error: %s" % msg)
           else:
               msg = "Executed 'tcp_extra_priv_ports_del' 6112 in running kernel"
               self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
               messages['messages'].append(msg)

        ##########################
        ## Edit /etc/default/ndd
        try:
            in_obj = open(self.__ndd_file, 'r')
            lines = in_obj.readlines()
            in_obj.close()
        except IOError, err:
            msg = "Unable to read %s" % self.__ndd_file
            self.logger.error(self.module_name, 'Error: ' + msg)
            messages['messages'].append("Error: %s" % msg)
            return False, '', messages

        try:
            outobj = open(self.__ndd_file, 'w')
            for line in lines:
                if not line.startswith('tcp_extra_priv_ports_add'):
                    outobj.write(line)
                    continue
                else:
                    (keyname, keyvalue) = line.rstrip().split('=')
                    if int(keyvalue) == 6112:
                        msg = "Removed 'tcp_extra_priv_ports_add=6112' from  %s" % self.__ndd_file
                        messages['messages'].append(msg)
                        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                        continue
                    else:
                        outobj.write(line)
            outobj.close()
        except IOError, err:
            msg = "Unable to update %s" % self.__ndd_file
            self.logger.error(self.module_name, 'Error: ' + msg)
            messages['messages'].append("Error: %s" % msg)
            return False, '', messages

        return True, '', messages

