#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import shutil
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class FstabRemovableMedia:

    def __init__(self):
        self.module_name = "FstabRemovableMedia"
        self.__target_file = '/etc/fstab'
        self.__tmp_file = '/tmp/.fstab.tmp'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        try:
            file = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
 
        analysis_failed = False
        for line in file:
            line = line.strip()

            if line.startswith('#'):
                continue
            elif line == '':
                continue

            dev,mt_point,fs_type,options,d,p = line.split()

            if mt_point == '/':
                continue
            elif mt_point.find('floppy') == -1 and mt_point.find('cdrom') == -1:
                continue
            elif options.find('nodev') != -1 and options.find('nosuid') != -1:
                continue

            analysis_failed = True
            break

        if analysis_failed:
            msg = "Found removable-media filesystems that can be mounted "\
                  "without the 'nodev' and 'nosuid' options"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        changes = ''

        for line in origfile:
            sline = line.strip()

            if sline.startswith('#'):
                workfile.write(line)
                continue
            elif sline == '':
                workfile.write(line)
                continue

            dev,mt_point,fs_type,options,d,p = sline.split()

            if mt_point == '/':
                workfile.write(line)
                continue

            elif mt_point.find('floppy') == -1 and mt_point.find('cdrom') == -1:
                workfile.write(line)
                continue

            # test separately for both 'nodev' and 'nosuid', and add them
            # if they're not already there
            new_options = options

            if options.find('nodev') == -1:
                new_options = '%s,nodev' % new_options
                have_nodev = True

            if options.find('nosuid') == -1:
                new_options = '%s,nosuid' % new_options
                have_nosuid = True

            # sanity check
            if new_options == options:
                workfile.write(line)
                continue

            # found a line we want to modify - save what device it's for
            # and the original options
            changes = '%s%s %s\n' % (changes, dev, options)

            # now modify the line - this will modify the in-line tabs and
            # spacing, but that's not too important
            line = '%s %s %s %s %s %s\n' % (dev, mt_point, fs_type,
                                            new_options, d, p)
            workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError, err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "all removable media will be mounted with the 'nodev' "\
              "and 'nosuid' options"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, changes.strip()

    ##########################################################################        
    def undo(self, action_record=None):
        """Undo previous change application."""


        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not action_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        list = action_record.split('\n')
        changes = {}
        for entry in list:
            dev, options = entry.split()
            changes[dev] = options

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))
 
        for line in origfile:
            sline = line.strip()

            if sline.startswith('#'):
                workfile.write(line)
                continue
            elif sline == '':
                workfile.write(line)
                continue

            try:
                dev,mt_point,fs_type,options,d,p = sline.split()
            except ValueError:
                msg = "Skipping malformed undo record: %s" % sline
                self.logger.debug(self.module_name, msg)
                continue 

            if dev not in changes.keys():
                # we didn't modify this line during apply_changes()
                workfile.write(line)
                continue

            # found a line we want to modify
            line = '%s %s %s %s %s %s\n' % (dev, mt_point, fs_type,
                                            changes[dev], d, p)
            workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "all 'nodev' and 'nosuid' options for removable media removed"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

