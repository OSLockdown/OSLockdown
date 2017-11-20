#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Remove the ftp account
#
#

import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.info
#import sb_utils.acctmgt.users
import sb_utils.acctmgt.acctfiles

class RemoveFTPaccount:

    def __init__(self):

        self.module_name = "RemoveFTPaccount"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):
        """Check for presence of ftp account."""
        if option != None: 
            option = None

        messages = {}
        messages['messages'] = []
        msg = "Checking for 'ftp' account in /etc/passwd"
        self.logger.info(self.module_name, msg)
        try:
            pwd.getpwnam('ftp')
        except KeyError:
            msg = "'ftp' account not present"
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            return True, msg, messages

        msg = "'ftp' account present"
        messages['messages'].append("Fail: %s" % msg)
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        return False, msg, messages


    ##########################################################################
    def apply(self, option=None):

        if option != None:
            option = None


        (result, reason, messages) = self.scan()
        if result == True:
            return False, reason, messages

        messages = {}
        messages['messages'] = []
        change_record = {}

        otherdirs = [ "/var/spool/mail/ftp"]
        
        change_record = sb_utils.acctmgt.acctfiles.removeSysAcct(sysAcctName="ftp", extraDirs=otherdirs) 
        msg = "'ftp' account removed and ownership of associated files changed to root."
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        messages['messages'].append("The 'ftp' account has been removed")
        messages['messages'].append("Files previously owned by 'ftp' are now owned by root")

        if change_record != None:
            return True, str(change_record), messages
        else:
            messages['messages'].append("'removeSysAcct()' return empty change record")
            return False, 'empty change record', messages   

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        (result, reason, messages) = self.scan()
        if result == False:
            messages['messages'].append("The 'ftp' account already exists.  No need for undo")
            return False, reason, messages

        messages = {}
        messages['messages'] = []

        if change_record == None : 
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            messages['messages'].append(msg)
            return False, 'no change record', messages

        if change_record == "":
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            messages['messages'].append(msg)
            return False, 'empty change record', messages

        # A 4.0.1 or earlier change record only had the uid of the account that had been deleted, and then the undo would explicitly
        # reference the /var/spool/mail/ftp file for chown-ing.
        # A 4.0.2 change record was a list with a string as the first element holding the account info, and remainging elements
        # being strings olding the name/uid/gid to restore
        # We need to handle both cases.  The uid only we can handle here by detecting a *short* first string with a single integer
        # value.  The second case we'll pass in to the restoreSysAccount directly, as it understands how to convert the 4.0.2 record
        
        uid = 0
        if len(change_record) < 10:
            uid = int(change_record[0:10].strip())
            if uid > 0: 
                msg = "detetecting 4.0.1 or earlier change record and translating to new change record format"
                self.logger.info(self.module_name,'Undo: ' + msg)
                acctinfo = {'uname':'ftp',
                        'uid':uid,
                        'gname':'ftp',
                        'gid':50,
                        'gecos':'ftp',
                        'homedir':'/var/ftp',
                        'shell':''}
                filelist = {'/var/spool/mail/ftp':{'group':'ftp', 'owner':'ftp'}}
                change_record = {'acctinfo':acctinfo, 'filelist':filelist}
            else:
                msg = "Malformed change record, restoration of 'ftp' account aborted with no changes"
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                messages['messages'].append(msg)
                return False, 'malformed change record', messages
                    
        retval = sb_utils.acctmgt.acctfiles.restoreSysAcct(change_record)
        msg = "'ftp' account restored."
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        messages['messages'].append(msg)
        return retval, msg, messages


