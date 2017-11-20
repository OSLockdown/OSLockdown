#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module sets password aging and inactivity periods on accounts
# 
# When scanning, it reads in /etc/shadow but exempts any account
# with uid < 100 and any account that is locked (*LK*)
#
# ---------
# When applying, it uses the passwd(1) command on the files repository
# as follows:
#
# passwd -r files -x max -w warn -n min useraccount
#
# It uses the usermod(1M) command to set the inactivity field as follows:
#
# usermod -f period useraccount
#
# ---------
# When undoing, it does not restore any previous aging that might
# have existed. It simply removes password aging completely from the 
# account. This is done by using a '-x -1' and a '-f 0' such as:
#
# passwd -x -1 useraccount
# usermod -f 0 useraccount
# 

import sys
import re
import pwd
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.acctmgt.users


class SetPassAgingOnAccts:
    """
    Set password aging
    """
    ##########################################################################
    def __init__(self, hmac_msg=None):
        self.module_name = "SetPassAgingOnAccts"
        self.__pass_min = 0
        self.__pass_max = 0
        self.__pass_warn = 0
        self.__pass_inact = 0

        self.__exemptSystemAccounts = []
        self.__exemptSpecificAccounts = []
        
        self.__usersWithRoles = self.getUsersWithRoles()
        self.logger = TCSLogger.TCSLogger.getInstance()

    def getUsersWithRoles(self):
        usersWithRoles = []
        if os.path.exists('/etc/user_attr'):
          for line in open('/etc/user_attr'):
            fields=line.strip().split(':')
            if len(fields) < 5 or fields[0].startswith('#'):
              continue
            if "type=role" in fields[4]:
                usersWithRoles.append(fields[0])
        return usersWithRoles

    ##########################################################################
    def scan(self, optionDict):
        """
        Find user accounts (uid > 499) with incorrect password aging.
        """
        self.validate_input(optionDict)

        try:
            infile = open('/etc/shadow', 'r')
        except IOError, err:
            msg = "Unable to open /etc/shadow: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))


        # Check each line in /etc/shadow (yes, we probably should call sb_utils.acctmgt.users.local_AllUsers(), but Solaris doesn't
        # have a python module to process the shadow entries, so just parse shadow directly here.
        
        for line in infile.readlines():
            flag = 0
            line = line.rstrip('\n')
            user = line.split(':')
            
            if len(user) != 9:
                msg = "You have a malformed /etc/shadow file; you should "\
                      "run the pwconv(1M) utility to correct it." 
                self.logger.critical(self.module_name, 'Scan Error: ' + msg)
                continue
                   
            try:
                pw_uid = pwd.getpwnam(user[0]).pw_uid
            except KeyError, err:
                msg = "Unable to get information on %s(%d) from local password file" % (user[0], pw_uid)
                self.logger.error(self.module_name, msg)
                continue 

            if user[0] in self.__exemptSystemAccounts:       
                msg =  'Skipping password aging check for %s - system users exempted' % user
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue
            if user[0] in self.__exemptSpecificAccounts:       
                msg =  'Skipping password aging check for %s - user specifically exempted' % user
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue


            if user[1] == '*LK*':
                msg = "Account %s(%d) is locked; ignoring" % (user[0], pw_uid)
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue

            try:
                sp_min   = int(user[3])
                sp_max   = int(user[4])
                sp_warn  = int(user[5])
                sp_inact = int(user[6])

            except Exception, err:
                # An exception typically occurs when one of the fields
                # is blank. Therefore, we can assume that password
                # aging is NOT set.
                msg = "Scan Failed: Unable to get password aging information "\
                      "on user account %s(%d)" % (user[0], pw_uid)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                flag = 1
                continue

            # Now check the current password aging fields against the
            # desired setings.
            if sp_max   != self.__pass_max:   
                flag = 1

            if sp_min   != self.__pass_min:   
                flag = 1

            if sp_warn  != self.__pass_warn:  
                flag = 1

            if sp_inact != self.__pass_inact: 
                flag = 1
            
            if flag == 1:
                msg = "User account %s(%d) has invalid password aging" % \
                      (user[0], pw_uid)
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)



        # Done checking every account. Now, close out and return status
        infile.close()
        if flag == 1:
            msg = "Found unlocked, non-system accounts without password aging"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict):


        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, reason
            
        action_record = []

        self.validate_input(optionDict)

        # Define command strings:
        cmd1 = '/usr/bin/passwd -r files -x %d -n %d -w %d' % \
                   ( self.__pass_max, self.__pass_min, self.__pass_warn )

        cmd2 = '/usr/sbin/usermod -f %d' % (self.__pass_inact)

        cmd3 = '/usr/sbin/rolemod -f %d' % (self.__pass_inact)

        # Open /etc/shadow
        try:
            infile = open('/etc/shadow', 'r')
        except IOError, err:
            msg = "Unable to open /etc/shadow: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        apply_fail_flag = False
        # Check each line in /etc/shadow
        for line in infile.readlines():
            flag = 0
            line = line.rstrip('\n')
            user = line.split(':')

            if len(user) != 9:
                msg = "You have a malformed /etc/shadow file; you should "\
                      "run the pwconv(1M) utility to correct it."
                self.logger.critical(self.module_name, 'Apply Error: ' + msg)
                continue

            pw_uid = pwd.getpwnam(user[0]).pw_uid
            if user[0] in self.__exemptSystemAccounts:       
                msg =  'Skipping password aging check for %s - system users exempted' % user
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue
            if user[0] in self.__exemptSpecificAccounts:       
                msg =  'Skipping password aging check for %s - user specifically exempted' % user
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue

            if user[1] == '*LK*':
                msg = "Account %s(%d) is locked; ignoring" % (user[0], pw_uid)
                self.logger.debug(self.module_name, 'Apply: ' + msg)
                continue

            try:
                sp_min   = int(user[3])
                sp_max   = int(user[4])
                sp_warn  = int(user[5])
                sp_inact = int(user[6])

            except Exception, err:
                # An exception typically occurs when one of the fields
                # is blank. Therefore, we can assume that password
                # aging is NOT set.
                cmd = "%s %s" % (cmd1, user[0])
                results = tcs_utils.tcs_run_cmd(cmd, True)
                if results[0] != 0:
                    msg = "Failed to execute '%s' (%s)" % (cmd, results[2])
                    self.logger.error(self.module_name, 'Apply Failed: ' + msg)
                    apply_fail_flag = True
                else:
                    msg = "Apply Performed: Password aging set: %s" % cmd
                    self.logger.notice(self.module_name, msg)

                if user[0] in self.__usersWithRoles:
                    cmd = "%s %s" % (cmd3, user[0])
                else:
                    cmd = "%s %s" % (cmd2, user[0])
                
                results = tcs_utils.tcs_run_cmd(cmd, True)
                if results[0] != 0:
                    msg = "Failed to execute '%s' (%s)" % (cmd, results[2])
                    self.logger.error(self.module_name, 'Apply Failed: ' + msg)
                    apply_fail_flag = True
                else:
                    msg = "Apply Performed: Inactivity field set: %s" % cmd
                    self.logger.notice(self.module_name, msg)

                action_record.append(user[0] + '\n')
                continue

            # Now check the current password aging fields against the
            # desired setings
            if sp_max   != self.__pass_max:   
                flag = 1

            if sp_min   != self.__pass_min:   
                flag = 1

            if sp_warn  != self.__pass_warn:  
                flag = 1

            if sp_inact != self.__pass_inact: 
                flag = 1

            if flag == 1:
                cmd = "%s %s" % (cmd1, user[0])
                results = tcs_utils.tcs_run_cmd(cmd, True)
                if results[0] != 0:
                    msg = "Failed to execute '%s' (%s)" % (cmd, results[2])
                    self.logger.error(self.module_name, 'Apply Failed: ' + msg)
                    apply_fail_flag = True
                else:
                    msg = "Apply Performed: Password aging set: %s" % cmd
                    self.logger.notice(self.module_name, msg)

                cmd = "%s %s" % (cmd2, user[0])
                results = tcs_utils.tcs_run_cmd(cmd, True)
                if results[0] != 0:
                    msg = "Failed to execute '%s' (%s)" % (cmd, results[2])
                    self.logger.error(self.module_name, 'Apply Failed: ' + msg)
                    apply_fail_flag = True
                else:
                    msg = "Apply Performed: Inactivity field set to max time between passwords: %s" % cmd
                    self.logger.notice(self.module_name, msg)

                action_record.append(user[0] + '\n')


        # Done checking/setting user accounts. Now close file and return status
        infile.close()
        if apply_fail_flag == True and len(action_record) < 1:
            msg = "Unable to set password aging on some accounts"
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return 0, '' 

        if action_record == []:
            return 0, '',

        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record):
        """
        Reset password aging on user accounts
        """


        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        cmd1 = '/usr/bin/passwd -r files -x -1'
        cmd2 = '/usr/sbin/usermod -f 0'
        cmd3 = '/usr/sbin/rolemod -f 0'

        undo_fail_flag = False

        for user in change_record.split('\n'):
            if not user:
                continue
   
            try:
                test = pwd.getpwnam(user)
            except Exception:
                msg = "User account '%s' does not exist" % user
                self.logger.warn(self.module_name, 'Undo: ' + msg)
                continue
            
            cmd = "%s %s" % (cmd1, user)
            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = "Failed to execute '%s' (%s)" % (cmd, results[2])
                self.logger.error(self.module_name, 'Undo Failed: ' + msg)
                undo_fail_flag = True
            else:
                msg = "Undo Performed: Password aging removed: %s" % cmd
                self.logger.notice(self.module_name, msg)

            if user in self.__usersWithRoles:
                cmd = "%s %s" % (cmd3, user)
            else:
                cmd = "%s %s" % (cmd2, user)

            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = "Failed to execute '%s' (%s)" % (cmd, results[2])
                self.logger.error(self.module_name, 'Undo Failed: ' + msg)
                undo_fail_flag = True
            else:
                msg = "Undo Performed: Inactivity field cleared: %s" % cmd
                self.logger.notice(self.module_name, msg)


        if undo_fail_flag == True:
            return 0
        else:
            return 1

    ##########################################################################
    # Verify each argument name is present in the diction, and is an integer
    # return the value or raise an exception
    
    def validate_argument(self, argName, optionDict):
        try:
            argValue = int(optionDict[argName],10)
        except:
            msg =  'Invalid option arg (%s) provided' % argName
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        return argValue


    ##########################################################################
    def validate_input(self, optionDict):
        """
        Validate option which must be min, max, warn, inactive
        in an array (i.e., [7,90,7,1])
        """

# RMS - solaris locks account on expiration - not allowing a grace period of inactivity like linux
#     - so we're 'creating' our own grace period by adding INACT to MAX, and
#     - use this value for pass_inact

        self.__pass_min   = self.validate_argument('passwordAgingMindays', optionDict)
        self.__pass_max   = self.validate_argument('passwordAgingMaxdays', optionDict)
        self.__pass_warn  = self.validate_argument('passwordAgingExpireWarning', optionDict)
        self.__pass_inact = self.validate_argument('passwordAgingInvalidate', optionDict) + self.__pass_max

        if optionDict['exemptSystemAccounts'] == '1':
            self.__exemptSystemAccounts = sb_utils.acctmgt.users.local_SystemUsers()
        else:
            self.__exemptSystemAccounts = []
            
        self.__exemptSpecificAccounts = tcs_utils.splitNaturally(optionDict['exemptSpecificAccounts'])
 
        flag = 0
        if self.__pass_min < 1 or self.__pass_max < 1 or \
               self.__pass_inact < 0 or self.__pass_warn < 1:
            flag = 1
    
        if self.__pass_max < self.__pass_min:
            flag = 1 
 
        if flag == 1:
            msg =  'Invalid option arg provided' 
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))


