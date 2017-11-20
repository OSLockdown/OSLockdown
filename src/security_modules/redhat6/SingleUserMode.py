#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Configure system to require password when going into
# single user mode

# Redhat uses upstart for this rather than /etc/inittab...
# *BUT* slightly differently than Fedora does
# RH attempts to use a variable (SINGLE) set in /etc/sysconfig/init indicating 
# the program to use, if not found then use /bin/sushell.  We'll set this to 
# 'SINGLE=/sbin/sulogin' instead.

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class SingleUserMode:
    """Handle single user mode password."""

    def __init__(self):
        self.module_name = "SingleUserMode"
        
        for tfile in ['/etc/sysconfig/init']:
            if os.path.exists(tfile):
                self.__target_file = tfile
                break
        self.problems = ''
        self.changes = ''
        self.changeRec = None
    
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.lines = []
        
    ##########################################################################
    def validate_input(self, option):
        """validate input"""
        if option and option != 'None':
            return 1
        return 0

    
    def makeChanges(self, mustExec):
        
        execLines = []
        
        for ln in range(len(self.lines)):
            line = self.lines[ln].strip()
            if '#' in line:
                line = line[:line.find('#')]
            fields = line.split('=')
            if not fields or fields[0] != 'SINGLE' or len(fields) != 2:
                continue
            execLines.append(ln)
        
        if len(execLines) == 0:    
            self.problems = "Did not find variable assignment for 'SINGLE' in '%s' " % (self.__target_file)
            msg = self.problems
            self.lines.append("SINGLE=%s\n" % mustExec)
            self.changeRec = "SINGLE="
        else:
            ln = execLines[0]
            foundCMD = self.lines[ln].strip()       
            foundArg = foundCMD.split('=')[1].strip()
            if not mustExec :
                self.changes = "Removed 'SINGLE=%s' from '%s'" % (foundArg, self.__target_file)
                self.changeRec=self.lines.pop(ln)
            elif foundArg != mustExec:
                self.problems = "Found 'SINGLE=%s' instead of 'SINGLE=%s' in '%s' "% (foundArg, mustExec, self.__target_file)
                self.lines[ln] = self.lines[ln].replace(foundArg, mustExec)
                self.changes = "Replaced 'SINGLE=%s' with 'SINGLE=%s' in '%s'" % (foundArg, mustExec, self.__target_file)
                self.changeRec = "SINGLE=%s" % foundArg


    ##########################################################################
    def scan(self, option=None):
        """ Check to see if sulogin is required."""

        retval = True
        messages={'messages':[]}
        msg = ""
        self.lines = open(self.__target_file).readlines()
        
        self.makeChanges("/sbin/sulogin")
        if not self.problems:
            msg = "Found 'SINGLE=%s' in '%s' " % (option, self.__target_file)
            self.logger.info(self.module_name, msg)
            retval = True
        else:
            msg = self.problems
            self.logger.info(self.module_name, self.problems)
            messages['messages'].append(self.problems)
            retval = False
                
        return retval, msg, messages
        
    ##########################################################################
    def apply(self, option=None):
        """Enable password requirement for single user mode."""

        result, reason, messages = self.scan()
        if result == True:
            return False, reason, messages
        # if we got here, we either fixed it or decided to punt because we didn't know how.  Raise a ManualActionReqd
        # unless we have a changeRec
        
        if not self.changeRec:
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, self.problems))
        else:
            messages['messages'] = [self.changes]
            open(self.__target_file,"w").writelines(self.lines)
        return True, self.changeRec, messages
        
    ##########################################################################
    def undo(self, change_record=None):
        """ Remove sulogin addition."""
        # Note - left code in here to revert what previous versions would have done....
        # old style change rec simply had 'added'
         
        if change_record == "added":
            try:
                origfile = open(self.__target_file, 'r')
                tmpFile = self.__target_file+".new"
                workfile = open(tmpFile, 'w')
            except IOError, err:
                self.logger.error(self.module_name, 'Undo Error: ' + str(err))
                raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))


            for line in origfile:
                if line == "~~:S:wait:/sbin/sulogin\n":
                    continue
                else:
                    workfile.write(line)

            origfile.close()
            workfile.close()

            try:
                shutil.copymode(self.__target_file, tmpFile)
                shutil.copy2(tmpFile, self.__target_file)
                sb_utils.SELinux.restoreSecurityContext(self.__target_file)
                os.unlink(tmpFile)
            except OSError, err:
                self.logger.error(self.module_name, 'Undo Error: ' + str(err))
                raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))

            msg = '/sbin/sulogin disabled for single user mode entry in inittab'
        else:
            # change record is formed "SINGLE=ARG", we want to ship ARG into makeChanges (or None if ARG is empty)
            changeArg = change_record.split('=')[-1]
            self.lines = open(self.__target_file).readlines()
            self.makeChanges(changeArg)
            if self.changes:
                open(self.__target_file,"w").writelines(self.lines)
                msg = self.changes
            else:
                msg = "Undo Error: Unable to revert changes to '%s' " % (self.__target_file)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

