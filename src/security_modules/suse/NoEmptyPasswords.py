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

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.info


class NoEmptyPasswords:

    def __init__(self):
        self.module_name = "NoEmptyPasswords"
        self.__config_file = '/etc/pam.d/common-auth'

        self.logger = TCSLogger.TCSLogger.getInstance()

        self._pkgname = 'pam'

    ##########################################################################
    def scan(self, option=None):
        
        scan_fail = False

        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' package is not installed" % self._pkgname
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
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
            if not line.startswith('auth'):
                continue
            pam_fields = line.split()
            if pam_fields[2] in ['pam_unix2.so', 'pam_unix.so']:
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
            msg = "'%s' package is not installed" % self._pkgname
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

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

            if not line.startswith('auth'):
                out_file.write(line + '\n')
                continue

            pam_fields = line.split()
            newline = line
            if pam_fields[2] in ['pam_unix2.so', 'pam_unix.so']:
                try:
                    if 'nullok' in pam_fields[3:]:
                        action_record.append("%d|%s\n" % (idx, line))
                        ptr = pam_fields.index('nullok')
                        pam_fields[ptr] = ''
                        newline = "%s\t%s\t%s\t%s" % (pam_fields[0], 
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
            os.unlink(newfile)
        except (OSError, IOError), err:
            msg = "Unable to replace %s with new version: %s" % (self.__config_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if action_record == []:
            return 0, ''
        else:
            return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        # Build a dictionary of old line numbers and the line itself from
        # change record

        # Change records will be in the form of:
        # <linenumber>|<oldline>
        line_map = {}
        for line in change_record.split('\n'):
            fields = line.split('|')
            if len(fields) != 2:
                continue
            line_map[fields[0]] = fields[1]


        # Open original file for reading
        try:
            pam_file = open(self.__config_file, 'r')
        except (IOError, OSError), err:
            msg = "Unable to read %s: %s" % (self.__config_file, err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Open new file for write
        newfile = "%s.new" % self.__config_file
        try:
            out_file = open(newfile, 'w')
        except (IOError, OSError), err:
            pam_file.close()
            msg = "Unable to create %s: %s" % (newfile, err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for idx, line in enumerate(pam_file.readlines()):
            line = line.strip()
            pam_fields = line.split()
            newline = line

            if line_map.has_key(str(idx)):
                restore_fields = line_map[str(idx)].split()
                if pam_fields[0] == restore_fields[0] and \
                   pam_fields[1] == restore_fields[1] and \
                   pam_fields[2] == restore_fields[2]:
#                    print "Current Line: ", pam_fields
#                    print "Restore Line: ", restore_fields
                    newline = line_map[str(idx)]
                    msg = "Restoring line %d with '%s'" % (idx+1, newline.strip())
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

                else:
                    msg = "Unable to restore line %d because the first "\
                       "three fields '%s' do not match what it was prior "\
                       "to OS Lockdown applying a change: (%s)" % (idx+1,
                        (' '.join(pam_fields[0:3])).lstrip(), 
                        (' '.join(restore_fields[0:3]).lstrip()) )
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)

            out_file.write(newline + '\n') 

        out_file.close()
        pam_file.close()

        # Switch old file with new one while preserving permissions
        try:
            shutil.copymode(self.__config_file, newfile)
            shutil.copy2(newfile, self.__config_file)
            os.unlink(newfile)
        except (OSError, IOError), err:
            msg = "Unable to replace %s with new version: %s" % (self.__config_file, err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1
