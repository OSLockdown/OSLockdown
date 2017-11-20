#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

# Search all user home directories for shell initialization 
# files for the use of "mesg -y"


import os
import sys
import pwd
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.exclusion
import sb_utils.acctmgt.users

class RestrictMesgCmd:

    def __init__(self):
        self.module_name = "RestrictMesgCmd"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self._shellInitFiles = ['.bashrc', '.bash_login', '.bash_profile', '.login', 
                          '.profile', '.cshrc', '.profile', '.tcshrc' ]


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    # if a home directory is part of an excluded directory, don't search it
    ##########################################################################
    def _homedir_dict(self):

        homedirs = {}

        noLoginUsers = []

        for userName in sb_utils.acctmgt.users.local_AllUsers():
            entry = pwd.getpwnam(userName)
            try:
                if entry[6].rstrip() == '/sbin/nologin':
                    noLoginUsers.append(entry[0])
                    continue
            except IndexError:
                continue

            is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(entry.pw_dir)
            if is_excluded:
                msg = "Skipping home account for %s : %s" % (entry.pw_name,why_excluded)
                self.logger.debug(self.module_name, msg)
                continue

            homedirs[entry[0]] = entry[5]

        
        if len(noLoginUsers) > 0:
            msg = "Excluding the following accounts because their shell is /sbin/nologin: %s" % str(noLoginUsers)
            self.logger.debug(self.module_name, msg)

        self.logger.debug(self.module_name, "Dictionary of home directories: %s"  % str(homedirs))
        return homedirs


    ##########################################################################
    def scan(self, option=None):

        self.logger.debug(self.module_name, 
              "Looking for local shell initialization files: %s" % str(self._shellInitFiles))

        regex = re.compile('(/usr/bin/mesg|mesg) y')

        homeDirectories = self._homedir_dict()

        scanFailure = False
        failCount = 0
        filesChecked = 0
        for user in homeDirectories.keys():
            if os.path.isdir(homeDirectories[user]):
                self.logger.debug(self.module_name, 
                      "'%s' home directory found: %s" % (user, homeDirectories[user]))
                for testFile in self._shellInitFiles:
                    shellRc = os.path.join(homeDirectories[user], testFile)
                    if os.path.isfile(shellRc):
                        filesChecked = filesChecked + 1
                        self.logger.debug(self.module_name, "Found %s, looking for the 'mesg' command" % shellRc)
                        try:
                            in_obj = open(shellRc, 'r')
                        except IOError, err:
                            msg =  "Unable to open file %s: %s" % (shellRc, err)
                            self.logger.error(self.module_name, 'Scan Error: ' + msg)
                            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

                        lines = in_obj.readlines()
                        in_obj.close()

                        for lineNumber, line in enumerate(lines):
                            if regex.search(line.strip()):
                                msg = """Found "%s" on line number %d of %s""" % (line.strip(), lineNumber+1, shellRc)
                                self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                                scanFailure = True
                                failCount = failCount + 1

        if scanFailure == True:
            msg = "%d local shell initialization file(s) had 'mesg y' present" % failCount
            self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
            return 'Fail', msg
        else:
            return 'Pass',''
       
    ##########################################################################
    def apply(self, option=None):

        regex = re.compile('(/usr/bin/mesg|mesg) y')

        homeDirectories = self._homedir_dict()
        actionRecord = []
        for user in homeDirectories.keys():
            if os.path.isdir(homeDirectories[user]):
                self.logger.debug(self.module_name, 
                      "'%s' home directory found: %s" % (user, homeDirectories[user]))
                for testFile in self._shellInitFiles:
                    shellRc = os.path.join(homeDirectories[user], testFile)
                    changeRequired = False
                    if os.path.isfile(shellRc):
                        newFile = []
                        try:
                            in_obj = open(shellRc, 'r')
                        except IOError, err:
                            msg =  "Unable to open file %s: %s" % (shellRc, err)
                            self.logger.error(self.module_name, 'Apply Error: ' + msg)
                            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                        lines = in_obj.readlines()
                        in_obj.close()

                        for lineNumber, line in enumerate(lines):
                            if regex.search(line.strip()):
                                msg = """Apply: Replacing line number %d of %s with 'mesg n'""" % (lineNumber+1, shellRc)
                                self.logger.notice(self.module_name, msg)
                                newFile.append(regex.sub('mesg y', 'mesg n'))
                                changeRequired = True
                            else:
                                newFile.append(line)

                        if changeRequired == True:
                            try:
                                out_obj = open(shellRc, 'w')
                            except IOError, err:
                                msg =  "Unable to write to file %s: %s" % (shellRc, err)
                                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                            
                            out_obj.write(''.join(newFile))
                            out_obj.write('\n')
                            out_obj.close()
                            msg =  "Updated %s" % (shellRc)
                            self.logger.debug(self.module_name, 'Apply: ' + msg)
                            actionRecord.append(shellRc)
                        else:
                            msg =  "%s is okay: no 'mesg y' found." % (shellRc)
                            self.logger.info(self.module_name, msg)

        if len(actionRecord) > 0:
            return 1, '\n'.join(actionRecord)
        else:
            return 0, ''
            

            
    ##########################################################################
    def undo(self, change_record=None):

        regex = re.compile('(/usr/bin/mesg|mesg) n')

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        for shellRc in change_record.split('\n'):
            changeRequired = False
            if not os.path.isfile(shellRc):
                msg =  "Skipping restoral of %s because it no longer exists" % (shellRc)
                self.logger.notice(self.module_name, 'Undo: ' + msg)
                continue
            
            msg =  "Restoring %s" % (shellRc)
            self.logger.notice(self.module_name, 'Undo: ' + msg)

            newFile = []
            try:
                in_obj = open(shellRc, 'r')
            except IOError, err:
                msg =  "Unable to open file %s: %s" % (shellRc, err)
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            lines = in_obj.readlines()
            in_obj.close()

            for lineNumber, line in enumerate(lines):
                if regex.search(line.strip()):
                    msg = """Undo Performed: Replacing line number %d of %s with 'mesg n'""" % (lineNumber+1, shellRc)
                    self.logger.notice(self.module_name, msg)
                    newFile.append(regex.sub('mesg n', 'mesg y'))
                    changeRequired = True
                else:
                    newFile.append(line)

            if changeRequired == True:
                try:
                    out_obj = open(shellRc, 'w')
                except IOError, err:
                    msg =  "Unable to write to file %s: %s" % (shellRc, err)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
                out_obj.write(''.join(newFile))
                out_obj.write('\n\n')
                out_obj.close()
                msg =  "Updated %s" % (shellRc)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1

