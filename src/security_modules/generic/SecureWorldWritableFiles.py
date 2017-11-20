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

class SecureWorldWritableFiles:
    """
    SecureWorldWritableFiles Security Module handles the guidelines 
    for securing world-writable files.
    """

    def __init__(self):
        self.module_name = "SecureWorldWritableFiles"
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
        Initiating File System Scan to find world-writable files
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

        secure_world_writable_files = True

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        for line in lines:
            if not line.startswith('f|') :
                continue

            fields = line.rstrip('\n').split('|')
            if len(fields) != 6:
                continue

            if fields[1][6] == 'X':
                try:
                    statinfo = os.stat(fields[5])
                except OSError, err:
                    msg = "Unable to stat %s: %s" % (fields[5], err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    continue

                if stat.S_IWOTH & statinfo.st_mode and not (stat.S_ISVTX & statinfo.st_mode) :
                    msg = "%s is world-writeable" % fields[5]
                    self.logger.notice(self.module_name, "Scan Failed: " + msg)
                    secure_world_writable_files = False

            del fields

        if secure_world_writable_files == False:
            return 'Fail', 'Insecure world-writable files exist'

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """Remove world-writable status"""


        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        secure_world_writable_files = True

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        file_list = []
        for line in lines:
            if not line.startswith('f|'):
                continue

            fields = line.rstrip('\n').split('|')
            if len(fields) != 6:
                continue

            if fields[1][6] == 'X':
                try:
                    statinfo = os.stat(fields[5])
                except OSError, err:
                    msg = "Unable to stat %s: %s" % (fields[5], err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    continue

                if stat.S_IWOTH & statinfo.st_mode and not (stat.S_ISVTX & statinfo.st_mode) :
                    file_list.append(fields[5])
                    secure_world_writable_files = False

            del fields


        # Problem files are no longer valid
        if secure_world_writable_files == True:
            return 0, ''

        change_record = {}

        # Remove world-writable status
        for testfile in file_list:

            try:
                statinfo = os.stat(testfile)
                changes_to_make = {'dacs':statinfo.st_mode & ~stat.S_IWOTH}
                change_record.update(sb_utils.file.fileperms.change_file_attributes( testfile, changes_to_make))
                
            except (OSError, IOError), err:
                msg = "Unable to change mode on %s: %s" % (testfile, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                continue

        if change_record == {}:
            return 0 , ''
        else:
            return 1, str(change_record)

    ##########################################################################
    def undo(self, change_record=None):
        """Undo removal of world-writable status on files"""


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1
        
        # old style change record only had a list of file names, so we'll have to walk through this 
        # getting the current status of the file and adding the S_IWOTH bits
        if not change_record[0:200].strip().startswith('{') : # does it look like the start of a dictionary?
            changelist = change_record.split('\n')
            change_record = {}
            # remove empty last entry
            if not changelist[len(changelist)-1]:
                del changelist[len(changelist)-1]

            for testfile in changelist:
                testfile = testfile.lstrip()
                if not testfile:
                    continue

                if not os.path.isfile(testfile):
                    msg = "%s does not exist; ignoring undo record" % testfile
                    self.logger.info(self.module_name, msg)
                    continue
 
                try:
                    statinfo = os.stat(testfile)
                    change_record[testfile] = {'dacs':statinfo.st_mode|stat.S_IWOTH}
                    
                except OSError:
                    msg = "Unable to stat file %s." % testfile
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    continue

        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

