#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

# This module reads a file produced by the sb-scanner binary
# The format of the file is as follows:
#
# <problemmask>|<perms>|<uid>|<guid>|<exp_uid>|<exp_gid>|<fullpath_of_file>
# 
# The problem mask is a simple 8-byte string with either a dash or 
# an X. The letter X indicates that it is True.
#
# 0 - No owner
# 1 - No group
# 2 - Uneven Perms
# 3 - SUID
# 4 - SGID
# 5 - Sticky bit
# 6 - World writeable
# 7 - Group writeable
#
#

import os
import sys


sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import sb_utils.file.fileperms

class CorrectUnevenPerms:
    """
    Provides class CorrectUnevenPerms
    """

    def __init__(self):
        self.module_name = "CorrectUnevenPerms"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option=None):
        """No options are available"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):
        """
        Check for uneven file permissions
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

        try:
            in_obj = open(self.__target_file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to read file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        found_bad_one = False
        for line in in_obj.xreadlines():
            fields = line.strip('\n').split('|')

            if len(fields) != 6:
                continue

            if fields[1][2] == "X":
                msg = '%s has uneven permissions (%s) .' % (fields[-1], fields[4])
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg )
                found_bad_one = True

            del fields


        in_obj.close()
        if found_bad_one == True:
            return 'Fail', ''

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """
        Corrects the permissions
        """

        change_record = {}


        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        try:
            in_obj = open(self.__target_file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        changes_to_make = {'dacs':0755}
        for line in in_obj.xreadlines():
            line = line.strip('\n')
            fields = line.split('|')

            if len(fields) != 6:
                continue

            # Uneven Perms?
            if fields[1][2] != 'X': 
                continue
            
            change_record.update(sb_utils.file.fileperms.change_file_attributes(fields[5], changes_to_make))

        in_obj.close()

        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the file permissions on home directories.
        """


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # check to see if this might be an oldstyle change record, which is a string of entries
        # where each entry has '|' separated fields 6
        # If so, convert that into the new dictionary style, where we only care about the
        # filename and original perms (fields 5 and 4 right now)
        # Note that the 4 field, with the dacs, already has a leading 0 to indicate octal, so import accordingly
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 6:
                    continue
                new_rec[fspecs[5]] = {'dacs':int(fspecs[4], 8)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)


        msg = ''
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

