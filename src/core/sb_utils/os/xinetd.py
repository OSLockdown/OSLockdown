#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import service

sys.path.append('/usr/share/oslockdown')
import TCSLogger

logger = TCSLogger.TCSLogger.getInstance()

##############################################################################
# Determine if XINETD-based service status
##############################################################################
def is_enabled(svcname=None):
    """Determine if a Xinetd-based service is enabled"""

    if svcname == None:
        return None

    fullpath = "/etc/xinetd.d/%s" % svcname
    if not os.path.isfile(fullpath):
        msg = "%s does not exist" % fullpath
        logger.log_debug('sb_utils.os.xinetd', msg)
        return False
    else:
        msg = "Analyzing %s - looking for 'disable = [yes|no]'" % fullpath
        logger.log_debug('sb_utils.os.xinetd', msg)

    try:
        infile = open(fullpath, 'r')
    except IOError, err:
        msg = "Unable to open %s: %s" % (fullpath, err)
        logger.log_err('sb_utils.os.xinetd', msg)
        return None
        
    for line in infile.readlines():
        line = line.strip()
        if line.startswith('service'):
            test = line.split(' ')[1]
            if test != svcname:
                msg = "Service name '%s' does not match the configuration" \
                      " file: '%s'" % (test, fullpath)
                logger.log_warn('sb_utils.os.xinetd', msg)
                infile.close()
                if test == "ftp" and svcname == "gssftp":
                    msg = "'gssftp' maps to 'ftp'; checking status..."
                    logger.log_warn('sb_utils.os.xinetd', msg)
                else:
                    return None
            else:
                msg = "Service name '%s' matches configuration" \
                      " file: '%s'" % (test, fullpath)
                logger.log_debug('sb_utils.os.xinetd', msg)
                continue

        if line.startswith('disable'):
            value = line.split('=')[1].strip()
            infile.close()
            msg = "'%s' has '%s' set in %s" % (svcname, line, fullpath)
            logger.log_info('sb_utils.os.xinetd', msg)
            if value == 'no':
                return True
            else:
                return False
        
    msg = "Could not find 'disable = [yes|no]' in %s" % fullpath
    logger.log_info('sb_utils.os.xinetd', msg)

    msg = "Trying alternate method to determine status of '%s'" % svcname
    logger.log_info('sb_utils.os.xinetd', msg)

    results = service.is_enabled(svcname)
    return results


##############################################################################
# Disable Service
##############################################################################
def disable(svcname=None):

    if svcname == None:
        return None
 
    return service.disable(svcname)


###############################################################################
# Enable Service
###############################################################################
def enable(svcname=None):

    if svcname == None:
        return None

    return service.enable(svcname)
