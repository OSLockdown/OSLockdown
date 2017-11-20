#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import glob

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.solaris


class DisableSerialLoginPrompt:

    def __init__(self):

        self.module_name = "DisableSerialLoginPrompt"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option_str):
        if not option_str:
            return 1
        try:
            value = int(option_str)
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        failure_flag = False
        for testfile in glob.glob('/dev/ttyS?'):
            nologin = "/etc/nologin.%s" % os.path.basename(testfile)
            if not os.path.isfile(nologin):
                msg = "%s is missing" % nologin
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)                                                                    
                failure_flag = True
            else:
                msg = "Found %s " % nologin
                self.logger.info(self.module_name, msg)                                                                    
            
        if failure_flag == True:
            msg = "Missing /etc/nologin.ttyS? file(s)"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)                                                                    
            return 'Fail', msg
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        action_record = []
        oldmask = os.umask(022)
        for testfile in glob.glob('/dev/ttyS?'):
            nologin = "/etc/nologin.%s" % os.path.basename(testfile)
            if not os.path.isfile(nologin):
                try:
                    outfile = open(nologin, 'w')
                    outfile.write('')
                    outfile.close()
                    msg = "Created %s" % nologin
                    self.logger.notice(self.module_name, 'Apply Performed: ' + msg)                                                                    
                    action_record.append(nologin)
                except IOError, err:
                    msg = "Unable to create %s: %s" % (nologin, err)
                    self.logger.error(self.module_name, "Apply Error: " + msg)                                                                    
            
        os.umask(oldmask)
        if action_record == []:
            return 0, ''
        else:
            return 1, ' '.join(action_record)

    ##########################################################################
    def undo(self, change_record):
        """Undo the previous action."""

        if change_record == None:
            msg = 'No change record provided; unable to perform undo.'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        for nologin in change_record.split(' '):
            if not os.path.isfile(nologin):
                continue
            try:
                os.unlink(nologin)
                msg = "Removed %s" % (nologin)
                self.logger.notice(self.module_name, "Undo Performed: " + msg)
            except IOError, err:
                msg = "Unable to remove %s: %s" % (nologin, err)
                self.logger.notice(self.module_name, "Undo Failed: " + msg)

        return 1


