#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable Java and Javascript in each user's Firefox Prefs File
#
#
##############################################################################

import os
import re
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.misc.unique
import sb_utils.SELinux


class DisableFirefoxJavascript:

    def __init__(self):
        self.module_name = self.__class__.__name__
        self.__dirloc    = '.mozilla/firefox'
        self.__prefsfile = 'prefs.js'
        self.__opts      = { 'javascript.enabled' : 'false',
                             'security.enable_java' : 'false' }

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []

        flag = 0
        for pref_file in self._get_moz_pref_files():
            bad_file = 0
            try:
                in_obj = open(pref_file, 'r') 
            except (IOError, OSError), err:
                msg = "Unable to read %s: " % (pref_file, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            msg = "Scan: Checking settings in %s" % pref_file
            self.logger.info(self.module_name, msg)

            # Initialize counters
            key_count = {}
            for key in self.__opts.keys():
                key_count[key] = 0
 
            # Count matches
            lines = in_obj.readlines()
            in_obj.close()
            for line in lines:
                if not line.startswith('user_pref('):
                    continue

                line = line.rstrip('\n')
                line = line.strip(' ')

                # Use Regex to extract the key-value pairs
                # Sample: user_pref("security.warn_entering_secure", false);
                 
                pat = re.compile('user_pref\("(\S+)",\s+(.*)\);')
                mat = pat.match(line)
                key = mat.group(1)
                cur_value = mat.group(2)
                cur_value = cur_value.strip('"')

                if self.__opts.has_key(key):
                    msg = "'%s' is currently set to '%s' (expecting '%s')" % \
                          (key, cur_value, self.__opts[key])
                    self.logger.debug(self.module_name, 'Scan: ' + msg)

                    if self.__opts[key] == cur_value: 
                        key_count[key] += 1

                    if key_count[key] > 0 and self.__opts[key] != cur_value:
                        key_count[key] += 1

            for key in self.__opts.keys():
                if key_count[key] != 1:
                    bad_file = 1
                    flag = 1

            if bad_file == 1:
                msg = "%s does not disable Java and Javascript" % pref_file
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append("Fail: %s" % msg)

        if flag == 1:
            reason = "Found Firefox prefs.js files which do not disable Java and Javascript"
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return False, reason, messages

        return True, "All Firefox prefs.js files are correct.", messages


    ##########################################################################
    def apply(self, option=None):

        messages = {'messages': []}
        action_record = ""

        for pref_file in self._get_moz_pref_files():
            # Protect file
            tcs_utils.protect_file(pref_file)

            try:
                in_obj = open(pref_file, 'r')
            except (IOError, OSError), err:
                msg = "Unable to read %s: %s" % (pref_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                messages['messages'].append("Error: %s" % msg)
                continue

            try:
                out_obj = open(pref_file + '.new', 'w')
            except Exception, err:
                in_obj.close()
                msg = "Unable to create temporary file (%s)." % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                messages['messages'].append("Error: %s" % msg)
                continue

            # Initialize counters
            key_count = {}
            for key in self.__opts.keys():
                key_count[key] = 0

            # Count matches
            lines = in_obj.readlines()
            in_obj.close()
            for line in lines:
                line = line.rstrip('\n')
                if line.startswith('user_pref('):
                    line = line.strip(' ')

                    # Use Regex to extract the key-value pairs
                    # Sample: user_pref("security.warn_entering_secure", false);

                    pat = re.compile('user_pref\("(\S+)",\s+(.*)\);')
                    mat = pat.match(line)
                    key = mat.group(1)
                    cur_value = mat.group(2)
                    cur_value = cur_value.strip('"')

                    if self.__opts.has_key(key):
                        if self.__opts[key] == cur_value: 
                            key_count[key] += 1

                        if self.__opts[key] != cur_value:
                            line = 'user_pref("'+key+'", '+self.__opts[key]+');'
                            key_count[key] += 1
                            msg = "Setting %s to %s in %s" % (key, self.__opts[key], pref_file)
                            self.logger.notice(self.module_name, "Apply Performed: " + msg)
                            messages['messages'].append(msg)

                        if key_count[key] > 1:
                            line = 'discard'

                if line != 'discard':
                    out_obj.write(line+'\n')
                
            for key in self.__opts.keys():
                if key_count[key] == 0:
                    line = 'user_pref("' + key + '", ' + self.__opts[key] + ');'
                    out_obj.write(line+'\n')

            out_obj.close()
            change_record = tcs_utils.generate_diff_record(pref_file + '.new', 
                pref_file) + '\n'

            action_record += change_record
            try:
                shutil.copymode(pref_file, pref_file + '.new')
                shutil.copy2(pref_file + '.new', pref_file)
                sb_utils.SELinux.restoreSecurityContext(pref_file)
                os.unlink(pref_file + '.new')
            except (OSError, IOError), err:
                msg = "Unable to replace %s with new version: %s" % (pref_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = pref_file + ' updated' 
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return True, action_record, messages


    ##########################################################################
    def _get_moz_pref_files(self):
        """
        Get a list of home directories from the passwd database
        """ 
        in_obj = open('/etc/passwd', 'r')
        lines = in_obj.readlines()
        dirs = []
        for line in lines:
            fields = line.split(':')
            if len(fields) < 7:
                continue
            homedir = line.split(':')[5] 
            homedir = homedir.strip('\n') 
            if os.path.isdir(homedir+'/'+self.__dirloc):
                dirs.append(homedir)

        in_obj.close()

        # Check for Firefox Pref file in each home dir
        # I prefer os.walk() over popen() which forks out and runs shell cmds
        pref_files = []
        unique = sb_utils.misc.unique.unique(dirs)
        for mdir in unique:
            for root, dirs, files in os.walk(os.path.join(mdir, self.__dirloc)):
                for name in files:
                    if name == self.__prefsfile:
                        pref_files.append(os.path.join(root, name))

        return pref_files


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, msg, {}

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Firefox preference files reverted for all users.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, {}


if __name__ == '__main__':
    Test = DisableFirefoxJavascript()
    print Test.scan()
    (flag, change_record, messages) = Test.apply()
    print Test.undo(change_record)
