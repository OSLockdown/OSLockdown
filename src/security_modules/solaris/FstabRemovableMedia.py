#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

# This module makes sure that nosuid mount option is used on
# removable media. It checks both /etc/rmmount.conf and /etc/vfstab.
#
# /etc/rmmount.conf must have the following line: 
#          mount * hsfs udfs ufs -o nosuid
#
# If /etc/vfstab has an 'NFS' mounted filesystem, it must have
# the 'nosuid' option specified.
#
#
# $Id: FstabRemovableMedia.py 23917 2017-03-07 15:44:30Z rsanders $ 
#
#

import sys
import shutil
import os
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class FstabRemovableMedia:

    def __init__(self):
        self.module_name = "FstabRemovableMedia"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        # 
        # PART 1: Check /etc/rmmount.conf
        #
        #pattern = re.compile('^mount \* hsfs udfs ufs -o nosuid')
        pattern = re.compile('^mount\s*\*\s*hsfs\s*udfs\s*ufs\s*-o\s*nosuid')
        try:
            infile = open('/etc/rmmount.conf', 'r')
        except IOError, err:
            msg = 'Unable to read /etc/rmmount.conf: %s' % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        found_it = False
        for line in infile.readlines():
            if pattern.search(line.strip()):
                msg = "Found 'mount * hsfs udfs ufs -o nosuid' in "\
                      "/etc/rmmount.conf"
                self.logger.info(self.module_name, msg)
                found_it = True
                break

        infile.close()
        if found_it == False:
            msg = "Missing 'mount * hsfs udfs ufs -o nosuid' in " \
                  "/etc/rmmount.conf"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                
        # 
        # PART 2: Check /etc/vfstab
        #
        try:
            infile = open('/etc/vfstab', 'r')
        except IOError, err:
            msg = 'Unable to read /etc/vfstab: %s' % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        line_nr = 0
        for line in infile.readlines():
            line = line.strip()
            line_nr += 1
            if line.startswith('#'):
                continue
            fields = line.split()
            try:
                if fields[3] != 'nfs':
                    continue
                options = fields[6].split(',')
            except IndexError:
                continue

            if 'nosuid' not in options:
                msg = "Missing 'nosuid' for nfs mounted filesystem: " \
                      "/etc/vfstab, line %d" % line_nr
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

        if found_it == False:
            msg = "Missing 'mount * hsfs udfs ufs -o nosuid' in "\
                  "/etc/rmmount.conf"
            return 'Fail', msg
        else:
            return 'Pass', '/etc/rmmount.conf and /etc/vfstab entries are okay'




    ##########################################################################
    def apply(self, option=None):

        action_record = []

        # 
        # PART 1: Update /etc/rmmount.conf
        #
        #pattern = re.compile('^mount\s\*\shsfs\sudfs\sufs\s-o\snosuid')
        pattern = re.compile('^mount\s*\*\s*hsfs\s*udfs\s*ufs\s*-o\s*nosuid')
        tcs_utils.protect_file('/etc/rmmount.conf')
        try:
            infile  = open('/etc/rmmount.conf', 'r')
            outfile = open('/etc/rmmount.conf.new', 'w')
        except IOError, err:
            msg = str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        found_it = False
        made_changes = False
        for line in infile.readlines():
            if pattern.search(line.strip()):
                found_it = True
            outfile.write(line)
            

        if found_it == False:
            made_changes = True
            outfile.write('mount * hsfs udfs ufs -o nosuid\n')

        infile.close()
        outfile.close()

        if made_changes == True:
            action_record.append(tcs_utils.generate_diff_record(\
                              '/etc/rmmount.conf.new', '/etc/rmmount.conf'))
            action_record.append('\n')

            try:
                shutil.copy2('/etc/rmmount.conf.new', '/etc/rmmount.conf')
                os.unlink('/etc/rmmount.conf.new')
            except OSError, err:
                msg = 'Unable to update /etc/rmmount.conf: %s' % err
                self.logger.info(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
            msg = "Updated /etc/rmmount.conf"
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)
        else:
            try:
                os.unlink('/etc/rmmount.conf.new')
            except OSError, err:
                msg = 'Unable to remove temporary workfile /etc/rmmount.conf.new'
                self.logger.error(self.module_name, 'Apply Error: ' + msg)


        # 
        # PART 2: Check /etc/vfstab
        #
        tcs_utils.protect_file('/etc/vfstab')
        try:
            infile  = open('/etc/vfstab', 'r')
            outfile = open('/etc/vfstab.new', 'w')
        except IOError, err:
            msg = str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        line_nr = 0
        made_changes = False
        for line in infile.readlines():
            line_nr += 1
            line = line.strip()
            fields = line.split()
            try:
                if fields[3] != 'nfs':
                    outfile.write(line + '\n')
                    continue

                options = fields[6].split(',')

            except IndexError:
                outfile.write(line + '\n')
                continue

            if 'nosuid' not in options:
                line = line.rstrip('\n')
                made_changes = True
                if fields[6] == '-':
                    line = line.rstrip('-')
                    outfile.write(line + 'nosuid\n')
                    continue

                outfile.write(line + ',nosuid\n')
            else:
                outfile.write(line + '\n')

        infile.close()
        outfile.close()


        if made_changes == True:
            action_record.append(tcs_utils.generate_diff_record(\
                                        '/etc/vfstab.new', '/etc/vfstab'))
            action_record.append('\n')
            try:
                shutil.copy2('/etc/vfstab.new', '/etc/vfstab')
                os.unlink('/etc/vfstab.new')

            except OSError, err:
                msg = 'Unable to update /etc/vfstab: %s' % err
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = "Updated /etc/vfstab"
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)

        else:
            try:
                os.unlink('/etc/vfstab.new')
            except OSError, err:
                msg = 'Unable to remove temporary workfile /etc/vfstab.new'
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
        
        if action_record == [] :
            return 0, ''
        else:
            return 1, ''.join(action_record)

    ##########################################################################        
    def undo(self, action_record=None):
        """Undo previous change application."""

        if not action_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            tcs_utils.apply_patch(action_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = "/etc/rmmount.conf and /etc/vfstab restored."
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
