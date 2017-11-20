#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.file.fileperms
import sb_utils.file.exclusion

class DisableSendmail:
    """
    Disable Sendmail Service and update /etc/sysconfig/sendmail
    """

    def __init__(self):

        self.module_name = 'DisableSendmail'
        self.__target_file = '/etc/sysconfig/sendmail'
        self.logger = TCSLogger.TCSLogger.getInstance()

        self._pkgname = "sendmail"
        self._svcname = "sendmail"
        self._svcdesc = "sendmail"


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    def processSingleConfigFile(self, action, fileName, requiredChanges):
        """
        requiredChanges is a dictionary.  The 'content' values are modified directly here, and the dictionary is passed in directly to 
        search_and_change_file_attributes to changes any DAC values (owner,group,dacs,ACLs, etc).
        The content field should be a list of two-tuples (key,value).  Searching will be done on the key, with value being the *desired*  value.
        A value of None indicates the key should be removed if found.  Any mismatch on value will result in a replacement being done
        """
        
        content = []
        messages = []
        changes = {fileName:{}} 
        fileData = []
        noFile = False
        if not os.path.exists(fileName):
            if action in ['scan', 'apply']:
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
            for thisChange in requiredChanges['content']:
                # break into our key/value tuple to process
                key, value = thisChange.split('=',1)
                breakNow = False
                found_it = False
                for ln in range(len(fileData)):
                    fileLine = fileData[ln].strip()
                    if not fileLine or fileLine.startswith('#'):
                        continue
                    # now break the line in to key/value tuple
                    lineKey, lineValue = fileLine.split('=',1)
                    
                    # found the indicated key
                    if key == lineKey:
                        # if the values don't match then we need to make a change -   
