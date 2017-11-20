#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Ensure System library files do not have permissions greater than 755
# 

import os
import sys
import stat
import pwd


sys.path.append("/usr/share/oslockdown")
import TCSLogger
import GenericPerms

class SysLibFilePerms:
    """
    SysLibFilePerms Security Module handles the guideline for access 
    permissions on system library files.
    """

    def __init__(self):
        self.module_name = "SysLibFilePerms"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, optionDict={}):

        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        return GenericPerms.apply(optionDict=optionDict)

    ########################################################################## 
    def undo(self, change_record=None):

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 0

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|mode\n"  - mode should be interpreted as decimal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 2:
                    continue
                new_rec[fspecs[0]] = {'dacs':int(fspecs[1], 10)}
            change_record = new_rec
            
        return GenericPerms.undo(change_record=change_record)
     
