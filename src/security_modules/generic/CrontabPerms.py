#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import stat
import glob
import sys
import pwd
import grp
import shlex

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms
import sb_utils.file.exclusion
import sb_utils.acctmgt.users

global QUICK_SCAN
try:
    if QUICK_SCAN == False:
        pass    
except NameError:
    QUICK_SCAN = False


class CrontabPerms:
    """
    CrontabPerms Security Module handles the guideline for access permissions
    on crontab files.
    """
    ##########################################################################
    def __init__(self):

        self.module_name = "CrontabPerms"
        
        self._userCanOwn = True
        self._allowed_unames = ['root']
        self._allowed_gnames = ['root']  

        self.logger = TCSLogger.TCSLogger.getInstance()

                
                        
    def checkUnames(self, passedUnames):
        self._allowed_unames = []
        for uname in tcs_utils.splitNaturally(passedUnames):
            try:
                pwd.getpwnam(uname)
                self._allowed_unames.append(uname)
            except KeyError,e:
                msg = "User '%s' doesn't exist, not including on allowed list" % uname
        if not self._allowed_unames:
            msg = "No valid usernames found - file ownership check will be skipped"
            self.logger.warn(self.module_name, msg)

    def checkGnames(self,passedGnames):
        self._allowed_gnames = []
        for gname in tcs_utils.splitNaturally(passedGnames):
            try:
                grp.getgrnam(gname)
                self._allowed_gnames.append(gname)
            except KeyError,e:
                msg = "Group '%s' doesn't exist, not including on allowed list" % gname
        if not self._allowed_gnames:
            msg = "No valid groupnames found - file group ownership check will be skipped"
            self.logger.warn(self.module_name, msg)
               

    def checkItems(self, optionDict, action):

        # premptively generate exclusion list
        sb_utils.file.exclusion.exlist()

        # we need to pre-process the usernames since we *may* be prepending usernames to them
        
        self.checkUnames(optionDict['allowedUnames'])
        self.checkGnames(optionDict['allowedGnames'])
        
        
        # set flags for the permissions checks...
        changes = {}
        if action == "scan":
            options = {'checkOnly':True}
        elif action == "apply":
            options = {'checkOnly':False}
        elif action == "undo":
            options = {'checkOnly':False, 'exactDACs':True}

        # get the list of local users, so we know who *may*  have a crontab entry
        localUsers = sb_utils.acctmgt.users.local_AllUsers()
        
        # These entries may be files or directories.  So complain if they don't exist, look in them if they are directories, and append
        # them otherwise
        
        fileList = []
        for entry in sb_utils.file.fileperms.splitStringIntoFiles(optionDict['userSpoolDirs']):
            if not os.path.exists(entry):
                self.logger.info(self.module_name,"'%s' does not exist" % entry)
            if not os.path.isdir(entry):
                fileList.append(entry)
            else:   
                fileList.extend( [ "%s/%s" % (entry,fileEntry) for fileEntry in os.listdir(entry)])

        
        # Ok, now look at each file to craft our allowed setup
        for fileEntry in fileList:
            allowedUnames = self._allowed_unames
            allowedGnames = self._allowed_gnames
            # is this a 'user' file?
            if self._userCanOwn and os.path.basename(fileEntry) in localUsers:
                userName = os.path.basename(fileEntry)
                groupName = grp.getgrgid(pwd.getpwnam(userName).pw_gid).gr_name
                allowedUnames.insert(0,userName)
                allowedGnames.insert(0,groupName)

            requiredChanges = {}
            if optionDict['dacs']:
                requiredChanges['dacs'] = optionDict['dacs']
            if allowedUnames:
                requiredChanges['owner'] = ','.join(allowedUnames)
            if allowedGnames:
                requiredChanges['group'] = ','.join(allowedGnames)
                
            changes.update( sb_utils.file.fileperms.search_and_change_file_attributes(fileEntry, requiredChanges, options))

        return changes

    ##########################################################################
    def scan(self, optionDict=None):
        """
        Check the file permissions on the crontab files (and dirs)
        """
    
        messages = {'messages':[]}
        
        changes = self.checkItems(optionDict, 'scan')
        if changes == {}:
            return True, '', messages
        else:
            # generate a set of module messages with offending filenames.
            badFiles = changes.keys()
            msg = "WARN:The following files have incorrect ownership or permissions: %s" % ', '.join(badFiles)
            messages['messages'].append(msg)
            return False, 'Found %d crontab files with problems' % len(badFiles), messages


    ##########################################################################
    def apply(self, optionDict=None):
        """
        Modify the file permissions on the crontab files.
        """

        messages = {'messages':[]}
        
        changes = self.checkItems(optionDict, 'apply')
        if changes == {}:
            return False, '', messages
        else:
            # generate a set of module messages with offending filenames.
            badFiles = changes.keys()
            msg = "Fixed ownership/permissions on %d files" % len(badFiles)
            messages['messages'].append(msg)
            return True, str(changes), messages
        
            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the permissions/ownership on the crontab files.
        """

        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "uid gid mode name\n"
        # If so, convert that into the new dictionary style

        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split(' ')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[3]] = {'owner':fspecs[0],
                                      'group':fspecs[1],
                                      'dacs':int(fspecs[2],8)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        msg = 'Permissions and ownership of crontab files restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', ''

if __name__ == '__main__':
    ll = TCSLogger.TCSLogger.getInstance()
    ll.force_log_level(6)
    ll._fileobj = sys.stderr
    test = CrontabPerms()
    optDict = {'userSpoolDirs': '/var/spool/cron /etc/cron.d /etc/crontab',
               'allowedUnames': 'root',
               'allowedGnames': 'root cron',
               'userCanOwn'   : '1',
               'dacs'         : '600'}
               
    print test.scan(optDict)
