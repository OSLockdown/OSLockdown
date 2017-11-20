#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable Firewire Kernel Module
#
#


import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import GenericKernelModprobe

class DisableKernelFirewire(GenericKernelModprobe.GenericKernelModprobe):

    def __init__(self):
        GenericKernelModprobe.GenericKernelModprobe.__init__(self, "DisableKernelFirewire")
        
        self.module_name = "DisableKernelFirewire"
        

if __name__ == '__main__':
    TEST = DisableKernelFirewire()
    optionDict = {'requiredLines': "install ieee1394 /bin/true" } 
    print TEST.scan(optionDict)
#    print TEST.apply()
