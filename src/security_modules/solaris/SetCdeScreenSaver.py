#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Every 'sys.resources' file under /usr/dt/config/* must have
# dtsession*saverTimeout and dtsession*lockTimeout set.
#

import os
import sys
import shutil
import glob

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software



class SetCdeScreenSaver:

    def __init__(self):
        self.module_name = "SetCdeScreenSaver"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, optionDict):

        if not optionDict or not 'cdeSaverActivate' in optionDict:
            return 1
        try:
            value = int(optionDict['cdeSaverActivate'])
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict=None):
        """Check to see if audit.rules file is correct"""

        results = sb_utils.os.software.is_installed(pkgname='SUNWdtwm')
        if results == False:
            msg = "CDE Window Manager (SUNWdtwm) is not installed"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

 
        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['cdeSaverActivate']

        msg = "Checking config files under/dt/config/* for "\
                 "dtsession*saverTimeout and dtsession*lockTimeout parameters"
        self.logger.info(self.module_name, 'Scan: ' + msg)

        for conf_file in glob.glob('/usr/dt/config/*/sys.resources'):
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
                if not line.startswith('dtsession'):
                    continue
                line = line.rstrip('\n')
                try:
                    param  = line.split(':')[0]
                    parval = line.split(':')[1]
                except IndexError:
                    continue

                if param == 'dtsession*saverTimeout' or \
                                              param == 'dtsession*lockTimeout':
                    if int(parval) != int(option):
                        msg = "%s set to %d; expected it to be %d" % \
                                              (param, int(option), int(parval))
                        self.logger.notice(self.module_name, 
                                                         'Scan Failed: ' + msg)
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
        option = optionDict['cdeSaverActivate']
        failure_flag = False

        for conf_file in glob.glob('/usr/dt/config/*/sys.resources'):
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
            found_it1 = False
            found_it2 = False
            for line in in_obj.readlines():
                orig_line = line
                line = line.lstrip(' ')

                if not line.startswith('dtsession'):
                    out_obj.write(orig_line)
                    continue

                line = line.rstrip('\n')
                try:
                    param  = line.split(':')[0]
                    parval = line.split(':')[1]
                except IndexError:
                    out_obj.write(orig_line)
                    continue

                if param == 'dtsession*saverTimeout':
                    found_it1 = True
                    if int(parval) != int(option):
                        out_obj.write('%s: %d\n' % (param, int(option)))
                        continue

                if param == 'dtsession*lockTimeout':
                    found_it2 = True
                    if int(parval) != int(option):
                        out_obj.write('%s: %d\n' % (param, int(option)))
                        continue

                out_obj.write(orig_line)
                    
            if found_it1 == False:
                out_obj.write('dtsession*saverTimeout: %d\n' % int(option))

            if found_it2 == False:
                out_obj.write('dtsession*lockTimeout: %d\n' % int(option))

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
            

        msg = 'CDE screen saver options set'
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

