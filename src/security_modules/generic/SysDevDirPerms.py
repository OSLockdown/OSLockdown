#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Ensure that NO directory under /dev and /devices do not have
# group or world write. Additionally, they should be owned by
# root.
#
# Solaris, has one exception: /dev/usb which is 770 by default.

import os
import sys
import stat
import pwd
sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms


class SysDevDirPerms:

    def __init__(self):
        self.module_name = "SysDevDirPerms"
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__listofdirs = [ '/dev', '/devices' ]

        if sb_utils.os.info.is_solaris() == True:
            self.__exclude = ['/dev/usb']
        else:
            self.__exclude = ['/dev/shm']


    ########################################################################## 
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def _get_list_of_badperms(self, startpoint=None):
       
        if startpoint == None:
            return None
  
        if not os.path.isdir(startpoint):
            return None

        msg = 'Analyzing directory %s' % startpoint
        self.logger.info(self.module_name, msg)
        badlist = {} 
        for root, dirs, files in os.walk(startpoint):

            for xdirs in dirs: 
                testdir = os.path.join(root, xdirs)
                try:
                    statinfo = os.stat(testdir)
                except OSError, err:
                    msg = "Unable to stat directory %s: %s" % (testdir, err)
                    self.logger.error(self.module_name, msg)
                    continue
 
                if stat.S_ISDIR(statinfo.st_mode) == False:
                    continue
     
            
                presvmode = stat.S_IMODE(statinfo.st_mode)
                dirmode   = int(oct(stat.S_IMODE(statinfo.st_mode)))
                grpwrite  = statinfo.st_mode & stat.S_IWGRP
                othwrite  = statinfo.st_mode & stat.S_IWOTH
                owner     = pwd.getpwuid(statinfo.st_uid)[0]
                
                if owner != 'root':
                    msg = "Directory %s is not owned by 'root'" % testdir
                    self.logger.notice(self.module_name, msg)
                    badlist[testdir] = presvmode
 
 
 
                if grpwrite or othwrite:
 
                    if testdir in self.__exclude:
                        msg = "Directory %s has permissions of %d but is on "\
                              "the exclusion list" % (testdir, dirmode)
                        self.logger.notice(self.module_name, msg)
                    else:
                        msg = 'Directory %s has permissions of %d' % (testdir, dirmode)
                        self.logger.notice(self.module_name, msg)
                        badlist[testdir] = presvmode
 
                    continue
     
 
                if dirmode > 755:
                    msg = 'Directory %s has permissions of %d' % (testdir, dirmode)
                    self.logger.notice(self.module_name, msg)
                    badlist[testdir] = presvmode
     
            return badlist 
     
     
    ########################################################################## 
    def scan(self, option=None):

        failure_flag = False

        for subdir in self.__listofdirs:
            results = self._get_list_of_badperms(startpoint=subdir) 
            if results == None:
                continue

            if len(results):
                failure_flag = True

        if failure_flag == True:
            return 'Fail', 'Found bad permissions on command files'

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        change_record = {}
        for subdir in self.__listofdirs:
            results = self._get_list_of_badperms(startpoint=subdir)
            if results == None:
                continue

            # If bad perms were found, set them to 0755
            if len(results):
                for key in results.keys():

                    changes_to_make = {'owner':'root',
                                       'group':'root',
                                       'dacs':0755}
                    change_record.update(sb_utils.file.fileperms.change_file_attributes( key, changes_to_make))
                                            
        if change_record == {}:
            return 0 , ''
        else:
            return 1, str(change_record)

    ########################################################################## 
    def undo(self, change_record=None):


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|uid|gid|mode\n"  - mode should be interpreted as decimal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[1],
                                      'group':fspecs[2],
                                      'dacs':int(fspecs[3],10)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)



        return 1
