#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable fstypes Kernel Module
#
#


# CCE-14089-7 Disable Cramfs 
# CCE-14457-6 Disable freevxfs 
# CCE-15087-0 Disable hfs 
# CCE-14093-9 Disable hfsplus
# CCE-14853-6 Disable jffs2 
# CCE-14118-4 Disable squashfs
# CCE-14871-8 Disable udf


import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import GenericKernelModprobe

class DisableKernelSprt_fstypes(GenericKernelModprobe.GenericKernelModprobe):

    def __init__(self):
        GenericKernelModprobe.GenericKernelModprobe.__init__(self, "DisableKernelSprt_fstypes")
        self.module_name = "DisableKernelSprt_fstypes"
        
