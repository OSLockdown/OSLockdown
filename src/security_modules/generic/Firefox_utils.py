#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Set Security Settings in User's Firefox Preference file
#
# NOTE: This is a generic, centralized module intended to be called from
#       other Firefox related modules. Those modules will provide a dictionary
#       of settings when this class is instantiated.
#
#
#
##############################################################################

import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.misc.unique
from  sb_utils.apps import Firefox


class Firefox_utils:

    def __init__(self, ff_settings):
        self.module_name = self.__class__.__name__
        self.__opts = ff_settings
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []

        user_pref_files = Firefox.getUserPrefFiles()
        if len(user_pref_files) < 1:
            msg = "No Firefox prefs.js files found"
            self.logger.error(self.module_name, 'Not Applicable:' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        fail_flag = False
        for pref_file in user_pref_files:
            ff_settings = Firefox.getSettings(pref_file)
            if len(ff_settings) < 1:
                continue
        
            this_file_failed = False
            for key in self.__opts.keys():
                if not ff_settings.has_key(key):
                    msg = "'%s' is not set in %s" % (key, pref_file)
                    self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                    this_file_failed = True     
                    continue

                if ff_settings[key] != self.__opts[key]:
                    msg = "'%s' is not set to '%s' in %s" % (key, self.__opts[key], pref_file)
                    self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                    this_file_failed = True     
                    continue

            if this_file_failed == True:
                fail_flag = True
                msg = "%s has incorrect settings" % pref_file
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, 'Scan Failed:' + msg)


        if fail_flag == False:
            return True, "All Firefox prefs.js files are correct", messages
        else:
            return False, "Some Firefox prefs.js files are incorrect", messages

    ##########################################################################
    def apply(self, option=None):


        # first things first - do we even *need* to apply
        (results, reason, messages) = self.scan()
        if results == True:
            return False, reason, messages
            
        messages = {}
        messages['messages'] = []
        action_record = {}

        user_pref_files = Firefox.getUserPrefFiles()
        if len(user_pref_files) < 1:
            msg = "No Firefox prefs.js files found"
            self.logger.error(self.module_name, 'Not Applicable:' + msg)
            return False, msg, messages

        for pref_file in user_pref_files:
            ff_settings = Firefox.getSettings(pref_file)
            if len(ff_settings) < 1:
                continue

            required_settings = self.__opts
            file_change_record = {}
            for key in self.__opts.keys():
                if not ff_settings.has_key(key):
                    file_change_record[key] = 'unset'
                    continue
                if ff_settings[key] == self.__opts[key]:
                    del required_settings[key]
                else:
                    file_change_record[key] = ff_settings[key]

            results = Firefox.setParameters(prefs_file=pref_file, params=required_settings)
            if results == True:
                if len(file_change_record) > 0:
                    action_record[pref_file] = file_change_record
                msg = "%s has been updated" % pref_file
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                messages['messages'].append(msg)
            else:
                msg = "Error: Unable to update %s " % pref_file
                messages['messages'].append(msg)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)

        return True, str(action_record), messages

    ##########################################################################
    def undo(self, change_record=None):

        messages = {}
        messages['messages'] = []
        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, msg, {}

        try:
            change_record = eval(change_record)
        except SyntaxError:
            msg = "Malformed change record. Unable to perform undo"
            self.logger.error(self.module_name, "Undo Error: " + msg)
            raise tcs_utils.ActionError("%s %s" % (self.module_name, msg))
        except Exception, err:
            msg = "Unable to perform undo: %s" % str(err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError("%s %s" % (self.module_name, msg))
           
        changes_made = False
        for pref_file in change_record.keys():
            if not os.path.isfile(pref_file):
                msg = "%s does not exist. Skipping undo" % (pref_file)        
                self.logger.info(self.module_name, 'Undo Error: ' + msg)
                messages['messages'].append(msg)
                continue
                
            results = Firefox.setParameters(prefs_file=pref_file, 
                                            params=change_record[pref_file])
            if results == True:
                msg = "%s has been restored" % pref_file
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                messages['messages'].append(msg)
                changes_made = True
            else:
                msg = "Error: Unable to restore %s " % pref_file
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                messages['messages'].append(msg)

        if changes_made == True:
            return True, "Firefox prefs.js files have been restored", messages
        else:
            return False, "No Firefox prefs.js have been restored", messages

