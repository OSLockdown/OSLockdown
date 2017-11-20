#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#  Sets Normal User (uid 500-65533) Home directory to
#  be owned that user and their primary group

import os
import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms
import sb_utils.file.exclusion
import sb_utils.acctmgt.users

class HomeDirOwnGrp:

    def __init__(self):
        self.module_name = "HomeDirOwnGrp"

        self.logger = TCSLogger.TCSLogger.getInstance() 

        # List of directories to NEVER, NEVER change ownership on!
        if sb_utils.os.info.is_solaris == True:
            self.__excl_dirs = ( '/', '/cdrom', '/dev', '/devices', '/etc', 
                                 '/export', '/home', '/kernel', '/lib', '/mnt',
                                 '/net', '/opt', '/platform', '/proc', 
                                 '/sbin', '/system', '/tmp', '/usr', 
                                 '/usr/bin', '/usr/lib', '/usr/sbin', 
                                 '/usr/share/lib', '/var/lib', '/vol' )
            self.__user_min = 99
            self.__user_max = 65534
        else:
            self.__excl_dirs = ('/usr', '/etc', '/lib', '/proc', '/opt', '/sbin',
                '/usr/bin', '/usr/sbin', '/', '/var/lib/nfs')
            self.__user_min = 499
            self.__user_max = 65534

    ##########################################################################
    def validate_input(self, option=None):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):
        if option != None:
            option = None

        flag = False
        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            user = pwd.getpwnam(userName)
            homedir = user.pw_dir
            if not os.path.isdir(homedir):
                msg = "Skipping %s home directory assigned to %s "\
                      "because it does not exist" % (homedir, user.pw_name)
                self.logger.info(self.module_name, msg)
                continue

            if homedir not in self.__excl_dirs:
                is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(homedir)
                if is_excluded == True:
                    msg = "Skipping %s (home directory assigned to %s) "\
                              "because it is on the exclusion list" % (homedir, user.pw_name)
                    self.logger.info(self.module_name, msg)
                    continue

                msg = "Checking %s ..." % homedir
                self.logger.debug(self.module_name, msg)
                try:
                    statinfo = os.stat(homedir)
                except OSError:
                    msg = "Unable to stat directory %s." % homedir
                    self.logger.error(self.module_name, 'Scan Error: ' \
                      + msg)

                # Does directory's owner/group match 
                # the real user account specs?
                if statinfo.st_uid != user.pw_uid or user.pw_gid != statinfo.st_gid:
                    msg = 'Owner/group on %s: expected uid/gid of %s/%s but got %s/%s' % \
                           ( homedir, 
                             str(user.pw_uid),
                             str(user.pw_gid),
                             statinfo.st_uid, 
                             statinfo.st_gid
                           )
                    flag = True
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        if flag == True:
            return 'Fail', 'Wrong owner/group found on home directories'

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        if option != None:
            option = None

        change_record = {}
        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            user = pwd.getpwnam(userName)
            homedir = user.pw_dir
            if not os.path.isdir(homedir):
                msg = "Skipping %s home directory assigned to %s "\
                      "because it does not exist" % (homedir, user.pw_name)
                self.logger.info(self.module_name, msg)
                continue

            if homedir not in self.__excl_dirs:
                is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(homedir)
                if is_excluded == True:
                    msg = "Skipping %s (home directory assigned to %s) "\
                              "because it is on the exclusion list" % (homedir, user.pw_name)
                    self.logger.info(self.module_name, msg)
                    continue

                try:
                    statinfo = os.stat(homedir)
                except OSError:
                    msg = "Unable to stat directory %s." % homedir
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    continue

                # Does directory's owner/group match the real user account specs?
                if statinfo.st_uid != user.pw_uid or user.pw_gid != statinfo.st_gid:
                    changes_to_make = {'owner':int(user.pw_uid),
                                       'group':int(user.pw_gid)}
                    change_record.update (sb_utils.file.fileperms.change_file_attributes( homedir, changes_to_make))
               
        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

    ##########################################################################
    def undo(self, change_record=None):
#                            change_record += '%s|%d|%d\n' % (homedir, statinfo.st_uid, statinfo.st_gid)

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0


        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|uid|gid\n"  - mode should be interpreted as octal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 3:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[1],
                                      'group':fspecs[2]}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

