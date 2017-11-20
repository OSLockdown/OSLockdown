#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#  Disable HP Printer Services (hplip)
#

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service

class DisableHPServices:

    def __init__(self):

        self.module_name = 'DisableHPServices'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

        # Couple of notes here - hplip appears to be the package name across the board,
        # but the SERVICE may or may not exist, depending on the actual OS distro and perhaps
        # the version os hplip - more recent OS's have the package but not the service.
        # Based on discussions with Greg, we'll do the following (NOTE : linux ONLY)
        #
        # SCAN - no package = N/A
        # SCAN - package, service disabled = PASS
        # SCAN - package, and service enabled= FAIL
        # SCAN - package, and no service = FAIL

        # APPLY - no package = Not required
        # APPLY - package, and service disabled = Not required
        # APPLY - package, and service enabled = disable the service, return APPLIED
        # APPLY - package, and no service = MANUAL ACTION REQUIRED
        
        self._pkgname = 'hplip'
        self._svcname = 'hplip'
        self._svcdesc = 'HP Printer Services'

    def serviceExists(self, svcname):
        """
        See if the service even exists, needed because the hplip software has migrated
        away from a service (which we could disable) to simply a package that should be removed
        So process the chkconfig --list hplip command looking for any error string (field 2)
        """

        cmd = "/sbin/chkconfig --list %s" % svcname
        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[2] != '':
            return False
        else: return True


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

        

    ##########################################################################
    def scan(self, option=None):


        if sb_utils.os.info.is_solaris() == True:
            msg = "'%s' service is not part of the standard Solaris "\
                  "distribution." % self._svcname
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        results =  sb_utils.os.software.is_installed(pkgname=self._pkgname)
        if results != True:
            msg = "'%s' is not installed on the system" % self._pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        msg = "'%s' package is installed." % self._pkgname
        self.logger.debug(self.module_name, msg)

        results = sb_utils.os.service.is_enabled(svcname=self._svcname)
        if results == True:
            msg = "'%s' service is on" % self._svcname
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        elif not self.serviceExists(self._svcname):
            msg = "'%s' service does not exist!  Manual action required to fix." % self._svcname
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        if results == None:
            msg = "'%s' does not appear to be a service in %s %s - nothing to disable, adminstrator should remove '%s' unless this package is required." % (self._svcname, 
                       sb_utils.os.info.getDistroName(), str(sb_utils.os.info.getDistroVersion()) , self._pkgname)
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        action_record = ''
        results = sb_utils.os.service.is_enabled(svcname=self._svcname)
        if not self.serviceExists(self._svcname):
            msg = "'%s' service does not exist!  Manual action required to remove this package" % self._svcname
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        if results == None:
            msg = "Unable to determine status of the '%s' service" % self._svcname
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if results == False:
            action_record = 'off'
        else:
            action_record = 'on'

        results = sb_utils.os.service.disable(svcname=self._svcname)
        if results != True:
            msg = 'Unable to disable: %s' % self._svcname
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            return 0, msg

        msg = '%s service is disabled.' % self._svcname
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        try:
            result, reason = self.scan()
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            return 0

        if sb_utils.os.info.is_solaris() == True:
            msg = "%s service is not part of the standard Solaris distribution." % self._svcname
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        if change_record not in ['off', 'on']:
            msg = "Skipping Undo: Uknown change record in state file: '%s'" % change_record
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0
             
        if change_record == 'on':
            results = sb_utils.os.service.enable(svcname = self._svcname )

        if change_record == 'off':
            results = sb_utils.os.service.disable(svcname = self._svcname )

        if results != True:
            msg = "Unable to set %s (%s) service to '%s' " % (self._svcdesc, self._svcname)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        msg = "%s (%s) service set to '%s' " % (self._svcdesc, self._svcname, change_record)
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1

