#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
# This module sets CRONLOG=YES in /etc/default/cron
#


import sys
import shutil
import os
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class SyslogCronLogging:

    def __init__(self, hmac_msg=None):

        self.module_name = "SyslogCronLogging"
        self.__target_file = '/etc/default/cron'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        if not os.path.isfile(self.__target_file):
            return 'Pass', ''

        try:
            in_obj = open(self.__target_file)
        except IOError, err:
            msg = 'Unable to read %s: %s' % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
             
        lines = in_obj.readlines() 
        in_obj.close()

        search_pattern = re.compile('^CRONLOG=NO$')
        count = 0
        for line in lines:
            count += 1
            if line.startswith('#'): 
                continue

            if search_pattern.search(line.rstrip('\n')):
                msg = 'Found CRONLOG=NO in %s, line %d' % \
                     (self.__target_file, count)
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg
           

        return 'Pass', ''
         

    ##########################################################################
    def apply(self, option=None):

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            in_obj = open(self.__target_file, 'r')
        except Exception, err:
            msg = "Unable to open file %s (%s)." % (self.__target_file, 
                                                    str(err))
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)" % str(err)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        search_pattern = re.compile('^CRONLOG=')

        lines = in_obj.readlines()
        for line in lines:
            if search_pattern.search(line):
                out_obj.write('CRONLOG=YES\n')
            else:
                out_obj.write(line)

        out_obj.close()
        in_obj.close()

        action_record = tcs_utils.generate_diff_record(self.__target_file + 
                                                       '.new', 
                                                       self.__target_file)
        try:
            shutil.copymode(self.__target_file, self.__target_file + '.new')
            shutil.copy2(self.__target_file + '.new', self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file 
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'CRONLOG=YES set in %s' % self.__target_file
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record

    ##########################################################################
    def undo(self, action_record=None):
        """ Remove sulogin addition."""

        result, reason = self.scan() 
        if result == 'Fail':
            return 0

        if not action_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            tcs_utils.apply_patch(action_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'CRONLOG restored in %s' % self.__target_file
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

