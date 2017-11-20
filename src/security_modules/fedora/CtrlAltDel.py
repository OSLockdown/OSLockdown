#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# CtrlAltDel module provides the class for handling the security guidelines
# regarding a systems support for ctrl-alt-del key combinations.
#
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux


class CtrlAltDel:
    """
    CtrlAltDel Security Module handles the guideline for disabling 
    ctrl-alt-del key sequence.
    """

    def __init__(self):
        self.module_name = "CtrlAltDel"
        
        if sb_utils.os.info.getOSMajorVersion() == '13':
            self.__target_file = '/etc/init/control-alt-delete.conf'
            self.__pattern = 'start on control-alt-delete'
        else:
            self.__target_file = '/etc/event.d/control-alt-delete'
            self.__pattern = 'exec /sbin/shutdown -r now'
        self.__tmp_file    = self.__target_file+'.new'
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


    ##########################################################################
    def scan(self, option=None):
        """ Check to see if the ctrl-alt-del key combination is allowed."""


        if not os.path.isfile(self.__target_file):
            msg = "%s does not exist" % self.__target_file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, str(err))
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
     
        
        msg = "Looking for lines starting with '%s' in %s" % (self.__pattern, self.__target_file)
        self.logger.info(self.module_name, 'Scan Error: ' + msg)

        lines = in_obj.readlines()
        in_obj.close()

        for line in lines:
            line = line.strip()
            if line.startswith(self.__pattern): 
                msg = "Ctrl-Alt-Delete not disabled"
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """ Disable the ctrl-alt-del key combination."""

        result, reason = self.scan()
        if result == 'Pass':
            return 0, reason
            
        # Protect file
        tcs_utils.protect_file(self.__target_file)

        search_pattern = re.compile(self.__pattern)
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open file %s (%s)" % (self.__target_file, str(err))
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        for line in lines:
            if search_pattern.search(line):
                new_line = "#" + line
                out_obj.write(new_line)
            else:
                out_obj.write(line)
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

        msg = 'Ctrl-alt-del key combination disabled in %s' % self.__target_file
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, 'added'

    ##########################################################################
    def undo(self, change_record):
        """ Re-enable the ctrl-alt-del key combination."""


        if not change_record : 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record != 'added' :
            msg = "Unable to perform undo operation with invalid change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + str(err))
            raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))


        for line in origfile:
            if line.startswith("#exec /sbin/shutdown -r now") or line.startswith('#start on control-alt-delete'):
                workfile.write(line[1:])
            else:
                workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + str(err))
            raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))

        msg = 'Ctrl-alt-del key combination enabled in /etc/inittab'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

