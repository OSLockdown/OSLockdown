#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Solaris 10 Specific Features
#   This module provides functions that are unique to the 
#   Solaris operating system such as Zones.
#


import sys
import re
import os

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils

##############################################################################
def zonename():
    """Return zonename"""
    
    logger = TCSLogger.TCSLogger.getInstance()

    cmd = '/sbin/zonename'
    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        msg = "Execution of '%s' failed: %s" % (cmd, output[2])
        logger.log_err('sb_utils.os.solaris', msg)
        del logger
        return None
    else:
        msg = "Execution of '%s' succeeded: %s" % (cmd, output[1].rstrip())
        logger.log_debug('sb_utils.os.solaris', msg)
        del logger
        return output[1].rstrip('\n')


##############################################################################
def ndd_get(param=None, driver=None):
    """
    Get ndd parameter
    """

    if param == None or driver == None:
        return None


    logger = TCSLogger.TCSLogger.getInstance()
 
    cmd = '/usr/sbin/ndd -get /dev/%s %s' % (driver, param)
    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        msg = "Execution of '%s' failed: %s" % (cmd, output[2])
        logger.log_err('sb_utils.os.solaris', msg)
        del logger
        return None
    else:
        msg = "Execution of '%s' succeeded: %s" % (cmd, output[1])
        logger.log_debug('sb_utils.os.solaris', msg)
        del logger
        return output[1].rstrip('\n')

##############################################################################
def ndd_set(param=None, paramValue=None, driver=None):
    """
    Get ndd parameter
    """
    logger = TCSLogger.TCSLogger.getInstance()

    if param == None or driver == None or paramValue == None:
        return False

    if paramValue == "":
        msg = "Ndd does not allow 'unsetting' of a value - reboot to pick up the default (if any) in /etc/default/ndd"
        logger.log_notice('sb_utils.os.solaris.ndd_set', msg)
        return True
        
    logger = TCSLogger.TCSLogger.getInstance()
 
    cmd = '/usr/sbin/ndd -set /dev/%s %s %s' % (driver, param, paramValue)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Execution of '%s' failed: %s" % (cmd, output[2])
        logger.log_err('sb_utils.os.solaris', msg)
        del logger
        return False
    else:
        msg = "Execution of '%s' succeeded: %s" % (cmd, output[1])
        logger.log_debug('sb_utils.os.solaris', msg)
        del logger
        return True

##############################################################################
def zonelist():
    """
    Return a list of zone names
    """
    logger = TCSLogger.TCSLogger.getInstance()
    myzonelist = []

    cmd = '/usr/sbin/zoneadm list'

    if not os.path.isfile('/usr/sbin/zoneadm'):
        msg = "%s command not available" % cmd
        logger.log_notice('sb_utils.os.solaris', msg)
        return None

    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        msg = "Execution of '%s' failed: %s" % (cmd, output[2])
        logger.log_err('sb_utils.os.solaris', msg)
        del logger
        return None

    msg = "Execution of '%s' succeeded: %s" % (cmd, output[1])
    logger.log_debug('sb_utils.os.solaris', msg)

    for zone in output[1].split('\n'):
        if not zone: 
            continue
        else:
            myzonelist.append(zone)
         
    return myzonelist


##############################################################################
def zonepath(zonename=None):
    """
    Get Zone's filesystem path
    """

    if zonename == None:
        return None

    if zonename == 'global':
        return None

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    cmd = "/usr/sbin/zonecfg -z %s info zonepath" % zonename
    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        msg = "Execution of '%s' failed: %s" % (cmd, output[2])
        logger.log_err('sb_utils.os.solaris', msg)
        del logger
        return None
    else:
        msg = "Execution of '%s' succeeded: %s" % (cmd, output[1])
        logger.log_debug('sb_utils.os.solaris', msg)
        del logger
        line = output[1].rstrip('\n')
        try:
            line = line.split(':')[1].lstrip(' ')
        except IndexError:
            return None
        return line


##############################################################################
def patchlist():
    """
    Return a dictionary of installed patches
    """

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()


    patchdict = {}

    cmd = "/usr/bin/showrev -p"
    try:
        pipe = os.popen(cmd, 'r')
    except KeyboardInterrupt:
        msg = "Caught keyboard interrupt; command did not complete"
        logger.log_crit('sb_utils.os.solaris', msg)
        del logger
        return {}

    regex = "Patch: (.*) Obsoletes: (.*) Requires: (.*) Incompatibles: (.*) Packages: (.*)"
    for line in pipe.readlines():
        scrubbed_line = unicode(line.strip(), 'utf-8')
        results = re.match(regex, scrubbed_line)

        patchnum = results.group(1)
        #patchobs = results.group(2).split(', ')
        #patchreq = results.group(3).split(', ')
        #patchcom = results.group(4).split(', ')
        patchpkg = results.group(5).split(', ')
        for pkg in patchpkg:
            if not patchdict.has_key(pkg.strip()):
                patchdict[pkg.strip()] = []
            patchdict[pkg.strip()].append(patchnum)

    del logger 
    return patchdict
