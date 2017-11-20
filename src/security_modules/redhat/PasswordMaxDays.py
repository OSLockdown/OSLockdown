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
import sb_utils.SELinux

class PasswordMaxDays:
    """
    PasswordMaxDays Security Module handles the guideline for maximum
    allowed time between password changes.
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "PasswordMaxDays"
        self.__target_file = '/etc/login.defs'
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'passwordMaxdays' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordMaxdays'])
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict):


        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordMaxdays']
        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg =  "Unable to open file %s for analysis (%s)." % \
                   (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        msg = "Checking %s for 'PASS_MAX_DAYS' setting" % (self.__target_file)
        self.logger.info(self.module_name, msg)

        search_pattern = re.compile("^PASS_MAX_DAYS\s*\d")

        value = 0
        for line in lines:
            if search_pattern.search(line):
                tokens = line.split()
                value = int(tokens[1])

        if value > int(option):
            reason = "PASS_MAX_DAYS option is set to %d" % value
            self.logger.info(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict):
        """
        Modify minimum password delay parameter to user value greater 
        than 1.
        """

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''

        option = optionDict['passwordMaxdays']
        # Protect file
        tcs_utils.protect_file(self.__target_file)

        # The line we're looking for is 
        search_pattern = re.compile("#*\s*PASS_MAX_DAYS\s*\d")

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
        old_value = '99999'
        for line in lines:
            if search_pattern.search(line):
                tokens = line.split()
                old_value = int(tokens[1])
                new_line = 'PASS_MAX_DAYS\t' + str(option) + '\n'
                out_obj.write(new_line)
                made_replacement = True
            else:
                out_obj.write(line)

        if not made_replacement:
            line_to_add = 'PASS_MAX_DAYS\t' + str(option) + '\n'
            out_obj.write('# Set the maximum days between password changes\n')
            out_obj.write(line_to_add)
        out_obj.close()

        action_record = old_value

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'PASS_MAX_DAYS directive in /etc/login.defs set to %s' % \
              str(option)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, str(action_record)

    ##########################################################################
    def undo(self, change_record):
        """Undo the previous action."""


        # XXX: Need to put some thought into this one.  I don't want to
        # change the api again just to get the option value for scan
        #result, reason = self.scan()
        #if result == 'Fail':
        #    return 0

        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open file %s (%s)." % (self.__target_file, 
                                                    str(err))
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if not change_record:
            change_record = '0'

        old_value = change_record

        lines = in_obj.readlines()
        in_obj.close()

        search_pattern = re.compile("#*\s*PASS_MAX_DAYS\s*\d")

        for line in lines:
            if search_pattern.search(line):
                new_line = 'PASS_MAX_DAYS\t%s\n' % str(old_value)
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
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'PASS_MAX_DAYS directive in /etc/login.defs set to %s' % \
              str(old_value)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1


