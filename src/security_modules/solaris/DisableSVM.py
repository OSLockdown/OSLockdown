#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#


import sys
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger

import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.solaris


class DisableSVM:

    def __init__(self):

        self.module_name = 'DisableSVM'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

        #
        # Identify the service and package name here:
        #
        self.__svcname = [ 'svc:/system/metainit:default',
                           'svc:/system/device/mpxio-upgrade:default',
                           'svc:/system/mdmonitor:default' ]

        self.__svcdesc = 'SVM initialization, multipath upgrade, and monitor services'
        self.__pkgname = 'SUNWmdr'


    ##########################################################################
    def do_metastat(self):
        
        cmd = "/usr/sbin/metastat"
        if not os.path.isfile(cmd):
            return

        results = tcs_utils.tcs_run_cmd(cmd, True) 
        if results[0] == 0:
            barline = ""
            for ix in range(0, 50): 
                barline += '#'
            self.logger.warn(self.module_name, barline)

            msg = "/usr/sbin/metastat reports that there are metadevice " \
                  "state database(s) present. Disable Solaris Volume Manager "\
                  "services with caution."
            self.logger.warn(self.module_name, msg)
            self.logger.warn(self.module_name, barline)

        else:
            msg = "/usr/sbin/metastat reports no metadevice " \
                  "state database(s) present. "
            self.logger.debug(self.module_name, msg)

        del msg
        del results

        return

    ##########################################################################
    def using_metadevice(self):
        
        try:
            infile = open('/etc/mnttab', 'r')
        except OSError, err:
            msg = "Unable to open /etc/mnttab: %s" % err
            return True

        found_one = False
        for line in infile.readlines():
            if line.startswith('/dev/md/'):
                fields = line.split('\t')
                msg = "%s is mounted on SVM metadevice %s" % (fields[1], fields[0])
                self.logger.warn(self.module_name, msg)
                found_one = True
        
        infile.close()
     
        if found_one == True:
            return True
        else: 
            return False


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): SVM services unavailable" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        if sb_utils.os.software.is_installed(pkgname=self.__pkgname) != True:
            msg = "%s (%s) package is not installed" % (self.__svcdesc, self.__pkgname)
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        self.do_metastat()

        fail_flag = False
        for chksvc in self.__svcname:
            results = sb_utils.os.service.is_enabled(svcname=chksvc)
            if results == True:
                msg = "svcprop reports %s is on" % chksvc
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                fail_flag = True

        if fail_flag == True:
            return 'Fail', msg
      

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        results, reason = self.scan(option)
        if results == 'Pass':
            return 0, ''

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): SVM services unavailable" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        action_record = []
        if sb_utils.os.software.is_installed(pkgname=self.__pkgname) != True:
            msg = "%s (%s) package is not installed" % (self.__svcdesc, self.__pkgname)
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''

        if self.using_metadevice() == True:
            msg = "There are mounted filesystems on SVM metadevices; this " \
              "module will NOT perform an apply."
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for chksvc in self.__svcname:
            results = sb_utils.os.service.is_enabled(svcname=chksvc)
            if results == True:
                action_record.append("on|%s\n" % chksvc) 

                results = sb_utils.os.service.disable(svcname=chksvc)
                if results != True:
                    msg = 'Failed to disable %s' % chksvc
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    msg = '%s (%s) disabled' % (self.__svcdesc, chksvc)
                    self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, ''.join(action_record) 

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if sb_utils.os.software.is_installed(pkgname=self.__pkgname) != True:
            msg = "%s (%s) package is not installed" % (self.__svcdesc, self.__pkgname)
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return 0

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Non-global Solaris zone (%s): SVM services unavailable" % (zonename)
            self.logger.notice(self.module_name, 'Scan: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        if change_record == None:
            msg = 'No change record provided; unable to perform undo.'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        for chksvc in change_record.split('\n'):
            if chksvc == "":
                continue
            fields = chksvc.split('|')
            if len(fields) != 2:
                msg = "Malformed change record: \"%s\"" % chksvc
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                continue
            if fields[0] == 'on':
                results = sb_utils.os.service.enable(svcname=fields[1])
                if results != True:
                    msg = 'Failed to enable %s' % fields[1]
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    msg = '%s (%s) enabled' % (self.__svcdesc, fields[1])
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return 1

