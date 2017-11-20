#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.exclusion
import sb_utils.file.fileperms

import pwd
import grp
import GenericPerms


class InetdXinetdConfigFilePerms:

    def __init__(self):
        self.module_name = "InetdXinetdConfigFilePerms"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, optionDict={}):

        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        return GenericPerms.apply(optionDict=optionDict)

    ##########################################################################
    def undo(self, change_record=None):

        return GenericPerms.undo(change_record=change_record)

