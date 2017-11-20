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
import sb_utils.os.info


class PasswordPolicyUppercase:
    def __init__(self):

        self.module_name = "PasswordPolicyUppercase"
        self.suse_version =  float(sb_utils.os.info.getDistroVersion())

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    ##########################################################################
    def validate_input(self, option_str):
        if not option_str:
            return 1
        try:
            value = int(option_str)
        except ValueError:
            return 1
        if value < 1:
            return 1
        return 0

    def check_version(self):
        if self.suse_version == 10.3:
            msg = "Module unsupported due to conflict with PasswordReuse"
            raise tcs_utils.ModuleUnsupported('%s %s' % (self.module_name, msg))

    ##########################################################################
    def scan(self, option=None):

        messages = {'messages': [] }
        self.check_version()
        if sb_utils.os.suse.pam.passwdqc_configured():
            msg = "It appears that pam_passwdqc is installed and configured. "\
                  "Presently, OS Lockdown only supports pam_cracklib."
            self.logger.info(self.module_name, msg)
            msg2 = "If wish this module to configure 'ucredit', unconfigure " \
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
        # If cracklib is not being used, then fail
        if len(cracklib_settings) == 0:
            msg = "PAM cracklib is not configured."
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, messages
        else:
            msg = "PAM cracklib is configured."
            self.logger.info(self.module_name, msg )
            messages['messages'].append("Okay: %s" % msg)

        #------------------------------------------
        # Check cracklib settings
        if not cracklib_settings.has_key('password'):
            msg = "PAM cracklib is not configured for 'password'" 
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, messages

        for pw_opt in cracklib_settings['password']:
            try:
                (pw_key, pw_val) = pw_opt.split('=')
            except (ValueError, IndexError):
                continue
            
            if pw_key == 'ucredit':
                msg = "PAM cracklib 'ucredit' option set to '%s' " % (pw_val)
                self.logger.info(self.module_name, msg)
                if int(pw_val) != -1:
                    msg = "PAM cracklib 'ucredit' option is not set to '-1'"
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    return False, msg, messages
                else:
                    msg = "PAM cracklib 'ucredit' option is set to '-1'"
                    return True, msg, messages
                    
        return False, 'ucredit parameter not set', messages


    ##########################################################################
    def apply(self, option=None):
    
        results, reason, messages = self.scan(option)
        if results == True:
            return False, '', messages
            
        action_record = ''
        self.check_version()

        messages = {'messages': [] }

        if sb_utils.os.suse.pam.passwdqc_configured():
            msg = "It appears that pam_passwdqc is installed and configured so,"\
              "OS Lockdown will not edit your PAM configuration. "\
              "Presently, OS Lockdown only supports pam_cracklib."
            self.logger.info(self.module_name, msg)
            return False, '', messages

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
            ucredit = sb_utils.os.suse.pam.cracklib_get('ucredit') 
            if ucredit == '-1':
                return False, 'none', messages

            action_record = "cracklib|%s" % str(ucredit)
            results = sb_utils.os.suse.pam.cracklib_set(option='ucredit', optValue='-1')

        # cracklib is DISABLED
        else:
            action_record = 'cracklib|'
            results = sb_utils.os.suse.pam.convert_to_cracklib()
            if results != True:
                msg = "Unable to switch from pam_pwcheck to pam_cracklib"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
            results = sb_utils.os.suse.pam.cracklib_set(option='ucredit', optValue='-1')
            if results != True:
                msg = "Unable to set pam_cracklib's ucredit parameter"
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "pam_cracklib's ucredit parameter set to '-1'"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, action_record, messages

    ##########################################################################
    def undo(self, change_record=None):

        self.check_version()
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
            return False, '', {}

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
            msg = "'ucredit' has been unset"
            results = sb_utils.os.suse.pam.cracklib_unset(option='ucredit')
        else:
            msg = "'ucredit' has been restored to '%s'" % option
            results = sb_utils.os.suse.pam.cracklib_set(option='ucredit', optValue=option)
                
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True

