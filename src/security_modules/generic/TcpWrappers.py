#!/usr/bin/env python
#
# Copyright (c) 2012-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import sha

import  xml.sax.saxutils

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.file.fileperms
import sb_utils.file.exclusion

class TcpWrappers:
    """
    Set the /etc/hosts.allow file contents
    While we hardcode the files, we're expecting the Profile to contain
    the acceptable UIDs/GIDs/DACs/ACLs, and required lines.  Note that we're
    *NOT* doing exactly content matching, but makeing sure that each of our
    required lines exist in the associated file.  If not, add them.  We are *not*
    removing lines during an apply(), but in the undo() we will remove lines added
    in the previous apply().
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "TcpWrappersAllow"
        self.__allow_file = '/etc/hosts.allow'
        self.__deny_file = '/etc/hosts.deny'
        
        self.logger = TCSLogger.TCSLogger.getInstance()

                 
    ##########################################################################
    def checkFile(self, action, fileName, requiredChanges):
        """
        Routine to do simple processing a file.
        - scan - verify file exists with required contents/permissions - complain if otherwise
        - apply - as scan, but add missing lines and set permissions as required, creating file if need be  - returns change set
        - undo - take change set from above and remove lines added, restoring permissions 
        """
        # generate exclusion list *early* to avoid cluttering log
        sb_utils.file.exclusion.exlist()

        messages = []
        contentChanges = []
        changes = {fileName:{}} 
        fileData = []
        noFile = False
        
        if not os.path.exists(fileName):
            if action == 'scan':
                msg = "'%s' does not exist" % fileName
                messages.append(msg)
                self.logger.warn(self.module_name, "Scan Error: "+ msg)
            noFile = True
        else:
            fileData = open(fileName).readlines()

        if action in ['scan', 'apply'] and ('content' not in requiredChanges or not requiredChanges['content']):
            msg = "No content for %s provided." % (fileName)
            self.logger.warn(self.module_name, msg)
            messages.append(msg)
        
        if 'content' in requiredChanges:
            for line in requiredChanges['content']:
    #            print "Looking for -> %s" % line
                continueNow = False
                for ln in range(len(fileData)):
    #                print "  Comparing against -> %s" % fileData[ln].strip()
                    if fileData[ln].strip() == line:
    #                    print " ->  Found"
                        if action != 'undo':
                            msg = "Found '%s' in '%s'" % ( line, fileName)
                            self.logger.info(self.module_name, msg)
                            continueNow = True
                        else:
                            contentChanges.append(fileData.pop(ln).strip())
                            msg = "Removed '%s' from '%s'" % (line, fileName)
                            self.logger.info(self.module_name, msg)
                            continueNow = True
                        break
                if continueNow:
                    continue
    #            print " ->    Not found"

                if action == "scan":
                    msg = "'%s' not found in '%s'" % (line, fileName)
                    self.logger.error(self.module_name, "Scan Error: "+ msg)
                    contentChanges.append(line)                
                if action == "apply":
                    msg = "Adding '%s' to '%s'" % (line, fileName)
                    self.logger.info(self.module_name, msg)
                    fileData.append(line+"\n")
                    contentChanges.append(line)
                if action == "undo":
                    msg = "Unable to find '%s' in '%s' for undo:" % (line, fileName)
                    self.logger.warn(self.module_name, "Undo Error: "+ msg)
        
        # done processing content        
        if action == "scan" and contentChanges:
            msg = "Fail: %s missing one or more required lines" % fileName
            messages.append(msg)
        
        if action in ['apply', 'undo'] and contentChanges:  
            if fileData:
                msg = "Writing revised contents to '%s'" % fileName
                self.logger.info(self.module_name, msg)
                open(fileName,"w").writelines(fileData)
                sb_utils.SELinux.restoreSecurityContext(fileName)
                if noFile:
                    changes[fileName]['created'] = True
            elif 'created' in requiredChanges:
                os.unlink(fileName)
                msg = "Removing '%s'" %( fileName)
                self.logger.info(self.module_name, msg)
           
        
        # prepare to process metadata (DACs/owner/ACLs)
        if action == "scan":
            options = {'checkOnly':True}
        elif action == "apply":
            options = {'checkOnly':False}
        elif action == "undo":
            options = {'checkOnly':False, 'exactDACs':True}
  
        if os.path.exists(fileName):
            changes.update( sb_utils.file.fileperms.search_and_change_file_attributes(fileName, requiredChanges, options))
            
        if contentChanges:
            changes[fileName]['content'] = contentChanges
        
        if changes[fileName] == {}: 
            changes = {}    

        return changes, messages             


    ##########################################################################
    def scan(self, optionDict={}):
        """Check to see if /etc/hosts.allow file is correct"""

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
        requiredChanges['content'] = optionDict['requiredLinesForAllow'].splitlines()           
        changes, messages = self.checkFile('scan', self.__allow_file, requiredChanges)         
        allChanges.update(changes)
        allMessages.extend(messages)

        # set content for deny file
        requiredChanges['content'] = optionDict['requiredLinesForDeny'].splitlines()           
        changes, messages = self.checkFile('scan', self.__deny_file, requiredChanges)         
        allChanges.update(changes)
        allMessages.extend(messages)
                
        if allChanges:
            retval = False
            msg = "Invalid content or permissions discovered"
        else:
            msg = ""
        return retval, msg, {'messages':allMessages}


    ##########################################################################
    def apply(self, optionDict={}):
        """Create and replace the /etc/hosts.allow configuration if it doesn't match."""

        retval = False
        requiredChanges = {}

        allChanges = {}
        allMessages = []

        # These are common to both files
        if optionDict['allowedUnames']:
            requiredChanges['owner'] = optionDict['allowedUnames']
        if optionDict['allowedGnames']:
            requiredChanges['group'] = optionDict['allowedGnames']
        if optionDict['dacs']:
            requiredChanges['dacs'] = optionDict['dacs']

        # set content for allow file
        requiredChanges['content'] = optionDict['requiredLinesForAllow'].splitlines()           
        changes, messages = self.checkFile('apply', self.__allow_file, requiredChanges)         
        allChanges.update(changes)
        allMessages.extend(messages)

        # set content for deny file
        requiredChanges['content'] = optionDict['requiredLinesForDeny'].splitlines()           
        changes, messages = self.checkFile('apply', self.__deny_file, requiredChanges)         
        allChanges.update(changes)
        allMessages.extend(messages)
        
        if allChanges:
            retval = True
        return retval, str(allChanges), {'messages':allMessages}


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        retval = False
        change_record = tcs_utils.string_to_dictionary(change_record)

        allChanges = {}
        allMessages = []
        for fileName, changesToUndo in change_record.items():
            changes, messages = self.checkFile('undo', fileName, changesToUndo)         
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

