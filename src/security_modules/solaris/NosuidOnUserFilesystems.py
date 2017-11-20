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

class NosuidOnUserFilesystems:
    """
    NosuidOnUserFilesystems Security Module modifies vfstab so that 
    users are prevented from mounting unauthorized devices.
    """

    def __init__(self):
        self.module_name = "NosuidOnUserFilesystems"
        self.__target_file = '/etc/vfstab'
        self.__tmp_file = '/tmp/.vfstab.tmp'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        self.__user_filesystems = ['/export/home', '/etc/dfs/sharetab']

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

            try: 
                dev, dev2fsck, mt_point, fs_type, fsck, mountatboot, options = line.split()
            except ValueError:
                msg = "Skipping malformed line in /etc/vfstab: %s" % line
                self.logger.error(self.module_name, msg)
                continue

            if mt_point == '/':
                continue

            if mt_point in self.__user_filesystems:
                if 'nosuid' not in options.split(','):
                    msg = "%s not mounted with 'nosuid' option; instead it "\
                          "is mounted with '%s'" % (mt_point, options)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    analysis_failed = True
                
        if analysis_failed == True:
            msg = "Found user filesystems that are mounted 'nosuid' option"
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

            try: 
                dev, dev2fsck, mt_point, fs_type, fsck, mountatboot, options = line.split()
            except ValueError:
                msg = "Skipping malformed line in /etc/vfstab: %s" % sline
                self.logger.error(self.module_name, msg)
                continue

            if mt_point == '/':
                workfile.write(line)
                continue

            if mt_point not in self.__user_filesystems:
                workfile.write(line)
                continue

            new_options = options
            if 'nosuid' not in options.split(','):
                new_options = '%s,nosuid' % new_options
                have_nosuid = True

            # sanity check - if we *do* actually match write the line as is
            if new_options == options:
                workfile.write(line)
                continue

            # found a line we want to modify - save what device it's for
            # and the original options
            changes = '%s%s %s\n' % (changes, dev, options)

            # now modify the line - this will modify the in-line tabs and
            # spacing, but that's not too important
            line = '%s %s %s %s %s %s %s\n' % (dev,dev2fsck,mt_point,fs_type,fsck,mountatboot,new_options)
            msg = "Adding 'nosuid' mount option to '%s' in /etc/vfstab" % (mt_point)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            os.unlink(self.__tmp_file)
        except (IOError, OSError), err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "all user filesystems will be mounted with the 'nosuid' option"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, changes.strip()

    ##########################################################################        
    def undo(self, action_record=None):
        """Undo previous change application."""

        result, reason = self.scan()
        if result == 'Fail':
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
                dev,dev2fsck,mt_point,fs_type,fsck,mountatboot,options = line.split()
            except ValueError:
                msg = "Skipping malformed line in /etc/vfstab: %s" % sline
                self.logger.error(self.module_name, msg)
                continue

            if dev not in changes.keys():
                # we didn't modify this line during apply_changes()
                workfile.write(line)
                continue

            # found a line we want to modify
            line = '%s %s %s %s %s %s %s\n' % (dev,dev2fsck,mt_point,fs_type,fsck,mountatboot,options.replace(',nosuid', ''))
            msg = "Restoring '%s' mount options to '%s' in /etc/vfstab" % (changes[dev], mt_point)
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError, err:
            self.logger.error(self.module_name, 'Undo Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "Mount options restored on user filesystems"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

