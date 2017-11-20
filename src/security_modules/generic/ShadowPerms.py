#!/usr/bin/env python
#
# Copyright (c) 2012 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import sha

import  xml.sax.saxutils

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import GenericPerms
import sb_utils.os.info

class ShadowPerms:
    """
    Ensure the permissions on the /etc/gshadow accurate for the Guideline specificed
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "ShadowPerms"
        
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, optionDict={}):

        # For SUSE/openSUSE platform, we need to make sure that 'shadow' is the only allowed owner.  This is an explicit override and should
        # be made *very* obvious in the logs.        
        if sb_utils.os.info.is_LikeSUSE():
            optionDict['allowedGnames'] = 'shadow'
            msg = "SUSE/openSUSE OS detected, shadow files *must* be owned by the 'shadow' group"
            self.logger.notice(self.module_name, msg)
            
        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        # For SUSE/openSUSE platform, we need to make sure that 'shadow' is the only allowed owner.  This is an explicit override and should
        # be made *very* obvious in the logs.        
        if sb_utils.os.info.is_LikeSUSE():
            optionDict['allowedGnames'] = 'shadow'
            msg = "SUSE/openSUSE OS detected, shadow files *must* be owned by the 'shadow' group"
            self.logger.notice(self.module_name, msg)
        return GenericPerms.apply(optionDict=optionDict)

    ##########################################################################
    def undo(self, change_record=None):

        return GenericPerms.undo(change_record=change_record)
