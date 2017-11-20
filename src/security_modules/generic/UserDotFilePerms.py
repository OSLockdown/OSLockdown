#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

#
# This module gets a list of all local non-system user accounts
# and their home directory.
#
# It then makes sure that non of the dot files (i.e., .profile)
# are not group or world writeable.
#
# It does not care about ownership. Only the home directory 
# contents module does.
#

import os
import stat
import glob
import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms
import sb_utils.acctmgt.users

###############################################################################
class UserDotFilePerms:
    """
    UserDotFilePerms Security Module handles the guideline for access
    permissions on user dot files.
    """

    def __init__(self):
        self.module_name = "UserDotFilePerms"
        self.__target_file = '/etc/passwd'
        self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.info.is_solaris() == True:
            self.__maxuid = 100
        else:
            self.__maxuid = 500

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """
        Check the file permissions on user dot files.
        """



        
        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            user = pwd.getpwnam(userName)
            msg = "Checking user '%s' home directory: %s" % (user[0], user[5])
            self.logger.debug(self.module_name, msg)

            homedir = user[5]
            filelist = glob.glob(os.path.join(homedir,'.[A-Za-z0-9]*'))
            for dotfile in filelist:
                try:
                    statinfo = os.stat(dotfile)
                except OSError, err:
                    msg = "Unable to stat %s: %s" % (dotfile, err)
                    self.logger.error(self.module_name, 'Scan Error: ' + msg)
                    continue

                if (statinfo.st_mode & 0020) or (statinfo.st_mode & 0002):
                    reason = '%s has permissions of %o' % \
                         (dotfile,stat.S_IMODE(statinfo.st_mode))
                    self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                    return 'Fail', reason

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """
        Modify the file permissions on user dot files.
        """

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''


        change_record = {}

        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            user = pwd.getpwnam(userName)
            if user[2] < self.__maxuid:
                msg = "Skipping user '%s', as UID %d is considered a system account" % (user[0], user[2])
                self.logger.debug(self.module_name, msg)
                continue

            msg = "Checking user '%s' home directory: %s" % (user[0], user[5])
            self.logger.debug(self.module_name, msg)

            homedir = user[5]
            filelist = glob.glob(os.path.join(homedir,'.[A-Za-z0-9]*'))
            for dotfile in filelist:
                changes_to_make = {}
                msg = "Checking %s" % dotfile
                self.logger.debug(self.module_name, msg)
                try:
                    statinfo = os.stat(dotfile)
                except OSError, err:
                    msg = "Unable to stat %s: %s" % (dotfile, err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    continue

                if (statinfo.st_mode & 0020) or (statinfo.st_mode & 0002):
                    newperms = statinfo.st_mode & 0755
                    changes_to_make ['dacs'] = newperms
                    change_record.update (sb_utils.file.fileperms.change_file_attributes( dotfile, changes_to_make))
#                    change_record += '%s %d\n' % (dotfile, stat.S_IMODE(statinfo.st_mode))

        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the file permissions on user dot files.
        """

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1, msg


        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename mode\n"  - mode should be interpreted as decimal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split(' ')
                if len(fspecs) != 2:
                    continue
                new_rec[fspecs[0]] = {'dacs':int(fspecs[1], 10)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1
