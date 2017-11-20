#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
# Restric the use of the 'traceroute' and 'ping' commands
# This is done by setting permissions on them to 0500
# which allows only root to execute them.
#

import os
import sys
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms


class DisableNetAnalysisTools:

    def __init__(self):
        self.module_name = "DisableNetAnalysisTools"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        # Define a dictionary of files and permissions. The permissions
        # are the operating system defaults. This module will set the 
        # file permissions to 0500 (root,root) and the permissions
        # identified in the dictionary are the what the module will
        # revert to when the undo method is called.

        self.__file_data = [ '/usr/sbin/tethereal', '/usr/sbin/wireshark',
                             '/usr/sbin/tshark',    '/usr/sbin/ethereal',
                             '/usr/sbin/tcpdump',   '/sbin/tcpdump',
                             '/usr/sbin/snoop' ]
      


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        file_count = 0
        failure_flag = False
        for testfile in self.__file_data:
            msg = "Checking execute permissions on %s" % testfile
            self.logger.info(self.module_name, msg)

            if not os.path.isfile(testfile):
                continue

            # For some reason, os.access(testfile, os.X_OK) does not report
            # correctly in Solaris Python -- so, I have to do it the long way:
            try:
                statinfo = os.stat(testfile)
            except (IOError, OSError) ,err:
                msg = "Unable to stat %s: %s" % (testfile, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                continue
              
            if statinfo.st_mode & stat.S_IXUSR or \
                       statinfo.st_mode & stat.S_IXGRP or \
                       statinfo.st_mode & stat.S_IXOTH:
                msg = "%s is executable" % testfile
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                file_count += 1
            
        if file_count > 0:
            return 'Fail', ''
        else:
            return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):

        change_record = {}
        for testfile in self.__file_data:
            if not os.path.isfile(testfile):
                continue

            msg = "Checking execute permissions on %s" % testfile
            self.logger.info(self.module_name, msg)

            try:
                fstatinfo = os.stat(testfile)
            except (IOError, OSError), err:
                msg = "Apply Error: Unable to stat %s: %s" % (testfile, err)
                self.logger.error(self.module_name, msg)
                continue

            execflag = False
            if fstatinfo.st_mode & stat.S_IXUSR:
                execflag = True
            if fstatinfo.st_mode & stat.S_IXGRP:
                execflag = True
            if fstatinfo.st_mode & stat.S_IXOTH:
                execflag = True
                        
            if execflag == False:
                continue
           
            changes_to_make = {'owner':'root',
                               'group':'root',
                               'dacs':0400}
            change_record.update(sb_utils.file.fileperms.change_file_attributes(testfile, changes_to_make))
            testfile_mode = int(oct(stat.S_IMODE(fstatinfo.st_mode)))
                    


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
        #   of "filename|mode|uid|gid\n" - note mode does not have leading zero
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[2],
                                      'group':fspecs[3],
                                      'dacs':int(fspecs[1],8)}  # assume octal perms
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

