#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.config
import sb_utils.SELinux

class PasswordPolicyMinlen:
    def __init__(self):

        self.module_name = "PasswordPolicyMinlen"
        self.__target_file = '/etc/pam.d/system-auth'
        self.__target_file_login = '/etc/login.defs'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'passwordMinLength' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordMinLength'])
        except ValueError:
            return 1
        if value < 1:
            return 1
        return 0


    ##########################################################################
    def scan(self, optionDict=None):

        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordMinLength']
        scan_failed = False
        failure_reason = ''

        #----------------------------------------------------------------------
        # Test for pam config
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)." % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = 'Checking pam_cracklib minlen setting in %s' % (self.__target_file)
        self.logger.info(self.module_name, msg)

        lines = in_obj.readlines()
        in_obj.close()

        minlen = re.compile('minlen')
        password = re.compile('^password\s+\S+\s+(\S*?/+)*pam_cracklib.so\s+')

        matched_line = None
        value = 0
        for line in lines:
            line = line.lstrip(' ')
            if password.search(line):
                if minlen.search(line):
                    matched_line = line
        if matched_line:
            tokens = matched_line.split()
            for token in tokens:
                if token.startswith('minlen'):
                    value_tokens = token.split('=')
                    value = int(value_tokens[1])

        if value >= int(option):
            msg = 'pam_cracklib minlen option is set to %d which is greater than or equal to %d' % (value, int(option))
            self.logger.info(self.module_name, msg)
        else:
            if not matched_line:
                msg = 'pam_cracklib minlen option not set'
            else:
                msg = 'pam_cracklib minlen option is set to %d instead of %d' % (value, int(option))

            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            scan_failed = True
            failure_reason = msg

        #----------------------------------------------------------------------
        # Test for minimum length in login.defs
        try:
            in_obj = open(self.__target_file_login, 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)." % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        login_lines = in_obj.readlines()
        in_obj.close()

        msg = "Checking PASS_MIN_LEN setting in %s" % (self.__target_file_login)
        self.logger.info(self.module_name, msg)

        minlen = re.compile('^\s*PASS_MIN_LEN\s*\d')

        matched_line = None
        value = 0
        for line in login_lines:
            if minlen.search(line):
                tokens = line.split()
                value = int(tokens[1])

        if value >= int(option):
            msg = "PASS_MIN_LEN is set to %d which is greater than or equal to %d" % (value, int(option))
            self.logger.info(self.module_name, msg)
        else:
            msg = 'PASS_MIN_LEN is set to %d instead of %d' % \
                  (value, int(option))
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            scan_failed = True
            if failure_reason:
                failure_reason += '\n' + msg
            else:
                failure_reason = msg

        if scan_failed == True:
            return 'Fail', failure_reason
        else:
            return 'Pass', failure_reason


    ##########################################################################
    def apply(self, optionDict=None):

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''
        option = optionDict['passwordMinLength']
        # Protect files
        tcs_utils.protect_file(self.__target_file)

        action_record = []

        #---------------------------------------------------------------------
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open file %s (%s)." % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Checking pam_cracklib minlen setting in %s' % (self.__target_file)
        self.logger.info(self.module_name, msg)

        lines = in_obj.readlines()
        in_obj.close()

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)" % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        minlen = re.compile('minlen=\d+')
        password = re.compile('^password\s+\S+\s+(\S*?/+)*pam_cracklib.so\s+')
        
        for line in lines:
            line = line.lstrip(' ')
            if password.search(line) :
                match_obj = minlen.search(line)
                if match_obj:
                    # May have to do a replacement but check first
                    old_string = match_obj.group()
                    tokens = old_string.split('=')
                    old_value = tokens[1]
                    if int(option) > int(old_value):
                        new_line = re.sub(old_string, 'minlen=%d' % int(option), line)
                        action_record.append('pam_minlen=%d' % int(old_value))
                    else:
                        # no substitution needed
                        new_line = line
                else:
                    new_line = line.rstrip('\n') + ' minlen=%d\n' % int(option)
                    action_record.append('pam_minlen=unset')
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
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = 'minlen option set for pam_cracklib in system-auth'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        
        #---------------------------------------------------------------------
        # login.defs change
        paramlist = {}
        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file_login, delim='\t')
        paramlist.update(sb_utils.os.config.get_list(configfile=self.__target_file_login, delim=' '))
        
        # First remove the parameter if it is set using a ' ' (this is not the default OS setting)
        results = sb_utils.os.config.unsetparam(configfile=self.__target_file_login, param='PASS_MIN_LEN', delim=' ')

        # Now set (or replace) setting using '\t' as a delimter
        results = sb_utils.os.config.setparam(configfile=self.__target_file_login, param='PASS_MIN_LEN', value=str(option), delim='\t')
        if results == False:
            msg = 'Unable to set PASS_MIN_LEN in /etc/login.defs set to %d' % int(option)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
        else:
            msg = 'PASS_MIN_LEN in login.defs set to %d' % int(option)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            if paramlist.has_key('PASS_MIN_LEN'):
                action_record.append('pass_min_len=%d' % int(paramlist['PASS_MIN_LEN']))
            else:
                action_record.append('pass_min_len=unset')

        return 1, '\n'.join(action_record)

    ##########################################################################
    def undo(self, change_record=None):


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        minlen = re.compile('minlen=\d+')
        password = re.compile('^password\s+\S+\s+(\S*?/+)*pam_cracklib.so\s+')
 
        for param in change_record.split('\n'):
            (pairKey, pairValue) = param.split('=')

            # Reset logind.defs / PASS_MIN_LEN 
            if pairKey == 'pass_min_len':
                if pairValue == 'unset':
                    results = sb_utils.os.config.unsetparam(configfile=self.__target_file_login, param='PASS_MIN_LEN', delim=' ')
                    msg = "Removed PASS_MIN_LEN from /etc/login.defs"
                else:
                    results = sb_utils.os.config.setparam(configfile=self.__target_file_login, param='PASS_MIN_LEN', value=str(pairValue), delim='\t')
                    msg = "Reset PASS_MIN_LEN to %s in /etc/login.defs" % str(pairValue)
                
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)


            # Reset PAM entry
            if pairKey == 'pam_minlen':
                try:
                    in_obj = open(self.__target_file, 'r')
                except Exception, err:
                    msg = "Unable to open file %s (%s)." % (self.__target_file, str(err))
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                lines = in_obj.readlines()
                in_obj.close()

                try:
                    out_obj = open(self.__target_file + '.new', 'w')
                except Exception, err:
                    msg = "Unable to create temporary file (%s)" % str(err)
                    self.logger.error(self.module_name, 'AUndo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                msg = ''
                for line in lines:
                    line = line.lstrip(' ')
                    if password.search(line):
                        match_obj = minlen.search(line)
                        if match_obj:
                            # May have to do a replacement but check first
                            old_string = match_obj.group()
                            tokens = old_string.split('=')
                            old_value = tokens[1]
                            if pairValue != 'unset':
                                new_line = re.sub(old_string, 'minlen=%d' % int(pairValue), line)
                                msg = "pam_cracklib's 'minlen' option restored to %d" % (int(pairValue))
                            else:
                                # no substitution needed
                                new_line = re.sub(old_string, '', line)
                                msg = "pam_cracklib's 'minlen' option removed" 
                        else:
                            new_line = line
                        out_obj.write(new_line)
                    else:
                        out_obj.write(line)

                # Swap the two files
                out_obj.close()
                try:
                    shutil.copymode(self.__target_file, self.__target_file + '.new')
                    shutil.copy2(self.__target_file + '.new', self.__target_file)
                    sb_utils.SELinux.restoreSecurityContext(self.__target_file)
                    os.unlink(self.__target_file + '.new')
                except OSError:
                    msg = "Unable to replace %s with new version." % self.__target_file
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                if msg != '':
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        
        return 1
