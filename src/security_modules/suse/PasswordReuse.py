#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software

import sb_utils.os.suse.pam


class PasswordReuse:
    def __init__(self):

        self.module_name = "PasswordReuse"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'passwordReuse' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordReuse'])
        except ValueError:
            return 1
        if value < 1:
            return 1
        return 0


    ##########################################################################
    def scan(self, optionDict=None):

        messages = {'messages': [] }
        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordReuse']
        option = int(option)
      
        results = sb_utils.os.software.is_installed(pkgname='pam-config')
        if results != True:
            msg = "'pam-config' package is not installed on the system."
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        pwhistory_settings = sb_utils.os.suse.pam.config(modName='pwhistory')

        #------------------------------------------
        # If pwhistory is not being used, check pwcheck settings
        if len(pwhistory_settings) == 0:
            msg = "PAM pwhistory is not configured"
            self.logger.notice(self.module_name, 'Scan Failed:' + msg)
            messages['messages'].append(msg)
            return False, '', messages
        else:
            msg = "Okay: PAM pwhistory is configured"
            messages['messages'].append(msg)

        #------------------------------------------
        # Check pwhistory settings
        if not pwhistory_settings.has_key('password'):
            msg = "PAM pwhistory is not configured for 'password'" 
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            messages['messages'].append(msg)
            return  False, '', messages

        for pw_opt in pwhistory_settings['password']:
            try:
                [pw_key, pw_val] = pw_opt.split('=')
            except (ValueError, IndexError):
                continue
            
            if pw_key == 'remember':
                msg = "PAM pwhistory 'remember' option set to '%s' " % (pw_val)
                self.logger.info(self.module_name, msg)
                if int(pw_val) > option:
                    msg = "PAM pwhistory 'remember' option is currently set "\
                      "to '%d' which is greater than '%d' " % (int(pw_val), option)
                    self.logger.info(self.module_name, 'Scan Passed: ' + msg)
                    return True, '', {}
                elif int(pw_val) == option:
                    msg = "PAM pwhistory 'remember' option is currently set to '%d'" % option
                    self.logger.info(self.module_name, 'Scan Passed: ' + msg)
                    return True, '', {}
                else:
                    msg = "PAM pwhistory 'remember' option is not set to '%d' or higher." % (option)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    messages['messages'].append(msg)
                    return False, '', messages
        msg = 'remember parameter not set'            
        messages['messages'].append(msg)
        return False, '', messages 


    ##########################################################################
    def apply(self, optionDict=None):

        action_record = ''

      
        result, reason, messages = self.scan(optionDict)
        if result == True:
            return False, reason, messages

        option = optionDict['passwordReuse']
        option = int(option)
                
        # Backup files in /etc/pam.d/* to a tar.gz file
        results = sb_utils.os.suse.pam.backup()
        if results == False:
            msg = "Unable to make backup of /etc/pam.d/* files"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        settings = sb_utils.os.suse.pam.config(modName='pwhistory')
        # pwhistory is already ENABLED
        if len(settings) != 0:
            remember = sb_utils.os.suse.pam.pwhistory_get('remember') 
            results = sb_utils.os.suse.pam.pwhistory_set(option='remember', optValue=option)

        # pwhistory is DISABLED
        else:
            results = sb_utils.os.suse.pam.enable(modName='pwhistory')
            if results != True:
                msg = "Unable to switch from pam_pwcheck to pam_pwhistory"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
            results = sb_utils.os.suse.pam.pwhistory_set(option='remember', optValue=option)
            if results != True:
                msg = "Unable to set pam_pwhistory's remember parameter"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                action_record = "pwhistory|"
        self.logger.debug(self.module_name, ' APPLY RECORD = '+action_record)
        return True, action_record, {}

    ##########################################################################
    def undo(self, change_record=None):


        if change_record == None:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            option = change_record.split('|')[1]
        except:
            msg = "Unable to perform undo operation due to invalid "\
                  "formatted change record"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
 

        results = sb_utils.os.software.is_installed(pkgname='pam-config')
        if results != True:
            msg = "'pam-config' package is not installed on the system."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        results = sb_utils.os.suse.pam.backup()
        if results == False:
            msg = "Unable to make backup of /etc/pam.d/* files"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if option == '':         
            msg = "'remember' has been unset"
            results = sb_utils.os.suse.pam.pwhistory_unset(option='remember')
        else:
            msg = "'remember' has been restored to '%s'" % option
            results = sb_utils.os.suse.pam.pwhistory_set(option='remember', optValue=option)
                
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True
