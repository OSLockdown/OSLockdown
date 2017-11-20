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


class PasswordPolicyDiffChars:
    def __init__(self):

        self.module_name = "PasswordPolicyDiffChars"
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, optionDict):
        if not optionDict or not 'passwordDiffChars' in optionDict:
            return 1
        try:
            value = int(optionDict['passwordDiffChars'])
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
        option = optionDict['passwordDiffChars']
        option = int(option)
      
        if sb_utils.os.suse.pam.passwdqc_configured():
            msg = "It appears that pam_passwdqc is installed and configured. "\
                  "Presently, OS Lockdown only supports pam_cracklib."
            self.logger.info(self.module_name, msg)
            msg2 = "If wish this module to configure 'difok', unconfigure " \
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

            found_difok = False
            for pw_opt in pwcheck_settings['password']:
                try:
                    (pw_key, pw_val) = pw_opt.split('=')
                except (ValueError, IndexError):
                    continue
                if pw_key == 'difok':
                    found_difok = True
                    msg = "PAM pwcheck 'difok' option set to '%s' " % (pw_val)
                    self.logger.info(self.module_name, msg)
                    if option != int(pw_val):
                        msg = "PAM pwcheck 'difok' option is not set to '%d'" % (option)
                        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                        return 'Fail', msg

            if found_difok == False:
                msg = "PAM pwcheck is configured but 'difok' parameter is not" \
                      " set so"
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
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
            
            if pw_key == 'difok':
                msg = "PAM cracklib 'difok' option set to '%s' " % (pw_val)
                self.logger.info(self.module_name, msg)
                if option != int(pw_val):
                    msg = "PAM cracklib 'difok' option is not set to '%d'" % (option)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    return 'Fail', msg
                else:
                    return 'Pass', ''
                    
        return 'Fail', 'difok parameter not set'


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
        option = optionDict['passwordDiffChars']
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
            difok = sb_utils.os.suse.pam.cracklib_get('difok') 
            action_record = "cracklib|%s" % str(difok)
            results = sb_utils.os.suse.pam.cracklib_set(option='difok', optValue=option)

        # cracklib is DISABLED
        else:
            settings = sb_utils.os.suse.pam.config(modName='pwcheck')
            results = sb_utils.os.suse.pam.pwcheck_get('difok')
            if results != '':
                action_record = "pwcheck|%s" % str(results)
            else:
                action_record = "pwcheck|-1"

            results = sb_utils.os.suse.pam.convert_to_cracklib()
            if results != True:
                msg = "Unable to switch from pam_pwcheck to pam_cracklib"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
            results = sb_utils.os.suse.pam.cracklib_set(option='difok', optValue=option)
            if results != True:
                msg = "Unable to set pam_cracklib's difok parameter"
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
            msg = "'difok' has been unset"
            results = sb_utils.os.suse.pam.cracklib_unset(option='difok')
        else:
            msg = "'difok' has been restored to '%s'" % option
            results = sb_utils.os.suse.pam.cracklib_set(option='difok', optValue=option)
                
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

