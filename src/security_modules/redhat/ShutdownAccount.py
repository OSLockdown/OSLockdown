#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import pwd
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
#import sb_utils.acctmgt.users
import sb_utils.acctmgt.acctfiles

class ShutdownAccount:

    def __init__(self):

        self.module_name = "ShutdownAccount"
        self.__target_file = '/etc/passwd'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Check for presence of shutdown account."""


        msg = "Checking for 'shutdown' account in /etc/passwd"
        self.logger.info(self.module_name, msg)

        try:
            pwd.getpwnam('shutdown')
        except KeyError:
            return 'Pass', ''

        msg = "'shutdown' account present"
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
        return 'Fail', msg

    ##########################################################################
    def apply(self, option=None):
        """Remove shutdown account."""


        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''


        change_record = {}

        otherdirs = [ "/var/spool/mail/shutdown" ]
        
        change_record = sb_utils.acctmgt.acctfiles.removeSysAcct(sysAcctName="shutdown", extraDirs=otherdirs) 
        msg = "'shutdown' account removed and ownership of associated files changed to root."
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, str(change_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if change_record == None :
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name,  msg)
            return 0

        if change_record == "":
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            return 0

        # Unfortunately an old style change record (pre 4.0.2) was an empty string.  We'll never see an empty change record 
        # passed in, so we're out of luck trying to restore this.  
        # If we *do* every allow for an empty change record then we can restore the account as 4.0.1 or earlier would have with
        # the following code
        
        if change_record == "":
            acctinfo={'uname':'shutdown','uid':6,'gname':'root','gid':0,'gecos':'','homedir':'/sbin','shell':'/sbin/shutdown'}
            filelist={'/var/spool/mail/shutdown':{'owner':'shutdown','group':'root'}}
            change_record={'acctinfo':acctinfo,'filelist':filelist}
        

        retval = sb_utils.acctmgt.acctfiles.restoreSysAcct(change_record)
        msg = "'halt' account restored."
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)


        return retval

