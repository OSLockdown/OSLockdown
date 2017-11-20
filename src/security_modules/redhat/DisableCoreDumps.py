#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

"""
  Disable Core Dumps 

"""

import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class DisableCoreDumps:
    """Disable Core Dumps"""

    def __init__(self):
        self.module_name = "DisableCoreDumps"
        self.__target_file = '/etc/security/limits.conf'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan_for_core_limits(self, option=None):

        limits_found = {'hard':False, 'soft':False}
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s file: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Checking %s for hard and soft 'core' settings to be "\
              "zero" % self.__target_file
        self.logger.info(self.module_name, 'Scan Failed: ' + msg)

        for line in in_obj:
            linelist = line.split()
            # ignore comments and other lines
            if len(linelist) < 4 or linelist[0].startswith('#'):
                continue
            if linelist[0] == '*' and linelist[1] == 'hard' and \
               linelist[2] == 'core' and linelist[3] == '0':
                limits_found['hard'] = True
            if linelist[0] == '*' and linelist[1] == 'soft' and \
               linelist[2] == 'core' and linelist[3] == '0':
                limits_found['soft'] = True
        in_obj.close()

        return limits_found

    ##########################################################################
    def scan(self, option=None):

        limits_found = self.scan_for_core_limits()
        if not limits_found['hard'] or not limits_found['soft'] :
            missing_limits = []
            for lmt in ['hard' , 'soft']:
                if not limits_found[lmt]:
                    missing_limits.append(lmt)
            msg = "Core dumps are not disabled - missing entries in %s for %s" % (self.__target_file, ', '.join(missing_limits))
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return False, '', {'messages':msg}
        else:
            return 'Pass', '', {}

    ##########################################################################
    def apply(self, option=None):

        action_record = ''
        messages = {'messages': [] }
        limits_found = self.scan_for_core_limits()
        
        if limits_found['hard'] and limits_found['soft'] :
            return False, '', {}
            
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError:
            msg = "Unable to open %s file" % self.__target_file
            messages['messages'].append(msg)
            self.logger.info(self.module_name, 'Apply Failed: ' + msg)
            return False, '', messages

        try:
            out_obj = open(self.__target_file + '.new', 'w')
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
        except IOError, err:
            msg = "Unable to create temporary %s.new file" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line in in_obj:
            out_obj.write(line)

        in_obj.close()

        # add the missing limit...
        if not limits_found['hard']:
            out_obj.write("* hard core 0\n")

        if not limits_found['soft']:
            out_obj.write("* soft core 0\n")
        out_obj.close()

        action_record = tcs_utils.generate_diff_record(self.__target_file + '.new',
                                             self.__target_file)

        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Core dumps have been disabled.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, action_record, messages


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, ignore, reason = self.scan()
        if result == 'Fail':
            return False, '', reason

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

        msg = 'Core dump configuration restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '' , {}

