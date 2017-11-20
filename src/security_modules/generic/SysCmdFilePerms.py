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
import sb_utils.os.info
import TCSLogger
import GenericPerms

class SysCmdFilePerms:
    ##########################################################################
    def __init__(self):
        self.module_name = "SysCmdFilePerms"
        
        self.logger = TCSLogger.TCSLogger.getInstance()

    def addShadow(self, nameList, listType):
        names = tcs_utils.splitNaturally(nameList, wordAdditions="<>*-_", whitespaceAdditions=",", uniq=True)
        if 'shadow' not in names:
            names.append('shadow')
            nameList = ' '.join(names)
            msg = "SUSE/openSUSE OS detected, adding 'shadow' to the approved %s users" % listType
            self.logger.notice(self.module_name, msg)
        return nameList
        
    ##########################################################################
    def scan(self, optionDict={}):

        if sb_utils.os.info.is_LikeSUSE():
            optionDict['allowedGnames'] = self.addShadow(optionDict['allowedGnames'], 'group')
            
        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        if sb_utils.os.info.is_LikeSUSE():
            optionDict['allowedGnames'] = self.addShadow(optionDict['allowedGnames'], 'group')
        return GenericPerms.apply(optionDict=optionDict)

    ##########################################################################
    def undo(self, change_record=None):

        return GenericPerms.undo(change_record=change_record)
