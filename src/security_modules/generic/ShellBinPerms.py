#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

# This module makes sure that shell binaries (i.e., /bin/bash) are
# owned by root and have permissions no greater than 0755.
# 
# This module first gets a list of default operating system shells
# and then appends any other shells found in /etc/shells to the list.
#
# It then loads the authorized SUID and SGID lists.
#
# Each file must be owned by root or bin, must not have group or 
# world write, and if it has SUID or SGID; it must be listed in 
# the authorized SUID/SGID lists.
#
# If it does not meet the above criteria, the file's ownership is
# is change to root and permissions set to 555.
#

import os
import sys
import pwd
import grp
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms
import sb_utils.file.whitelists
import GenericPerms

class ShellBinPerms:
    """
    ShellBinPerms Security Module handles the guideline for access permissions
    on shell binaries
    """

    def __init__(self):
        self.module_name = "ShellBinPerms"
        self.logger = TCSLogger.TCSLogger.getInstance()

        self._get_shells()
        
    ##########################################################################
    def _get_shells(self):
        
        # Read in /etc/shells and append items to the list (unique of course)
        default_shells = []
        
        try:
            infile = open('/etc/shells', 'r')
            shells = infile.readlines()
            infile.close()
            for shell in shells:
                if os.path.isfile(shell.strip()):
                    default_shells.append(shell.strip())
        except IOError, e:
            msg = "Unable to read '/etc/shells' - may need to use 'Allowed Shells in /etc/shells' Module - %s" % str(e)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
       
        self.shell_list = ' '.join(default_shells)



    ##########################################################################
    def scan(self, optionDict={}):

        optionDict['fileList'] = self.shell_list
        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        optionDict['fileList'] = self.shell_list
        return GenericPerms.apply(optionDict=optionDict)


    ##########################################################################
    def undo(self, change_record=None):


        if not change_record: 
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

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
                                      'dacs':int(fspecs[1],8)}
            change_record = new_rec

        return GenericPerms.undo(change_record=change_record)
            

        return 1

