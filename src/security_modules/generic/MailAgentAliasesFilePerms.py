#!/usr/bin/env python
#
# Copyright (c) 2013 Forcepoint LLC.
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
import GenericPerms
import sb_utils.file.fileperms

class MailAgentAliasesFilePerms:

# This module has potentially has an override for a specific filename, so we need to iterate through them.
    ##########################################################################
    def __init__(self):
        self.module_name = "MailAgentAliasesFilePerms"
        
        self.logger = TCSLogger.TCSLogger.getInstance()

    def scanFiles(self, optionDict, action):
    
        changes = {}
        messages = []
        
        # We need to operate one file at a time here... so we'll rebuild our dictiony of stuff to do as we go...
        for fileName in sb_utils.file.fileperms.splitStringIntoFiles(optionDict['fileList']):
            options = {}
            thisOptDict = {'fileList':fileName}
            if optionDict['dacs']:
                thisOptDict['dacs'] = optionDict['dacs']
            
            if optionDict['allowedUnames']:
                thisOptDict['allowedUnames'] = optionDict['allowedUnames']
            
            if fileName.endswith('aliases.db'):
                if optionDict['allowedGnamesAliasesDB']:
                    thisOptDict['allowedGnames'] = optionDict['allowedGnamesAliasesDB']
            elif optionDict['allowedGnames']:
                thisOptDict['allowedGnames'] = optionDict['allowedGnames']
 
            if action == "scan":
                r1, r2 = GenericPerms.scan(optionDict=thisOptDict)
                if r2:
                    changes['changes'] = 'yes'
            else:
                r1, r2 = GenericPerms.apply(optionDict=thisOptDict)
                if r2 != '{}':
                    changes.update(tcs_utils.string_to_dictionary(r2))
             
            if changes:
                messages.append("%s has incorrect perms/ownership" % fileName)
        return changes, messages
            
    ##########################################################################
    def scan(self, optionDict={}):

        retval = True
        changes, messages = self.scanFiles(optionDict, 'scan')
        if changes:
            retval = False
        return retval, "", {'messages':messages}

    ##########################################################################
    def apply(self, optionDict={}):

        retval = False
        changes, messages = self.scanFiles(optionDict, 'apply')
        if changes:
            retval = True
        return retval, str(changes),{'messages':messages} 

    ##########################################################################
    def undo(self, change_record=None):

        # Even though we didn't call GenericPerms to *make* the changes, we can still pop the change record back through
        # that code...
        return GenericPerms.undo(change_record=change_record)
if __name__ == "__main__":
    test = MailAgentAliasesFilePerms()
    myLog = TCSLogger.TCSLogger.getInstance()
    myLog.force_log_level (7)
    myLog._fileobj = sys.stdout

    optionDict={}
    optionDict['fileList'] = "/etc/aliases /etc/aliases.db"
    optionDict['allowedUnames'] = 'root'
    optionDict['allowedGnames'] = 'root'
    optionDict['allowedGnamesAliasesDB'] = 'smmsp'
    optionDict['dacs'] = '644'
    print test.scan(optionDict)
