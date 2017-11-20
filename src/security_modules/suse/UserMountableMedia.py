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

class UserMountableMedia:
    """
    UserMountableMedia Security Module removes the ability 
    of users to mount removable media
    """

    def __init__(self):
        self.module_name = "UserMountableMedia"

        self.__target_file = '/etc/fstab'
        self.__tmp_file = '/etc/fstab.new'
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def scan(self, option=None):
        messages = {'messages':[]}
        
        try:
            file = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
 
        msg = "Checking mounts in %s" % self.__target_file
        self.logger.info(self.module_name, msg)

        analysis_failed = False
        for line in file:
            line = line.strip()

            if line.startswith('#'):
                continue
            elif line == '':
                continue

            try:
                dev, mt_point, fs_type, options, d, p = line.split()
            except ValueError:
                msg = "Ignoring malformed line: %s" % line
                self.logger.notice(self.module_name, msg)
                continue

            if 'user' in options.split(','):
                msg = "%s is mounted with 'user' option" % (mt_point)
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                analysis_failed = True
                
        if analysis_failed == True:
            msg = "Found user filesystems that are mounted 'user' option"
            messages['messages'].append(msg)
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return False, '', messages
        else:
            return True, '', {}


    ##########################################################################
    def apply(self, option=None):

        result, reason, messages = self.scan()
        if result == True:
            return False, '', messages

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
                dev, mt_point, fs_type, options, d, p = line.split()
            except ValueError:
                msg = "Ignoring malformed line: %s" % line
                self.logger.notice(self.module_name, msg)
                continue

            new_options = options
            if 'user' in options.split(','):
                new_options = new_options.replace('user','nouser')
                have_nosuid = True
            else:
                workfile.write(line)
                continue

            # found a line we want to modify - save what device it's for
            # and the original options
            changes = '%s%s %s\n' % (changes, dev, options)

            # now modify the line - this will modify the in-line tabs and
            # spacing, but that's not too important
            line = '%s %s %s %s %s %s\n' % (dev, mt_point, fs_type,
                                            new_options, d, p)
            msg = "Changing 'user' to 'nouser' mount option to '%s' in /etc/fstab" % (mt_point)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
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

        msg = "All filesystems in /etc/fstab mounted with 'user' has been switched to 'nouser'"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return True, changes.strip(), {}

    ##########################################################################        
    def undo(self, action_record=None):
        """Undo previous change application."""

        result, reason, messages = self.scan()
        if result == False:
            return False, '', messages

        if not action_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {}

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
                dev, mt_point, fs_type, options, d, p = sline.split()
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
            msg = "Restoring '%s' mount options to '%s' in /etc/fstab" % (changes[dev], mt_point)
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
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

        msg = "Mount options restored on user filesystems"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {}

