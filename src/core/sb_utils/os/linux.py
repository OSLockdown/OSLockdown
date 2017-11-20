#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Linux Specific Features
#   This module provides functions that are unique to the 
#   Linux operating system such as sysctl.
#


import sys

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils

MODULE_NAME = 'sb_utils.os.linux'

##############################################################################
class sysctl:
    def __init__(self):
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

    def getlist(self):
        sysdict = {}

        results = tcs_utils.tcs_run_cmd('/sbin/sysctl -a', True)
        if results[0] != 0: 
            self.logger.log_err(MODULE_NAME, results[2])
            return sysdict
    
        for line in results[1].split('\n'):
            try:
                param    = line.split('=')[0].strip()
                paramval = line.split('=')[1].strip()
                sysdict[param] = paramval
            except IndexError:
                continue


        del results
        return sysdict



    def setparam(self, paramname=None, paramval=None):
        if paramname == None or paramval == None:
            return False

        cmd = "/sbin/sysctl -w %s=%s" % (str(paramname), str(paramval))
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0: 
            self.logger.log_err(MODULE_NAME, results[2])
            return False

        del results
        return True



##############################################################################
