#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import pwd
import grp
import glob
import stat

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.file.fileperms

#
# Make sure all files in /etc/init.d/ are owned by
# root and have permissions no greater than 755
#
#
#

class SysRcScriptPerms:
    """
    SysRcScriptPerms Security Module handles the guideline for access permissions
    on System Control Scripts
    """

    def __init__(self):
        self.module_name = "SysRcScriptPerms"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__log_analyze = 1

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):
        """
        Check the file permissions on system run control scripts
        """

        failure_flag = False

        # Grab all rc scripts from /etc/init.d/ and /etc/rc?.d directories
        rcfiles = glob.glob('/etc/init.d/*')
        rcfiles.extend(glob.glob('/etc/rc?.d/*'))

        for testfile in rcfiles:
            try:
                statinfo = os.stat(testfile)
            except OSError, err:
                msg = "Scan Error: %s: %s" % (testfile, err)
                self.logger.error(self.module_name, msg)
                continue
           
            testfile_mode  = int(oct(stat.S_IMODE(statinfo.st_mode)))
            testfile_owner = pwd.getpwuid(statinfo.st_uid)[0]
            testfile_group = grp.getgrgid(statinfo.st_gid)[0]

            statmsg = "found perms %s, owned by '%s', and group '%s'" % \
                    (testfile_mode, testfile_owner, testfile_group)

            # Simple debug log message
            msg = "Checking %s; %s" % (testfile, statmsg)
            self.logger.debug(self.module_name, msg)
           
            # Owner must be root or bin
            if testfile_owner != 'root' and testfile_owner != 'bin':
                msg = "Scan Failed: %s owner not 'root' or 'bin'; %s" % \
                       (testfile, statmsg)
                self.logger.notice(self.module_name, msg)
                failure_flag = True
                continue

            # Group owner of file okay? (root, bin, or sys)
            if statinfo.st_gid not in [0, 2, 3]:
                msg = "Scan Failed: %s group is not 'root', 'sys', or "\
                      "'bin'; %s" % (testfile, statmsg)
                self.logger.notice(self.module_name, msg)
                failure_flag = True
                continue

            # Group or world writeable
            if statinfo.st_mode & stat.S_IWGRP or \
                                              statinfo.st_mode & stat.S_IWOTH:
                msg = "Scan Failed: %s should only be writable by "\
                      "owner; %s" % (testfile, statmsg)
                self.logger.notice(self.module_name, msg)
                failure_flag = True
                continue

        if failure_flag == True:
            return 'Fail', 'Some RC scripts have bad permissions'
        else:
            return 'Pass', ''



    ##########################################################################
    def apply(self, option=None):
        """
        Modify the file permissions on system run control scripts
        """

        change_record = {}

        # Grab all rc scripts from /etc/init.d/ and /etc/rc?.d directories
        rcfiles = glob.glob('/etc/init.d/*')
        rcfiles.extend(glob.glob('/etc/rc?.d/*'))

        for testfile in rcfiles:
            try:
                statinfo = os.stat(testfile)
            except OSError, err:
                msg = "Apply Error: %s: %s" % (testfile, err)
                self.logger.error(self.module_name, msg)
                continue

            testfile_owner = pwd.getpwuid(statinfo.st_uid)[0]

            # Owner must be root or bin
            changes_to_make = {}
            if (testfile_owner != 'root' and testfile_owner != 'bin') or \
                                            statinfo.st_gid not in [0, 2, 3]:
                changes_to_make['owner'] = 'root'
                changes_to_make['group'] = 'root'


            # Group or world writeable
            if statinfo.st_mode & stat.S_IWGRP or \
                                              statinfo.st_mode & stat.S_IWOTH:
                changes_to_make['dacs'] = 0755


            if changes_to_make != {}:
                change_record.update(sb_utils.file.fileperms.change_file_attributes( testfile, changes_to_make))
        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the file permissions on system run control scripts.
        """

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|mode|uid|gid\n"  - mode should be interpreted as octal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[2],
                                      'group':fspecs[3],
                                      'dacs':int(fspecs[1], 8)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

