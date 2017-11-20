#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable IA32 Microcode Utility
#
#
##############################################################################

import sys
import os
sys.path.append('/usr/share/oslockdown')
import tcs_utils

try:
    import Enable_Disable_Any_Service
except ImportError:
    raise

class DisableIA32MicrocodeUtility:

    def __init__(self):
        self.module_name = self.__class__.__name__
        self.__IA32 = self._isOldIntelCpuPresent()


    def scan(self, option=None):
        if self.__IA32 == True:
            msg = "An Intel CPU (Family < 6) is installed"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        if not os.path.exists('/etc/init.d/microcode.ctl'):
            msg = "The 'microcode_ctl' service does not seem to be present"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        
        return Enable_Disable_Any_Service.scan(self.module_name, enable=False)    


    def apply(self, option=None):
        messages = {}
        messages['messages'] = []
        if self.__IA32 == True:
            msg = "An Intel CPU (Family < 6) is installed"
            messages['messages'].append(msg)
            messages['messages'].append('Not disabling the service utility')
            return False, msg, messages

        if not os.path.exists('/etc/init.d/microcode.ctl'):
            msg = "The 'microcode_ctl' service does not seem to be present"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        return Enable_Disable_Any_Service.apply(self.module_name, enable=False)    


    def undo(self, change_record=None):
        return Enable_Disable_Any_Service.undo(self.module_name, change_record=change_record)    


    def _isOldIntelCpuPresent(self):
        """Determine if an older IA32 Intel CPU is present. (Family < 6)"""
        try:
            cpuinfo = open('/proc/cpuinfo', 'r')
        except:
            return None 
 
        lines = cpuinfo.readlines() 
        cpuinfo.close()

        current_cpu_vendor = ""
        for line in lines:
            if line.startswith('vendor_id'):
                current_cpu_vendor = line.split(':')[1].strip()

            if line.startswith('cpu family'):
                cpu_family = line.split(':')[1].strip()
                if cpu_family.isdigit():
                    if int(cpu_family) < 6 and current_cpu_vendor == 'GenuineIntel':
                        return True

        return False
