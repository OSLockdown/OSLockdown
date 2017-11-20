#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable Zeroconf Networking
#
#

import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger


class DisableZeroconfNet:

    def __init__(self):
        self.module_name = "DisableZeroconfNet"
        self.__target_file = "/etc/sysconfig/network"
        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    
    ##########################################################################
    # Look through /etc/sysconfig/network for a line 'NOZEROCONFIG=<value>',
    # and return :
    #   missing - line not found
    #   <value> - if line found
    
    def search_for_line(self, option = None):
        retval = 'missing'
        try:
            lines = open(self.__target_file).readlines()
            for line in lines:
                if line.startswith('NOZEROCONF='):
                    retval = line.split('=')[1].rstrip()
                    break
        except Exception, err:
            msg = "Unable to process file %s: %s" % (self.__target_file, str(err))
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
        return retval, lines

    ##########################################################################
    def scan(self, option=None):


        messages = {}
        messages['messages'] = []

        setting, lines = self.search_for_line()
        
        if setting == 'missing':
            msg = "%s is missing NOZEROCONF entry" % self.__target_file
        else:
            msg = "%s has 'NOZEROCONF=%s'" % ( self.__target_file, setting)

        self.logger.notice(self.module_name, msg)
        messages['messages'].append(msg)
        
        if setting not in ['yes', 'YES'] :
            return False, '' ,'Zeroconf networking is not enabled'
        else:
            return True, '', 'Zeroconf networking is enabled'
  
    ##########################################################################
    def apply(self, option=None):

        messages = {}
        messages['messages'] = []

        setting, lines = self.search_for_line()
        
        if setting not in ['yes', 'YES' ] :
            if setting == 'missing':
                lines.append('NOZEROCONF=yes\n')
                change_record = 'missing'
                messages['messages'].append("Adding 'NOZEROCONF=yes' to %s" %self.__target_file)
            else:
                for linenum in range(len(lines)):
                    if lines[linenum].startswith('NOZEROCONF='):
                        lines[linenum] = 'NOZEROCONF=yes\n'
                        break
                messages['messages'].append("Setting 'NOZEROCONF=yes' in %s" %self.__target_file)
            retval = True
            change_record = setting       
            open(self.__target_file,"w").writelines(lines)
        else:
            retval = False
            change_record = ""
        
        return retval, str(change_record), messages
                                                            
            
    ##########################################################################
    def undo(self, change_record=None):


        if not change_record or change_record == '': 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        messages = {}
        messages['messages'] = []

        if not os.path.exists(self.__target_file):
            msg = "Unable to find %s to revert changes" % self.__target_file
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = open(self.__target_file,"r").readlines()
        
        # we're counting on the fact that the NOZEROCONF should appear once at most
        made_change = False
        if change_record == 'missing':
            for linenum in range(len(lines)):
                if lines[linenum].startswith('NOZEROCONF='):
                    del(lines[linenum])
                    made_change = True
                    messages['messages'].append("Removing 'NOZEROCONF' entry from %s" %self.__target_file)
                    break
        else:
            for linenum in range(len(lines)):
                if lines[linenum].startswith('NOZEROCONF='):
                    lines[linenum] = 'NOZEROCONF=%s\n' % change_record
                    made_change = True
                    break
            messages['messages'].append("Restoring 'NOZEROCONF=%s' in %s" % (change_record, self.__target_file))
        
        if made_change:
            open(self.__target_file,"w").writelines(lines)
        else:
            msg = "Unable to revert change, 'NOZEROCONF' entry not found in %s" % self.__target_file
            messages['messages'].append(msg)
            self.logger.warning(self.module_name,'Undo Error: ' + msg)

        return made_change, '', messages

