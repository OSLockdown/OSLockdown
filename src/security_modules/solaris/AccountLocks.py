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

import sb_utils.os.service
import sb_utils.os.info


class AccountLocks:
    """
    AccountLocks Security Module handles the guideline for locking
    user accounts after three unsuccessful login attempts.
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "AccountLocks"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option=None):
        """ Check to see if account locks are in place."""

        # 
        # /etc/default/login needs RETRIES=3 (or less)
        #
        try:
            in_obj = open('/etc/default/login', 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)" % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        foundit = False
        retry_setting = re.compile('^RETRIES=')
        line_count = 0
        for line in lines:
            line_count += 1
            if retry_setting.search(line):
                msg = "Scan: Found '%s' in /etc/default/login, line %d" % \
                    (line.rstrip('\n'), line_count)
                self.logger.info(self.module_name, msg)
                retry_value = int(line.split('=')[1].rstrip('\n'))
                if retry_value <= 3:
                    foundit = True
                else:
                    foundit = False

        if foundit == False:
            msg = "RETRIES not set to 3 or less in /etc/default/login"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        # 
        # /etc/security/policy.conf needs LOCK_AFTER_RETRIES=YES
        #
        try:
            in_obj = open('/etc/security/policy.conf', 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)" % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        foundit = False
        retry_setting = re.compile('^LOCK_AFTER_RETRIES=')
        line_count = 0
        for line in lines:
            line_count += 1
            if retry_setting.search(line):
                msg = "Scan: Found '%s' in /etc/security/policy.conf, line %d" % \
                    (line.rstrip('\n'), line_count)
                self.logger.info(self.module_name, msg)
                retry_value = str(line.split('=')[1].rstrip('\n'))
                if retry_value == 'YES':
                    foundit = True
                else:
                    foundit = False

        if foundit == False:
            msg = "LOCK_AFTER_RETRIES=YES not set correctly in "\
                  "/etc/security/policy.conf"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def apply(self, option=None):
        """Enable account locking after 3 unsuccessful login attempts."""

        action_record = ''
        result, reason = self.scan() 
        if result == 'Pass':
            return 0, action_record

        # 
        # /etc/default/login needs RETRIES=3 (or less)
        #
        # Protect file
        tcs_utils.protect_file('/etc/default/login')

        try:
            in_obj = open('/etc/default/login', 'r')
        except Exception, err:
            msg = "Unable to open file /etc/default/login (%s)." %  str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open('/tmp/.default_login.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)" % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        auth = re.compile('^RETRIES')
        new_line = "RETRIES=3\n\n"
        
        made_change = False
        for line in lines:
            if auth.search(line) and not made_change:
                # Insert the new line
                out_obj.write(new_line)
                made_change = True
            else:
                out_obj.write(line)

        if made_change == False:
            out_obj.write('\n# Added by OS Lockdown\n')
            out_obj.write(new_line)

        out_obj.close()
        action_record = tcs_utils.generate_diff_record('/tmp/.default_login.new',
                                                       '/etc/default/login')

        try:
            shutil.copymode('/etc/default/login', '/tmp/.default_login.new')
            shutil.copy2('/tmp/.default_login.new', '/etc/default/login')
            os.unlink('/tmp/.default_login.new')
        except OSError:
            msg = "Unable to replace /etc/default/login with new version."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'RETRIES=3 set in /etc/default/login'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)


        # 
        # /etc/security/policy.conf needs LOCK_AFTER_RETRIES=YES
        #
        # Protect file
        tcs_utils.protect_file('/etc/security/policy.conf')

        try:
            in_obj = open('/etc/security/policy.conf', 'r')
        except Exception, err:
            msg = "Unable to open file /etc/security/policy.conf (%s)." % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open('/tmp/.policy.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)" % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        auth = re.compile('^LOCK_AFTER_RETRIES=')
        new_line = "LOCK_AFTER_RETRIES=YES\n\n"

        made_change = False
        for line in lines:
            if auth.search(line) and not made_change:
                # Insert the new line
                out_obj.write(new_line)
                made_change = True
            else:
                out_obj.write(line)

        if made_change == False:
            out_obj.write('\n# Added by OS Lockdown\n')
            out_obj.write(new_line)

        out_obj.close()
        action_record += '\n' + tcs_utils.generate_diff_record('/tmp/.policy.new',
                           '/etc/security/policy.conf')

        try:
            shutil.copymode('/etc/security/policy.conf', '/tmp/.policy.new')
            shutil.copy2('/tmp/.policy.new', '/etc/security/policy.conf')
            os.unlink('/tmp/.policy.new')
        except OSError:
            msg = "Unable to replace /etc/security/policy.conf with new version."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'LOCK_AFTER_RETRIES=YES set in /etc/security/policy.conf'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)


        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Disable account locking after 3 unsuccessful login attempts."""

        result, reason = self.scan() 
        if result == 'Fail':
            return 0

        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "/etc/default/login (RETRIES) and "\
              "/etc/security/policy.conf (LOCK_AFTER_RETRIES) reset"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

