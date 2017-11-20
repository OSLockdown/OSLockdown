#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Remove the Sync Account 
#
#
##############################################################################

import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
#import sb_utils.acctmgt.users
import sb_utils.acctmgt.acctfiles

class SyncAccount:

    def __init__(self):

        self.module_name = "SyncAccount"
        self.__target_file = '/etc/passwd'
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):
        """Check for presence of sync account."""

        messages = {}
        messages['messages'] = []

        msg = "Checking for 'sync' account in /etc/passwd"
        self.logger.info(self.module_name, msg)

        try:
            pwd.getpwnam('sync')
        except KeyError:
            msg = "'sync' account not present"
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            return True, msg, messages

        msg = "'sync' account present"
        messages['messages'].append("Fail: %s" % msg)
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        return False, msg, messages


    ##########################################################################
    def apply(self, option=None):

        (result, reason, messages) = self.scan()
        if result == True:
            return False, reason, messages

        messages = {}
        messages['messages'] = []

        change_record = {}

        otherdirs = [ "/var/spool/mail/sync" ]
        
        change_record = sb_utils.acctmgt.acctfiles.removeSysAcct(sysAcctName="sync", extraDirs=otherdirs) 
        msg = "'sync' account removed and ownership of associated files changed to root."
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        messages['messages'].append("The 'sync' account has been removed")
        messages['messages'].append("Files previously owned by 'sync' are now owned by root")

        if change_record != None:
            return True, str(change_record), messages
        else:
            messages['messages'].append("'removeSysAcct()' return empty change record")
            return False, 'empty change record', messages   



    ##########################################################################
    def undo(self, change_record=None):

        (result, reason, messages) = self.scan()
        if result == False:
            messages['messages'].append("The 'sync' account already exists. No need for undo")

            # Sending back 'reason' in the change record field will have no 
            # impact since we are returning False. This tells the core engine
            # not to update the state file. 

            return False, reason, messages

        messages = {}
        messages['messages'] = []
        if change_record == None :
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name,  msg)
            messages['messages'].append(msg)
            return False, "No change record", messages


        retval = sb_utils.acctmgt.acctfiles.restoreSysAcct(change_record)
        msg = "'sync' account restored."
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return retval, msg, messages
