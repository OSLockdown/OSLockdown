#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
#

import sys
import os
import pwd
import grp

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import GenericPerms

class MIBFilePerms:

    def __init__(self):
        self.module_name = "MIBFilePerms"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT
        self.logger = TCSLogger.TCSLogger.getInstance()
        

    ##########################################################################
    def scan(self, optionDict={}):
        """
        Initiating File System Scan to find unowned files
        """

        return GenericPerms.scan(optionDict=optionDict)

    ##########################################################################
    def apply(self, optionDict={}):
        """Change user/group of unowned files to nobody"""

        return GenericPerms.apply(optionDict=optionDict)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo removal of user/group change of unowned files"""

        return GenericPerms.undo(change_record=change_record)

if __name__ == "__main__":
    test = MIBFilePerms()
    options = {'dacs':644}
    print test.scan(options)
