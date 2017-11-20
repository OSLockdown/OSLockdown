#!/usr/bin/env python
#
# Copyright (c) 2008 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module sets the application defaults for the XscreenSaver 
# application. This application is used by many window managers
# including Gnome.
#
# This module sets the '*timeout, *lockTimeout, and *lock parameters
# in the /usr/openwin/lib/app-defaults/XscreenSaver file.
#


import os
import sys
import shutil
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software



class SetXScreenSaverDefaults:

    def __init__(self):
        self.module_name = "SetXScreenSaverDefaults"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, optionDict):

        if not optionDict or not 'XscreenSaverActivate' in optionDict:
            return 1
        try:
            value = int(optionDict['XscreenSaverActivate'])
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict=None):
        """Check to see if audit.rules file is correct"""

        results = sb_utils.os.software.is_installed(pkgname='SUNWxwsvr')
        if results == False:
            msg = "X Screen Saver/Locker is not installed"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

 
        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['XscreenSaverActivate']

        search_pattern = re.compile('^\*(lock|lockTimeout|timeout):')
        for conf_file in ['/usr/openwin/lib/app-defaults/XScreenSaver']:
            msg = "Checking %s" % conf_file
            self.logger.info(self.module_name, 'Scan: ' + msg)
            try:
                in_obj = open(conf_file, 'r')
            except IOError, err:
                msg = "Unable to open %s: %s" % (conf_file, err)
                self.logger.info(self.module_name, 'Scan Error: ' + msg)
                continue

            for line in in_obj.readlines():
                line = line.lstrip(' ')
                if not search_pattern.search(line):
                    continue
                line = line.rstrip('\n')
                try:
                    param  = line.split(':')[0]
                    parval = ''.join(line.split(':')[1:]).lstrip('\t')
                except IndexError:
                    continue

                msg = 'Found %s set to %s' % (param, parval)
                self.logger.debug(self.module_name, msg)

                if param == '*lock' and parval.strip().lower() != 'true':
                    msg = 'Scan Failed: *lock not set to true'
                    self.logger.notice(self.module_name, msg)
                    in_obj.close()
                    return 'Fail', msg

                if param == '*lockTimeout' and parval != '00000':
                    msg = 'Scan Failed: *lockTimeout not set to 0:00:00'
                    self.logger.notice(self.module_name, msg)
                    in_obj.close()
                    return 'Fail', msg

                if param == '*timeout':
                    testval = '0%02d00' % int(option)
                    partest = '0%02d' % int(parval)
                    if partest != testval:
                        msg = 'Scan Failed: *timeout not set %s' % testval
                        self.logger.notice(self.module_name, msg)
                        in_obj.close()
                        return 'Fail', msg

            in_obj.close()

        return 'Pass', ''



    ##########################################################################
    def apply(self, optionDict=None):
        """Create and replace the audit rules configuration."""

        action_record = []

        try:
            result, reason = self.scan(optionDict=optionDict)
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = "module is not applicable for this system"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        option = optionDict['XscreenSaverActivate']
        failure_flag = False

        for conf_file in ['/usr/openwin/lib/app-defaults/XScreenSaver']:
            # Protect file
            tcs_utils.protect_file(conf_file)

            # Open existing configuration file
            try:
                in_obj = open(conf_file, 'r')
            except IOError, err:
                msg = "Unable to open %s: %s" % (conf_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                failure_flag = True
                continue
 
            # Create temporary working file 
            try:
                out_obj = open(conf_file + '.new', 'w')
            except IOError, err:
                msg = "Unable to create temporary file: %s" % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                failure_flag = True
                continue


            # Read every line from main configuration file and write 
            # out new settings to temporary file

            search_pattern = re.compile('^\*(lock|lockTimeout|timeout):')

            found_it1 = False
            found_it2 = False
            found_it3 = False

            for line in in_obj.readlines():
                orig_line = line
                line = line.lstrip(' ')

                if not search_pattern.search(line):
                    out_obj.write(orig_line)
                    continue

                line = line.rstrip('\n')
                try:
                    param  = line.split(':')[0]
                    parval = ''.join(line.split(':')[1:]).lstrip('\t')
                except IndexError:
                    out_obj.write(orig_line)
                    continue

                if param == '*lock':
                    found_it1 = True
                    if parval.lower() != 'true':
                        out_obj.write('*lock: true\n')
                        continue

                if param == '*lockTimeout':
                    found_it2 = True
                    if parval != '00000':
                        out_obj.write('*lockTimeout: 0:00:00\n')
                        continue

                testval = '0%02d00' % int(option)
                if param == '*timeout':
                    found_it3 = True
                    if parval != testval:
                        out_obj.write('*timeout: 0:%02d:00\n' % int(option))
                        continue
              

                out_obj.write(orig_line)
                    
            if found_it1 == False:
                out_obj.write('*lock: true\n')

            if found_it2 == False:
                out_obj.write('*lockTimeout: 0:00:00\n')

            if found_it3 == False:
                out_obj.write('*timeout: 0:%02d:00\n' % int(option))


            in_obj.close()
            out_obj.close()

            action_record.append(tcs_utils.generate_diff_record(conf_file + '.new',
                                                           conf_file) + '\n')

            try:
                shutil.copymode(conf_file, conf_file+ '.new')
                shutil.copy2(conf_file + '.new', conf_file)
                os.unlink(conf_file + '.new')
            except OSError:
                msg = "Unable to replace %s with new version." % conf_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                failure_flag = True


        if failure_flag == True:
            msg = 'Unable to set CDE screen saver options'
            self.logger.error(self.module_name, 'Apply Failed: ' + msg)
            return 0, ''
            

        msg = 'X Screen Saver default options set'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'CDE Screen saver options reset'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