#                        print "Key=%s    val=<%s>   lineVal=<%s>" % (key, value, lineValue)
                        found_it = True
                        if value != lineValue:
                            # save what was there
                            content.append(fileLine)
                            # and make a change if 'value' is not empty
                            if value:
                                # ok, find the '=' sign and replace the trailing
                                equalSign = fileData[ln].find('=')
                                fileData[ln] = fileData[ln][0:equalSign+1]+value+"\n"
                            else:
                                fileData.pop(ln)
                            if action == 'scan':
                                msg = "Scan failed: Found '%s' instead of '%s' in '%s'" % (fileLine, thisChange, fileName)
                            elif action == 'apply':
                                msg = "Replacing '%s' with  '%s' in '%s'" % (fileLine, thisChange, fileName)
                            elif action == 'undo':
                                if not value :
                                    msg = "Removing '%s' from '%s'" % (fileLine, fileName)
                                else:
                                    msg = "Replacing '%s' with  '%s' in '%s'" % (fileLine, thisChange, fileName)
                            self.logger.info(self.module_name, msg)
                            break
                        elif action != 'undo':
                            msg = "Found '%s' in '%s'" % (fileLine, fileName)
                            self.logger.info(self.module_name, msg)
                if found_it :
                    continue
                if action == 'scan':
                    msg = "Scan failed: Did not find '%s' in '%s'" % (thisChange, fileName)
                    content.append(thisChange)
                elif action == 'apply':
                    msg = "Adding '%s' to '%s'" % (thisChange, fileName)
                    content.append("%s=" % key)
                    fileData.append(thisChange+"\n")
                elif action == 'undo':
                    msg = "Did not find '%s' to revert in '%s'" %(thisChange, fileName)
                self.logger.info(self.module_name, msg)
        if action in ['apply', 'undo'] and content:
            if fileData:
                open(fileName,"w").writelines(fileData)
                sb_utils.SELinux.restoreSecurityContext(fileName)
                if noFile:
                    changes[fileName]['created'] = True
            elif 'created' in requiredChanges:
                os.unlink(fileName)
                msg = "Removing '%s'" %( fileName)
                self.logger.info(self.module_name, msg)
                
        if action == "scan":
            options = {'checkOnly':True}
        elif action == "apply":
            options = {'checkOnly':False}
        elif action == "undo":
            options = {'checkOnly':False, 'exactDACs':True}
          
        if content:
             changes[fileName]['content'] = content
             
        if changes == {fileName:{}}:
            changes = {}
        return changes, messages
                   
    def processState(self, action, requiredChanges):
        allMessages = []
        allChanges = {}
        
        # generate exclusion list *early* to avoid cluttering log
        sb_utils.file.exclusion.exlist()

        if 'state' in requiredChanges:
            results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
            if results != True:
                msg = "'%s' package is not installed on the system" % self._pkgname
                self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
                raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

            results = sb_utils.os.service.is_enabled(svcname=self._svcname)
            if results == None:
                msg = "Unable to determine status of the '%s' service" % self._svcname
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            elif results == True:
                results = 'on'
            else:
                results = 'off'
                
            if requiredChanges['state'] == results:
                msg = "'%s' already in desired state(%s)" % (self._svcname, requiredChanges['state'])
                self.logger.notice(self.module_name,msg)
            elif action == 'scan':
                msg = '%s service is on' % self._svcdesc
                allChanges['state'] = 'on'
                allMessages.append(msg)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            else:
                if requiredChanges['state'] == 'on':
                    stateChange = 'enable'
                    oldState = 'off'
                    results = sb_utils.os.service.enable(svcname = self._svcname)
                else:
                    stateChange = 'disable'
                    oldState = 'on'
                    results = sb_utils.os.service.disable(svcname = self._svcname)
                
                if results != True:
                    msg = 'Unable to %s service: %s' % (self._svcname, stateChange)
                    self.logger.notice(self.module_name, ' Failed: ' + msg)
                    allMessages.append(msg)
                else:
                    allChanges['state'] = oldState   
        return allChanges, allMessages        

    def processAllConfigFiles(self, action, requiredChanges):
        allMessages = []
        allChanges = {}
        if 'files' in requiredChanges:
            allChanges['files'] = {}
            for fileName, fileChanges in requiredChanges['files'].items():
                changes, messages = self.processSingleConfigFile(action, fileName, fileChanges)
                allChanges['files'].update(changes)
                allMessages.extend(messages)
            if allChanges['files'] == {}:
                allChanges = {}
        return allChanges, allMessages
                               
    def processDesiredChanges(self, action, requiredChanges):

        allMessages = []
        allChanges = {}
        
        # generate exclusion list *early* to avoid cluttering log
        sb_utils.file.exclusion.exlist()

        changes, messages = self.processState(action, requiredChanges)
        if changes:
            allChanges.update(changes)
        allMessages.extend(messages)
        
        changes, messages = self.processAllConfigFiles(action, requiredChanges)
        if changes:
            allChanges.update(changes)
        allMessages.extend(messages)
                
        return allChanges, allMessages
        
    ##########################################################################
    def scan(self, optionDict=None):
        """
        Check to see if sendmail rpm is intalled, service is enabled, 
        and DAEMON=no in /etc/sysconfig/sendmail
        """

        messages = []
        retval = True
        requiredChanges = {}
        fileChanges = {}

        if optionDict['requiredLines']:
            fileChanges['content'] = optionDict['requiredLines'].splitlines()           

        requiredChanges['state'] = 'off'
        allChanges = {}
        allMessages = []
        
        requiredChanges['files'] = {self.__target_file: fileChanges}
        changes, messages = self.processDesiredChanges('scan', requiredChanges)

        allChanges.update(changes)
        allMessages.extend(messages)
                
        if allChanges:
            retval = False
            msg = "Service enabled or config file not correct"
        else:
            msg = ""
        return retval, msg, {'messages':allMessages}
    


    ##########################################################################
    def apply(self, optionDict=None):


        messages = []
        retval = True

        requiredChanges = {}
        fileChanges = {}

        if optionDict['requiredLines']:
            fileChanges['content'] = optionDict['requiredLines'].splitlines()           

        requiredChanges['state'] = 'off'
        requiredChanges['files'] = {self.__target_file: fileChanges}
        allChanges = {}
        allMessages = []
        
        changes, messages = self.processDesiredChanges('apply', requiredChanges)

        allChanges.update(changes)
        allMessages.extend(messages)
                
        if allChanges:
            retval = True
        else:
            retval = False
        return retval, str(allChanges), {'messages':messages}
        

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        allChanges = {}
        allMessages = []
        retval = False
        # and oldstyle change record is only going to say 'on' or 'off'
        if change_record in ['off', 'on']:
            requiredChanges = {'state':change_record }
            if os.path.isfile(self.__target_file):
                requiredChanges.update({'content':['DAEMON=yes','QUEUE=1h']})
                allChanges = { self.__target_file:requiredChanges}
        else:
            allChanges = tcs_utils.string_to_dictionary(change_record)
             
        changes = {}
        messages = []
        changes, messages = self.processDesiredChanges('undo', allChanges)

        allChanges.update(changes)
        allMessages.extend(messages)
                
        if allChanges:
            retval = True
        else:
            retval = False

        return retval, '', {'messages':messages}
        

