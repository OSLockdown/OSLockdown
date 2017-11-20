#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import sb_utils.file.fileperms

class SecureWorldWritableDirectories:

    def __init__(self):
        self.module_name = "SecureWorldWritableDirectories"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT


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
        """
        Initiating File System Scan to find world writable directories
        """

        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        secure_world_writable_dirs = True

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        for line in lines:
            if not line.startswith('d|'):
                continue

            fields = line.rstrip('\n').split('|')
            if len(fields) != 6:
                continue

            if fields[1][6] == 'X':
                if fields[1][5] == 'X':
                    msg = "%s is world-writeable but sticky bit is set; " \
                          "which is good." % fields[5]
                    self.logger.info(self.module_name, msg)
                else:
                    msg = "%s is world-writeable but sticky bit NOT set" % fields[5]
                    self.logger.notice(self.module_name, "Scan Failed: " + msg)
                    secure_world_writable_dirs = False

            del fields

        if secure_world_writable_dirs == False:
            return 'Fail', 'Insecure world writable directories exist'

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """Add sticky bit "t" to all world writable directories"""

        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        secure_world_writable_dirs = True
        dir_list = []

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        for line in lines:

            if not line.startswith('d|'):
                continue

            fields = line.rstrip('\n').split('|')

            # Wrong number of fields?
            if len(fields) != 6:
                continue

            # World Writeable?
            if fields[1][6] == 'X':
                # Sticky bit set?
                if fields[1][5] != 'X':
                    try:
                        statinfo = os.stat(fields[5])
                    except OSError, err:
                        msg = "Unable to stat %s: %s" % (fields[5], err)
                        self.logger.error(self.module_name, 'Apply Error: ' + msg)
                        continue

                    if stat.S_IWOTH & statinfo.st_mode and not (stat.S_ISVTX & statinfo.st_mode) :
                        dir_list.append(fields[5])
                        secure_world_writable_dirs = False


        in_obj.close()

        # Are previously detected, problem directories still an issue?
        if secure_world_writable_dirs == True:
            return 0, ''

        change_record = {}

        # Add "sticky" to world writable directories.  Since we're explicitly adding the bit to the current permissions, 
        # pass through the 'exactDACs' option...
        options =  {'checkOnly':False, 'exactDACs':True}
        for insdir in dir_list:
            changes_to_make = {'dacs':(statinfo.st_mode&07777) |stat.S_ISVTX}
            change_record.update( sb_utils.file.fileperms.change_file_attributes( insdir, changes_to_make, options))

        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

    ##########################################################################
    def undo(self, change_record=None):
        """Undo addition of sticky bit "t" on world writable directories"""


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # old style change record only had a list of directory names, so we'll have to walk through this 
        # getting the current status of the directory and removing the sticky bit

        if not change_record[0:200].strip().startswith('{') : # does it look like the start of a dictionary? 
        
            changelist = change_record.split('\n')
            
            change_record = {}
            # remove empty last entry
            if not changelist[len(changelist)-1]:
                del changelist[len(changelist)-1]

            for insdir in changelist:
                insdir = insdir.lstrip()
                if not os.path.isdir(insdir):
                    msg = "%s no longer exists; ignoring change record" % insdir
                    self.logger.info(self.module_name, 'Undo Error: ' + msg)
                    continue

                try:
                    statinfo = os.stat(insdir)
                    change_record[insdir] = {'dacs':(statinfo.st_mode &07777) & ~stat.S_ISVTX}
                except (IOError, OSError), err:
                    msg = "Unable to change mode on directory %s: %s" % (insdir, err)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    continue

        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)
        

        return 1

