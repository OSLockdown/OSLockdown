#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import re
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import sb_utils.file.fileperms

class SecureNetrcFiles:
    """
    SecureNetrcFiles Security Module handles the guidelines for securing
    .netrc files, if they must exist.
    """

    def __init__(self):
        self.module_name = "SecureNetrcFiles"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT

        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """
        Initiating File System Scan to find .netrc Files
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

        secure_netrc_files = True
        netrc_pattern = re.compile(".*/.netrc$")
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError:
            msg = "Unable to open file %s." % self.__target_file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        for line in lines:
            if line.startswith('d|'):
                continue

            if netrc_pattern.search(line):
                fields = line.rstrip('\n').split('|')
                if len(fields) != 6:
                    continue

                msg = "%s exists" % fields[5]
                self.logger.warn(self.module_name, msg)

                if fields[4] not in ['0700', '0600', '0400']:
                    msg = "%s exists with insecure permissions %s " % \
                                                            (fields[5], fields[4])

                    self.logger.notice(self.module_name, "Scan Failed: " + msg)
                    secure_netrc_files = False
                
        if secure_netrc_files == True:
            return 'Pass', ''

        msg = 'Insecure .netrc files exist'
        self.logger.info(self.module_name, 'Scan Failed: ' + msg)
        return 'Fail', msg

    ##########################################################################
    def apply(self, option=None):
        """Change access to mode 0600 on .netrc files"""


        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file): 
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        file_list = []
        secure_netrc_files = True
        netrc_pattern = re.compile(".*/.netrc$")
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        for line in lines:
            if line.startswith('d|'):
                continue

            if netrc_pattern.search(line):
                fields = line.rstrip('\n').split('|')
                if len(fields) != 6:
                    continue

                msg = "%s exists" % fields[5]
                self.logger.warn(self.module_name, msg)

                if fields[4] not in ['0700', '0600', '0400']:
                    msg = "%s exists with insecure permissions %s" % \
                                                            (fields[5], fields[4])
                    file_list.append(fields[5])
                    secure_netrc_files = False

        # Problem files are no longer valid
        if secure_netrc_files == True:
            return 0, ''

        change_record = {}

        # Change .netrc files to mode 600
        for insfile in file_list:
            changes_to_make = {'dacs':0600}
            change_record.update(sb_utils.file.fileperms.change_file_attributes(insfile, changes_to_make))

        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

    ##########################################################################
    def undo(self, change_record=None):
        """Undo change of .netrc files to mode 0600"""

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "mode:filename\n"  - mode should be interpreted as decimal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split(':')
                if len(fspecs) != 2:
                    continue
                new_rec[fspecs[1]] = {'dacs':int(fspecs[0], 10)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)
                
        return 1
