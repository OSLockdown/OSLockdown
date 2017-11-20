#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import os
import stat
import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import GenericPerms
import sb_utils.file.fileperms

class RootHomePerms:
    """
    RootHomePerms Security Module handles the guideline for access permissions
    on root's home directory.
    """

    def __init__(self):
        self.module_name = "RootHomePerms"
        self.__target_file = '/root'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, optionDict=None):

        # First, let's see if root's home directory is /root
        u_obj = pwd.getpwnam('root')
        if u_obj[5] != '/root':
            reason = "Root home directory IS NOT /root; you must manually " \
                     "change root's home directory or this module will continue to fail."
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, reason))

        optionDict['fileList'] = u_obj[5]
        return GenericPerms.scan(optionDict=optionDict)
        


    ##########################################################################
    def apply(self, optionDict=None):

        # First, let's see if root's home directory is /root
        u_obj = pwd.getpwnam('root')
        if u_obj[5] != '/root':
            reason = "Root home directory IS NOT /root; you must manually " \
                     "change root's home directory or this module will continue to fail."
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, reason))

        optionDict['fileList'] = u_obj[5]
        return GenericPerms.apply(optionDict=optionDict)

            
    ##########################################################################
    def undo(self, change_record=None):

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # Old style change record was simply the permissions to restore, so if we only get a number as the change_record
        # treat it as such (with DECIMAL perms) and create the newstyle change record

        if not change_record[0:200].strip().startswith('{') :
            newperms = int(change_record, 10)
            change_record = {}
            change_record[self.__target_file] = {'dacs':newperms}
        else:
            change_record = tcs_utils.string_to_dictionary(change_record)

        return GenericPerms.undo(change_record=change_record)
                


