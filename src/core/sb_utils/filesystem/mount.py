##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

#
# Filesystem Module
#

import sys
import re
import os

sys.path.append('/usr/share/oslockdown')
try:
    import TCSLogger
    import sb_utils.os.info
except ImportError, merr:
    print "Unable to load modules: %s" % merr
    sys.exit(1)

MODULE_NAME = 'sb_utils.filesystem.mount'


##############################################################################
def list():
    """List of mounted filesystems and types"""

    logger = TCSLogger.TCSLogger.getInstance()

    mount_list = {}

    if sb_utils.os.info.is_solaris() == True:
        return __solaris_list()
    else:
        return __redhat_list()

          
##############################################################################
def __redhat_list():
    """RedHat mounted filesystem list"""

    mount_list = {}

    logger = TCSLogger.TCSLogger.getInstance()
    try:
        infile = open('/etc/mtab', 'r')
    except IOError, err:
        logger.log_err(MODULE_NAME, "Unable to open /etc/mtab: %s" % err)
        return mount_list

    logger.log_debug(MODULE_NAME, "Scanning /etc/mtab")
    for line in infile.readlines():
        fields = line.strip('\n').split(' ')
        mount_list[fields[1]] = fields[2]        

    msg = "Found %d mounted filesystems: %s" % (len(mount_list), str(mount_list.keys()))
    logger.log_debug(MODULE_NAME, msg)
    
    infile.close()
    del msg
    del infile
    del logger

    return mount_list

##############################################################################
def __solaris_list():
    """Solaris mounted filesystem list"""

    mount_list = {}

    logger = TCSLogger.TCSLogger.getInstance()
    try:
        infile = open('/etc/mnttab', 'r')
    except IOError, err:
        logger.log_err(MODULE_NAME, "Unable to open /etc/mnttab: %s" % err)
        return mount_list

    logger.log_debug(MODULE_NAME, "Scanning /etc/mnttab")
    for line in infile.readlines():
        fields = line.strip('\n').split('\t')
        mount_list[fields[1]] = fields[2]

    msg = "Found %d mounted filesystems: %s" % (len(mount_list), str(mount_list.keys()))
    logger.log_debug(MODULE_NAME, msg)

    infile.close()
    del msg
    del infile
    del logger

    return mount_list


##############################################################################
if __name__ == '__main__':
    print list()
