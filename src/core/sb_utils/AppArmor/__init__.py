#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# SUSE AppArmor 
#
#

MODULE_NAME = "AppArmor"
MODULE_REV  = "$Rev: 23917 $".strip('$').strip()

import sys
import os
import re

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils
import sb_utils.os.info 


LOADED = False
CONF_DIR = '/etc/apparmor'

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()



def isLoaded():
    """Determine if AppArmor Kernel module is loaded"""

    if sb_utils.os.info.is_LikeSUSE() == False:
        return False


    if os.path.isdir('/sys/module/apparmor'):
        return True

    try:
        modlist = open("/proc/modules", "r")
    except (IOError, OSError), err:
        logger.error(MODULE_NAME, str(err))
        return False

    regexp = re.compile('^(subdomain|apparmor)\s+')
    lines = modlist.readlines()
    modlist.close()
    for line in lines:
        if regexp.search(line):
            return True
        
    return False

##############################################################################
LOADED = isLoaded()
