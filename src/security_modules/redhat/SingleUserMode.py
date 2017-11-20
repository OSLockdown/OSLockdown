#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Configure system to require password when going into
# single user mode

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class SingleUserMode:
    """Handle single user mode password."""

    def __init__(self):
        self.module_name = "SingleUserMode"
        self.__target_file = '/etc/inittab'
        self.__tmp_file = self.__target_file+'.new'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """ Check to see if sulogin is required."""


        cmd = r'/bin/grep -v "^#" ' + self.__target_file + \
              r' | /bin/grep -c "sulogin"'
        output_tuple = tcs_utils.tcs_run_cmd(cmd, True)
        if output_tuple[0] != 0 or int(output_tuple[1]) == 0:
            msg = 'sulogin is not configured in /etc/inittab' 
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        elif output_tuple[0] == 0 and int(output_tuple[1]) > 0:
            return 'Pass', ''
        else:
            msg = "Unexpected return value (%s)" % str(output_tuple[0])
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

    ##########################################################################
    def apply(self, option=None):
        """Enable password requirement for single user mode."""


        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open file %s (%s)." % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)" % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        search_pattern = re.compile('sulogin')
        comment_pattern = re.compile('^#')

        lines = in_obj.readlines()
        for line in lines:
            if search_pattern.search(line):
                if not comment_pattern.search(line):
                    # XXX: line already exist, should verify it's correct
                    msg = 'Line is present in file'
                    self.logger.info(self.module_name, 
                                         'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, 
                                                 msg))
            out_obj.write(line)

        password_line = '~~:S:wait:/sbin/sulogin\n'
        comment = '\n# Require password authentication for single user mode\n'
        out_obj.write(comment)
        out_obj.write(password_line)

        out_obj.close()
        in_obj.close()

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file 
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = '/sbin/sulogin added to single user mode entry in inittab'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, 'added'

    ##########################################################################
    def undo(self, change_record=None):
        """ Remove sulogin addition."""

        result, reason = self.scan() 
        if result == 'Fail':
            return 0

        if not change_record :
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1


        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + str(err))
            raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))


        for line in origfile:
            if line == "~~:S:wait:/sbin/sulogin\n":
                continue
            else:
                workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + str(err))
            raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))
            


        msg = '/sbin/sulogin disabled for single user mode entry in inittab'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

