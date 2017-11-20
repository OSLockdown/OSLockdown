#!/usr/bin/env python
#
# Copyright (c) 2007 Forcepoint LLC.
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

class RestrictTracerouteUse:
    """
    
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "RestrictTracerouteUse"
        
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
