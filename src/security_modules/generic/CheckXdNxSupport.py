#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Check CPU to see if it supports the Execute Disable (XD) or No Execute (NX) 
#    (Only on 32-bit x86 Systems)
#
#
##############################################################################

import os
import platform
import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info

class CheckXdNxSupport:

    def __init__(self):
        self.module_name = self.__class__.__name__

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 
        
    ###########################################################################
    def scan(self, option=None):
        messages = {}
        messages['messages'] = []

        if platform.machine() == 'x86_64':
            msg = "Not applicable on Intel-based 64 bit (x86_64) systems"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if platform.machine().startswith('s390'):
            msg = "Not applicable on S390 hardware (System z)"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if  sb_utils.os.info.is_solaris() == True:
            msg = "Not applicable in Solaris"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        has_support = self._hasNDorNXSupport()
        if has_support == True:
            msg = "CPU has NX and PAE support"
        else:
            msg = "CPU does not have NX and PAE support"

        self.logger.debug(self.module_name, msg)
        messages['messages'].append(msg)

        kernel_name = os.uname()[2]
        if not kernel_name.endswith('PAE'):
            msg = "Running kernel is not PAE enabled. (%s does not end with 'PAE')" % kernel_name
            self.logger.info(self.module_name, "Scan Failed: " + msg)
            return False, msg, messages
        else:
            msg = "Running kernel is PAE enabled. (%s ends with 'PAE')" % kernel_name
            return True, msg, messages


    ###########################################################################
    def apply(self, option=None):
        messages = {}
        messages['messages'] = []

        if platform.machine() == 'x86_64':
            msg = "Not applicable on Intel-based 64 bit (x86_64) systems"
            return False, msg, {}

        if platform.machine().startswith('s390'):
            msg = "Not applicable on S390 hardware (System z)"
            return False, msg, {}

        if  sb_utils.os.info.is_solaris() == True:
            msg = "Not applicable in Solaris "
            return False, msg, {}

        has_support = self._hasNDorNXSupport()
        if has_support == True:
            msg = "CPU has NX and PAE support"
        else:
            msg = "CPU does not have NX and PAE support"

        self.logger.debug(self.module_name, msg)
        messages['messages'].append(msg)

        kernel_name = os.uname()[2]
        if not kernel_name.endswith('PAE'):
            msg = "Running kernel is not PAE enabled. (%s does not end with 'PAE')"
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            msg = "YOU must install the 'kernel-pae' package and reboot with this kernel"
            self.logger.info(self.module_name, "Manual: %s" % msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
            #return False, msg, messages
        else:
            msg = "Running kernel is PAE enabled. (%s ends with 'PAE')"
            return False, msg, messages

    ###########################################################################
    def undo(self, change_record=None):
        return False, "Nothing to undo", {}


    def _hasNDorNXSupport(self):
        """Determine if cpu has 'pae' and 'nx' flags"""

        try:
            cpuinfo = open('/proc/cpuinfo', 'r')
        except:
            return None 
 
        lines = cpuinfo.readlines() 
        cpuinfo.close()

        for line in lines:
            if line.startswith('flags'):
                flags = line.split(':')[1].strip().split()
                if 'pae' in flags and 'nx' in flags:
                    return True

        return False
     

if __name__ == '__main__':
    TEST = CheckXdNxSupport()
    print TEST.scan()
    #(x, y, z) = TEST.apply()
    #print x,y,z
    #print TEST.undo(y)
