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

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms


class DisableFspd:
    """
    Disable the fspd client binary
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'DisableFspd'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__targetpath = [ '/bin/fspd', 
                              '/sbin/fspd', 
                              '/usr/bin/fspd', 
                              '/usr/sbin/fspd', 
                              '/usr/local/bin/fspd', 
                              '/usr/sfw/bin/fspd',
                              '/usr/local/sbin/fspd'   ]

    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Check for file and file permissions"""
        if option != None:
            option = None


        loc = 'None'
        found = False
        for loc in self.__targetpath:
            msg = "Looking for %s" % loc
            self.logger.debug(self.module_name, msg)

            if  os.path.isfile(loc):
                msg = "Found %s" % loc
                self.logger.info(self.module_name, msg)
                found = True
            else:
                continue

            #Now check the file permissions$
            try:
                statinfo = os.stat(loc)
            except (IOError, OSError), err:
                msg = "Unable to stat %s: %s" % (loc, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            # We want the permissions to 000
            if statinfo.st_mode & 0777 ^ 0000 != 0:
                reason = loc + ' has permissions of %o instead of 000' % \
                    stat.S_IMODE(statinfo.st_mode)
                self.logger.notice(self.module_name, 'Scan Failed: ' \
                + reason)
                return 'Fail', reason

            elif statinfo.st_uid != 0:
                reason = loc + ' has owner %d instead of 0 (root)' % \
                    statinfo.st_uid
                self.logger.notice(self.module_name, 'Scan Failed: ' \
                + reason)
                return 'Fail', reason

        if found == False:
            msg = "Fspd is not installed on the system"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """
        Disable the executable if present
        """

        change_record = {}
        try:
            result = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        loc = 'None'
        found = False
        changes_to_make = {'newroot':'root',
                           'group':'root',
                           'dacs':0}
        for loc in self.__targetpath:
            if os.path.isfile(loc):
                found = True
                change_record.update(sb_utils.file.fileperms.change_file_attributes(loc, changes_to_make))
            
        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        try:
            result = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0


        # Old module just blindly set perms on files.  New module only undoes the one it actually applied
        
        if not change_record[0:200].strip().startswith('{') :
            change_record = {}
            for loc in self.__targetpath:
                if os.path.isfile(loc):
                    change_record['loc'] = {'dacs': 0755}
        
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

