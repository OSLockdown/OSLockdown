#!/usr/bin/env python
# 
# Copyright (c) 2008-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import shutil
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.info
import sb_utils.SELinux

class NoEmptyPasswords:

    def __init__(self):
        self.module_name = "NoEmptyPasswords"
        self.__config_file = '/etc/pam.d/system-auth'

        self.logger = TCSLogger.TCSLogger.getInstance()

        self._pkgname = 'pam'

    ##########################################################################
    def scan(self, option=None):

        
        scan_fail = False

        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed on the system" % self._pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        msg = "Examining %s to see if the 'nullok' parameter is set for pam_unix.so and "\
              "pam_unix2.so"  % self.__config_file
        self.logger.info(self.module_name, msg)

        try:
            pam_file = open(self.__config_file, 'r')
        except (IOError, OSError), err:
            msg = "Unable to read %s: %s" % (self.__config_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
            
         
        for idx, line in enumerate(pam_file.readlines()):
            line = line.strip()
#            if not line.startswith('auth'):
#                continue
            if not line or line.startswith('#'):
                continue
                
            pam_fields = line.split()
            if pam_fields[2].split('/')[-1] in ['pam_unix2.so', 'pam_unix.so']:
                msg = "Found '%s' at line %d in %s" % (' '.join(pam_fields), 
                                                     idx+1, self.__config_file)
                self.logger.debug(self.module_name, msg)
                try:
                    if 'nullok' in pam_fields[3:]:
                        msg = "Line %d of %s includes the 'nullok' "\
                              "parameter" % (idx+1, self.__config_file)
                        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                        scan_fail = True
                        
                except IndexError:
                    continue
   
        pam_file.close()

        if scan_fail == True:       
            return 'Fail', "'nullok' parameter found in %s" % self.__config_file
        else:
            return 'Pass', "'nullok' parameter not found in %s" % self.__config_file

    ##########################################################################
    def apply(self, option=None):


        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed on the system" % self._pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        action_record = ''
        result, reason = self.scan() 
        if result == 'Pass':
            return 0, action_record

        msg = "Removing the 'nullok' parameter on pam_unix.so and "\
              "pam_unix2.so from %s"  % (self.__config_file)

        # Open original file for reading
        try:
            pam_file = open(self.__config_file, 'r')
        except (IOError, OSError), err:
            msg = "Unable to read %s: %s" % (self.__config_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Open new file for write
        newfile = "%s.new" % self.__config_file
        try:
            out_file = open(newfile, 'w')
        except (IOError, OSError), err:
            pam_file.close()
            msg = "Unable to create %s: %s" % (newfile, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Write each line from orginal file into new file minus the 'nullok'
        action_record = []
        for idx, line in enumerate(pam_file.readlines()):
            line = line.strip()

#            if not line.startswith('auth'):
#                out_file.write(line + '\n')
#                continue
            if not line or line.startswith('#'):
                out_file.write(line + '\n')
                continue

            pam_fields = line.split()
            newline = line
            if pam_fields[2].split('/')[-1] in ['pam_unix2.so', 'pam_unix.so']:
                try:
                    if 'nullok' in pam_fields[3:]:
                        action_record.append("%d|%s\n" % (idx, line))
                        ptr = pam_fields.index('nullok')
                        pam_fields[ptr] = ''
                        newline = "%s\t%s\t%s\t%s\t\t#Added by OS Lockdown" % (pam_fields[0], 
                             pam_fields[1], pam_fields[2], 
                                            ' '.join(pam_fields[3:]))
                except IndexError:
                    pass

            out_file.write(newline + '\n')
   

        pam_file.close()
        out_file.close()

        # Switch old file with new one while preserving permissions
        try:
            shutil.copymode(self.__config_file, newfile)
            shutil.copy2(newfile, self.__config_file)
            sb_utils.SELinux.restoreSecurityContext(self.__config_file)
            os.unlink(newfile)
        except (OSError, IOError), err:
            msg = "Unable to replace %s with new version: %s" % (self.__config_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        return 1, 'added '
        
    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record :
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        # silly case of no need to undo, already done (perhaps by hand?)
        result, reason = self.scan()
        if result == 'Fail':
            return 0
	    
        newfile = "%s.new" % self.__config_file

        try:
            origfile = open(self.__config_file, 'r')
            workfile = open(newfile, 'w')
        except IOError, err:
            msg = 'Undo Error: %s' % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
 

        for line in origfile:
            if not line.startswith('auth') and not line.endswith('#Added by OS Lockdown\n') :
                workfile.write(line)
                continue

            pam_fields = line.split()
            newline = line
            if pam_fields[2].split('/')[-1] in ['pam_unix2.so', 'pam_unix.so']:
                try:
                    ptr = pam_fields.index('#Added')
                    pam_fields = pam_fields[:ptr]
                    pam_fields.insert(3,'nullok')
                    newline = ' '.join(pam_fields)+'\n'
                except IndexError:
                    pass

            workfile.write(newline)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__config_file, newfile)
            shutil.copy2(newfile, self.__config_file)
            sb_utils.SELinux.restoreSecurityContext(self.__config_file)
            os.unlink(newfile)
        except Exception, err:
            msg = 'Undo Error: %s' % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        msg = "'nullok' directive restored to %s" % (self.__config_file)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

