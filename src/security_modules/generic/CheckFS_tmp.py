#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Ensure the specific directory path is its own, dedicated file system. 
#
#
#############################################################################

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux
import sb_utils.filesystem.mount

class CheckFS_tmp:

    def __init__(self):
        self.module_name = "CheckFS_tmp"
        self.__fsname = '/tmp'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option=None):

        messages = {'messages' : [] }

        msg = "Checking to see if %s is a separate file system" % self.__fsname
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        fslist = sb_utils.filesystem.mount.list()
        if fslist == {}:
            msg = "Unable to retrieve list of mounted file systems."
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = '' 
        results = False
        if self.__fsname in fslist.keys():
            msg = "%s (%s) is mounted separately." % (self.__fsname, fslist[self.__fsname])
            results = True
        else:
            msg = "%s is NOT mounted separately." % self.__fsname
        
        return results, msg, messages

    ##########################################################################
    def apply(self, option=None):

        messages = {}
        action_record = 'none'
        try:
            (result, reason, messages) = self.scan()
            if result == False:
                msg = "Manual Action: You must create a separate file system for %s" % self.__fsname
                self.logger.info(self.module_name, msg)
                raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        except tcs_utils.ScanError, err:
            self.logger.error(self.module_name, err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))


        return False, action_record, messages

    ##########################################################################
    def undo(self, change_record=None):
        return False, "Nothing to undo", {}


#if __name__ == '__main__':
#    Test = CheckFS_tmp()
#    print Test.scan()
#    print Test.apply()
#    print Test.undo()
