#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module ensures the default list of system accounts (below)
# are either locked (*LK*) or blocked (*NP*) in /etc/shadow.
#
#
# Note - RH/Oracle/CentOS 4 needs some help to determine account status...


import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.acctmgt.users

class BlockSystemAccounts:

    def __init__(self):
        self.module_name = "BlockSystemAccounts"
        self.__target_file = '/etc/passwd'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.valid_shells = []
        self.read_shadow_manually = False
        
        cpe_name = sb_utils.os.info.getCpeName().split(':')
        self.logger.debug(self.module_name,"CPE_NAME = %s" % cpe_name)

        cpe_os = cpe_name[2]
        cpe_maj_ver = cpe_name[4].split('.')[0]
        
        self.logger.info(self.module_name,"CPE_OS = %s  CPE_MAJ_VER = %s" %(cpe_os, cpe_maj_ver))
        if cpe_os in ['centos' , 'oracle', 'redhat' ] and cpe_maj_ver == "4":
            self.read_shadow_manually = True
        
        # rather than list the accounts discretely, go get the list of 'system' accounts from the /etc/passwd files.
        # Explicitly remove the 'root' user
        self.__accts = [ user for user in sb_utils.acctmgt.users.local_SystemUsers() if user != 'root' ]


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def _read_shadow(self, username):

        results = [ 1 , '', 'Unable to find user %s in /etc/shadow' % username ]
        shadowlines = open('/etc/shadow', 'r').readlines()
        for line in shadowlines:
            fields = line.split(':')
            if fields[0] != username:
                continue
            results[0] = 0
            results[2] = "" 
            if fields[1] == "":
                results[1] = "%s NP" % username
            elif fields[1].startswith('!'):
                results[1] = "%s LK" % username
            elif fields[1].startswith('*'):
