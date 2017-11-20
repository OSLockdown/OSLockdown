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
import stat
import glob

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.exclusion
import sb_utils.file.fileperms
import sb_utils.acctmgt.users

QUICK_SCAN = False 
try:
    if QUICK_SCAN == False:
        pass    
except NameError:
    QUICK_SCAN = False


class HomeDirContentPerms:
    """
    HomeDirContentPerms Security Module handles the guideline for 
    access permissions on home directories.
    """

    def __init__(self):
        self.module_name = "HomeDirContentPerms"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


        if sb_utils.os.info.is_solaris == True:
            self.__user_min = 99
            self.__user_max = 65534
        else:
            self.__user_min = 499
            self.__user_max = 65534


        self.__ignore_dirs = ['/sbin', '/bin', '/dev', '/var/lib/nfs', 
                              '/var/spool', '/usr/share', '/usr/net/nls', 
                              '/usr/lib/uucp', '/var/adm', '/var/lib/rpm' ]

        self.__ignore_users = ['daemon', 'nobody', 'apache', 'bin', 
                               'operator', 'listen', 'uucp', 'rpm' ] 
      
        self.excludes = sb_utils.file.exclusion.ExclusionList()
        
    ##########################################################################
    def validate_input(self, option=None):
        """No options are available"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def _homedir_dict(self):

        homedirs = {}
        
        self.excludes.add_excludes(self.__ignore_dirs)

        msg = "For safety, adding %s to master exclusion list" % str(self.__ignore_dirs)
        self.logger.info(self.module_name, msg) 

        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            entry = pwd.getpwnam(userName)
            if entry.pw_shell.rstrip() == '/sbin/nologin':
                msg = "Excluding %s because %s's shell is /sbin/nologin" % (entry.pw_dir, entry.pw_name)
                self.logger.debug(self.module_name, msg)
                continue
                
            is_excluded, why_excluded = self.excludes.file_is_excluded(entry.pw_dir)
            if is_excluded == True:
                msg = "Excluding %s because %s's home directory is on the exclusion list" % (entry.pw_dir, entry.pw_name)
                self.logger.debug(self.module_name, msg)
                continue

            homedirs[entry.pw_name] = entry.pw_dir

        return homedirs

    ##########################################################################
    def scan(self, option=None):
        """
        Check the file permissions on home directories.
        """

        global QUICK_SCAN 

        homedirs = self._homedir_dict()
        if len(homedirs) < 1:
            msg = "Unable to get list of home directories"
            self.logger.error(self.module_name, "Scan Error: " + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        checked_root_files = False
        badfiles = False
        for username in homedirs.keys():
            testdir = homedirs[username]
            msg = "Checking homedir for user %s -> %s" % (username, testdir)

            # In addition to the master exclusion list, there are certain directory
            # paths we should just avoid
            if testdir == '/' or testdir in self.__ignore_dirs:
                msg = "Skipping check of %s which is assigned to %s" % (testdir, username)
                self.logger.debug(self.module_name, msg)
                continue

            ignore_flag = False
            for xdir in self.__ignore_dirs:
                if testdir.startswith(xdir):
                    msg = "Skipping check of %s which is assigned to %s" % (testdir, username)
                    self.logger.debug(self.module_name, msg)
                    ignore_flag = True
                    break

            if ignore_flag == True:
                continue
 
            if username in self.__ignore_users:
                msg = "Skipping check of %s which is assigned to %s" % (testdir, username)
                self.logger.debug(self.module_name, msg)
                continue

            if not os.path.isdir(testdir):
                msg = "%s does not exist but is assigned to %s" % (testdir, username)
                self.logger.error(self.module_name, "Scan Error: " + msg)
                continue

            #-----------------------------------------------------------------
            msg = "Entering %s's assigned home directory " \
                  "%s" % (username, testdir)
            self.logger.debug(self.module_name, msg)

            try:
                statinfo = os.stat(testdir)
            except OSError, err:
                msg = "Unable to stat %s: %s" % (testdir, err)
                self.logger.error(self.module_name, "Scan Error: " + msg)
                continue
                
            if int(pwd.getpwnam(username).pw_uid) != statinfo.st_uid:
                msg = "%s is not owned by '%s'; recommend using 'Home Directory "\
                      "Ownership' module" % (testdir, username)
                self.logger.warn(self.module_name, msg)

            #-----------------------------------------------------------------
            # Traverse the home directory and check each file
            testuid = int(pwd.getpwnam(username).pw_uid)

            for theroot, thedir, subfiles in os.walk(testdir):
                is_excluded, why_excluded = self.excludes.file_is_excluded(theroot)
                if is_excluded == True:
                    self.logger.info(self.module_name, why_excluded)
                    subfiles[:] = []
                    thedir[:] = []
                    continue
                    
                list_of_files = []
                list_of_files.extend(subfiles)
                list_of_files.extend(thedir)

                if checked_root_files == False:
                    extra_files = glob.glob('/.*')
                    for test in extra_files:
                        if os.path.isfile(test):
                            list_of_files.append(test)
                    checked_root_files = True

                for testfile in list_of_files:
                    if testfile.startswith('/'):
                        fullpath = testfile
                    else:
                        fullpath = os.path.join(theroot, testfile)
                    
                    # Ok, see if this is part of our exclusion list...we're looking for things here, since there is
                    # a bug with some versions of FUSE (SUSE11.0 / OpenSuse11 for instance) where the .gvfs *dir*
                    # appears as an an unaccessable file even to root.
                    
                    is_excluded, why_excluded = self.excludes.file_is_excluded(fullpath)
                    if is_excluded == True:
                        self.logger.info(self.module_name, why_excluded)
                        if testfile in thedir:
                            thedir.remove(testfile)
                        continue

                    try: 
                        fileinfo = os.stat(fullpath)
                    except OSError, err:
                        # Ok, see if the name was '.gvfs', if so log it as a warning but *not* a failure
                        if fullpath.endswith('.gvfs') :
                            msg = "Ignoring potential FUSE mount - %s: %s" % (fullpath, err)
                            self.logger.warning(self.module_name, "Apply Error: " + msg)
                        else:
                            msg = "Unable to stat %s: %s" % (fullpath, err)
                            self.logger.error(self.module_name, "Apply Error: " + msg)
                        continue

                    #---------------------------------------------------------
                    # Check local initialization files...
                    if testfile.startswith('.') and stat.S_ISREG(fileinfo.st_mode) == True:
                        filemode = int(oct(stat.S_IMODE(fileinfo.st_mode)))

                        # Special rules for .Xauthority files
                        if testfile == '.Xauthority':
                            if fileinfo.st_mode & 077:
                                msg = "%s has group and other permissions; currently set "\
                                      "to %d (DISA UNIX STIG GEN005180)" % (fullpath, filemode)
                                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                                badfiles = True

                            # User execute Permission?
                            elif fileinfo.st_mode & stat.S_IXUSR:
                                msg = "%s has user execute permission; currently set "\
                                      "to %d (DISA UNIX STIG GEN005180)" % (fullpath, filemode)
                                self.logger.notice(self.module_name, "Scan Failed: " + msg)
                                badfiles = True

                        # Group execute bit enabled?
                        if fileinfo.st_mode & stat.S_IXGRP:
                            msg = "%s has group execute permission; currently set "\
                                  "to %d (DISA UNIX STIG GEN001880)" % (fullpath, filemode)
                            self.logger.notice(self.module_name, "Scan Failed: " + msg)
                            badfiles = True

                    #---------------------------------------------------------
                    # All /.* files must be owned by root
                    if fullpath.startswith('/.'): 
                        if int(fileinfo.st_uid) != 0:
                            msg = "%s is not owned by 'root'" % (fullpath)
                            self.logger.notice(self.module_name, "Scan Failed: " + msg)
                            badfiles = True

                    else:
                        filemode = int(oct(stat.S_IMODE(fileinfo.st_mode)))

                        #-----------------------------------------------------
                        # Is file owned by the same owner as the directory?
                        if testuid != fileinfo.st_uid:
                            msg = "%s is not owned by '%s'" % (fullpath, username)
                            self.logger.notice(self.module_name, "Scan Failed: " + msg)
                            badfiles = True

                        # Group write bit enabled?
                        if fileinfo.st_mode & stat.S_IWGRP:
                            msg = "%s has group write permission; currently set "\
                                  "to %d " % (fullpath, filemode)
                            self.logger.notice(self.module_name, "Scan Failed: " + msg)
                            badfiles = True

                        # Any other permissions?
                        if fileinfo.st_mode & 007:
                            msg = "%s has permissions granted to other; currently set " \
                                  "to %d " % (fullpath, filemode)
                            self.logger.notice(self.module_name, "Scan Failed: " + msg)
                            badfiles = True

                
                    #---------------------------------------------------------
                    if QUICK_SCAN == True and badfiles == True:
                        msg = "Quick Scan Enabled - Module finishes after first issue detected"
                        self.logger.info(self.module_name, msg)
                        return 'Fail', ''

            
        if badfiles == True:
            return 'Fail', ''

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """
        Modify the file permissions on files inside home directories.
        """
        change_record = {}

        already_have = {}
        homedirs = self._homedir_dict()
        if len(homedirs) < 1:
            msg = "Unable to get list of home directories"
            self.logger.error(self.module_name, "Apply Error: " + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        checked_root_files = False
        for username in homedirs.keys():
            testdir = homedirs[username]

            # In addition to the master exclusion list, there are certain directory           
            # paths we should just avoid                         
            if testdir == '/' or testdir in self.__ignore_dirs:  
                msg = "Skipping check of %s which is assigned to %s" % (testdir, username)    
                self.logger.debug(self.module_name, msg)     
                continue                                         
                                                                 
            ignore_flag = False
            for xdir in self.__ignore_dirs:
                if testdir.startswith(xdir):
                    msg = "Skipping check of %s which is assigned to %s" % (testdir, username)
                    self.logger.debug(self.module_name, msg) 
                    ignore_flag = True
                    break

            if ignore_flag == True:
                continue

            if username in self.__ignore_users:
                msg = "Skipping check of %s which is assigned to %s" % (testdir, username)    
                self.logger.debug(self.module_name, msg)     
                continue                                         
                                                                 
            if not os.path.isdir(testdir):                       
                msg = "%s does not exist but is assigned to %s" % (testdir, username)         
                self.logger.error(self.module_name, "Scan Error: " + msg)                   
                continue     

            #-----------------------------------------------------------------
            msg = "Entering %s's assigned home directory " \
                  "%s" % (username, testdir)
            self.logger.debug(self.module_name, msg)

            try:
                statinfo = os.stat(testdir)
            except OSError, err:
                msg = "Unable to stat %s: %s" % (testdir, err)
                self.logger.error(self.module_name, "Scan Error: " + msg)
                continue
                
            if int(pwd.getpwnam(username).pw_uid) != statinfo.st_uid:
                msg = "%s is not owned by '%s'; recommend using 'Home Directory "\
                      "Ownership' module" % (testdir, username)
                self.logger.warn(self.module_name, msg)

            #-----------------------------------------------------------------
            # Traverse the home directory and check each file
            testuid = int(pwd.getpwnam(username).pw_uid)
            for theroot, thedir, subfiles in os.walk(testdir):

                is_excluded, why_excluded = self.excludes.file_is_excluded(theroot)
                if is_excluded == True:
                    self.logger.info(self.module_name, why_excluded)
                    subfiles[:] = []
                    thedir[:] = []
                    continue
                list_of_files = []                    
                list_of_files.extend(subfiles)        
                list_of_files.extend(thedir)        
                                                      
                if checked_root_files == False:       
                    extra_files = glob.glob('/.*')    
                    for test in extra_files:          
                        if os.path.isfile(test):      
                            list_of_files.append(test)
                    checked_root_files = True         
                                                      
                for testfile in list_of_files:        
                    if testfile.startswith('/'):      
                        fullpath = testfile           
                    else:                             
                        fullpath = os.path.join(theroot, testfile)   

                    # Ok, see if this is part of our exclusion list...we're looking for things here, since there is
                    # a bug with some versions of FUSE (SUSE11.0 / OpenSuse11 for instance) where the .gvfs *dir*
                    # appears as an an unaccessable file even to root.
                    
                    is_excluded, why_excluded = self.excludes.file_is_excluded(fullpath)
                    if is_excluded == True:
                        self.logger.info(self.module_name, why_excluded)
                        if testfile in thedir:
                            thedir.remove(testfile)
                        continue

                    try: 
                        fileinfo = os.stat(fullpath)
                    except OSError, err:
                        # Ok, see if the name was '.gvfs', if so log it as a warning but *not* a failure
                        if fullpath.endswith('.gvfs') :
                            msg = "Ignoring potential FUSE mount - %s: %s" % (fullpath, err)
                            self.logger.warning(self.module_name, "Apply Error: " + msg)
                        else:
                            msg = "Unable to stat %s: %s" % (fullpath, err)
                            self.logger.error(self.module_name, "Apply Error: " + msg)
                        continue
                    changes_to_make = {'dacs':fileinfo.st_mode}

                    #---------------------------------------------------------
                    # Check local initialization files...
                    if testfile.startswith('.') and stat.S_ISREG(fileinfo.st_mode) == True:
#                        filemode = int(oct(stat.S_IMODE(fileinfo.st_mode)))

                        # Special rules for .Xauthority files
                        if testfile == '.Xauthority':
                            if fileinfo.st_mode & 077 or fileinfo.st_mode & stat.S_IXUSR:
                                changes_to_make['dacs'] = 0600

                        # Group execute bit enabled?
                        if fileinfo.st_mode & stat.S_IXGRP:
                            changes_to_make['dacs'] &= ~stat.S_IXGRP


                    #---------------------------------------------------------
                    # All slash dot files must be owned by root
                    if fullpath.startswith('/.'):
                        if int(fileinfo.st_uid) != 0:
                            changes_to_make['owner'] = 'root'

                    else:

                        #---------------------------------------------------------
                        # Is file owned by the same owner as the directory?
                        if testuid != fileinfo.st_uid:
                            changes_to_make['owner'] = testuid

                    # Group Write bit enabled?
                    if fileinfo.st_mode & stat.S_IWGRP:
                        changes_to_make['dacs'] &= ~stat.S_IWGRP

                    # Any other permissions?
                    if fileinfo.st_mode & 007:
                        changes_to_make['dacs'] &= ~007

                    if changes_to_make['dacs'] != fileinfo.st_mode or len(changes_to_make) > 1:
                        if already_have.has_key(fullpath):
                            continue
                        already_have[fullpath] = "xx"
                        change_record.update(sb_utils.file.fileperms.change_file_attributes(fullpath, changes_to_make))
                        

        del already_have

        if change_record == {} :
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
        #   of "filename|uid|gid|mode\n"  - mode should be interpreted as DECIMAL
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[1],
                                      'group':fspecs[2],
                                      'dacs':int(fspecs[3],10)}  # explictly decimal
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

