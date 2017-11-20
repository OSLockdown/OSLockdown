#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import stat
import sys
import pwd
import grp
import sb_utils.file.fileperms

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import GenericPerms

class PasswdPerms:

    def __init__(self):
        self.module_name = "PasswdPerms"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, optionDict={}):

        # For SUSE/openSUSE platform, we need to make sure that 'shadow' is the only allowed owner.  This is an explicit override and should
        # be made *very* obvious in the logs.        
        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        # For SUSE/openSUSE platform, we need to make sure that 'shadow' is the only allowed owner.  This is an explicit override and should
        # be made *very* obvious in the logs.        
        return GenericPerms.apply(optionDict=optionDict)

    ##########################################################################
    def undo(self, change_record=None):

            
        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|mode|uid|gid\n"  - mode should be interpreted as DECIMAL
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[2],
                                      'group':fspecs[3],
                                      'dacs':int(fspecs[1],10)}
            change_record = str(new_rec)
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1


