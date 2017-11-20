#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Look for files with the SELinux context of 'unlabeled_t' - if SELinux supported and not disabled
#

import sys
import os
import pwd
import grp

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import sb_utils.file.fileperms

class SELinuxFindUnlabeledFiles:

    def __init__(self):
        self.module_name = "SELinuxFindUnlabeledFiles"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__checkAllFiles = False

    ##########################################################################
    def validate_input(self, optionDict=None):

         if optionDict['checkWhichFiles'] == '1':
            self.__checkAllFiles=True

         if self.__checkAllFiles == True:
             msg = "Module will check *all* files."
         else:
             msg = "Module will check only files in the /dev filesystem."
         self.logger.notice(self.module_name,  msg)

    ##########################################################################
    def scan(self, optionDict=None):
        """
        Initiating File System Scan to find unowned files
        """

        self.validate_input(optionDict)
        messages = {}
        messages['messages'] = []

        all_files_labeled = True
        msg = ""
        retval = True
        
        # Only run FS scan if it hasn't been run this scan *AND* SELinux is enabled.  
        # 
        if not sb_utils.SELinux.isSELinuxSupportedOnBox() :
            msg = "SELinux is unsupported on this box - context checking not performed"
        elif not sb_utils.SELinux.isSELinuxEnabled():
            msg = "SELinux is disabled on this box - context checking not performed"
        else:    
            if tcs_utils.fs_scan_is_needed():
                sb_utils.filesystem.scan.perform()
                if not os.path.isfile(self.__target_file):
                    msg = "Unable to find %s" % self.__target_file
                    self.logger.error(self.module_name, 'Scan Error: ' + msg)
                    raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

                # let others know we ran the fs scanner
                tcs_utils.update_fs_scanid()

            try:
                in_obj = open(self.__target_file, 'r')
                lines = in_obj.readlines()
                for line in lines:
                    fields = line.rstrip('\n').split('|')

                    if len(fields) != 6:
                        continue

                    # Unless we're checking all files, restrict checks to those entries starting with '/dev/' 
                    if self.__checkAllFiles == False and not fields[-1].startswith('/dev/'):
                        continue
                    if fields[1][8] == 'X':
                        all_files_labeled = False
                        msg = "%s has the unlabeled_t SELinux context." % fields[-1]
                        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                        if len(messages['messages']) < 10:
                            messages['messages'].append("Fail: %s" % msg)
                        else:
                            if len(messages['messages']) > 10:
                               continue
                            messages['messages'].append("See log for full list of failures...")

                    del fields
                in_obj.close()

            except IOError, err:
                msg = "Unable to open file %s: %s" % (self.__target_file, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            if not all_files_labeled:
                msg = "One or more files have the unlabeled_t SELinux context."


        return all_files_labeled, msg, messages

    ##########################################################################
    def apply(self, optionDict=None):
        """Change user/group of unowned files to nobody"""

        reason = ""
        messages = {'messages':[]}

        result, reason, messages = self.scan(optionDict)
        if result == True:
            return False, '', messages
        reason = ""
        
        msg = "One or more files has the unlabeled_t SELinux security context.  The Administrator should investigate and fix as required."
        self.logger.warning(self.module_name, msg)
        messages['messages'].append('Warning:%s' % msg)
        raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        return False, reason, messages


    ##########################################################################

    def undo(self, change_record=None):
        return False, "Nothing to undo", {}

if __name__ == '__main__':
    optionsDict = {'checkAllFiles':'0'}
    TEST = SELinuxFindUnlabeledFiles()
    print TEST.scan(optionsDict)

