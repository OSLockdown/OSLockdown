#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#
# Restrict the use of compiler tools such as gcc to only root
# by setting their permissions to 0700.
#

import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import pwd
import stat
import sb_utils.file.fileperms

class RestrictCompilerTools:

    def __init__(self):
        self.module_name = "RestrictCompilerTools"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__file_analyze = 1

        # fspec : octal mode MASK, owner, group, recursive
        # owner/group: use -1 for "leave as is"
        # recursive: use a 1 to indicate a directory to recurse
        if sb_utils.os.info.is_solaris() == True: 
            self.__file_data = {
                 '/usr/sfw/bin/gcc': '0500,root,root,0',
                 '/usr/sfw/bin/g++': '0500,root,root,0' }
        else:
            self.__file_data = {
                 '/usr/bin/gcc': '0500,root,root,0',
                 '/usr/bin/g++': '0500,root,root,0'}

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        file_count = 0
        failure_flag = False
        for testfile in self.__file_data.keys():
            msg = "Scan: checking ownership and permissions on %s" % testfile
            self.logger.info(self.module_name, msg)

            if not os.path.exists(testfile):
                msg = "%s does not exist" % testfile
                self.logger.warn(self.module_name, msg)
                continue
                
            if not os.path.isfile(testfile):
                msg = "%s is not a file" % testfile
                self.logger.warn(self.module_name, msg)
                continue

            file_count += 1
            try:
                statinfo = os.stat(testfile)
            except OSError, err:
                msg = "Unable to stat file %s: %s" % (testfile, err)
                self.logger.error(self.module_name, msg)
                continue

            if stat.S_ISREG(statinfo.st_mode) == False:
                msg = "%s is not a regular file" % testfile
                self.logger.warn(self.module_name, msg)
                continue

            filemode = int(oct(stat.S_IMODE(statinfo.st_mode)))
            try:
                testfile_owner = pwd.getpwuid(statinfo.st_uid)[0]
            except KeyError:
                msg = "Unable to determine owner of %s" % (testfile)
                self.logger.error(self.module_name, msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        
            if filemode != 500 or testfile_owner != 'root':
                msg = "%s is owned by '%s' with perms %d; expected " \
                      "it to be owned by 'root' with perms 500" % \
                      (testfile, testfile_owner, filemode) 
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                failure_flag = True
 
        
        if file_count == 0:
            msg = "compiler tools not found"
            self.logger.notice(self.module_name, msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        if failure_flag == True:
            reason = "compiler tools are not restricted."
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        change_record = {}
        for testfile in self.__file_data.keys():
            if not os.path.isfile(testfile):
                continue
                        
            changes_to_make = {'owner':'root',
                               'group':'root',
                               'dacs': 0500}
            change_record.update(sb_utils.file.fileperms.change_file_attributes(testfile, changes_to_make))

        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)

            
    ##########################################################################
    def undo(self, change_record=None):

        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


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
                                      'dacs':int(fspecs[1],8)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

