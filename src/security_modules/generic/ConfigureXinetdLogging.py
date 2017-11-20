#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
# Modify the /etc/xinetd.conf and /etc/xinetd.d/* files to add
# the required lines.  Note that the /etc/xinetd.d/* files will
# automatically *start* with everything that is defined in /etc/xinetd.conf,
# and will override with their own settings.
# 
#

import sys
import os
import shutil

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.config
import sb_utils.SELinux

class ConfigureXinetdLogging:
    def __init__(self):
        self.module_name = 'ConfigureXinetdLogging'
        self.__mainFile = '/etc/xinetd.conf'
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.settings = {}
        self.addToSubFiles = False
        self.delim = "[+-]?="   # config files can have =, +=, or -= as settings
    
    def validate_options(self, optionsDict):
        # explicitly strip on name as it isn't a valid setting for the files
        for tag, value in optionsDict.iteritems():
            if tag == 'addToSubFilesIfMissing':
                if value == '1':
                    self.addToSubFiles = True
            else:
                self.settings[tag] = value

    def processThisFile(self, fileName, action):
        changes = {}
        messages = []
        if not os.path.exists(fileName):
            return changes, messages
        
        # Check to see if our required lines are present
        fileValues = sb_utils.os.config.get_list(configfile=fileName, delim=self.delim)
        for tag in self.settings.keys():
            problem = "none"
            try:
                if self.settings[tag] != fileValues[tag]:
                    problem = "differ"
            except KeyError:
                problem = "missing"
            
            if action == "scan":
                if problem == "differ":
                    msg = "Settings for '%s' differ in '%s'" % (tag, fileName)
                    messages.append(msg)
                    self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                    changes[tag] = fileValues[tag]
                elif problem == "missing":
                    if fileName != '/etc/xinetd.conf' and self.addToSubFiles == False:
                        msg = "Setting for '%s' is missing from '%s', but would be inherited from /etc/xinetd.conf" % (tag, fileName)
                        self.logger.debug(self.module_name, msg)
                    else:
                        msg = "Setting '%s' is missing from '%s" % (tag, fileName)
                        messages.append(msg)
                        self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                        changes[tag] = ""
                
            elif action == "apply":
                if problem == "differ":
                    origValue = sb_utils.os.config.setparam(configfile=fileName, delim=self.delim, param=tag, value=self.settings[tag])
                    changes[tag] = origValue
                elif problem == "missing" and (fileName == '/etc/xinetd.conf' or self.addToSubFiles == True):
                    # ok, we need to do this ourselves since the files use the '{}' characters as structural.  We know
                    # we need to add the missing lines, we'll rip through the file quickly to find the line with '}' and
                    # add the missing field before it.
                    lines = open(fileName).readlines()
                    newLine = "%s = %s\n" % (tag, self.settings[tag])
                    for lineNum in range(len(lines)):
                        if lines[lineNum].strip() == "}":
                            msg = "Adding setting for '%s' to '%s' at line %d" % (tag, fileName,lineNum)
                            self.logger.debug(self.module_name, msg)
                            lines.insert(lineNum, newLine)
                            break
                    open(fileName,'w').writelines(lines)
                    changes[tag] = ""
            
        return changes, messages

    def processFiles(self, action):
        
        allChanges = {}
        allMessages = {}
        
        try:
            fileList = ['/etc/xinetd.conf']
            fileList.extend([ '/etc/xinetd.d/'+fileName for fileName in os.listdir("/etc/xinetd.d")] )       
        except Exception, err:
            msg = "Unable to generate list of xinetd files to process : %s" % str(err)
            self.logger.error(self.module_name, "Scan Error: %s" % msg)
            raise tcs_utils.ActionError("%s %s" % (self.module_name, msg))

        for fileName in fileList:
            changes, messages = self.processThisFile(fileName, action)
            messages.extend(messages)
            if changes:
                allChanges[fileName] = changes
        
        return allChanges, allMessages
        
    def scan(self, optionsDict):
        self.validate_options(optionsDict)
        changes, messages = self.processFiles('scan')
        retval = True
        msg = ''
        if changes:
            msg = "One or more files are not correctly configured"
            retval = False
        return retval, msg, messages
        
        
    def apply(self, optionsDict):
        self.validate_options(optionsDict)
        changes, messages = self.processFiles('apply')
        retval = False
        msg = ''
        if changes:
            retval = True

        return retval, str(changes), messages
        
    ##########################################################################
    def undo(self, change_record=None):

        change_record = tcs_utils.string_to_dictionary(change_record)
         
        for fileName, changes in change_record.iteritems():
            for xparam, xvalue in changes.iteritems():
                if xvalue == '': 
                    results = sb_utils.os.config.unsetparam(configfile=fileName, param=xparam, delim=self.delim)
                else:
                    results = sb_utils.os.config.setparam(configfile=fileName, param=xparam, value=xvalue, delim=self.delim)

                if results == False:
                    msg = "Unable to set %s in %s" % (xparam, fileName)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        self.logger.notice(self.module_name, "Undo Performed")

        return True, '',  {}
        
    
