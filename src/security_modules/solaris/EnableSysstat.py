#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################
#
# This module enables system accounting.
#
# (1) SUNWaccu package must be installed
#
# (2) svc:/system/sar:default must be enabled
#
# (3) Examine 'sys' crontab entry and make sure
#     that /usr/lib/sa/sa1 and /usr/lib/sa/sa2 
#     are scheduled to run. If not, put in 
#     a standard scheduled time. (entry1 and entry2)
#

import sys
import re
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.acctmgt.users
import sb_utils.file.fileperms

class EnableSysstat:

    def __init__(self):

        self.module_name = 'EnableSysstat'
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__pkgname = 'SUNWaccu'
        self.__svcfmri = 'svc:/system/sar:default'

        self.__cmd1   = '/usr/lib/sa/sa1'
        self.__entry1 = {       'min': '0,20,40',
                               'hour': '*',
                       'day_of_month': '*',
                              'month': '*',
                        'day_of_week': '*'   }

        self.__cmd2   = '/usr/lib/sa/sa2 -s 0:00 -e 23:59 -i 1200 -A'
        self.__entry2 = {       'min': '45',
                               'hour': '23',
                       'day_of_month': '*',
                              'month': '*',
                        'day_of_week': '*'   }


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        # Check to see if the account package is installed
        results = sb_utils.os.software.is_installed(pkgname = self.__pkgname)
        if results != True:
            msg = 'System Accounting (SUNWaccu) is not installed.'
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, {'messages':[msg]}

        # Check to see if the service is enabled
        results = sb_utils.os.service.is_enabled(svcname = self.__svcfmri)
        if results != True:
            msg = 'System accounting (%s) is not enabled' % self.__svcfmri
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, {'messages':[msg]}


        # See if /usr/lib/sa/sa1 command is scheduled to run
        cmd = '/usr/bin/crontab -l sys'
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = '/usr/lib/sa/sa1 not scheduled to run in sys crontab: %s' % results[2]
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, {'messages':[msg]}

        pattern1 = re.compile('/usr/lib/sa/sa1')
        pattern2 = re.compile('/usr/lib/sa/sa2')
        found = 0

        for line in results[1].split('\n'):
            if line.startswith('#'):
                continue
            if pattern1.search(line) or pattern2.search(line):
                found += 1

        if found > 1:
            msg = '/usr/lib/sa/sa1 and sa2 are running from sys crontab'
#            self.logger.notice(self.module_name, 'Scan Passed: ' + msg)
            return True, '', {}

        return False, 'System accounting scheduled to run', {}


    ##########################################################################
    def apply(self, option=None):

        result, reason, messages = self.scan()
        if result == True:
            return False, reason, messages

        # Check to see if the account package is installed
        results = sb_utils.os.software.is_installed(pkgname = self.__pkgname)
        if results != True:
            msg = "System Accounting (SUNWaccu) is not installed; you must "\
                  "install this yourself from your vendor-provided media."
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return False, msg, {'messages':[msg]}


        # Enable the service
        results = sb_utils.os.service.enable(svcname = self.__svcfmri)
        if results != True:
            msg = 'Unable to enable: %s' % self.__svcfmri
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return False, msg, {'messages':[msg]}


        # Check cron.allow
        if not os.path.isfile('/etc/cron.d/cron.allow'):
            try:
                outCrontab = open('/etc/cron.d/cron.allow', 'w')
                outCrontab.write('root\nsys\n')
                outCrontab.close()
            except IOError, err:
                msg = "Unable to create /etc/cron.d/cron.allow : %s" % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
        else:        
            try:
                inCrontab = open('/etc/cron.d/cron.allow', 'r')
                lines = []
                for entry in inCrontab.readlines():
                    lines.append(entry.strip())    
                inCrontab.close()
                if 'sys' not in lines:
                    try:
                        outCrontab = open('/etc/cron.d/cron.allow', 'a')
                        outCrontab.write('\nsys\n')
                        outCrontab.close()
                    except IOError, err:
                        msg = "Unable to add 'sys' to /etc/cron.d/cron.allow : %s" % str(err)
                        self.logger.error(self.module_name, 'Apply Error: ' + msg)

            except IOError, err:
                msg = "Unable to open /etc/cron.d/cron.allow : %s" % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)

        # Set Owner/Group to root:root and perms 0600
        changes_to_make = {'owner': 0,
                            'group': 0,
                            'dacs': 0600}
        ignore_results = sb_utils.file.fileperms.change_file_attributes( '/etc/cron.d/cron.allow', changes_to_make)

        # Make crontab entries
        results = sb_utils.acctmgt.users.cronjob( user = 'sys',
                            command = self.__cmd1, schedule = self.__entry1 )
        if results == False:
            msg = 'Unable to update sys crontab'
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return False, msg, {'messages':[msg]}

        results = sb_utils.acctmgt.users.cronjob( user = 'sys',
                            command = self.__cmd2, schedule = self.__entry2 )
        if results == False:
            msg = 'Unable to update sys crontab'
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return False, msg, {'messages':[msg]}


        return True, 'enabled', {}


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record or change_record != 'enabled':
            msg = "unable to undo without valid change record"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, '', {}
            
        # Check to see if the account package is installed
        results = sb_utils.os.software.is_installed(pkgname = self.__pkgname)
        if results != True:
            msg = "System Accounting (SUNWaccu) is not installed; you must "\
                  "install this yourself from your vendor-provided media."
            self.logger.notice(self.module_name, 'Undo Failed: ' + msg)
            return False, '', {}


        # Enable the service
        results = sb_utils.os.service.disable(svcname = self.__svcfmri)
        if results != True:
            msg = 'Unable to enable: %s' % self.__svcfmri
            self.logger.notice(self.module_name, 'Undo Failed: ' + msg)
            return False, '', {}


        # Make crontab entries
        results = sb_utils.acctmgt.users.del_cronjob( user = 'sys',
                            command = self.__cmd1, schedule = self.__entry1 )
        if results == False:
            msg = 'Unable to revert sys crontab'
            self.logger.notice(self.module_name, 'Undo Failed: ' + msg)
            return False, '', {}

        results = sb_utils.acctmgt.users.del_cronjob( user = 'sys',
                            command = self.__cmd2, schedule = self.__entry2 )
        if results == False:
            msg = 'Unable to revert sys crontab'
            self.logger.notice(self.module_name, 'Undo Failed: ' + msg)
            return False, '', {}

        return True, '', {}

if __name__ == '__main__':
    test = EnableSysstat()
    
