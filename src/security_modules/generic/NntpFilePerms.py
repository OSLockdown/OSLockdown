#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

import GenericPerms

global QUICK_SCAN
try:
    if QUICK_SCAN == False:
        pass    
except NameError:
    QUICK_SCAN = False

class NntpFilePerms:
    """
    Permissions of files /etc/news
    """

    ##########################################################################
    def __init__(self):
        self.module_name = "NntpFilePerms"
        
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
