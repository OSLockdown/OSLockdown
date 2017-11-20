#!/usr/bin/python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import stat
import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sbProps
import sb_utils.os.info
import sb_utils.os.software

try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

MODULE_NAME = 'sb_utils.file.info'

##############################################################################
def elfSize(filepath=None):
    """
    Determine file type. Currently, this function only returns 'elf64', 'elf32',
    or '' if it isn't an ELF or if just can't figure it out.
    """
    retString = ''
    try:
        f = open(filepath, 'rb')
        padding = f.read(1)
        f_type = str(f.read(3))
        if f_type == 'ELF':
            f_bitsize = ord(f.read(1))
            if f_bitsize == 2:
                retString = 'elf64'
            if f_bitsize == 1:
                retString = 'elf32'
        f.close()
    
    except:
        pass

    return retString


if __name__ == '__main__':
    print elfSize(filepath='/usr/share/oslockdown/lib/libAffirm.so')
