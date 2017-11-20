#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#  RootPath Security Module searches for '.' and world-writable directories
#  in the root user's path.
#
 
import os
import stat
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms

class RootPath:

    def __init__(self):
        self.module_name = "RootPath"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        path = os.getenv('PATH')

        msg = "Analyzing PATH environment variable which is currently set "\
              "to: %s" % path
        self.logger.debug(self.module_name, 'Scan: ' + msg)

        if not path:
            # don't think this will ever happen, but we'll test for it
            return 'Pass', ''

        for mydir in path.split(':'):
            if mydir == '.':
                reason = "root user's PATH environment variable contains '.'"
                self.logger.info(self.module_name, 'Scan Failed: ' + reason)
                return 'Fail', reason

            # check for world-writable dirs
            if not os.path.isdir(mydir):
                continue
            try:
                statinfo = os.stat(mydir)
            except OSError, err:
                msg = "Unable to stat directory %s: %s" % (mydir, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            if statinfo.st_mode & stat.S_IWGRP or \
                        statinfo.st_mode & stat.S_IWOTH:
                msg = "root user has writable directories in PATH"
                self.logger.error(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """
        Remove group- and other-writable status of directories in root's PATH
        """

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        path = os.getenv('PATH')

        change_record = {}

        for mydir in path.split(':'):

            if mydir == '.':
                reason = "root user's PATH environment variable contains '.'; you must "\
                         "manually find the shell resource file and correct it."
                self.logger.notice(self.module_name, reason)

            # check for world-writable dirs
            if not os.path.isdir(mydir):
                continue
            try:
                statinfo = os.stat(mydir)

            except OSError:
                msg = "Unable to stat directory %s." % mydir
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            if statinfo.st_mode & stat.S_IWGRP or \
                        statinfo.st_mode & stat.S_IWOTH:

                changes_to_make = {'dacs' : statinfo.st_mode & ~(stat.S_IWGRP | stat.S_IWOTH) }
                change_record.update(sb_utils.file.fileperms.change_file_attributes( mydir, changes_to_make))


        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)


    ##########################################################################
    def undo(self, change_record=None):
        """
        Restore group- and other-writable status in root's PATH
        """

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # check to see if this might be an oldstyle change record, which is a single line like
        # "dirname:mode", where mode is DECIMAL
        # if found, convert to newstyle
        
        if not change_record[0:200].strip().startswith('{') and len(change_record.split(':')) == 2:
            fspecs = change_record.split(':')
            change_record = {}
            change_record[fspecs[0]] = {'dacs':int(fspecs[1], 10)}
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)


        return 1
