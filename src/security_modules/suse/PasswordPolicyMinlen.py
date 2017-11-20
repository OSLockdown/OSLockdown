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


class PasswordPolicyMinlen:
    def __init__(self):

        self.module_name = "PasswordPolicyMinlen"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'passwordMinLength' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordMinLength'])
        except ValueError:
            return 1
        if value < 1:
            return 1
        return 0


    ##########################################################################
    def scan(self, optionDict=None):

        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordMinLength']
        option = int(option)
      
        if sb_utils.os.suse.pam.passwdqc_configured():
            msg = "It appears that pam_passwdqc is installed and configured. "\
                  "Presently, OS Lockdown only supports pam_cracklib."
            self.logger.info(self.module_name, msg)
            msg2 = "If wish this module to configure 'minlen', unconfigure " \
                   "pam_passwdqc."
            self.logger.info(self.module_name, msg2)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        results = sb_utils.os.software.is_installed(pkgname='pam-config')
        if results != True:
            msg = "'pam-config' package is not installed on the system."
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        results = sb_utils.os.software.is_installed(pkgname='cracklib')
        if results != True:
            msg = "'cracklib' package is not installed on the system."
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
    
        cracklib_settings = sb_utils.os.suse.pam.config(modName='cracklib')

        #------------------------------------------
        # If cracklib is not being used, check pwcheck settings
        if len(cracklib_settings) == 0:
            pwcheck_settings  = sb_utils.os.suse.pam.config(modName='pwcheck')
            msg = "PAM cracklib is not configured; checking PAM pwcheck settings"
            self.logger.info(self.module_name, msg)
            if not pwcheck_settings.has_key('password'):
                msg = "PAM pwcheck is not configured either" 
                self.logger.info(self.module_name, msg)
                self.logger.notice(self.module_name, 'Scan Failed.')
                return 'Fail', ''

            if len(pwcheck_settings['password']) == 0:
                msg = "PAM pwcheck is not set; assuming default "\
                      "minlen value of 5"
                self.logger.info(self.module_name, 'Scan Failed.')
                if option != 5:
                    self.logger.notice(self.module_name, 'Scan Failed.')
                    return 'Fail', ''
                else:
                    return 'Pass', ''

            found_minlen = False
            for pw_opt in pwcheck_settings['password']:
                try:
                    (pw_key, pw_val) = pw_opt.split('=')
                except (ValueError, IndexError):
                    continue
                if pw_key == 'minlen':
                    found_minlen = True
                    msg = "PAM pwcheck 'minlen' option set to '%s' " % (pw_val)
                    self.logger.info(self.module_name, msg)
                    if option != int(pw_val):
                        msg = "PAM pwcheck 'minlen' option is not set to '%d'" % (option)
                        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                        return 'Fail', msg

            if found_minlen == False:
                msg = "PAM pwcheck is configured but 'minlen' parameter; is not" \
                      " set so, assuming default minlen value of 5"
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                if option != 5:
                    return 'Fail', ''
                
            return 'Pass', ''

        #------------------------------------------
        # Check cracklib settings
        if not cracklib_settings.has_key('password'):
            msg = "PAM cracklib is not configured for 'password'" 
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        for pw_opt in cracklib_settings['password']:
            try:
                (pw_key, pw_val) = pw_opt.split('=')
            except (ValueError, IndexError):
                continue
            
            if pw_key == 'minlen':
                msg = "PAM cracklib 'minlen' option set to '%s' " % (pw_val)
                self.logger.info(self.module_name, msg)
                if option != int(pw_val):
                    msg = "PAM cracklib 'minlen' option is not set to '%d'" % (option)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    return 'Fail', msg
                else:
                    return 'Pass', ''
                    
        return 'Fail', 'minlen parameter not set'


    ##########################################################################
    def apply(self, optionDict=None):

        results, reason = self.scan(optionDict)
        if results == 'Pass':
            return 0, ''
            
        action_record = ''

        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        option = optionDict['passwordMinLength']
        option = int(option)
      
        if sb_utils.os.suse.pam.passwdqc_configured():
            msg = "It appears that pam_passwdqc is installed and configured so,"\
              "OS Lockdown will not edit your PAM configuration. "\
              "Presently, OS Lockdown only supports pam_cracklib."
            self.logger.info(self.module_name, msg)
            return 0, ''

        results = sb_utils.os.software.is_installed(pkgname='pam-config')
        if results != True:
            msg = "'pam-config' package is not installed on the system."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        results = sb_utils.os.software.is_installed(pkgname='cracklib')
        if results != True:
            msg = "'cracklib' package is not installed on the system."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Backup files in /etc/pam.d/* to a tar.gz file
        results = sb_utils.os.suse.pam.backup()
        if results == False:
            msg = "Unable to make backup of /etc/pam.d/* files"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        settings = sb_utils.os.suse.pam.config(modName='cracklib')
        # cracklib is already ENABLED
        if len(settings) != 0:
            minlen = sb_utils.os.suse.pam.cracklib_get('minlen') 
            action_record = "cracklib|%s" % str(minlen)
            results = sb_utils.os.suse.pam.cracklib_set(option='minlen', optValue=option)

        # cracklib is DISABLED
        else:
            settings = sb_utils.os.suse.pam.config(modName='pwcheck')
            results = sb_utils.os.suse.pam.pwcheck_get('minlen')
            if results != '':
                action_record = "pwcheck|%s" % str(results)
            else:
                action_record = "pwcheck|5"

            results = sb_utils.os.suse.pam.convert_to_cracklib()
            if results != True:
                msg = "Unable to switch from pam_pwcheck to pam_cracklib"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
            results = sb_utils.os.suse.pam.cracklib_set(option='minlen', optValue=option)
            if results != True:
                msg = "Unable to set pam_cracklib's minlen parameter"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1, action_record

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
 

        if sb_utils.os.suse.pam.passwdqc_configured():
            msg = "It appears that pam_passwdqc is installed and configured so,"\
              "OS Lockdown will not edit your PAM configuration. "\
              "Presently, OS Lockdown only supports pam_cracklib."
            self.logger.info(self.module_name, msg)
            return 0, ''

        results = sb_utils.os.software.is_installed(pkgname='pam-config')
        if results != True:
            msg = "'pam-config' package is not installed on the system."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        results = sb_utils.os.software.is_installed(pkgname='cracklib')
        if results != True:
            msg = "'cracklib' package is not installed on the system."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        results = sb_utils.os.suse.pam.backup()
        if results == False:
            msg = "Unable to make backup of /etc/pam.d/* files"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

#        results = sb_utils.os.suse.pam.convert_to_cracklib()
#        if results != True:
#            msg = "Unable to switch from pam_pwcheck to pam_cracklib"
#            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if option == '':         
            msg = "'minlen' has been unset"
            results = sb_utils.os.suse.pam.cracklib_unset(option='minlen')
        else:
            msg = "'minlen' has been restored to '%s'" % option
            results = sb_utils.os.suse.pam.cracklib_set(option='minlen', optValue=option)
                
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

