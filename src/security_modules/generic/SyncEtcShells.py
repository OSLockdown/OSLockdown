#!/usr/bin/env python


# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.


# SyncEtcShells module synchronizes shells between /etc/shells
# and /etc/passwd. We do not put /dev/null or /sbin/nologin in 
# /etc/shells.
# If an account has a shell, then it must be listed in /etc/shells
# except for the "__ignore_shells" list.
#

import os
import sys
import shutil
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.misc.unique
import sb_utils.SELinux
import sb_utils.acctmgt.users

class SyncEtcShells:
    """
    """

    def __init__(self):
        self.module_name = "SyncEtcShells"
        self.__shells = '/etc/shells'
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__ignore_shells = ['/bin/sync', '/dev/null', '/sbin/nologin',
                                '/usr/bin/false', '/bin/false', '/sbin/halt',
                                '/sbin/shutdown' ]

    ##########################################################################
    def validate_input(self, option):
        """Validate input - This class requires none"""
        if option and option != 'None':
            return 1
        return 0

    def get_shells(self):
        # Read /etc/shells
        try:
            shells = tcs_utils.splitNaturally(open(self.__shells).read(), wordAdditions="/-_")
        except Exception, err:
            msg = "Unable to read '/etc/shells' - may need to use 'Allowed Shells in /etc/shells' Module - %s" % str(err)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        return shells
        
    ##########################################################################
    def scan(self, option=None):
        """
        """

        retval = True
        messages = []
        
        shells = self.get_shells()
        
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            userShell = pwd.getpwnam(userName)[6]
            if userShell == "":
                msg = "User '%s' has empty shell, assuming it to be /bin/sh as per manual" % (userName)
                self.logger.notice(self.module_name, msg)
                userShell = "/bin/sh"
                
            if userShell in shells:
                msg = "User '%s' using acceptable shell '%s' from /etc/shells" % (userName, userShell)
                self.logger.debug(self.module_name, msg)
                continue
            elif userShell in self.__ignore_shells:
                msg = "User '%s' using acceptable implicit nologin shell of shell '%s'" % (userName, userShell)
                self.logger.debug(self.module_name, msg)
                continue
            
            msg = "User '%s' using an unacceptable shell '%s' " % (userName, userShell)    
            
            if sb_utils.acctmgt.users.is_locked(userName) == True:
                msg = msg + ", but account is already locked"
            else:
                msg = msg + ", account should be locked until shell is corrected"
                
            messages.append(msg)
            self.logger.warning(self.module_name, msg)
            retval = False

        if retval == True:
            msg = "All users using approved shell programs found in /etc/shells"
        else:
            msg = "One or more users is using a shell program not in /etc/shells"

        return retval, msg, {'messages':messages}

    ##########################################################################
    def apply(self, option=None):

        retval = False
        messages = []
        
        shells = self.get_shells()
        
        lockedAccounts = []        
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            lockIt = False
            userShell = pwd.getpwnam(userName)[6]
            
            if userShell == "":
                msg = "User '%s' has empty shell, assuming it to be /bin/sh as per manual" % (userName)
                self.logger.notice(self.module_name, msg)
                userShell = "/bin/sh"
                
            if userShell in shells:
                msg = "User '%s' using acceptable shell '%s' from /etc/shells" % (userName, userShell)
                self.logger.debug(self.module_name, msg)
                continue
            elif userShell in self.__ignore_shells:
                msg = "User '%s' using acceptable implicit nologin shell of shell '%s'" % (userName, userShell)
                self.logger.debug(self.module_name, msg)
                continue
            
            msg = "User '%s' using an unacceptable shell '%s' " % (userName, userShell)    
            if sb_utils.acctmgt.users.is_locked(userName) == True:
                msg = msg + ", but account is already locked"
            else:
                msg = msg + ", account should be locked until shell is corrected"
                lockIt = True
            messages.append(msg)
    
            self.logger.warning(self.module_name, msg)
            if lockIt == True:
                if sb_utils.acctmgt.users.lock(userName) == True:
                    lockedAccounts.append(userName)
                    msg = "User '%s' account is now locked' " % (userName)    
                    retval = True
                else:
                    msg = "Problem locking '%s' account" % (userName)
            
                    
                self.logger.warning(self.module_name, msg)
                messages.append(msg)
            
        if lockedAccounts:
            change_rec = {'LockedUsers': lockedAccounts}
        else:
            change_rec = None
        return retval, str(change_rec), {'messages':messages}

    ##########################################################################
    def undo(self, change_record=None):
        
        if not change_record.startswith('{'):
            msg = "Found oldstyle (pre4.1.1) change record - unable to perform undo due to potential conflicts with other modules"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        usersToUnlock = tcs_utils.string_to_dictionary(change_record)
        for userName in usersToUnlock['LockedUsers']:
            sb_utils.acctmgt.users.unlock(userName, doSysAccounts=True)  
        
        return 1
            
    ##########################################################################
    def undo_OLD(self, change_record=None):
        """
        Restore /etc/shells
        """

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record == '':
            return 0, "Empty change record"
            
        if change_record == 'remove':
            try:
                os.unlink(self.__shells)
            except IOError, err:
                msg = "Unable to undo previous changes (%s)." % str(err)
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            return 1


        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % str(err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Modifications to /etc/shells file undone.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

