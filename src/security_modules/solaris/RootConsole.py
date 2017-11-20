#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger


class RootConsole:
    """
    RootConsole Security Module handles the guideline for root login on console.
    """

    def __init__(self):

        self.module_name = "RootConsole"
        self.__target_file = '/etc/default/login'
        self.__tmp_file    = '/etc/default/login.new'
        self.logger = TCSLogger.TCSLogger.getInstance()
        self._orig_console = ''

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """
        Check CONSOLE in /etc/default/login
        """

        try:
            infile = open(self.__target_file, 'r')
        except IOError, err:
            msg = 'Scan Failed: %s' % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        foundit = False

        # We don't break out of the for loop after the first find
        # because we must find that last entry in the file.
        line_count = 0
        for line in infile:
            line_count += 1
            if str(line).startswith('CONSOLE='):
                self._orig_console = line.split('=')[1].rstrip('\n')
                msg = "Scan: Found '%s' in %s, line number %d" % \
                       (str(line).rstrip('\n'), self.__target_file, line_count)
                self.logger.info(self.module_name, msg )
                foundit = True

        infile.close()
        if foundit:
            # compare the digits of the umask with 027
            if self._orig_console != '/dev/console':
                msg = 'CONSOLE is set to  %s' % self._orig_console
                self.logger.info(self.module_name, msg)
                return 'Fail', msg
        else:
            msg = 'No CONSOLE setting found in %s' % self.__target_file
            self.logger.info(self.module_name, msg)
            return 'Fail', msg

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """
        Set CONSOLE to /dev/console in /etc/default/login
        """

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = 'Apply Failed: %s' % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        foundit = False
        for line in origfile:
            if str(line).startswith('CONSOLE='):
                self._orig_console = line.split('=')[1].rstrip('\n')
                line = str('CONSOLE=/dev/console\n')
                foundit = True
                workfile.write(line)
            else:
                workfile.write(line)

        # stick the CONSOLE setting in if we didn't find it
        if not foundit:
            workfile.write('CONSOLE=/dev/console\n')

        origfile.close()
        workfile.close()

        shutil.copymode(self.__target_file, self.__tmp_file)
        shutil.copy2(self.__tmp_file, self.__target_file)
        os.unlink(self.__tmp_file)

        # save the original umask for the action record
        msg = 'CONSOLE=/dev/console set in %s' % self.__target_file
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        change_record = ['yes\n',self._orig_console]
        return 1, ''.join(change_record)
            
    ##########################################################################
    def undo(self, change_record=None):
        """Undo previous change application."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if change_record == None : 
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 0

        fields=change_record.split()
        if len(fields) != 2 or fields[0] != "yes":
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            return 0

        orig_console_name=fields[1]

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = 'Undo Failed: %s' % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        foundit = False
        for line in origfile:
            if line.strip().startswith('CONSOLE='):
                # found it
                workfile.write('CONSOLE=%s\n' % orig_console_name)
                foundit = True
            else: 
                workfile.write(line)

        # file didn't have the line - stick one in
        if not foundit:
            workfile.write('CONSOLE=%s' % orig_console_name)

        origfile.close()
        workfile.close()

        shutil.copymode(self.__target_file, self.__tmp_file)
        shutil.copy2(self.__tmp_file, self.__target_file)
        os.unlink(self.__tmp_file)

        msg = 'Reset CONSOLE setting to %s' % orig_console_name
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

