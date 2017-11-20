#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class NoPlusPasswdEntries:
    """
    NoPlusPasswdEntries module provides the NoPlusPasswdEntries class which is
    capable of handling the security guidelines regarding no '+' entries in
    password and group files.
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "NoPlusPasswdEntries"
        self.__target_file1 = '/etc/passwd'
        self.__target_file2 = '/etc/shadow'
        self.__target_file3 = '/etc/group'

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

        found1 = False
        found2 = False
        found3 = False

        try:
            in_obj = open(self.__target_file1, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file1, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = """Checking %s for any line starting with a "+" """ %  self.__target_file1
        self.logger.info(self.module_name, 'Scan: ' + msg)

        for line in in_obj:
            if line.startswith('+'):
                found1 = True

        in_obj.close()

        ##########
        msg = """Checking %s for any line starting with a "+" """ %  self.__target_file2
        self.logger.info(self.module_name, 'Scan: ' + msg)
        try:
            in_obj = open(self.__target_file2, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file2, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line in in_obj:
            if line.startswith('+'):
                found2 = True
        in_obj.close()


        ##########
        msg = """Checking %s for any line starting with a "+" """ %  self.__target_file3
        self.logger.info(self.module_name, 'Scan: ' + msg)
        try:
            in_obj = open(self.__target_file3, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file3, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line in in_obj:
            if line.startswith('+'):
                found3 = True
        in_obj.close()


        ########## Now check to see if any files had a + ###############
        if found1: 
            msg = "Found a '+' entry in %s" % self.__target_file1
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        elif found2: 
            msg = "Found a '+' entry in %s" % self.__target_file2
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        elif found3: 
            msg = "Found a '+' entry in %s" % self.__target_file3
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """Apply changes."""

        action_record = ''
        result, reason = self.scan()
        if result == 'Pass':
            return 0, action_record

        try:
            in_obj = open(self.__target_file1, 'r')
        except IOError, err:
            msg = "Unable to open %s file" % self.__target_file1
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        try:
            out_obj = open(self.__target_file1 + '.new', 'w')
            shutil.copymode(self.__target_file1, self.__target_file1 + '.new')
        except IOError, err:
            msg = "Unable to create temporary %s.new file" % self.__target_file1
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Removing any lines beginning with '+' from %s" % self.__target_file1
        self.logger.info(self.module_name, msg )
        for line in in_obj:
            if not line.startswith('+'):
                out_obj.write(line)

        in_obj.close()
        out_obj.close()

        try:
            in_obj = open(self.__target_file2, 'r')
        except IOError, err:
            msg = "Unable to open %s file" % self.__target_file2
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        try:
            out_obj = open(self.__target_file2 + '.new', 'w')
            shutil.copymode(self.__target_file2, self.__target_file2 + '.new')
        except IOError, err:
            msg = "Unable to create temporary %s.new file" % self.__target_file2
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Removing any lines beginning with '+' from %s" % self.__target_file2
        self.logger.info(self.module_name, msg )
        for line in in_obj:
            if not line.startswith('+'):
                out_obj.write(line)

        in_obj.close()
        out_obj.close()

        try:
            in_obj = open(self.__target_file3, 'r')
        except IOError, err:
            msg = "Unable to open %s file" % self.__target_file3
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        try:
            out_obj = open(self.__target_file3 + '.new', 'w')
            shutil.copymode(self.__target_file3, self.__target_file3 + '.new')
        except (OSError, IOError), err:
            msg = "Unable to create temporary %s.new file" % self.__target_file3
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Removing any lines beginning with '+' from %s" % self.__target_file3
        self.logger.info(self.module_name, msg )
        for line in in_obj:
            if not line.startswith('+'):
                out_obj.write(line)

        in_obj.close()
        out_obj.close()

        action_record = tcs_utils.generate_diff_record(self.__target_file1 + '.new',
                                             self.__target_file1)

        action_record += '\n'
        action_record += tcs_utils.generate_diff_record(self.__target_file2 + '.new',
                                             self.__target_file2)

        action_record += '\n'
        action_record += tcs_utils.generate_diff_record(self.__target_file3 + '.new',
                                             self.__target_file3)

        try:
            shutil.copymode(self.__target_file1, self.__target_file1 + '.new')
            shutil.copy2(self.__target_file1 + '.new', self.__target_file1)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file1)
            os.unlink(self.__target_file1 + '.new')
        except (IOError, OSError):
            msg = "Unable to replace %s with new version" % self.__target_file1
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            shutil.copymode(self.__target_file2, self.__target_file2 + '.new')
            shutil.copy2(self.__target_file2 + '.new', self.__target_file2)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file2)
            os.unlink(self.__target_file2 + '.new')
        except (OSError, IOError):
            msg = "Unable to replace %s with new version" % self.__target_file2
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            shutil.copymode(self.__target_file3, self.__target_file3 + '.new')
            shutil.copy2(self.__target_file3 + '.new', self.__target_file3)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file3)
            os.unlink(self.__target_file3 + '.new')
        except (IOError, OSError):
            msg = "Unable to replace %s with new version" % self.__target_file3
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'All "+" password entries removed.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = 'All "+" password entries restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

