#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import hmac
import sha
import inspect

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class PasswordPolicySpecial:
    """
    PasswordPolicySpecial Security Module handles the guideline for requiring
    a minimum of two special characters in passwords.
    """
    ##########################################################################
    def __init__(self):

        self.module_name = "PasswordPolicySpecial"
        self.__target_file = '/etc/pam.d/system-auth'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):


        msg = 'Opening %s to check for ocredit' % self.__target_file
        self.logger.info(self.module_name, msg)
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)." % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        ocredit = re.compile('ocredit=')
        password = re.compile('^password\s+\S+\s+(\S*?/+)*pam_cracklib.so\s+')

        for lineNr, line in enumerate(lines):
            line = line.lstrip(' ')
            if password.search(line):
                msg = "Line %d of %s, found: '%s'" % (lineNr+1, self.__target_file, line.strip())
                self.logger.debug(self.module_name, msg)
                if ocredit.search(line):
                    msg = "Line %d of %s, pam_cracklib has 'ocredit' set" % (lineNr+1, self.__target_file)
                    self.logger.info(self.module_name, msg)
                    return 'Pass', ''
                else:
                    msg = "Line %d of %s, pam_cracklib is missing 'ocredit' option." % (lineNr+1, self.__target_file)
                    self.logger.info(self.module_name, msg)

        msg = 'ocredit option is not being used'
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
        return 'Fail', msg


    ##########################################################################
    def apply(self, option=None):


        action_record = ""

        # Protect file
        tcs_utils.protect_file(self.__target_file)
        
        msg = 'Opening %s' % self.__target_file
        self.logger.info(self.module_name, msg)
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open file %s (%s)" % (self.__target_file, 
                                                   str(err))
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        ocredit = re.compile('ocredit=')
        password = re.compile('^password\s+\S+\s+(\S*?/+)*pam_cracklib.so\s+')

        for lineNr, line in enumerate(lines):
            line = line.lstrip(' ')
            if password.search(line):
                if ocredit.search(line):
                    out_obj.write(line)
                else:
                    action_record = "added"
                    msg = "Added ocredit=-2 to pam_crackline on line %d of %s" % (lineNr+1, self.__target_file)
                    self.logger.info(self.module_name, 'Apply Performed: ' + msg)
                    out_obj.write("%s ocredit=-2\n" % (line.rstrip()))
            else:
                out_obj.write(line)

        out_obj.close()

        try:
            if action_record == "added":
                shutil.copymode(self.__target_file, self.__target_file + '.new')
                shutil.copy2(self.__target_file + '.new', self.__target_file)
                sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError, err:
            msg = "Unable to update %s: %s" % (self.__target_file, err)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if action_record == "added":
            msg = 'ocredit option set for pam_cracklib in %s' % (self.__target_file)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            return 1, action_record
        else:
            msg = 'No changes required: ocredit option is already set for pam_cracklib in %s' % (self.__target_file)
            self.logger.notice(self.module_name, msg)
            return 0, ''


    ##########################################################################
    def undo(self, action_record=None):
        """Undo the previous action."""


        if action_record != "added":
            msg = "Skipping Undo: No change record to indicate an undo is required."
            self.logger.notice(self.module_name, msg)
            return 1

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        msg = 'Opening %s' % self.__target_file
        self.logger.info(self.module_name, msg)
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open %s: %s" % (self.__target_file, str(err))
            self.logger.info(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.info(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        ocredit = re.compile('ocredit=')
        password = re.compile('^password\s+\S+\s+(\S*?/+)*pam_cracklib.so\s+')

        replacePat = re.compile(' ocredit=-\d+')

        for lineNr, line in enumerate(lines):
            line = line.lstrip(' ')
            if password.search(line):
                if ocredit.search(line):
                    msg = "Removed ocredit option from line %d of %s" % (lineNr+1, self.__target_file)
                    self.logger.info(self.module_name, 'Undo Performed: ' + msg)
                    line = replacePat.sub(' ', line)

            out_obj.write(line)

        out_obj.close()

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError, err:
            msg = "Unable to update %s: %s" % (self.__target_file, err)
            self.logger.info(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1
