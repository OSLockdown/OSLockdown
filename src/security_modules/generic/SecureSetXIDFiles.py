#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#
# This module finds unautorized SUID and SGID files
# and removes the respective SGID/SUID bits if necessary.
# It also finds any SUID/SGID files with group or world
# write and removes said write bit(s).
#
# Note: During the scanning phase, the module will report
# a failure and halt the scanning after the first problem
# it finds in order to help speed up scanning process.
#
# When executed in a global zone, it first generates a 
# list of zones. Then it gets the zonepath for each 
# non-global zones. When it builds a list of all SUID/SGID
# files, it ignores files which fall under the non-global
# zone paths.
#
# CCE 14340-4 SUID
# CCE 14970-8 SGID


import sys
import os
import stat
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.solaris
import sb_utils.os.info
import sb_utils.file.exclusion
import sb_utils.file.fileperms
import sb_utils.file.whitelists

global QUICK_SCAN
try:
    if QUICK_SCAN == False:
        pass    
except NameError:
    QUICK_SCAN = False


class SecureSetXIDFiles:
    """
    SecureSetXIDFiles Security Module finds and removes the 
    set-UID and set-GID bits from unauthorized files
    """

    def __init__(self):
        self.module_name = "SecureSetXIDFiles"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """
        Initiating File System Scan to find suid and sgid files
        """

        messages = {}
        messages['messages'] = []


        failure_flag = False
        for root, dirs, files in os.walk('/'):

            if os.path.islink(root) and os.path.isdir(root):
                msg = "%s is a link to another directory; skipping" % (root)
                self.logger.debug(self.module_name, msg)
                continue

            # Before stat'ing file, make sure its path isn't in the 
            # excluded path list
            is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(root)
            if is_excluded == True:
                dirs[:] = []
                files[:] = []
                msg = "Skipping %s and any children : %s" % (root, why_excluded)
                self.logger.notice(self.module_name, msg)
                continue

            for xfile in files:
                testfile = os.path.join(root, xfile)
                try:
                    statinfo = os.stat(testfile)
                except OSError, err:
                    if os.path.islink(testfile) == True:
                        msg = "%s is a broken link; you should fix this by removing "\
                          "it or restoring its target file."  % testfile
                        self.logger.warn(self.module_name, msg)
                    else:
                        msg = "Unable to stat file %s: %s" % (testfile, err)
                        self.logger.error(self.module_name, 'Scan Error: ' + msg)
                        #messages['messages'].append("Error: %s" % msg)
                    continue

                # Get DAC information
                setuid = statinfo.st_mode & stat.S_ISUID
                setgid = statinfo.st_mode & stat.S_ISGID 
                grpwrite = statinfo.st_mode & stat.S_IWGRP
                othwrite = statinfo.st_mode & stat.S_IWOTH

                if not setuid and not setgid:
                    continue

                if (grpwrite or othwrite) and (setuid or setgid):
                    msg = "%s is SUID/SGID but is writeable by group or world." % testfile
                    messages['messages'].append("Fail: %s" % msg)
                    self.logger.notice(self.module_name, "Scan Failed: " + msg)
                    failure_flag = True

                if os.path.islink(testfile):
                    continue

                if setuid :
                    whitelisted, why = sb_utils.file.whitelists.is_SUID_whitelisted(testfile)
                    if not whitelisted:
                        msg = "+++(CCE 14340-4) %s is an unauthorized SUID file." % testfile
                        self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                        messages['messages'].append("Fail: %s" % msg)
                        failure_flag = True
                    else:
                        msg = "(CCE 14340-4) %s is a whitelisted SUID file." % testfile
                        self.logger.info(self.module_name, "%s" % msg)
                    
                if setgid :
                    whitelisted, why =  sb_utils.file.whitelists.is_SGID_whitelisted(testfile)
                    if not whitelisted:
                        msg = "+++(CCE 14970-8) %s is an unauthorized SGID file."  % testfile
                        messages['messages'].append("Fail: %s" % msg)
                        self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                        failure_flag = True
                    else:
                        msg = "(CCE 14970-8) %s is a whitelisted SGID file." % testfile
                        self.logger.info(self.module_name, "%s" % msg)
                
                if QUICK_SCAN == True and failure_flag == True:
                    msg = "Quick Scan Enabled - Module finishes after first issue detected"
                    self.logger.info(self.module_name, msg)
                    return False, 'Found unauthorized or insecure SUID/SGID files', messages


        if failure_flag == True:
            msg = "Unauthorized or insecure SUID/SGID files were found"
            self.logger.notice(self.module_name, msg)
            return False, msg, messages
        else:
            return True, '', messages



    ##########################################################################
    def apply(self, option=None):
        """Remove setXID status from unauthorized files"""

        messages = {}
        messages['messages'] = []


        change_record = {}

        for root, dirs, files in os.walk('/'):

            # Before stat'ing file, make sure its path isn't in the 
            # excluded path list

            is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(root)
            if is_excluded == True:
                dirs[:] = []
                files[:] = []
                msg = "Skipping %s and any children : %s" % (root, why_excluded)
                self.logger.notice(self.module_name, msg)
                continue

            for xfile in files:
                failure_flag = False
                badwrite     = False
                badsuid      = False
                badsgid      = False

                testfile = os.path.join(root, xfile)
                try:
                    statinfo = os.stat(testfile)
                except OSError, err:
                    if os.path.islink(testfile) == True:
                        msg = "%s is a broken link; you should fix this by removing "\
                          "it or restoring its target file."  % testfile
                        self.logger.warn(self.module_name, msg)
                    else:
                        msg = "Unable to stat file %s: %s" % (testfile, err)
                        self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    continue

                # Get DAC information
                setuid = statinfo.st_mode & stat.S_ISUID
                setgid = statinfo.st_mode & stat.S_ISGID
                grpwrite = statinfo.st_mode & stat.S_IWGRP
                othwrite = statinfo.st_mode & stat.S_IWOTH
                testfile_mode = stat.S_IMODE(statinfo.st_mode)

                if not setuid and not setgid:
                    continue

                msg = "Checking permissions of %s..." % testfile
                self.logger.debug(self.module_name, msg)
 
                if (grpwrite or othwrite) and (setuid or setgid):
                    msg = "%s is SUID/SGID but is writeable "\
                          "by group or world." % testfile
                    self.logger.info(self.module_name, msg)
                    failure_flag = True
                    badwrite = True

                if os.path.islink(testfile):
                    continue

                if setuid :
                    whitelisted, why = sb_utils.file.whitelists.is_SUID_whitelisted(testfile)
                    if not whitelisted:
                        msg = "+++(CCE 14340-4) %s is an unauthorized SUID file." % testfile
                        self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                        messages['messages'].append("Fail: %s" % msg)
                        failure_flag = True
                        badsuid = True
                    else:
                        msg = "(CCE 14340-4) %s is a whitelisted SUID file." % testfile
                        self.logger.info(self.module_name, "%s" % msg)
                    
                if setgid :
                    whitelisted, why =  sb_utils.file.whitelists.is_SGID_whitelisted(testfile)
                    if not whitelisted:
                        msg = "+++(CCE 14970-8) %s is an unauthorized SGID file."  % testfile
                        messages['messages'].append("Fail: %s" % msg)
                        self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                        failure_flag = True
                        badsgid = True
                    else:
                        msg = "(CCE 14970-8) %s is a whitelisted SGID file." % testfile
                        self.logger.info(self.module_name, "%s" % msg)
  
                if failure_flag == False:
                    continue


                #----------------------------------------
                # Okay, this is where we fix any problems
                #----------------------------------------

                # we'll remove bits from testfile_mode as we go
#                print "%s -> %s (%s)   %s (%s)" % (testfile, setuid, badsuid, setgid, badsgid)
                # Remove SETGID
                if badsgid and setgid:              
                    testfile_mode &= ~stat.S_ISGID

                # Remove SETUID
                if badsuid and setuid :
                    testfile_mode &= ~stat.S_ISUID

                if badwrite:
                    # Remove Group Write
                    if grpwrite:
                        testfile_mode &= ~stat.S_IWGRP

                    # Remove World Write
                    if othwrite:
                        testfile_mode &= ~stat.S_IWOTH

                if testfile_mode != statinfo.st_mode :
                    changes_to_make = {'dacs': testfile_mode}
                    change_record.update(sb_utils.file.fileperms.change_file_attributes(testfile , changes_to_make))

        if change_record == {}:
            return False, 'none', messages
        else:
            return True, str(change_record), messages
 




    ##########################################################################
    def undo(self, change_record=None):
        """Restore setXID status to files"""

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return True

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|mode|uid|gid\n"  - mode should be interpreted as decimal
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

        return True


#if __name__ == '__main__':
    #TEST = SecureSetXIDFiles()
    #print TEST.scan()
