#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.SELinux

class EnableAdditionalFTPLogging_vsftpd:
    ##########################################################################
    def __init__(self):

        self.module_name = "EnableAdditionalFTPLogging_vsftpd"
        self.__target_file = '/etc/vsftpd/vsftpd.conf'
        self.__secondary_target_file = '/etc/vsftpd.conf'
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):
        """
        Check the vsftpd configuration for additional logging switch.
        """

        results =  sb_utils.os.software.is_installed(pkgname='vsftpd')
        if results != True:
            msg = "'vsftpd' package is not installed on the system"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError:
            try:
                in_obj = open(self.__secondary_target_file, 'r')
                self.__target_file = self.__secondary_target_file
            except IOError, err:
                msg =  "Unable to open file %s for analysis (%s)." % \
                       (self.__target_file, str(err))
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()


        msg = "Checking %s for 'xferlog_std_format=NO' and 'log_ftp_protocol=YES' "\
              "settings" % self.__target_file
        self.logger.info(self.module_name, msg)

        search_pattern = re.compile("xferlog_std_format\s*=\s*[YES|NO]")
        search_pattern2 = re.compile("log_ftp_protocol\s*=\s*[YES|NO]")
        comment_pattern = re.compile("^\s*#")

        # variables for keeping track of first test parameter
        test1_passed = False
        test1_enabled = False
        test1_disabled = False
        # variables for keeping track of second test parameter
        test2_passed = False
        test2_enabled = False
        test2_disabled = False
        for line in lines:
            if comment_pattern.search(line):
                continue
            if search_pattern.search(line):
                tokens = line.rstrip('\n').split('=')
                if tokens[1] == 'YES':
                    test1_enabled = True
                elif tokens[1] == 'NO':
                    test1_disabled = True
            if search_pattern2.search(line):
                tokens = line.rstrip('\n').split('=')
                if tokens[1] == 'YES':
                    test2_enabled = True
                elif tokens[1] == 'NO':
                    test2_disabled = True

        if test1_disabled and not test1_enabled:
            test1_passed = True
        if test2_enabled and not test2_disabled:
            test2_passed = True

        if test1_passed and test2_passed:
            return 'Pass', ''
        elif test1_passed and not test2_passed:
            msg = 'log_ftp_protocol option is not set to YES.'
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        elif test2_passed and not test1_passed:
            msg = 'xferlog_std_format option is not set to NO.'
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            msg = 'xferlog_std_format option is not set to NO.'
            msg += '\nlog_ftp_protocol option is not set to YES.'
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg


    ##########################################################################
    def apply(self, option=None):
        """
        set xferlog_std_format option to NO and log_ftp_protocol to YES
        """

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        # The line we're looking for is 
        search_pattern = re.compile("xferlog_std_format\s*=\s*[YES|NO]")
        search_pattern2 = re.compile("log_ftp_protocol\s*=\s*[YES|NO]")

        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open file %s (%s)." % (self.__target_file, 
                                                    str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        made_replacement = False
        made_replacement2 = False
        for line in lines:
            if search_pattern.search(line):
                if made_replacement:
                    continue
                new_line = "xferlog_std_format=NO\n"
                out_obj.write(new_line)
                made_replacement = True
            elif search_pattern2.search(line):
                if made_replacement2:
                    continue
                new_line = "log_ftp_protocol=YES\n"
                out_obj.write(new_line)
                made_replacement2 = True
            else:
                out_obj.write(line)

        if not made_replacement or not made_replacement:
            new_line = "\n# OS Lockdown generated addition\n"
            out_obj.write(new_line)
        if not made_replacement:
            new_line = "xferlog_std_format=NO\n"
            out_obj.write(new_line)
        if not made_replacement2:
            new_line = "log_ftp_protocol=YES\n"
            out_obj.write(new_line)

        out_obj.close()

        action_record = tcs_utils.generate_diff_record(self.__target_file + 
                                                       '.new', 
                                                       self.__target_file)

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'xferlog_std_format set to NO and log_ftp_protocol set to ' + \
              'YES in ' + self.__target_file
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0, ''

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Restore file to what it was before the apply
        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = 'xferlog_std_format and log_ftp_protocol option ' + \
              'modifications reverted.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1


