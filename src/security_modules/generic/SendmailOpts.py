#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.SELinux

class SendmailOpts:

    def __init__(self):
        self.module_name = "SendmailOpts"
        self.logger = TCSLogger.TCSLogger.getInstance()
        
        if sb_utils.os.info.is_LikeSUSE() != True:
            self.__file = '/etc/mail/sendmail.cf'
        else:
            self.__file = '/etc/sendmail.cf'
        
        self.__opts = { 
          'O PrivacyOptions': 'authwarnings,novrfy,noexpn,restrictqrun',
          'O LogLevel' : '9',
          'O ForwardPath' : '',
          'O SmtpGreetingMessage': 'Mail Server Ready ; $b',
          'O AllowBogusHELO' : 'False' } 



    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []
        pkg = "sendmail"

        if sb_utils.os.info.is_solaris() == True:
            pkg = "SUNWsndmr"

        results = sb_utils.os.software.is_installed(pkgname = pkg)
        if results == False:
            msg = "sendmail does not appear to be installed on the system"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        msg = "%s package is installed" % pkg
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        if not os.path.isfile(self.__file):
            msg = "%s is installed but %s is missing" % (pkg, self.__file)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to read file %s: %s" % (self.__file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Checking %s" % self.__file
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        key_count = {} 
        for k in self.__opts.keys():
            key_count[k] = 0
        
        lines = in_obj.readlines()
        in_obj.close()
        reason = ''
        flag = 0
        for line in lines:
            if not line.startswith('O '):
                continue
        
            line = line.rstrip('\n')
            key = line.split('=')[0]
            key = key.strip(' ')
        
            cur_value = line.split('=')[1]
            cur_value = cur_value.strip(' ')
        
            if self.__opts.has_key(key):
                exp_value = self.__opts[key]
                key_count[key] += 1
            else:
                continue
                exp_value = ''
        

            if exp_value != cur_value:
                if exp_value  :
                    flag = 1
                    reason = "%s not set to '%s'" % (key.split()[1], exp_value)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                    messages['messages'].append("Fail: %s" % reason)
                else:
                    flag = 1
                    reason = "%s set to '%s' instead of being unset" % (key.split()[1], cur_value)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                    messages['messages'].append("Fail: %s" % reason)
            else:
                if key in self.__opts.keys():
                    reason = "Okay: %s is set to '%s'" % (key.split()[1], exp_value)
                    self.logger.debug(self.module_name, reason)
                    messages['messages'].append(reason)
        
        for k in self.__opts.keys():
            if key_count[k] > 1:
                flag = 1
                reason = "Duplicate entry %s found." % k
                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                messages['messages'].append("Fail: %s" % reason)

            if key_count[k] == 0 and self.__opts[k]: # if we didn't see a tag, *and* the value for said isn't empty, complain
                flag = 1
                reason = "%s not set to '%s'" % (k, self.__opts[k])
                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                messages['messages'].append("Fail: %s" % reason)


        if flag == 1:
            return False, "Sendmail options not set correctly", messages

        return True, "Sendmail options set correctly", messages
        

    ##########################################################################
    def apply(self, option=None):

        action_record = []

        (result, reason, messages) = self.scan()
        if result == True:
            return False, '', {}

        messages = {}
        messages['messages'] = []

        tcs_utils.protect_file(self.__file)
        msg = "Made backup copy of %s" % self.__file
        messages['messages'].append(msg)

        try:
            in_obj = open(self.__file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to read file %s: %s" % (self.__file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Reading %s" % self.__file
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        # Keep track of which has already been written to avoid duplicates
        key_count = {} 
        for k in self.__opts.keys():
            key_count[k] = 0
        
        lines = in_obj.readlines()
        in_obj.close()

        try:
            out_obj = open(self.__file, 'w')
        except Exception, err:
            in_obj.close()
            msg = "Unable to write to %s: %s" % (self.__file, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line_nr, line in enumerate(lines):
            line = line.rstrip('\n')
            commented_out = False
            if line.startswith('O ') or line.startswith('#O '):
                key = line.split('=')[0]
                if key.startswith('#'):
                    commented_out = True
                    key = key.lstrip('#')

                key = key.strip()
                try:
                    cur_value = line.split('=')[1]
                except IndexError:
                    out_obj.write("%s\n" % line)
                    continue
                cur_value = cur_value.strip()

                if key not in self.__opts.keys():
                    out_obj.write("%s\n" % line)
                    continue
                     
                exp_value = self.__opts[key]
                if exp_value != cur_value:
                    if exp_value:
                        line = "%s=%s" % (key, exp_value)
                        action_record.append("%s=%s\n" % (key, cur_value))
                        reason = "%s set to %s in %s, line number %d" % (key, exp_value, self.__file, line_nr+1)
                        messages['messages'].append(reason)
                        self.logger.debug(self.module_name, 'Apply Performed: %s' % reason)
                    else:
                        line = ""
                        action_record.append("%s=%s\n" % (key, cur_value))
                        reason = "%s was unset in %s, line number %d" % (key, self.__file, line_nr+1)
                        messages['messages'].append(reason)
                        self.logger.debug(self.module_name, 'Apply Performed: %s' % reason)
                if commented_out == True and exp_value == cur_value:
                    line = "%s=%s" % (key, exp_value)
                    action_record.append("%s=commented\n" % key)
                    reason = "%s set to %s in %s, line number %d" % (key, exp_value, self.__file, line_nr+1)
                    messages['messages'].append(reason)
                    self.logger.debug(self.module_name, 'Apply Performed: %s' % reason)
                

                if self.__opts.has_key(key):
                    if key_count[key] > 0:
                        line = 'discard'
                    key_count[key] += 1
    
            # Write line but skip duplicates.
            if line != 'discard':
                out_obj.write(line + '\n')

        # Check for anything not already set.
        for k in self.__opts.keys():
            if key_count[k] == 0:
                reason = "%s set to %s in %s" % (k, exp_value, self.__file)
                action_record.append("%s=unset\n" % k)
                out_obj.write("%s=%s\n" % (k, self.__opts[k]))
                messages['messages'].append(reason)
                key_count[k] = 1

        out_obj.close()

        flag = 0

        messages['messages'].append("Manual Action: For these settings to take effect, you must restart the Sendmail service")
        return True, ''.join(action_record), messages


    ##########################################################################
    def undo(self, change_record=None):


        if not change_record or change_record == '':
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        messages = {}
        messages['messages'] = []

        changes = {}
        for entry in change_record.split('\n'):
            entry = entry.strip()
            if not entry:
                continue
            key = entry.split('=')[0]
            key = key.strip()
            optval = entry.split('=')[1]
            optval = optval.strip()
            changes[key] = optval

        # Read in current file
        try:
            in_obj = open(self.__file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to read file %s: %s" % (self.__file, err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()
        msg = "Reading %s" % self.__file
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        # Open file for write
        try:
            out_obj = open(self.__file, 'w')
        except Exception, err:
            in_obj.close()
            msg = "Unable to write to %s: %s" % (self.__file, str(err))
            self.logger.error(self.module_name, 'Undo Error: ' + msg)

        for line_nr, line in enumerate(lines):
            if not line.startswith('O '):
                out_obj.write(line)
                continue

            line = line.rstrip('\n')
            optkey = line.split('=')[0]
            optval = line.split('=')[1]
           
            if optkey not in changes.keys():
                out_obj.write("%s\n" % line)
                continue
   
            change = changes.pop(optkey)
            
            if change == 'unset':
                messages['messages'].append("Removed %s from %s" % (optkey, self.__file))
                changes.pop(optkey)
                continue 

            if change == 'commented':
                messages['messages'].append("Commented out %s in %s" % (optkey, self.__file))
                out_obj.write("#%s\n" % line)
                continue 
            
            messages['messages'].append("Reset %s to %s in %s" % (optkey, change, self.__file))
            out_obj.write("%s=%s\n" % (optkey, change))

        for change in changes.keys():
            messages['messages'].append("Restoring %s to %s in %s" % (change, changes[change], self.__file))
            out_obj.write("%s=%s\n" % (change, changes[change]))
            
        out_obj.close()


        msg = 'Sendmail options reverted.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, messages

