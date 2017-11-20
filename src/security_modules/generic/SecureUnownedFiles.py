#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
# Look for Unowned files, if found change ownership to 'nobody'
#

import sys
import os
import pwd
import grp

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import sb_utils.file.fileperms

class SecureUnownedFiles:

    def __init__(self):
        self.module_name = "SecureUnownedFiles"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option=None):
        """
        Initiating File System Scan to find unowned files
        """

        messages = {}
        messages['messages'] = []


        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        all_files_owned = True
        try:
            in_obj = open(self.__target_file, 'r')
            lines = in_obj.readlines()
            for line in lines:
                fields = line.rstrip('\n').split('|')

                if len(fields) != 6:
                    continue

                if fields[1][0] == 'X':
                    all_files_owned = False
                    msg = "(CCE 4223-4) %s is unowned." % fields[-1]
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    if len(messages['messages']) < 10:
                        messages['messages'].append("Fail: %s" % msg)
                    else:
                        if len(messages['messages']) > 10:
                           continue
                        messages['messages'].append("See log for full list of failures...")

                if fields[1][1] == 'X':
                    all_files_owned = False
                    msg = "(CCE 3573-3) %s has no group assigned." % fields[-1]
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    if len(messages['messages']) < 10:
                        messages['messages'].append("Fail: %s" % msg)
                    else:
                        if len(messages['messages']) > 10:
                           continue
                        messages['messages'].append("See log for full list of failures...")

                del fields

        except IOError, err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        in_obj.close()
        if all_files_owned == True:
            return True, '', messages

        return False, 'Unowned files exist', messages

    ##########################################################################
    def apply(self, option=None):
        """Change user/group of unowned files to nobody"""

        messages = {}
        messages['messages'] = []

        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        all_files_owned = True
        file_list = []
        try:
            in_obj = open(self.__target_file, 'r')
            lines = in_obj.readlines()
            for line in lines:
                fields = line.rstrip('\n').split('|')
                if len(fields) != 6:
                    continue

                if fields[1][0] == 'X' or fields[1][1] == 'X':
                    file_list.append(fields[-1])

                del fields

        except IOError, err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        change_record = {}

        # Get numeric values for nobody
        try:
            nobody_uid = pwd.getpwnam("nobody")[2]
            nobody_gid = grp.getgrnam("nobody")[2]
        except KeyError:
            msg = "Unable to to determine UID/GID of 'nobody'"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
 
        #  Change unowned user/group to "nobody"
        for filename in file_list:
            
            changes_to_make = {}
            # Get stat info for current file
            try:
                statinfo = os.stat(filename)
            except OSError, err:
                msg = "Unable to stat %s: %s" % (filename, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                continue

            # Record original settings
            try:
                # try to translate uid top name
                pwd.getpwuid(statinfo.st_uid)
            except KeyError:
                changes_to_make['owner'] = nobody_uid

            try:
                # try to translate gid to name
                grp.getgrgid(statinfo.st_gid)
            except KeyError:
                changes_to_make['group'] = nobody_gid
                
            if changes_to_make != {}:
                change_record.update(sb_utils.file.fileperms.change_file_attributes( filename, changes_to_make))
                all_files_owned = False

        # Problem files are no longer valid
        if all_files_owned or change_record == {}:
            return False, 'empty', messages
        else:
            return True, str(change_record), messages

    ##########################################################################
    def undo(self, change_record=None):
        """Undo removal of user/group change of unowned files"""


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return True

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "uid:gid:filename\n"  - mode should be interpreted as octal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split(':')
                if len(fspecs) != 3:
                    continue
                new_rec[fspecs[2]] = {'owner':int(fspecs[0]),
                                      'group':int(fspecs[1])}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return True


#if __name__ == '__main__':
#    TEST = SecureUnownedFiles()
#    print TEST.scan()

