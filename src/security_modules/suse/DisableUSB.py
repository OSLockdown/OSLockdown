#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import sb_utils.os.syslog
import tcs_utils

class DisableUSB:
    """
    Disable the USB and PCMCIA subsystems.
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'DisableUSB'

        cfg_files = [ "/etc/modprobe.d/50-blacklist.conf" ,
                      "/etc/modprobe.d/blacklist.conf",
                      "/etc/modprobe.d/blacklist",
                      "/etc/modprobe.conf" ]

        for cfg_file in cfg_files:
            if os.path.exists(cfg_file):
                self.__target_file = cfg_file


        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 



    ##########################################################################
    def validate_input(self, option_str):
        """Expect either a one or a two
           If you don't get either, then fail
        """

        if not option_str or int(option_str) not in [1, 2]:
            msg = "Invalid option present (%s) - no action taken" % str(option_str)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = int(option_str)
        
        self.change_set = {}
        ctm = []
        # These are the lines to turn off the usb-storage and pcmcia modules
        ctm.append( {'search'       : [ '^remove\s+(usb-|usb_)storage\s+/sbin/modprobe\s+-r\s+(usb-|usb_)storage$' ],
                     'replace_with' : 'remove usb-storage /sbin/modprobe -r usb-storage'})
        ctm.append( {'search'       : [ '^blacklist\s+usb-storage$', '^blacklist\s+usb_storage$'],
                     'replace_with' : 'blacklist usb-storage'})
        ctm.append( {'search'       : [ '^blacklist\s+usb-storage.ko$', '^blacklist\s+usb_storage.ko$' ],
                     'replace_with' : 'blacklist usb-storage.ko'})
        ctm.append( {'search'       : [ '^blacklist\s+pcmcia$' ],
                     'replace_with' : 'blacklist pcmcia'})

        if option == 1:
            ctm.append( {'search'       : [ '^blacklist\s+usb-storage.ko$', '^blacklist\s+usb_storage.ko$' ],
                         'replace_with' : 'blacklist usb-storage.ko'})
        
        self.change_set[self.__target_file] = ctm                         
        
        try:
            value = int(option_str)
        except ValueError:
            return 1
        if value < 1 or value > 2:
            return 1
        return 0

    ##########################################################################
    def process_change_set(self, change_set, action):
        messages = []
        changes = {}
        for file_to_change in change_set:
            changes_to_make = change_set[file_to_change]
            
            m, c = sb_utils.os.syslog.process_arbitary_file(file_to_change, changes_to_make, action)

            messages.extend(m)
            if c != []:
                changes[file_to_change] = c
        
        return messages, changes
        
    ##########################################################################
    def scan_TBD(self, option=None):
    

        messages = []

        option = int(option)
        
        all_messages, changes = self.process_change_set(self.change_set, "scan")
        
        for level, text in all_messages:
            if level in ['ok']:
                self.logger.notice(self.module_name, text)
                messages.append(text)
            elif level in [ 'problem']:
                self.logger.info(self.module_name, text)
                messages.append(text)
            elif level in ['error' ]:
                self.logger.error(self.module_name, text)
                messages.append(text)
        if changes != {}:
            retval = False
        else: 
            retval = True
    
        return retval, "", {'messages':messages}
    
    
    ##########################################################################
    def apply_TBD(self, option=None):
        messages = []

        option = int(option)
        all_messages, changes = self.process_change_set(self.change_set, "apply")
        
        for level, text in all_messages:
            if level in ['ok']:
                self.logger.notice(self.module_name, text)
                messages.append(text)
            elif level in [ 'problem', 'fix']:
                self.logger.info(self.module_name, text)
                messages.append(text)
            elif level in ['error' ]:
                self.logger.error(self.module_name, text)
                messages.append(text)

        if changes == {}:
            retval = False
            changes = ""
        else: 
            retval = True
    
        return retval, str(changes), {'messages':messages}

    ##########################################################################
    def undo_TBD(self, change_record=None):
        """Undo the previous action."""

         
        messages = []
        if change_record == 'none':
            #Ok, we need to create our remove data from whole cloth...
            change_set = {}
            ctm = []    
            ctm.append( {'search' : 'remove usb-storage /sbin/modprobe -r usb-storage' })
            change_set[self.__target_file] = ctm                         
        else:
            change_set = tcs_utils.string_to_dictionary(change_record)
        
        all_messages, changes = self.process_change_set(change_set, "undo")
        
        for level, text in all_messages:
            if level in ['ok']:
                self.logger.notice(self.module_name, text)
                messages.append(text)
            elif level in [ 'problem', 'fix']:
                self.logger.info(self.module_name, text)
                messages.append(text)
            elif level in ['error' ]:
                self.logger.error(self.module_name, text)
                messages.append(text)

        if changes == {}:
            retval = False
            changes = ""
        else: 
            retval = True
    
        return retval, str(changes), {'messages':messages}

    ##########################################################################
    def scan(self, optionDict=None):
        msg = "Module is currently unsupported (TCS is investigating correct actions)"
        raise tcs_utils.ModuleUnsupported('%s %s' % (self.module_name, msg))

    ##########################################################################
    def apply(self, optionDict=None):
        messages = []
        msg = "Module is currently unsupported (TCS is investigating correct actions)"
        raise tcs_utils.ModuleUnsupported('%s %s' % (self.module_name, msg))
           
    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""
        msg = "Module is currently unsupported (TCS is investigating correct actions)"
        raise tcs_utils.ModuleUnsupported('%s %s' % (self.module_name, msg))
