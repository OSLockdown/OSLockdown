#!/usr/bin/env python
 
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

# 
# This module restricts the use of the 'cron' and 'at' services.
# By default operating system lists which user accounts may NOT
# use the service by listing accounts in at.deny and cron.deny.
#
# However, this security requirement wants you to identify
# implicility who CAN use the service. This is accomplished
# by listing the account in cron.allow.
# 
# This module will remove at.deny and cron.deny if they are
# found. If cron.allow is not found, it will create one
# with only 'root' and 'sys' listed.
#
# When the module performs an "undo" it will only
# remove cron.allow if it did not exist before. If it 
# did exist before, it won't do anything to the file.
# If cron.deny and at.deny existed, it will restore
# the contents of those files.
#


import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms
import sb_utils.SELinux

class RestrictAtCron:

    def __init__(self):
        self.module_name = "RestrictAtCron"
      
        if sb_utils.os.info.is_solaris() == True:
            self.__target_file1 = '/etc/cron.d/at.deny'
            self.__target_file2 = '/etc/cron.d/cron.deny'
            self.__target_file3 = '/etc/cron.d/cron.allow'
            self.__target_file4 = '/etc/cron.d/at.allow'
        else:
            self.__target_file1 = '/etc/at.deny'
            self.__target_file2 = '/etc/cron.deny'
            self.__target_file3 = '/etc/cron.allow'
            self.__target_file4 = '/etc/at.allow'
  
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        if os.path.isfile(self.__target_file1):
            msg = "Found %s" % self.__target_file1
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        if os.path.isfile(self.__target_file2):
            msg = "Found %s" % self.__target_file2
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        if not os.path.isfile(self.__target_file3):
            msg = "%s does not exist" % self.__target_file3
            self.logger.notice(self.module_name, 'Scan Filed: ' + msg)
            return 'Fail', msg

        if not os.path.isfile(self.__target_file4):
            msg = "%s does not exist" % self.__target_file4
            self.logger.notice(self.module_name, 'Scan Filed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, err

        action_record = []

        #------------------------------
        # Process at.deny
        if os.path.isfile(self.__target_file1):
            try:
                tfile = open(self.__target_file1,'r')
            except IOError, err:
                msg = "Unable to read %s: %s" % (self.__target_file1, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = "%s was found, reading contents..." % (self.__target_file1)
            self.logger.debug(self.module_name, 'Apply: ' + msg)
            users = []
            for line in tfile.readlines():
                users.append(line.strip('\n') + ' ')
            
            action_record.append(self.__target_file1 + '|' + ''.join(users) + '\n')

            try:
                os.unlink(self.__target_file1)
            except (OSError, IOError), err:
                msg = "Unable to remove %s: %s" % (self.__target_file1, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = "%s removed" % (self.__target_file1)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            tfile.close()

        else:
            action_record.append(self.__target_file1 + '|-1\n')



        #------------------------------
        # Process cron.deny
        if os.path.isfile(self.__target_file2):
            try:
                tfile = open(self.__target_file2,'r')
            except IOError, err:
                msg = "Unable to read %s: %s" % (self.__target_file2, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = "%s was found, reading contents..." % (self.__target_file2)
            self.logger.debug(self.module_name, 'Apply: ' + msg)
            users = []
            for line in tfile.readlines():
                users.append(line.strip('\n') + ' ')

            action_record.append(self.__target_file2 + '|' + ''.join(users) + '\n')

            try:
                os.unlink(self.__target_file2)
            except (OSError, IOError), err:
                msg = "Unable to remove %s: %s" % (self.__target_file2, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = "%s removed" % (self.__target_file2)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            tfile.close()

        else:
            action_record.append(self.__target_file1 + '|-1\n')


        #-------------------------------------------------
        # Check for /etc/cron.allow, if not exists 
        # creat it with just root in it
        if not os.path.isfile(self.__target_file3):
            tcs_utils.protect_file(self.__target_file3)
            try:
                out_obj = open(self.__target_file3, 'w')
            except IOError, err:
                msg = "Unable to create %s: %s" % \
                      (self.__target_file3, str(err))
                self.logger.error(self.module_name, 'Apply Error: ' + msg) 
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            out_obj.write("root")
            out_obj.close()
            # Set Owner/Group to root:root and perms 0600
            changes_to_make = {'owner':'root',
                               'group':'root',
                               'dacs':0600}
            ignore_results = sb_utils.file.fileperms.change_file_attributes(self.__target_file3, changes_to_make)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file3)
                

            action_record.append(self.__target_file3 + '|-1\n')

            msg = "%s has been created with only 'root' listed" % \
                      self.__target_file3
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        #-------------------------------------------------
        # Check for /etc/at.allow, if not exists 
        # creat it with just root in it
        if not os.path.isfile(self.__target_file4):
            tcs_utils.protect_file(self.__target_file4)
            try:
                out_obj = open(self.__target_file4, 'w')
            except IOError, err:
                msg = "Unable to create %s: %s" % \
                      (self.__target_file4, str(err))
                self.logger.error(self.module_name, 'Apply Error: ' + msg) 
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            out_obj.write("root")
            out_obj.close()
            # Set Owner/Group to root:root and perms 0600
            changes_to_make = {'owner':'root',
                               'group':'root',
                               'dacs':0600}
            ignore_results = sb_utils.file.fileperms.change_file_attributes(self.__target_file4, changes_to_make)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file4)

            action_record.append(self.__target_file4 + '|-1\n')

            msg = "%s has been created with only 'root' listed" % \
                      self.__target_file4
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        failure_flag  = False
        for line in change_record.split('\n'):
            if not line:
                continue
            fields = line.split('|')

            if len(fields) < 2:
                failure_flag = True
                continue

            if fields[1] != '-1':
                users = fields[1].split(' ')
                os.umask(077)
                try:
                    outfile = open(fields[0], 'w')
                    for entry in users:
                        if not entry:
                            continue
                        outfile.write(entry + '\n')
                    outfile.close()
                    sb_utils.SELinux.restoreSecurityContext(fields[0])
                except IOError, err:
                    msg = "Unable to restore %s: %s" % (fields[0], err)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    failure_flag = True
                    continue

                msg = "Undo Performed: %s restored" % (fields[0])
                self.logger.notice(self.module_name, msg)
 
            else:

                try:
                    os.unlink(fields[0])
                except (IOError, OSError), err:
                    msg = "Unable to remove %s: %s" % (fields[0], err)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    failure_flag = True
                    continue

                msg = "Undo Performed: %s removed" % (fields[0])
                self.logger.notice(self.module_name, msg)

        if failure_flag == True:
            return 0
        else:
            return 1
