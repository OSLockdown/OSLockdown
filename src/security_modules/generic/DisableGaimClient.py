#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

"""
DisableGaimClient

 If gaim (or pidgin) rpm is installed, remove file permissions from it's
 executable.

 GAIM was renamed to pidgin
"""

import sys
import os
import stat

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info
import sb_utils.file.fileperms


class DisableGaimClient:

    def __init__(self):
        self.module_name = 'DisableGaimClient'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()
        if sb_utils.os.info.is_solaris() == True:
            self._gaim_path = '/usr/local/bin/gaim'
            self._pidgin_path = '/usr/local/bin/pidgin'
        else:
            self._gaim_path = '/usr/bin/gaim'
            self._pidgin_path = '/usr/bin/pidgin'
        
    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def _scan_for_file(self, filename):
        reason = ""
        if os.path.isfile(filename):
            msg = "Scan: Checking permissions/ownership of %s" % filename
            self.logger.info(self.module_name, msg)

            try:
                statinfo = os.stat(filename)
            except (OSError, IOError), err: 
                reason = "Unable to stat file %s: %s" % (filename, err)
                self.logger.error(self.module_name, 'Scan Error: ' + reason)
                raise tcs_utils.ScanError("%s %s" % (self.module_name, msg))
    
            # We want the permissions to 000 so it can not be executed or read
            if statinfo.st_mode & 0777 ^ 0000 != 0:
                reason = '%s has permissions of %o instead of 000' % \
                         (filename, stat.S_IMODE(statinfo.st_mode))
                self.logger.info(self.module_name, 'Scan Failed: ' + reason)

    
            elif statinfo.st_uid != 0:
                reason = '%s has owner %d instead of 0 (root)' % \
                        (filename, statinfo.st_uid)
                self.logger.info(self.module_name, 'Scan Failed: ' + reason)
        return reason
    

    ##########################################################################
    def scan(self, option=None):
        """Check for rpm and file permissions"""
        if option != None:
            option = None


        # For Linux look for the package name to see if it is installed
        if sb_utils.os.info.is_solaris() == False:
            results1 = sb_utils.os.software.is_installed(pkgname='gaim')
            results2 = sb_utils.os.software.is_installed(pkgname='pidgin')
            if results1 == False and results2 == False:
                msg = "Neither gaim or pidgin is installed on the system"
                self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
                raise tcs_utils.ScanNotApplicable('%s %s' % 
                                              (self.module_name, msg))

        # Check gaim
        gaim_reason = self._scan_for_file(self._gaim_path)
            
        # Now check pidgin
        pidgin_reason = self._scan_for_file(self._pidgin_path)

        if gaim_reason != "" or pidgin_reason != "":
            return 'Fail','Either gaim or pidgin is not owned by root, with perms 000'
        else:
            return 'Pass', ''



    ##########################################################################
    def apply(self, option=None):

        change_record = {}
        
        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        changes_to_make = {'newroot':'root',
                          'group':'root',
                          'dacs':0}
        
        change_record.update(sb_utils.file.fileperms.change_file_attributes(self._gaim_path, changes_to_make))
        change_record.update(sb_utils.file.fileperms.change_file_attributes(self._pidgin_path, changes_to_make))
                          
        
        if change_record == {} :
            return 0, ''
        else:
            return 1, str(change_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        if change_record == "" :    # got a pre 4.0.1 oldstyle change record , fill in with default restore values - should never get
            change_record = {}
            change_record['/usr/bin/gaim'] = {'owner':'root',
                                              'group':'root',
                                              'dacs':0755}
            change_record['/usr/bin/pidgin'] = {'owner':'root',
                                              'group':'root',
                                              'dacs':0755}
        else:
        # check to see if this might be an 4.0.1 or 4.0.2 style change record, which is a string of entries
        #   of "filename|mode|uid|gid\n"
        # If so, convert that into the new dictionary style
        
            if not change_record[0:200].strip().startswith('{') :
                new_rec = {}
                for line in change_record.split('\n'):
                    fspecs = line.split('|')
                    if len(fspecs) != 4:
                        continue
                    new_rec[fspecs[0]] = {'owner':fspecs[2],
                                          'group':fspecs[3],
                                          'dacs':int(fspecs[1],8)}
                change_record = new_rec

        
        
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

#if __name__ == '__main__':
#    test = DisableGaimClient()
#    print test.scan()
#    res,rec=test.apply()
#    print rec
#    os.system("ls -l /usr/bin/gaim /usr/bin/pidgin")
#    rec=""
#    print test.undo(rec)
#    os.system("ls -l /usr/bin/gaim /usr/bin/pidgin")
