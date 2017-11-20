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


class CrontabScriptPerms:
    """
    """
    ##########################################################################
    def __init__(self):

        self.module_name = "CrontabScriptPerms"
        
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

        # Explicitly assuming these entries are directories to look in, if not - complain
        
        fileList = []
        for dirEntry in sb_utils.file.fileperms.splitStringIntoFiles(optionDict['crontabScriptDirs']):
            if not os.path.isdir(dirEntry):
                self.logger.info(self.module_name,"Directory '%s' does not exist" % dirEntry)
                continue
            fileList.extend( [ "%s/%s" % (dirEntry,fileEntry) for fileEntry in os.listdir(dirEntry)])

        
        # Ok, now look at each file to craft our allowed setup
        for fileEntry in fileList:
            allowedUnames = self._allowed_unames
            allowedGnames = self._allowed_gnames

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
            return False, 'Found %d crontab script files with problems' % len(badFiles), messages


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

        msg = 'Permissions and ownership of crontab script files restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', ''

if __name__ == '__main__':
    ll = TCSLogger.TCSLogger.getInstance()
    ll.force_log_level(6)
    ll._fileobj = sys.stderr
    test = CrontabScriptPerms()
    optDict = {'crontabScriptDirs': '/etc/cron.daily /etc/cron.hourly /etc/cron.monthly /etc/cron.weekly',
               'allowedUnames': 'root',
               'allowedGnames': 'root cron',
               'dacs'         : '700'}
               
    print test.scan(optDict)
