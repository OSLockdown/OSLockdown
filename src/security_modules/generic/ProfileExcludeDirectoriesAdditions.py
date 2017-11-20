#!/usr/bin/env python
#
# Copyright (c) 2013 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys

sys.path.append("/usr/share/oslockdown")
import sbProps
import UpdateProfileAdditions

class ProfileExcludeDirectoriesAdditions:
    ##########################################################################
    def __init__(self):
        self.module_name = "ProfileExcludeDirectoriesAdditions"
        
    ##########################################################################
    def scan(self, optionDict={}):

        return UpdateProfileAdditions.writeFile(sbProps.EXCLUSION_DIRS, optionDict['fileList'])

    ##########################################################################
    def apply(self, optionDict={}):

        return UpdateProfileAdditions.writeFile(sbProps.EXCLUSION_DIRS, optionDict['fileList'])

    ##########################################################################
    def undo(self, change_record=None):

        return False, "" , {}
