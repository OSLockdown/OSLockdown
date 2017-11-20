#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Set Password History - Users can use any of X number of previous passwords
# 
# Set remember=x on 'password ... pam_auth.so' line in /etc/pam.d/system-auth 
#

import re
import os
import sys
import shutil


sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class PasswordReuse:

    def __init__(self):

        self.module_name = "PasswordReuse"
        self.__target_file = '/etc/pam.d/system-auth'
        self.logger = TCSLogger.TCSLogger.getInstance()



    ##########################################################################
    def validate_input(self, optionDict):
        """Validate Input"""
        if not optionDict or not 'passwordReuse' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordReuse'])
        except ValueError:
            return 1

        if value < 1:
            return 1

        return 0

    ##########################################################################
    def scan(self, optionDict=None):
        """Check for password reuse support."""


        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordReuse']

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg =  "Unable to open file %s: %s." % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        msg = "Checking %s for '^password .* pam_unix.so .* remember=\\d'" % \
                                                         (self.__target_file)
        self.logger.info(self.module_name, msg)

        remember = re.compile('remember=\d+')
        password = re.compile('^\s*password')
        pam_unix = re.compile('pam_unix.so')

        matched_line = None
        value = 0
        for line in lines:
            if password.search(line):
                if pam_unix.search(line):
                    if remember.search(line):
                        matched_line = line
                        break

        if matched_line:
            tokens = matched_line.split()
            for token in tokens:
                if token.startswith('remember'):
                    value_tokens = token.split('=')
                    value = int(value_tokens[1])
                    msg = "Found '%s'" % matched_line
                    self.logger.info(self.module_name, msg)

        msg = "Found 'remember' = %d; expecting at least %d" % (value, int(option))
        self.logger.info(self.module_name, msg)

        if value >= int(option):
            return 'Pass', ''

        else:
            return 'Fail', msg


    ##########################################################################
    def apply(self, optionDict=None):
        """Enable password reuse limits."""


        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''
        option = optionDict['passwordReuse']
        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open file %s: %s." % (self.__target_file, str(err))
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except IOError, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        lines = in_obj.readlines()
        in_obj.close()

        password = re.compile('^\s*password')
        pam_unix = re.compile('pam_unix.so')
        remember = re.compile('remember=\d+')
        
        action_record = 0

        for line in lines:
            if password.search(line) and pam_unix.search(line):
                match_obj = remember.search(line)
                if match_obj:
                    old_string = match_obj.group()
                    tokens = old_string.split('=')
                    if len(tokens) == 2:
                        old_value = tokens[1]
                    else:
                        old_value = 0
                    new_line = re.sub(old_string, 'remember=%d' % int(option),
                                      line)
                    action_record = old_value
                else:
                    new_line = line.rstrip('\n') + \
                               ' remember=%d\n' % int(option)
                out_obj.write(new_line)
            else:
                out_obj.write(line)
        out_obj.close()

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "'remember' option set to %d for password in %s" % (int(option), self.__target_file)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, str(action_record)

    ##########################################################################
    def undo(self, action_record=None):
        """Undo the previous action."""


        if not action_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        try:
            action_record = int(action_record)
        except ValueError:
            msg = "Invalid undo change record provided"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
           
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open file %s: %s" % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except IOError, err:
            msg = "Unable to create temporary file: %s " % str(err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        remember = re.compile('remember=\d+')
        password = re.compile('^\s*password')
        pam_unix = re.compile('pam_unix.so')
        
        for line in lines:
            if password.search(line) and pam_unix.search(line) and \
               remember.search(line):
                if int(action_record) == 0:
                    new_line = remember.sub('', line)
                    out_obj.write(new_line)
                else:
                    match_obj = remember.search(line)
                    if match_obj:
                        old_string = match_obj.group()
                        new_line = re.sub(old_string, 'remember=%d' % 
                                          int(action_record), line)
                    out_obj.write(new_line)
            else:
                out_obj.write(line)
        out_obj.close()

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace " + self.__target_file + \
                  " with new version."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Remember option reset for password in pam'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

