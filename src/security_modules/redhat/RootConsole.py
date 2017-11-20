#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil
import stat
import shlex
try:
    foobar = set([])
except NameError:
    from sets import Set as set

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms
import sb_utils.SELinux




class RootConsole:

    def __init__(self):

        self.module_name = "RootConsole"
        self.__target_file = '/etc/securetty'
        self.logger = TCSLogger.TCSLogger.getInstance()


    def checkSecuretty(self, action, fileName, requiredChanges):
        messages = []
        changes = {fileName:{}}
        
        sb_utils.file.exclusion.exlist()
        
        # if 'content' is empty, then skip checking the actual file contents and move on to permissions
        linesLeft = []
        linesMissing = []
        
        if requiredChanges['content']:
            currentLines = []
            try:
                currentLines = open(fileName,'r').read().splitlines()
            except Exception, err:
                msg =  "Unable to open file for analysis (%s)." % str(err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            lexer = shlex.shlex(requiredChanges['content'])
            lexer.whitespace += ","
            secureDevices = [ path for path in lexer]

            secureSet = set(secureDevices)
            currentSet = set(currentLines)
            # if we have anything in currentFile after removing allowedLines, then we've got a problem
        
            linesLeft    = currentSet - secureSet
            linesMissing = secureSet - currentSet
        
                
            if linesLeft :
                messages.append("/etc/securetty contains entries not on the approved list")
                for entry in linesLeft:
                    msg = "Found '%s' in '%s' " % ( entry, fileName)
                    self.logger.info(self.module_name, "Scan Fail: " + msg)
        
            if linesMissing :
                messages.append("/etc/securetty is missing required entries from the approved list")
                for entry in linesMissing:
                    msg = "Missing '%s' from '%s' " % ( entry, fileName)
                    self.logger.info(self.module_name,"Scan Fail: " + msg)
             
            if not linesLeft and not linesMissing:
                msg = "All required lines present in '%s'" % (fileName)
                self.logger.notice(self.module_name, msg)
                
        
            # In either case, we want to have /etc/securetty *match* the approved list.
            # so for apply if we don't match, simply write out the approved list and 
            # pass the old one back as a list to be restored.  No need for a patch file
            # *but* we our undo will be able to handle a patch set...
        

            if action in ['apply', 'undo'] and (linesLeft or linesMissing):
                try:
                    open(fileName, "w").writelines([ entry+"\n" for entry in secureSet])
                except OSError:
                    msg = "Unable to write '%s' with required lines." % fileName
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        
        options = {}
        if action == "scan":
            options = {'checkOnly':True}
        elif action == "apply":
            options = {'checkOnly':False}
        elif action == "undo":
            options = {'checkOnly':False, 'exactDACs':True}

        changes.update( sb_utils.file.fileperms.search_and_change_file_attributes(fileName, requiredChanges, options))

        if linesLeft or linesMissing:
            changes[fileName]['content'] = '\n'.join(currentLines)

        if changes[fileName] == {}: 
            changes = {}    
        return changes, messages

    ##########################################################################
    def scan(self, optionDict=None):

        messages = []
        retval = True

        requiredChanges = {}

        # These are common to both files
        if optionDict['allowedUnames']:
            requiredChanges['owner'] = optionDict['allowedUnames']
        if optionDict['allowedGnames']:
            requiredChanges['group'] = optionDict['allowedGnames']
        if optionDict['dacs']:
            requiredChanges['dacs'] = optionDict['dacs']

        allChanges = {}
        allMessages = []
               
        # set content for allow file
        requiredChanges['content'] = optionDict['secureDevices']           
        changes, messages = self.checkSecuretty('scan', self.__target_file, requiredChanges)         
        allChanges.update(changes)
        allMessages.extend(messages)

                
        if allChanges:
            retval = False
            msg = "'%s' does not matched allowed secure device list" % self.__target_file
        else:
            msg = ""
        return retval, msg, {'messages':allMessages}


    ##########################################################################
    def apply(self, optionDict=None):
        """Enable root logins only from console."""
        messages = []
        retval = False

        requiredChanges = {}

        # These are common to both files
        if optionDict['allowedUnames']:
            requiredChanges['owner'] = optionDict['allowedUnames']
        if optionDict['allowedGnames']:
            requiredChanges['group'] = optionDict['allowedGnames']
        if optionDict['dacs']:
            requiredChanges['dacs'] = optionDict['dacs']

        allChanges = {}
        allMessages = []
               
        # set content for allow file
        requiredChanges['content'] = optionDict['secureDevices']           
        changes, messages = self.checkSecuretty('apply', self.__target_file, requiredChanges)         
        allChanges.update(changes)
        allMessages.extend(messages)

        if allChanges:
            retval = True

        return retval, str(allChanges), {'messages':allMessages}

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        retval = False
        allChanges = {}
        allMessages = []

        # oldstyle change record is a simple patchset, and we have no history on the original permissions, so
        # don't alter them, but we do need to revert the patch the oldway.  
        
        if not change_record.startswith('{'):
            msg = "Detected oldstyle change record" 
            self.logger.info(self.module_name, msg)
            
            try:
                tcs_utils.apply_patch(change_record)
                allChanges = "{}"
            except tcs_utils.ActionError, err:
                msg = "Unable to undo previous changes (%s)." % err 
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            change_record = tcs_utils.string_to_dictionary(change_record)
            for fileName, changesToUndo in change_record.items():
                changes, messages = self.checkSecuretty('undo', fileName, changesToUndo)         
                allChanges.update(changes)
                allMessages.extend(messages)

        if allChanges:
            msg = "Undo Performed"
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            retval = True
        else:
            msg = "No changes were reverted"
            self.logger.error(self.module_name, 'Undo Performed: ' + msg)
            retval = False
        
        return retval, msg, {'messages':allMessages}


