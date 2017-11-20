#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import pwd
import grp
import stat
import glob

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.dac
import sb_utils.file.fileperms
import GenericPerms

class ConfigureLddPerms:

    def __init__(self):
        self.module_name = "ConfigureLddPerms"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.fileName = "/usr/bin/ldd"
        self.desired_changes = {}

        
    def scan(self, optionDict=None):
        optionDict['fileList'] = self.fileName
        return GenericPerms.scan(optionDict=optionDict)
        
    ##########################################################################
    def apply(self, optionDict=None):
        optionDict['fileList'] = self.fileName
        return GenericPerms.apply(optionDict=optionDict)

    ##########################################################################
    def undo(self, change_record=None):

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|mode|uid|gid\n"  - mode should be interpreted as octal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[2],
                                      'group':fspecs[3],
                                      'dacs':int(fspecs[1], 8)}
            change_record = new_rec
            
        return GenericPerms.undo(change_record=change_record)


if __name__ == '__main__':
    TEST = ConfigureLddPerms()
    print TEST.scan()
    # results, change_record = TEST.apply()
