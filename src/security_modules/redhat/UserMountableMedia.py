#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import shutil
import re
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class UserMountableMedia:
    """
    UserMountableMedia Security Module removes the ability 
    of users to mount removable media
    """

    def __init__(self):
        self.module_name = "UserMountableMedia"
        self.__target_file = ''
        possible_targets = [ '/etc/security/console.perms.d/50-default.perms', '/etc/security/console.perms']
        
        for target in possible_targets:
            if os.path.isfile(target):
                self.__target_file = target
                break

        self.__tmp_file = '/tmp/.50-default.perms.tmp'
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.allowed_devs = [ 'sound', 'fb', 'kbd', 'joystick', 
                              'v4l',   'mainboard', 'gpm', 'scanner' ]

    ##########################################################################
    def validate_input(self, option):
        """
        Validates Input
        """
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        match_re = re.compile('^<console>\s')
        media_found = []
        if not os.path.isfile(self.__target_file):
            if self.__target_file != "" :
                msg = "% does not exist" % self.__target_file
                raise tcs_utils.ScanError('%s %s' % ( self.module_name, msg))
            else:
                msg = "No configuration found to scan."
                self.logger.notice(self.module_name, 'Scan Passed: ' + msg)
                return True, "", {'messages':[msg]}
        try:
            thefile = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Examining %s..." % (self.__target_file)
        self.logger.notice(self.module_name, msg)

        for line in thefile:
            if not match_re.search(line):
                continue

            # the following gets the third column and strips off the '<' and
            # '>' from the beginning and end of the device name
            try:
                dev = line.split()[2][1:-1]
            except IndexError:
                continue 

            if dev not in self.allowed_devs:
                media_found.append(dev)

        thefile.close()
        if media_found != [] :
            msg = "Found user-mountable media : %s" % ','.join(media_found)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, '', {'messages':msg}
        else:
            return True, '', {'messages':[]}

    ##########################################################################
    def apply(self, option=None):
        """
        Applies Changes
        """

        match_re = re.compile('^<console>\s')

        result, reason, messages = self.scan()
        if result == True:
            return False, '', {'messages':[]}

        if not os.path.isfile(self.__target_file):
            if self.__target_file != "" :
                msg = "% does not exist" % self.__target_file
                raise tcs_utils.ActionError('%s %s' % ( self.module_name, msg))
            else:
                msg = "No configuration found to edit, no action taken."
                return False, "", {'messages':[msg]}
                     
        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = "%s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        change_record = []

        for line in origfile:
            if not match_re.search(line):
                workfile.write(line)
                continue

            # the following gets the third column and strips off the '<' and
            # '>' from the beginning and end of the device name
            try:
                dev = line.split()[2][1:-1]
            except IndexError:
                continue

            if dev not in self.allowed_devs:
                change_record.append(dev)
                workfile.write('#%s' % line)
            else:
                workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except Exception, err:
            msg = "%s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
 

        msg = "Commented out user-mountable media : %s" % ','.join(change_record)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, ' '.join(change_record), {'messages':[msg]}


    ##########################################################################        
    def undo(self, action_record=None):
        """Undo previous change application."""


        match_re = re.compile('^#<console>\s')
        media_reverted = []
        result, reason, messages = self.scan()

        if result == False:
            return False, '', {'messages':[]}

        if not action_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {'messages':[]}

        changes = action_record.split()

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = "%s" % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line in origfile:
            if not match_re.search(line):
                workfile.write(line)
                continue

            # the following gets the third column and strips off the '<' and
            # '>' from the beginning and end of the device name
            try:
                dev = line.split()[2][1:-1]
            except (ValueError, IndexError):
                continue

            if dev in changes:
                workfile.write('%s' % line[1:])
                media_reverted.append(dev)
            else:
                workfile.write(line)

        origfile.close()
        workfile.close()

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except Exception, err:
            msg = "%s" % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            

        msg = "Re-enabled user-mountable media : %s" % ','.join(media_reverted)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {'messages':[msg]}
