#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

"""
LimitAccessFromSu module provides the LimitAccessFromSu class which is
capable of handling the security guidelines regarding limiting access
to root account from su.

Requires to portions:
  if pam_wheel.so is not correctly in place then access is unrestricted
  we also have a fall back to check to see if there are users *other than root* 
  as members of the wheel group.  By default we will not enforce these changes
  unless there is someone other than root as a member.  This can be defeated by
  setting the option 'requireNonRootWheelMember' to 0.
"""

import sys
import os
import shutil
import grp

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class LimitAccessFromSu:

    def __init__(self):
        self.module_name = "LimitAccessFromSu"
        self.__target_file = '/etc/pam.d/su'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        messages = {'messages':[]}
        
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s file: %s" % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        found = False

        msg = "Checking %s for an 'auth required' entry for pam_wheel.so" % (self.__target_file)
        self.logger.info(self.module_name, msg)

        for line in in_obj:
            linelist = line.split()
            # ignore comments and other lines
            if len(linelist) < 4 or linelist[0].startswith('#'):
                continue
            if linelist[0] == 'auth' and linelist[1] == 'required' and \
               'pam_wheel.so' in linelist[2] and linelist[3] == 'use_uid':
                found = True

        in_obj.close()

        msg = ''
        if not found: 
            msg = "Access to root account from su is not restricted"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            retval = False
        else:
            retval = True
        
        return retval, msg, messages

    ##########################################################################
    def apply(self, optionDict=None):
        """Apply changes."""

        action_record = ''
        messages = {'messages' : [] }
        
        nonRootUserInWheelGroup = False
        result, reason, messages = self.scan()
        if result == True:
            return False, action_record, messages

        # check if any users (besides root) belong to the wheel group
        wheelusers = grp.getgrnam('wheel').gr_mem
        for user in wheelusers:
            if user != 'root':
                nonRootUserInWheelGroup = True
                break
        if optionDict['requireNonRootWheelMember'] == '1' and not nonRootUserInWheelGroup:
            msg = "You must have at least one user in the wheel group to "\
                  "apply this module. Applying this module without members in "\
                  "the wheel group can lock you out of the system."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
        elif not nonRootUserInWheelGroup:
                msg = "WARNING: Applying module despite no non-root users in the wheel group.  This can prevent any user from using the 'su' command."
                messages['messages'].append(msg)
                self.logger.warn(self.module_name, msg)
   
        try:
            linesIn = open(self.__target_file, 'r').readlines()
        except IOError, err:
            msg = "Unable to open %s file: %s" % (self.__target_file, str(err))
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
        except IOError, err:
            msg = "Unable to create temporary %s.new file" % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Ok, we didn't find it.  So start at the *end* and work backword for the first 'auth' line , and insert this immdiately before it
        inserted = False

        for ln in range(len(linesIn)-1,-1,-1):
            line = linesIn[ln]
            linelist = line.split()
            if len(linelist) >= 3 and linelist[0] == 'auth' :
                inserted = True
                msg = "Adding 'auth\trequired\tpam_wheel.so\tuse_uid' to %s" % self.__target_file
                self.logger.notice(self.module_name, msg)
                linesIn.insert(ln,"auth\trequired\tpam_wheel.so\tuse_uid\n")
                break

        if inserted == True:
        
            out_obj.writelines(linesIn)
            out_obj.close()

            action_record = tcs_utils.generate_diff_record(self.__target_file + '.new',
                                                 self.__target_file)

            try:
                shutil.copymode(self.__target_file, self.__target_file + '.new')
                shutil.copy2(self.__target_file + '.new', self.__target_file)
                sb_utils.SELinux.restoreSecurityContext(self.__target_file)
                os.unlink(self.__target_file + '.new')
            except OSError:
                msg = "Unable to replace %s with new version" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


            msg = 'Access to root account from su has been restricted.'
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        else:
            msg = 'Unable to add required lines to %s' % self.__target_file
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        return True, action_record, messages


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Restore file to what it was before the apply
        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'The su configuration has been restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {}

if __name__ == "__main__":
    test = LimitAccessFromSu()
    test.logger.forceToStdout()
    optionDict = { 'requireNonRootWheelMember':'0'}
    test.scan(optionDict)
