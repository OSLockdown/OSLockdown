#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
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
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.SELinux

class RemoveSMBguest:

    def __init__(self):
        self.module_name = self.__class__.__name__

        if sb_utils.os.info.is_solaris() == True:
            self.__conf_file = '/etc/sfw/smb.conf'
            self.__pkgname = 'SUNWsmbar'
        else:
            self.__conf_file = '/etc/samba/smb.conf'
            if sb_utils.os.info.is_LikeSUSE() == True:
                self.__pkgname = 'samba'
            else:
                self.__pkgname = 'samba-common'

        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        messages = {'messages': [] }
        results = sb_utils.os.software.is_installed(pkgname = self.__pkgname)
        if results == None:
            msg = "Unable to determine if %s installed." % self.__pkgname
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if results == False:
            msg = "Samba (%s) is not installed on the system" % self.__pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "Samba (%s) package is installed" % self.__pkgname
            messages['messages'].append(msg)

        found = False

        if not os.path.isfile(self.__conf_file):
            msg = "%s does not exist" % self.__conf_file
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "Checking %s for 'smb guest' parameter" % self.__conf_file
            messages['messages'].append(msg)

        try:
            in_obj = open(self.__conf_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s " % (self.__conf_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        for line_number, line in enumerate(in_obj.readlines()):
            line = line.strip()
            if not line.startswith('guest ok'):
                continue
            guest_value = line.split('=')[-1].strip()
            if guest_value.lower() == 'yes':
                msg = "Found 'guest ok = yes' at line %d in %s" % (line_number+1, self.__conf_file)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append("Fail: %s " % msg)
                found = True

        in_obj.close()


        if found: 
            msg = "guest access is allowed"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, messages
        else:
            return True, '', messages

    ##########################################################################
    def make_change(self, option=None):

        action_record = ""
        messages = {'messages': []}

        try:
            in_obj = open(self.__conf_file, 'r')
        except IOError, err:
            msg = "Unable to open %s file: %s" % (self.__conf_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        temp_file = "%s.new" % self.__conf_file
        try:
            out_obj = open(temp_file, 'w')
        except (OSError, IOError), err:
            msg = "Unable to write to %s" % temp_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        made_change = False
        for line_number, line in enumerate(lines):
            if not line.strip().startswith('guest ok'):
                out_obj.write(line)
                continue

            guest_value = line.split('=')[-1].strip()
            key_value = line.split('=')[0]
            if guest_value.lower() == option:
                out_obj.write(line)
            else:
                action_record = guest_value.lower()
                out_obj.write("%s= %s\n" % (key_value, option))  # Note split above would keep trailing white space, so don't add any more
                msg = "Set 'guest ok = %s' at line %d in %s" % (option, line_number+1, self.__conf_file)
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                messages['messages'].append(msg)
                made_change = True

        out_obj.close()
        if made_change == False:
            try:
                os.unlink(temp_file)
            except (OSError, IOError), err:
                pass
            return False, '', messages
        else:
            try:
                shutil.copymode(self.__conf_file, temp_file)
                shutil.copy2(temp_file, self.__conf_file )
                sb_utils.SELinux.restoreSecurityContext(self.__conf_file)
                os.unlink(temp_file)
            except (OSError, IOError), err:
                msg = "Unable to replace %s: %s" % (self.__conf_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Disabled Guest Access.'
        return True, action_record, messages



    ##########################################################################
    def apply(self, option=None):

        action_record = ""
        messages = {'messages': []}

        result, reason, messages = self.scan()
        if result == True:
            return False, '', messages
        
        return  self.make_change(option="no")
            

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # BANDAID ALERT
        # Due to a conflict between SBM_Conf and this module, we're fudging the undo a bit
        # SMB_Conf alters the file during processing (removes leading whitespace) which totally broke
        # how this moduel was working using patch/diff.  So we're going to take the presence of a change_record
        # as indicitive that the proper undo is to find 'guest ok = " in the /etc/samba/smb.conf file and set it
        # to 'guest ok = yes', trying to preserve whitespace.
        
        result, change_record, messages = self.make_change(option = "yes")
        
    
        msg = 'The guest access support has been restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', messages
