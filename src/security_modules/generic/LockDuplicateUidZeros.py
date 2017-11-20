#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import tcs_utils


class LockDuplicateUidZeros:
    """
    Lock accounts with uid zero which are NOT root
    """

    def __init__(self):
        self.module_name = "LockDuplicateUidZeros"

        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option=None):
        """
        Find user accounts with UID Zero
        """
        if option != None:
            option = None


        msg = "Checking /etc/passwd for accounts other than 'root' with a uid of zero"
        self.logger.info(self.module_name, msg)

        # look for duplicates including any external account sources
        for user in pwd.getpwall():
            if user.pw_name != 'root' and user.pw_uid == 0:
                msg = "Duplciate UID 0 (%s) found" % (user.pw_name)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """
        Lock user accounts with UID 0 which are not ROOT
        """
        if option != None:
            option = None

        action_record = ''
        lockstatus = self.lock_status()
        # look for duplicates including any external account sources
        for user in pwd.getpwall():
            if user.pw_name != 'root' and user.pw_uid == 0:
                if lockstatus[user.pw_name] == 'unlocked':
                    cmd = "/usr/bin/passwd -l %s" % user.pw_name
                    output = tcs_utils.tcs_run_cmd(cmd, True)
                    if output[0] != 0:
                        msg = "Unable to lock %s: %s" % (user.pw_name, output[2])
                        self.logger.error(self.module_name, 'Scan Failed: ' + msg)
                        continue

                    action_record += user.pw_name + ':'
                    msg = 'User ' + user.pw_name + ' locked'
                    self.logger.notice(self.module_name, 
                                           'Apply Performed: ' + msg)
                else:
                    msg = 'User ' + user.pw_name + ' already locked'
                    self.logger.notice(self.module_name, 
                                           'Apply Performed: ' + msg)


        if action_record == '':
            return 0, ''
        else:
            return 1, action_record


    ##########################################################################
    def lock_status(self):
        """
        Get list of all user accounts and password status
        """

        try:
            in_obj = open('/etc/shadow', 'r')
        except IOError, err:
            msg = "Unable to read /etc/shadow: %s" % err
            self.logger.error(self.module_name, msg)
            return {}

        lines = in_obj.readlines()
        in_obj.close()

        lock_status = {}
        for line in lines:
            line = line.rstrip('\n')
            entry = line.split(':')

            # Don't store password in object
            # just store 'locked' or 'unlocked'
            if entry[1] == '':
                entry[1] = 'locked'
            else:
                try:
                    if entry[1][0] == '!' or entry[1][0] == '*':
                        entry[1] = 'locked'
                    else:
                        entry[1] = 'unlocked'
                except IndexError, err:
                    self.logger.error(self.module_name, err)
                    continue
 
            lock_status[entry[0]] = entry[1]


        return lock_status


    ##########################################################################
    def undo(self, change_record=None):

        if change_record == None:
            return 0, 'No change record provided'

        changelist = change_record.split(':')
        for user in changelist:
            if not user:
                continue
            try:
                cmd = "/usr/bin/passwd -f -u %s" % user
                output = tcs_utils.tcs_run_cmd(cmd, True)
                if output[0] != 0:
                    msg = "Unable to unlock %s: %s" % (user, output[2])
                    self.logger.error(self.module_name, 'Undo Failed: ' + msg)
                    continue

                msg = '%s user unlocked' % user
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            except Exception, err:
                self.logger.error(self.module_name, 'Undo Error: ' + str(err))
                continue

        return 1


    ##########################################################################
    def validate_input(self, option=None):
        """
        Validate option which is blank
        """
        return 0



if __name__ == '__main__':
    TEST = LockDuplicateUidZeros()
    print TEST.scan()
    print TEST.apply()
    
