#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Remove the gnome-games account (the 'games' account)
#
#
#

import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.software
#import sb_utils.acctmgt.users
import sb_utils.acctmgt.acctfiles

class RemoveGamesAccount:

    def __init__(self):

        self.module_name = "RemoveGamesAccount"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):
        """Check for presence of games account."""
        if option != None: 
            option = None

        messages = {}
        messages['messages'] = []

        msg = "Checking for 'games' account in /etc/passwd"
        self.logger.info(self.module_name, msg)
        try:
            pwd.getpwnam('games')
        except KeyError:
            msg = "'games' account not present"
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            return True, msg, messages

        msg = "'games' account present"
        messages['messages'].append("Fail: %s" % msg)
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        return False, msg, messages


    ##########################################################################
    def apply(self, option=None):
        """Remove games user account."""
        if option != None:
            option = None


        (result, reason, messages) = self.scan()
        if result == True:
            return False, reason, messages

        messages = {}
        messages['messages'] = []
        change_record = {}

        results = sb_utils.os.software.is_installed(pkgname='gnome-games')
        if results == True:
            msg = "'gnome-games' package is installed, you should manually remove this package"

            self.logger.notice(self.module_name, msg)           

#        otherdirs = [ "/var/lib/games" , "/var/spool/games", "/usr/bin", "/var/spool/mail/games" ]
        otherdirs = []
        otherfiles = sb_utils.os.software.listAllFilesForPackage('gnome-games')
        change_record = sb_utils.acctmgt.acctfiles.removeSysAcct(sysAcctName="games", extraDirs=otherdirs, extraFiles=otherfiles) 
        msg = "'gnome-games' account removed and ownership of associated files changed to root."
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        
        messages['messages'].append("The 'games' account has been removed")
        messages['messages'].append("Files previously owned by 'games' are now owned by root")


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
            messages ['messages'].append("The 'halt' account already exists.  No need for undo")
            return False, reason, messages
            
        messages = {}
        messages['messages'] = []
        if change_record == None:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            messages['messages'].append(msg)
            return False, "No change record", messages
        
        if change_record == "":
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, msg)
            messages['messages'].append(msg)
            return False, "Empty change recrd", messages
               
        # Pre 4.0.2 change records are a list of entries, with 3 fields per entry. 
        # We'll look at the first 200 characters of the change record, and if 
        # splits into lines, and the first line has 3 fields, we'll assume it to 
        # be a 4.0.1 or earlier record and turn that into a post 4.0.2 record to 
        # pass on.  If not, assume it to be a 4.0.2 record and pass it in as is
        
        first_rec = change_record[0:200].splitlines()[0]
        if len(first_rec.split('|')) == 3:
            #synthesize the info to restore the account proper
            fields = first_rec.split('|')
            acctrec = "games|%s|games|%s|games|/usr/games|/sbin/nologin\n" % (fields[0], fields[1])
            change_record = acctrec + change_record

        retval = sb_utils.acctmgt.acctfiles.restoreSysAcct(change_record)
        msg = "'games' account restored."
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return retval, msg, messages

