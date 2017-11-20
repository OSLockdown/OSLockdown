#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import re
import glob
import shlex

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.SELinux
import sb_utils.file.exclusion
import sb_utils.file.fileperms

class SetMesgN:
    """
    SetMesgN module restricts write access to a terminal to only the owner
    """

    ##########################################################################
    def __init__(self):

        self.module_name = "SetMesgN"
        self.regex = re.compile(r'^(\s*[^#]?mesg\s+-?)([nNyY])')
        
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def _change_one_file(self, action, fileName):

        # generate exclusion list *early* to avoid cluttering log
        sb_utils.file.exclusion.exlist()

        # Protect file
        tcs_utils.protect_file(fileName)

        action_record = ""
        madeChange = False
        mesg_found = False
        actionName = action[0].upper()+action[1:]

        msg = "%s: Examining '%s' " % (actionName, fileName)
        self.logger.debug(self.module_name, msg)
        lines = []
        try:
            lines = open(fileName, 'r').readlines()
        except Exception, err:
            msg = "Unable to open file %s (%s)." % (fileName, str(err))
            self.logger.error(self.module_name, '%s Error: %s' % (actionName, msg))

        numLines = len(lines)
        for lr in range(numLines):
            match = self.regex.search(lines[lr])
            if match:
#                print >>sys.stderr,"Found match at line %s:%d" % (fileName,lr)
                mesg_found = True
                newline = self.regex.sub(r'\1n',lines[lr])
                mesg_found = True
                if newline != lines[lr]:
                    msg = " found '%s' instead of '%s' at line %d of '%s'" % (lines[lr].strip(), newline.strip(), lr+1,fileName)
                    self.logger.notice(self.module_name,"Scan Failure: %s" % msg) 
                    madeChange = True
                    lines[lr] = newline
                else:
                    msg = "%s: found '%s' at line %d of '%s'" % (actionName, lines[lr].strip(), lr+1,fileName)
                    self.logger.debug(self.module_name, msg) 
                    
#        self.logger.info(self.module_name, 'Read %d lines from %s, mesg_found = %s' % (len(lines), fileName, mesg_found))
        if mesg_found != True:
            if numLines > 0 and not lines[-1].endswith("\n"):
                lines.append("\n")
            lines.append("mesg n\n")
            madeChange = True
            msg = "Error: Did not find any 'mesg' commands in '%s'" % (fileName)
            self.logger.notice(self.module_name, 'Scan Error: %s' % (msg))
            if action == 'apply':
                msg = "Added 'mesg n' to '%s'" % ( fileName)
                self.logger.notice(self.module_name, 'Apply: %s' % (msg))

        if madeChange:
            if action == 'apply':
                try:
                    out_obj = open(fileName + '.new', 'w').writelines(lines)
                except Exception, err:
                    msg = "Unable to create/write to temporary file (%s)." % str(err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
    

                action_record = tcs_utils.generate_diff_record(fileName + '.new', fileName)

                try:
                    shutil.copymode(fileName, fileName + '.new')
                    shutil.copy2(fileName + '.new', fileName)
                    sb_utils.SELinux.restoreSecurityContext(fileName)
                    os.unlink(fileName + '.new')
                except OSError:
                    msg = "Unable to replace %s with new version." % fileName
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record = "Changed"
        return action_record

    ##########################################################################
    def scan(self, optionDict=None):

        allFiles = sb_utils.file.fileperms.splitStringIntoFiles(optionDict['filesToSearch'], globbing=True)
        retval = False  # assume a change is needed, if we actually pass we'll change this 
        allChanges=[]

        for thisFile in allFiles:
            if not os.path.exists(thisFile):
                continue
            changesNeeded = self._change_one_file('scan', thisFile)
            allChanges.append(changesNeeded)
            if not changesNeeded:
                retval = True
                break
        allChanges = ''.join(allChanges)
        
        if not allChanges:
            return retval, '"mesg n" command found in at least one file', {}
        else:
            return retval, '"mesg n" command not found in at least initialization file(s)', {}
    

    ##########################################################################
    def apply(self, optionDict=None):

        result,reason,msg = self.scan(optionDict)
        if result == True:
            return False, reason,msg
        
        allFiles = sb_utils.file.fileperms.splitStringIntoFiles(optionDict['filesToSearch'], globbing=True)
        
        allChanges=[]
        allMessages = []

        for thisFile in allFiles:
            if not os.path.exists(thisFile):
                continue
            changesMade = self._change_one_file('apply', thisFile)
            allChanges.append(changesMade)
            if changesMade:
                break
        allChanges = ''.join(allChanges)
        if not allChanges:
            return False, 'No changes to initialization file(s) required', ''
        else:
            return True, str(allChanges), ''
    


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        if change_record == '':
            msg = "Empty change record supplied - undo has nothing to do"
            self.logger.warn(self.module_name, 'Undo Error: ' + msg)
            return False

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "'mesg n' entry reverted in shell resource files."
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True

