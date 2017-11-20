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
import sb_utils.os.info
import sb_utils.SELinux

class FstabNodev:
    """
    FstabNodev Security Module modifies fstab so that users 
    are prevented from mounting unauthorized devices.
    """

    def __init__(self):
        self.module_name = "FstabNodev"
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


        if sb_utils.os.info.is_solaris() == True:
            msg = "The 'nodev' mount option is not available in the "\
                  "standard Solaris distribution."
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = 'Unable to read %s: %s' % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        analysis_failed = False
        for line in in_obj:
            line = line.strip()

            if line.startswith('#'):
                continue
            elif line == '':
                continue

            dev, mt_point, fs_type, options, d, p = line.split()

            if mt_point == '/':
                continue
            if mt_point == '/dev':
                continue
            elif fs_type != 'ext2' and fs_type != 'ext3':
                continue
            elif options.find('nodev') != -1:
                continue

            analysis_failed = True
            break

        in_obj.close()
 
        if analysis_failed:
            msg = "Found non-root filesystems that are mounted without the 'nodev' option"
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

            dev, mt_point, fs_type, options, d, p = sline.split()

            if mt_point == '/':
                workfile.write(line)
                continue
            if mt_point == '/dev':
                workfile.write(line)
                continue
            elif fs_type != 'ext2' and fs_type != 'ext3':
                workfile.write(line)
                continue
            elif options.find('nodev') != -1:
                # 'nodev' already in the line
                workfile.write(line)
                continue

            # found a line we want to modify - save what device it's for,
            # and separate each with a space as a delimiter
            changes = '%s %s' % (changes, dev)

            # now modify the line - this will modify the in-line tabs and
            # spacing, but that's not too important
            line = '%s %s %s %s %s %s\n' % (dev, mt_point, fs_type,
                                            "%s,nodev" % options, d, p)
            workfile.write(line)

        origfile.close()
        workfile.close()
     
        try:
            shutil.copymode( self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except Exception, err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "all non-root partitions will now be mounted with the 'nodev' option"
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
            self.logger.notice(self.module_name, msg)
            return 0

        changes = action_record.split()

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

            dev, mt_point, fs_type, options, d, p = sline.split()

            if mt_point == '/':
                workfile.write(line)
                continue
            elif fs_type != 'ext2' and fs_type != 'ext3':
                workfile.write(line)
                continue
            elif options.find('nodev') == -1:
                # 'nodev' not in the line
                workfile.write(line)
                continue
            elif dev not in changes:
                # we didn't modify this line during apply_changes()
                workfile.write(line)
                continue

            # found a line we want to modify
            line = '%s %s %s %s %s %s\n' % (dev, mt_point, fs_type,
                                            options.replace(',nodev', ''), d, p)
            workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode( self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except Exception, err:
            self.logger.error(self.module_name, 'Undo Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "all 'nodev' options for nonroot filesystems removed"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

