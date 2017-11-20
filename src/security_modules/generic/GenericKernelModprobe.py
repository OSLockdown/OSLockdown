#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
# Generic routines for disabling kernel modules via modprobe settings
#
#


import sys
import os
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class Found(Exception): pass

class GenericKernelModprobe:

    def __init__(self, realModuleName="GenericKernelModprobe"):
        self.module_name = realModuleName
        self.__sb_remediations = '/etc/modprobe.d/oslockdown_remediations.conf'       
        self.requiredLines = []
        
        # Our regex is basically a line that:
        #   starts with optional whitespace  (group 1)
        #   the word 'install' or 'alias'    (group 2)
        #   whitespace                       (group 3)
        #   nonwhitespace                    (group 4)
        #   whitespace                       (group 5)
        #   any/everything else              (group 6)
        
        self.regex = re.compile("^(\s*)(install|alias|options)(\s*)(\S*)(\s*)(.*)")

                    
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    def validate_options(self, optionDict):
        # parse our list to generate the 'lines_to_find'
        if not optionDict or not 'requiredLines' in optionDict:
           msg = "No options provided to look for"
           self.logger.warn(self.module_name, msg)
           raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        self.requiredLines = optionDict['requiredLines'].splitlines()
        
    ##########################################################################
    # Look through a specific file for a specific line that matches our first two parameters
    # if the arbitraryData paramter is different, replace it and generate a change record
    # Note that we need to distinguish between no changes required (correct line found) and
    # line not found, so say so
    # We will assume that a particular setting combo will only occur *ONCE* in a file
        
    def search_for_line_in_file(self, action, fileName, lineToFind):
        
        changes = []
        messages = []
        correctLineFound = False
        searchFields = self.regex.search(lineToFind)
        if not searchFields:
            msg = "'%s' does not appear to be a valid line to search for" % lineToFind
            self.logger.warn(self.module_name, msg)
            # returning True so we don't make *any* changes with this line
            return True, messages, changes
        field2 = searchFields.group(2)
        field4 = searchFields.group(4)
        arbitraryData = searchFields.group(6)
        try:
            lines = open(fileName).readlines()
            for ln in range(len(lines)):
                line = lines[ln]
                match = self.regex.search(line)
                if not match:
                    continue
                if match.group(2) != field2 or match.group(4) != field4:
                    continue
                # ok, found a match, does it have the *right* setting? 
                if match.group(6) == searchFields.group(6):
                    msg = "Found '%s' at line %d in %s" % (line.strip(), ln, fileName)
                    self.logger.info(self.module_name, msg)
                    correctLineFound = True
                    continue
                # incorrect setting - fix it
                msg = "Found '%s' at line %d in %s instead of '%s'" % (line.strip(), ln, fileName, lineToFind)
                messages.append(msg)
                self.logger.warning(self.module_name, msg)

                fields = list(match.groups())
                # remember group(0) = entire string, so decrement field by one for reassignment
                fields[5] = arbitraryData+'\n'
                
                newline = ''.join(fields)
                changes.append({'lookFor':newline,'replaceWith':line})
                lines[ln] = newline
                if action == 'apply':
                    msg = "Setting '%s' at line %d in %s" % (newline.strip(), ln, fileName)
                    self.logger.warning(self.module_name, msg)
                break
                
            if action == "apply" and changes:
                open(fileName,"w").writelines(lines)
        except Exception, err:
            msg = "Unable to process file %s: %s" % (fileName, str(err))
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
        return correctLineFound, messages, changes            

    ##########################################################################
    # Look through all of the files in /etc/modprobe.conf and /etc/modprobe.d/*
    # for *each* of the required lines.  If we don't find a match, then we need
    # to generate a list of lines to be added internally (file to be written at the end
    # If we find correct lines, then move on to the next file (to deal with cases where
    # a setting occurs (correctly or oncorrectly) in multiple files.
        
    def search_Files(self, action):
        filesToSearch = []
        linesToAdd = []
        if os.path.exists('/etc/modprobe.conf'): 
            filesToSearch.append('/etc/modprobe.conf')
        if os.path.isdir('/etc/modprobe.d'):
            filesToSearch.extend(['/etc/modprobe.d/%s'%entry for entry in os.listdir('/etc/modprobe.d')])
        # Yes, we're processing files multiple times.  The only other way to do this would be to read *all* the files 
        # into memory at once, iterate over all items/files, then write changed files out at the end.  Doable, yes.  but 
        # would take time to do *right* and well.  So we'll waste cycles doing each one multiple times potentially, keeping
        # track of the lines we change

        allChanges = {}
        allMessages = []
        for searchData in self.requiredLines:
            addLine = True
            for fileName in filesToSearch:
                foundCorrect, messages, changes = self.search_for_line_in_file(action, fileName, searchData)
                # if we found it correct *ONCE* or we corrected it *ONCE* we don't need to add it.
                if foundCorrect or changes:
                    addLine = False  
                allMessages.extend(messages)
                if changes:
                    if fileName not in allChanges:
                        allChanges[fileName] = []
                    allChanges[fileName].extend(changes)
            
            if addLine:
                msg = "Missing '%s' from modprobe files" % searchData
                self.logger.warning(self.module_name, msg)
                allMessages.append(msg)
                linesToAdd.append(searchData)

        if linesToAdd:
            if os.path.exists('/etc/modprobe.d'):
                targetFile = self.__sb_remediations
            else:
                targetFile = '/etc/modprobe.conf'
            if targetFile not in allChanges:
                allChanges[targetFile] = []
            for entry in linesToAdd:
                allChanges[targetFile].append({'lookFor':entry+"\n",'replaceWith':None})
            
            if action == "apply":
                try:
                    outputFile = open(targetFile,"a")
                    for entry in linesToAdd:
                        outputFile.write(entry+"\n")
                        msg = "Adding '%s' to %s" % (entry, targetFile)
                        self.logger.info(self.module_name, msg)
                    
                except Exception, err: 
                    msg = "Unable to update '%s' with changes : %s" % (targetFile, str(err))
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        return allMessages, allChanges

    def undoFile(self, fileName, changes):
        # remember that we need to iterate the changes in *reverse* order, and process the file backwards also
        madeChanges = False
        messages = []
        try:
            lines = open(fileName).readlines()
            for change in reversed(changes):
                lookFor = change['lookFor'].strip()
                replaceWith = change['replaceWith']
                try:
                    for ln in reversed(range(len(lines))):
                        line = lines[ln]
                        if line.strip() == lookFor:
                            if replaceWith:
                                lines[ln] = replaceWith
                                msg = "Restored line %d in %s to %s" % (ln, fileName, replaceWith.strip())
                            else:
                                msg = "Removed '%s' from %s" % (lines.pop(ln).strip(), fileName)
                            self.logger.info(self.module_name, msg)
                            madeChanges = True
                            # again, we're assuming each change done *once* per file
                            raise Found
                    msg = "Did not find line '%s' in '%s' to undo" % (lookFor.strip(), fileName)
                    messages.append(msg)
                    self.logger.warning(self.module_name, msg)
                except Found:
                    pass
                    
            if madeChanges:
                if lines:
                    msg = "Writing '%s' back to disk" % fileName
                    open(fileName, "w").writelines(lines) 
                else:
                    msg = "All lines removed from '%s' - unlinking file" % fileName 
                    os.unlink(fileName)  
                self.logger.info(self.module_name, msg)
                      
        except Exception, err:
            msg = "Unable to revert file %s: %s" % (fileName, str(err))
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        return messages
        
    ##########################################################################
    def scan(self, optionDict=None):


        retval = True
        self.validate_options(optionDict)
        messages, change_record = self.search_Files('scan')
        if change_record:
            retval = False
            
        return retval, '', {'messages':messages}
  
    ##########################################################################
    def apply(self, optionDict=None):

        retval = False
        self.validate_options(optionDict)
        messages, change_record = self.search_Files('apply')
        if change_record:
            retval = True
        return retval, str(change_record), {'messages':messages}
                                                            
            
    ##########################################################################
    def undo(self, change_record=None):


        messages = {}
        messages['messages'] = []

        change_record = tcs_utils.string_to_dictionary(change_record)
        
        # we're counting on the fact that each line to remove should appear once at most
        allMessages = []
        for fileName, changes in change_record.items():
            allMessages.extend(self.undoFile(fileName, changes))
            
        return True,'',{'messages':allMessages}

class foobar(GenericKernelModprobe):
    def __init__(self):
        GenericKernelModprobe.__init__(self,"foobar")        



if __name__ == '__main__':
    try:
        boo = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
        boo = TCSLogger.TCSLogger.getInstance() 
    TEST = foobar()
    boo.forceToStdout()
    lines = 'install frabatz /bin/true\nalias geblorpt kaplouaaie'
    optionDict={'requiredLines':lines}
    print TEST.scan(optionDict)
#    a,b,c = TEST.apply(optionDict)
#    if a:
#        TEST.undo(b)
