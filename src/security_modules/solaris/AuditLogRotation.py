#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module makes an entry in root's crontab to run
# the 'audit -n' every day at 00:00
#
# Specifcally, it will add the followign to root's crontab:
#
# 0 0 * * * /usr/sbin/audit -n
#
# This module can be tested by using the crontab(1) command
# crontab -l to list
# crontab -e to edit

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.acctmgt.users

class AuditLogRotation:

    def __init__(self):

        self.module_name = "AuditLogRotation"
        self.__target_file = '/etc/logrotate.d/audit'
        self.logger = TCSLogger.TCSLogger.getInstance()


        # Elements of the cronjob entry:
        self.__cronuser  = 'root'
        self.__croncmd   = '/usr/sbin/audit -n'

        self.__cronsched = {    'min': '0',
                               'hour': '0',
                       'day_of_month': '*',
                              'month': '*',
                        'day_of_week': '*'   }


    ##########################################################################
    def validate_input(self, option):
        """Verify option input"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        results = sb_utils.acctmgt.users.is_cronjob( user = self.__cronuser,
                                                  command = self.__croncmd,
                                                 schedule = self.__cronsched )

        if results == False:
            msg = "%s crontab does not have: %s %s" % (self.__cronuser,
                                                       self.__cronsched,
                                                       self.__croncmd )
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', '/usr/sbin/audit -n entry not found'

        msg = '/usr/sbin/audit -n found in root crontab'
#        self.logger.notice(self.module_name, 'Scan Passed: ' + msg)
        return 'Pass', msg
        

    ##########################################################################
    def apply(self, option=None):
        """Create and replace the audit configuration for logrotate."""

        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''

        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, err

        results = sb_utils.acctmgt.users.cronjob( user = self.__cronuser,
                                                  command = self.__croncmd,
                                                 schedule = self.__cronsched )

        if results != True:
            msg = "Unable to add %s crontab entry to execute %s" % \
                        (self.__cronuser, self.__croncmd)
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return 0, ''
            

        msg = "Added %s crontab entry to execute %s" % \
                   (self.__cronuser, self.__croncmd)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, 'enabled'


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record or change_record != 'enabled':
            msg = "unable to undo without valid change record"
            self.logger.error(self.module_name,'Undo Error: ' + msg)
            return 0,''
            
        results = sb_utils.acctmgt.users.del_cronjob( user = self.__cronuser,
                                                  command = self.__croncmd,
                                                 schedule = self.__cronsched )

        if results != True:
            msg = "Unable to remove %s crontab entry %s which executes %s" % \
                        (self.__cronuser, self.__croncmd)
            self.logger.notice(self.module_name, 'Undo Failed: ' + msg)
            return 0, ''


        msg = "Removed %s crontab entry which executes %s" % \
                   (self.__cronuser, self.__croncmd)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1
