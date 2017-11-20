#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class AccountLocks:
    """
    AccountLocks Security Module handles the guideline for locking
    user accounts after three unsuccessful login attempts.
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "AccountLocks"
        #self.__target_file = '/etc/pam.d/system-auth'
        self.__target_file = '/etc/pam.d/login'
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):
        """ Check to see if account locks are in place."""

        messages = {'messages': []}
        reason = 'pam tally has not been set'
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)" % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        msg = "Checking %s for pam_tally setting" % self.__target_file
        messages['messages'].append(msg)
        self.logger.info(self.module_name, msg)

        deny = re.compile('deny=[1-3]')
        auth = re.compile('^auth')
        pam_tally = re.compile('pam_tally.so')

        for lineNr, line in enumerate(lines):
            if auth.search(line):
                if pam_tally.search(line):
                    if deny.search(line):
                        msg = "Found pam_tally set on line %d of "\
                              "%s" % (lineNr+1, self.__target_file)
                        messages['messages'].append(msg)
                        return True, 'pam_tally is set', messages

        msg = 'Use of pam_tally was not detected.'
        self.logger.info(self.module_name, 'Scan Failed: ' + msg)
        return False, reason, messages



    ##########################################################################
    def apply(self, option=None):
        """Enable account locking after 3 unsuccessful login attempts."""

        action_record = ''
        (result, reason, messages) = self.scan() 
        if result == True:
            return False, reason, {}

        messages = {'messages': []}
        # Protect file
        tcs_utils.protect_file(self.__target_file)

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
            msg = "Unable to create temporary file (%s)" % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        msg = "Editing %s" % (self.__target_file)
        messages['messages'].append(msg)

        auth = re.compile('^auth')
        new_line = "auth     required      pam_tally.so deny=3 onerr=fail magic_root\n"
        
        made_change = False
        for lineNr, line in enumerate(lines):
            if auth.search(line) and not made_change:
                # Insert the new line
                out_obj.write(new_line)
                out_obj.write(line)
                made_change = True
                msg = "Inserting 'auth required pam_tally' at line %d" % (lineNr+1)
                messages['messages'].append(msg)
            else:
                out_obj.write(line)

        out_obj.close()

        action_record = tcs_utils.generate_diff_record(self.__target_file + 
                                                       '.new', 
                                                       self.__target_file)

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file 
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Pam_tally added to authentication service for pam.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, action_record, messages


    ##########################################################################
    def undo(self, change_record=None):
        """Disable account locking after 3 unsuccessful login attempts."""

        (result, reason, messages) = self.scan() 
        if result == False:
            return False, reason, {}

        messages = {'messages': []}
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

        messages['messages'].append("Restored %s" % self.__target_file)
        msg = 'Pam_tally removed as authentication service for PAM.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, messages

