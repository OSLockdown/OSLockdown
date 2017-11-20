##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Verify /etc/yum.conf and /etc/yum.repos.d/* are configured to have gpgcheck=1
#
# NOTE: None.
#
#
##############################################################################
import rpm
import sys
import pwd
import re
import os
import pwd
import grp

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import tcs_utils
import sb_utils.file.iniHandler


class EnsureYumReposUseGPGCheck:
 
    def __init__(self):
 
        self.module_name = self.__class__.__name__
        self.yumConfig = '/etc/yum.conf'
        self.yumrepodir = '/etc/yum.repos.d'
        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    def checkRepoFile(self, repoName, action, name, value, sectionName=None):
        iniFile = sb_utils.file.iniHandler.iniHandler()
        iniFile.read_file(repoName)
        
        messages = []
        changes = []
        for section in iniFile.get_section_names():
            if not sectionName or section == sectionName:
                # just set the value, and then check what the returned *old* values was for logging
                oldValue = iniFile.set_section_value((section, name, value))
                if oldValue[2]==value and action == 'scan':
                    msg = "Section '%s' of '%s' has a '%s' setting of '%s'" % (section, repoName, name, oldValue[2])  
                    self.logger.info(self.module_name, msg)
                    
                if oldValue[2]!=value:    
                    changes.append(oldValue)
                    if value == None:
                        msg = "Removing '%s' from section '%s' of '%s'" % (name, section, repoName) 
                    elif oldValue[2] != None:
                        msg = "Section '%s' of '%s' has a '%s' setting of '%s'" % (section, repoName, name, oldValue[2])  
                    else :
                        msg = "Section '%s' of '%s' missing '%s=%s'" % (section, repoName,name, value)
                    self.logger.notice(self.module_name, msg)

        if changes and action in ["apply", "undo"]:
            for change in changes:
                if change[2]:
                    msg = "Setting '%s' to '%s' in section '%s' in '%s'" % (change[1], value, change[0], repoName)
                else:
                    msg = "Removing '%s' from section '%s' in '%s'" % (change[1], change[0], repoName)
                self.logger.notice(self.module_name, msg)
            iniFile.write_file(repoName)
        
        if changes:
            changes = {repoName:changes}
        else:
            changes = {}
        
        return messages, changes
        
    def scan(self, optionDict=None):
        results = False
        reason = ""
        allMessages = []
        allChanges = {}
        
        if os.path.exists(self.yumConfig):
            allMessages, allChanges = self.checkRepoFile(self.yumConfig, 'scan', 'gpgcheck', '1', 'main')
        for entry in os.listdir(self.yumrepodir):
            if entry.endswith('.repo'):
                messages, changes = self.checkRepoFile('%s/%s' % (self.yumrepodir,entry), 'scan', 'gpgcheck', '1')
                allMessages.extend(messages)
                allChanges.update(changes)  
        
        if allChanges:
            results = False
            reason = "One or more yum repository configuration files missing gpgcheck=1"
        else:
            results = True
                
        return results, reason, {'messages':messages} 
 
    def apply(self, optionDict=None):
        results = False
        reason = ""
        messages = []
        allChanges = {}
        
        if os.path.exists(self.yumConfig):
            allMessages, allChanges = self.checkRepoFile(self.yumConfig, 'apply', 'gpgcheck', '1', 'main')
        for entry in os.listdir(self.yumrepodir):
            if entry.endswith('.repo'):
                messages, changes = self.checkRepoFile('%s/%s' % (self.yumrepodir,entry), 'apply', 'gpgcheck', '1')
                allMessages.extend(messages)
                allChanges.update(changes)  
        
        if allChanges:
            results = True
        else:
            results = False
                
                
        return results, str(allChanges), {'messages':messages} 
 
    def undo(self, change_record=None):
        results = False
        reason = ""
        messages = []
        
        change_record = tcs_utils.string_to_dictionary(change_record)
        # Ugly, but iterate over *each* change so we could read/write each repo multiple times potentially
        for repoName, fileChanges in change_record.items():
            for change in fileChanges:
                messages, undoChanges = self.checkRepoFile(repoName, 'undo', change[1], change[2], change[0])
                if undoChanges:
                    results = True 
        return results, reason, {'messages':messages} 

        
if __name__ == '__main__':
    test = EnsureYumReposUseGPGCheck()
    test.logger.forceToStdout()
    test.yumConfig = '/tmp/testing/yum.conf'
    test.yumrepodir = '/tmp/testing/yum.repos.d'
    
    a,b,c = test.apply()
    print
    print
    print b
    if a:
        test.undo(b)
    
