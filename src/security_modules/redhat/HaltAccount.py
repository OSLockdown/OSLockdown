#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Remove the Halt Account 
#
#
##############################################################################

import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
#import sb_utils.acctmgt.users
import sb_utils.acctmgt.acctfiles

class HaltAccount:

    def __init__(self):

        self.module_name = "HaltAccount"
        self.__target_file = '/etc/passwd'
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):
        """Check for presence of halt account."""

        messages = {}
        messages['messages'] = []

        msg = "Checking for 'halt' account in /etc/passwd"
        self.logger.info(self.module_name, msg)

        try:
            pwd.getpwnam('halt')
        except KeyError:
            msg = "'halt' account not present"
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            return True, msg, messages

        msg = "'halt' account present"
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

        otherdirs = [ "/var/spool/mail/halt" ]
        
        change_record = sb_utils.acctmgt.acctfiles.removeSysAcct(sysAcctName="halt", extraDirs=otherdirs) 
        msg = "'halt' account removed and ownership of associated files changed to root."
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        messages['messages'].append("The 'halt' account has been removed")
        messages['messages'].append("Files previously owned by 'halt' are now owned by root")

        if change_record != None:
            return True, str(change_record), messages
        else:
            messages['messages'].append("'removeSysAcct()' return empty change record")
            return False, 'empty change record', messages   



    ##########################################################################
    def undo(self, change_record=None):

        (result, reason, messages) = self.scan()
        if result == False:
            messages['messages'].append("The 'halt' account already exists. No need for undo")

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

        if change_record == "":
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            messages['messages'].append(msg)
            return False, "Empty change record", messages

 
        # Unfortunately an old style change record (pre 4.0.2) was an empty 
        # string.  We'll never see an empty change record passed in, so we're 
        # out of luck trying to restore this. If we *do* every allow for an 
        # empty change record then we can restore the account as 4.0.1 or 
        # earlier would have with the following code

        if change_record == "":
            acctinfo = {'uname':   'halt', 
                        'uid':     -1, 
                        'gname':   'root', 
                        'gid':     0, 
                        'gecos':   '',
                        'homedir': '/sbin',
                        'shell':   '/sbin/halt' }

            filelist = {'/var/spool/mail/halt': {'owner': 'halt', 'group':'root'}}
            change_record = {'acctinfo': acctinfo, 'filelist': filelist}
        

        retval = sb_utils.acctmgt.acctfiles.restoreSysAcct(change_record)
        msg = "'halt' account restored."
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return retval, msg, messages
