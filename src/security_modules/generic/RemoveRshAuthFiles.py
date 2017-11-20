#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
#  Remove the Rsh auth files (/etc/hosts.equiv, ${HOME}/.rhosts) files
#

import sys
import os
import pwd
import grp

try:
    foobar = set([])
except NameError:
    from sets import Set as set

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info 
import sb_utils.SELinux
import sb_utils.file.fileperms
import sb_utils.acctmgt.users

class RemoveRshAuthFiles:

    def __init__(self):
        self.module_name = "RemoveRshAuthFiles"
        self.__target_file = '/etc/pam.d/'
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.hostsequiv = '/etc/hosts.equiv'
        
    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        messages = []
        retval = True
         
        # check /etc/hosts.equiv
        filesToLookFor = set()
        
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            entry = pwd.getpwnam(userName)
            candidate = "%s/.rhosts" % (entry[5])
            filesToLookFor.add (candidate)
        filesToLookFor = [self.hostsequiv] + list(filesToLookFor)
        
        for entry in filesToLookFor:
            msg = "Checking for %s..." % entry
            self.logger.debug(self.module_name, msg)
            if not os.path.exists(entry):
                continue
            msg = "Found %s" % entry
            messages.append(msg)
            self.logger.warning(self.module_name, 'Scan Failed: %s' % msg)
            retval = False
        
        if retval == True:
            msg = "Did not rsh authorization files found"
        else:
            msg = "One or more rsh authorization files found"

        return retval, msg, {'messages': messages}
        
    ##########################################################################
    def apply(self, option=None):
        messages = []
        change_rec = {}
        retval = False
        filesToLookFor = set()
        
        # check /etc/hosts.equiv
        
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            entry = pwd.getpwnam(userName)
            candidate = "%s/.rhosts" % (entry[5])
            filesToLookFor.add (candidate)
        filesToLookFor = [self.hostsequiv] + list(filesToLookFor)
        
        for entry in filesToLookFor:
            msg = "Checking for %s..." % entry
            messages.append(msg)
            self.logger.debug(self.module_name, msg)
            if not os.path.exists(entry):
                continue
                
            msg = "Found %s" % entry
            self.logger.debug(self.module_name, 'Apply -> found  %s' % msg)
            fileData = {}
            # Get current owner/group/perms/data
            statinfo = os.stat(entry)
            fileData['metadata'] = {}
            fileData['metadata']['dacs'] = statinfo.st_mode & 07777
            fileData['metadata']['owner'] = pwd.getpwuid(statinfo.st_uid)[0]
            fileData['metadata']['group'] = grp.getgrgid(statinfo.st_gid)[0]
            fileData['contents'] = open(entry).read()
            change_rec[entry] = fileData
            os.unlink(entry)
            msg = "Deleting '%s'..." % entry
            self.logger.notice(self.module_name, msg)
            retval = True
        
        return retval, str(change_rec), {'messages': messages}
        

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""
        
        filesList = tcs_utils.string_to_dictionary(change_record)
        dacsToRestore = {}
        options = {'exactDACs':True, 'checkOnly':False}
        for fileName in filesList.keys():
            fileInfo = filesList[fileName]
            fileMetaData = fileInfo['metadata']
            fileData = fileInfo['contents']
            
            try:
                # Verify user/group still exists!
                try:
                    pwd.getpwnam(fileMetaData['owner'])
                    grp.getgrnam(fileMetaData['group'])
                except KeyError:
                    msg = "Unable to find username or groupname infomation for %s:%s" % (fileMetaData['owner'], fileMetaData['group'])
                except:
                    raise
                    
                open(fileName,"w").write(fileData)
                sb_utils.SELinux.restoreSecurityContext(fileName)
                dacsToRestore[fileName] = fileMetaData
                sb_utils.file.fileperms.change_file_attributes(fileName, changes = fileMetaData, options = options)
            except:
                msg = "Unable to restore '%s'"% fileName
                self.logger.warning(self.module_name, msg)
        return 1
        