#                results[1] = "%s BL" % username
                results[1] = "%s LK" % username
            else:
                results[1] = "%s PS" % username
        return results      
    
    ##########################################################################
    def _lock_status(self):
        """
        Get list of all user accounts and password status
        """

        lock_status = {}
        cmd = ""
        # only look at the system users
        for user in self.__accts:
            results = [ 1 , '', 'Unable to find user %s in /etc/shadow' % user ]
            acctStatus = sb_utils.acctmgt.users.status(user)
            status = True
            if acctStatus not in ['LK', 'NL']:
                status = False
            lock_status[user] = [ status, acctStatus]


        return lock_status

    ##########################################################################
    def scan(self, option=None):
        """
        Check the system shells
        """
        
        lockstatus =  self._lock_status()
        if len(lockstatus) < 1:
            msg = "Unable to obtain password status of local accounts in /etc/shadow"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))  

        bad_account = False
       
        # Check accounts which should be locked (LK or !*) in shadow field
        try:
            msg = "Ensuring the following accounts are blocked: %s" % ' '.join(sorted(self.__accts))
        except NameError:
            msg = "Ensuring the following accounts are blocked: %s" % ' '.join(self.__accts)

        self.logger.debug(self.module_name, msg)
        
        for user in self.__accts:
            if not lockstatus.has_key(user):
                continue

            if lockstatus[user][0] == False:
                msg = "Scan Failed: '%s' is NOT blocked" % user
                self.logger.notice(self.module_name, msg)
                bad_account = True
            else:
                msg = "'%s' system account is blocked." % (user)
                self.logger.debug(self.module_name, msg)

            usershell = pwd.getpwnam(user).pw_shell
            if usershell == '/usr/bin/false':
                msg = "'%s' is locked but shell is /usr/bin/false. "\
                      "CIS wants this shell but DISA STIGS does not; "\
                      "ignoring" % user
                self.logger.warn(self.module_name, msg)
            
        del lockstatus
        if bad_account == True:
            return 'Fail', 'Some system accounts are not blocked'
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):


        change_record = []

        if sb_utils.os.info.is_solaris() == True:
            cmd1 = """/usr/bin/passwd -r files -l """
            cmd2 = """/usr/sbin/passmgmt -m -s "" """
            cmd3 = """/usr/bin/passwd -r files -N """
        else:
            cmd1 = """/usr/sbin/usermod -L """
            cmd2 = """/usr/sbin/usermod -s /sbin/nologin """
            cmd3 = """/usr/sbin/usermod -L """

        apply_fail = False
        
        lockstatus =  self._lock_status()
        if len(lockstatus) < 1:
            msg = "Unable to obtain password status of local accounts in /etc/shadow"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))  
        
        
        for user in self.__accts:
            if not lockstatus.has_key(user):
                continue

            bad_account = False

            if lockstatus[user][0] == False: 
                msg = "%s is not blocked; its password status is %s" % (user, lockstatus[user][1])
                self.logger.info(self.module_name, msg)

                cmd = "%s %s" % (cmd1, user)
                results = tcs_utils.tcs_run_cmd(cmd, True) 
                if results[0] != 0:
                    msg = "Unable to block '%s': %s" % (user, results[2])
                    self.logger.error(self.module_name, 'Apply Error:' + msg)
                    apply_fail = True
                else:
                    bad_account = True
                    msg = "Apply Performed: '%s' is blocked; executed: %s" \
                           % (user, cmd)
                    self.logger.notice(self.module_name, msg)
            
            # Check Shell
            usershell = pwd.getpwnam(user).pw_shell
            if usershell == '/usr/bin/false':
                cmd = "%s %s" % (cmd2, user)
                results = tcs_utils.tcs_run_cmd(cmd, True)
                if results[0] != 0:
                    msg = "Unable to reset shell for '%s': %s" % \
                                                (user, results[2])
                    self.logger.error(self.module_name, 
                                            'Apply Failed:' + msg)
                    apply_fail = True
                else:
                    bad_account = True
                    msg = "Apply Performed: '%s' shell is reset; executed:  %s" \
                        % (user, cmd)
                    self.logger.notice(self.module_name, msg)

            if bad_account == True:
                record = "%s|%s|%s\n" % (user, lockstatus[user][1], usershell)
                change_record.append(record)


        if apply_fail == True:
            msg = "There were problems blocking some system accounts"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)

        if change_record:
            return 1, ''.join(change_record)
        else:
            return 0, ''

            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the shells for system accounts
        """

        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        for entry in change_record.split('\n'):
            if not entry:
                continue
            username, status, shell = entry.split('|')

            try:
                pwd.getpwnam(username)
            except KeyError:
                msg = "Ignoring change record; '%s' no longer exists" % username
                self.logger.error(self.module_name, msg)
                continue

            #---------------------------
            # Reset password status
            if status == 'LK':
                cmd = "/usr/bin/passwd -l %s " % username

            else:
                if status == 'NP':
                    if sb_utils.os.info.is_solaris() == True:
                        cmd = "/usr/bin/passwd -r files -N %s " % username
                    else:
                        cmd = "/usr/bin/passwd -f -u %s " % username

                else: 
                    if sb_utils.os.info.is_solaris() == True:
                        cmd = "/usr/bin/passwd -r files -u  %s " % username
                    else:
                        cmd = "/usr/bin/passwd -u %s " % username

            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = "Unable to execute: %s (%s)" % (cmd, results[2])
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, results[2]))
            else:
                msg = 'Successfully executed: %s' % cmd
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

            #---------------------------
            # Reset shells
            if sb_utils.os.info.is_solaris() == True:
                cmd = "/usr/sbin/passmgmt -m -s "
            else:
                cmd = "/usr/sbin/usermod -s "

            if not shell:
                cmd = """%s "" %s""" % (cmd, username)
            else:
                cmd = """%s %s %s""" % (cmd, shell, username)

            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = "Unable to execute: %s (%s)" % (cmd, results[2])
                self.logger.error(self.module_name, 'Undo Error: ' + results[2])
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                msg = 'Successfully executed: %s' % cmd
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1

if __name__ == '__main__':
    TEST = BlockSystemAccounts()
