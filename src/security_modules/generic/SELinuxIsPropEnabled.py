#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Ensure SELinux is properly configured
#
#
#############################################################################

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux
import sb_utils.os.config
import sb_utils.filesystem.mount

class SELinuxIsPropEnabled:

    def __init__(self):
        self.module_name = "SELinuxIsPropEnabled"
        self.__config = '/etc/selinux/config'
        self.logger = TCSLogger.TCSLogger.getInstance()

        # will be set via options in Profile
        self.settings = {'SELINUX':None , 'SELINUXTYPE':None}
   
    def validate_options(self, optionDict):
        for tag in self.settings.keys():
            self.settings[tag] = optionDict[tag]
        
        
    ##########################################################################
    def scan(self, optionsDict=None):

        messages =  []
        self.validate_options(optionsDict)
        results = True 
        #=============================================
        # Step 1: Does this platform support SELinux?
        #
        results = sb_utils.SELinux.isSELinuxSupportedOnBox()
        if results == False:
            msg = "SELinux is not supported"
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        #=============================================
        # Step 2: Is SELinux Enabled?
        #
        results = sb_utils.SELinux.isSELinuxEnabled()
        if results == False:
            msg = "(CCE-3977-6) SELinux is not enabled." 
            self.logger.notice(self.module_name, "Scan Failed: %s " % msg)
            messages.append("Fail: %s" % msg)
            results = False
        else:
            msg = "(CCE-3977-6) SELinux is enabled"
            self.logger.info(self.module_name, msg)
#            messages.append("Okay: %s" % msg)

        #=============================================
        # Step 4: Check current running mode (enforcing or permissive)
        #
        selinux_mode = sb_utils.SELinux.SELinuxMode() 
        
        if selinux_mode != self.settings['SELINUX']:
            msg = "SELinux is not currently in %s mode" % self.settings['SELINUX']
            self.logger.notice(self.module_name, "Scan Failed: %s " % msg)
            messages.append("Fail: %s" % msg)
            results = False
        else:
            msg = "SELinux is currently in %s mode" % selinux_mode
            self.logger.notice(self.module_name, msg)
            messages.append("Okay: %s" % msg)

        #=============================================
        # Step 5: Check for Policy (targeted, mls, or strict)
        #
        try:
            selinux_policy = sb_utils.SELinux.SELinuxPolicy()[0][1] 
        except:
            selinux_policy = ''

        if selinux_policy not in ['targeted', 'mls', 'strict']:
            msg = "SELinux policy not currently set to targeted, mls, or strict"
            self.logger.notice(self.module_name, "Scan Failed: %s " % msg)
            messages.append("Fail: %s" % msg)
            results = False
        else:
            msg = "SELinux policy is currently '%s'" % selinux_policy
            self.logger.notice(self.module_name, msg)
            messages.append("Okay: %s" % msg)


        #=============================================
        # Step 5: Check for what is in the config file
        #
        paramlist = sb_utils.os.config.get_list(configfile=self.__config, delim='=') 
        for key,val in self.settings.iteritems():
            try:
                
                if paramlist[key] != self.settings[key]:
                    msg = "%s is set to %s instead of '%s' in %s" % (key, paramlist[key], self.settings[key], self.__config) 
                    self.logger.notice(self.module_name, "Scan Failed: %s " % msg)
                    messages.append("Fail: %s" % msg)
                    results = False
                else:
                    msg = "%s is set to %s in %s" % (key, paramlist[key], self.__config) 
                    self.logger.notice(self.module_name, msg)
            except KeyError, err:
                msg = "%s is not set at all in %s" % (key, self.__config)
                self.logger.notice(self.module_name, "Scan Failed: %s " % msg)
                messages.append("Fail: %s" % msg)
                results = False
        if self.settings['SELINUX'] == 'enforcing' and selinux_mode == 'disabled':
            msg = "OS Lockdown will not implement a transition from 'disabled' to 'enforcing' mode..  " + \
                  "An apply will alter the desired mode on the fly to 'permissive'.  A reboot, second apply, and another reboot will be required to finish the transistion to 'enforcing'."
            self.logger.warning(self.module_name, msg)
            messages.append("Warning: %s "% msg)                 
             
        if results == True:
           msg = "SELinux is properly configured."
        else:
           msg = "SELinux is not properly configured."
 
        return results, msg, {'messages':messages}

    ##########################################################################
    def apply(self, optionsDict=None):

        messages = []
        self.validate_options(optionsDict)
        changeRec = {}
        retval = False
        
        #=============================================
        # Step 1: Does this platform support SELinux?
        #
        results = sb_utils.SELinux.isSELinuxSupportedOnBox()
        if results == False:
            msg = "SELinux is not supported"
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        # If we're going to enforcing, *and* we are currently in disabled mode, than downgrade the mode to permissive.
        # Bad things can happen trying to boot a box in enforcing mode which does not have correct security contexts 
        # Note this with a message, and carry on.
        
        currentMode = sb_utils.SELinux.SELinuxMode()
        if self.settings['SELINUX'] == 'enforcing' and currentMode == 'disabled':
            msg = "OS Lockdown will not implement a transition from 'disabled' to 'enforcing' mode..  " + \
                  "Altering the desired mode on the fly to 'permissive'.  Please reboot, reapply this profile, and reboot again to finish the transistion to 'enforcing'."
            self.logger.warning(self.module_name, msg)
            messages.append("Warning: %s "% msg)
            self.settings['SELINUX'] = 'permissive'

        
        paramlist = sb_utils.os.config.get_list(configfile=self.__config, delim='=') 
        for key,val in self.settings.iteritems():
            try:
                if paramlist[key] == self.settings[key]:
                    continue
            except KeyError, err:
                    pass
            retval = True
            oldParam = sb_utils.os.config.setparam(configfile=self.__config, delim='=', param=key, value=val)
            changeRec[key] = oldParam

        if changeRec:
            # Set trigger file for /.autorelabel trigger file
            try:
                open("/.autorelabel", 'w+')    
            except Exception, err:
                msg = "Unable to create/open trigger file '/.autorelabel' : %s" % str(err)
                messages.append(msg)
                self.logger.error(self.module_name, msg)
        else:
            changeRec=""
                
        return retval, str(changeRec),{'messages':messages}

    ##########################################################################
    def undo(self, change_record=None):
        change_record = tcs_utils.string_to_dictionary(change_record)
        messages =[]
        for key,val in change_record.iteritems():
            oldParam = sb_utils.os.config.setparam(configfile=self.__config, delim='=', param=key, value=val)

        if change_record:
            # Set trigger file for /.autorelabel trigger file
            try:
                open("/.autorelabel", 'w+')    
            except Exception, err:
                msg = "Unable to create/open trigger file '/.autorelabel' : %s" % str(err)
                messages.append(msg)
                self.logger.error(self.module_name, msg)
            
        return True, "", {'messages':messages}


if __name__ == '__main__':
    Test = SELinuxIsPropEnabled()
    print Test.scan()
#    print Test.apply()
#    print Test.undo()
