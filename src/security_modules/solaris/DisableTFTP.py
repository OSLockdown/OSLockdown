#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module disables the TFTP service. It first looks to see
# if TFTP is registered with SMF, then it checks the 
# /etc/inet/inetd.conf file.
#


import sys
import re
import shutil
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service


class DisableTFTP:

    def __init__(self):
        self.module_name = 'DisableTFTP'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        # Is TFTP server package installed?
        if sb_utils.os.software.is_installed(pkgname='SUNWtftp') != True:
            msg = "TFTP Server (SUNWtftp) package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        if sb_utils.os.service.is_enabled(svcname='tftp') == True:
            msg = "TFTP service is enabled."
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg


        self.logger.debug(self.module_name, 'Checking /etc/inet/inetd.conf')

        try:
            infile = open('/etc/inet/inetd.conf', 'r')
        except IOError, err: 
            msg = "Unable to read /etc/inet/inetd.conf: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        pattern = re.compile('^tftp\s+.*/usr/sbin/in.tftpd')
        found_it = False
        for line_nr, line in enumerate(infile.readlines()):
            if pattern.search(line):
                msg = "'tftp' enabled in /etc/inet/inetd.conf, line %d" % line_nr
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                found_it = True
                break

        infile.close()
        
        if found_it == True:
            return 'Fail', 'Tftp is enabled'
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        results, reason = self.scan(option)
        if results == 'Pass':
            return 0, ''

        # Is TFTP server package installed?
        if sb_utils.os.software.is_installed(pkgname='SUNWtftp') != True:
            msg = "TFTP Server (SUNWtftp) package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''


        if sb_utils.os.service.is_enabled(svcname='tftp') == True:
            results = sb_utils.os.service.disable(svcname='tftp')
            if results == True:
                msg = "Apply Performed: TFTP service disabled"
                self.logger.notice(self.module_name, msg)
                return 1, 'services'
     
        change_record = ''
        newfile = '/etc/inet/inetd.conf.new'
        oldfile = '/etc/inet/inetd.conf'

        tcs_utils.protect_file(oldfile)

        try:
            outfile = open(newfile, 'w')
            infile  = open(oldfile, 'r')
        except IOError, err: 
            msg = str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        pattern = re.compile('^tftp\s+.*/usr/sbin/in.tftpd')
        for line_nr, line in enumerate(infile.readlines()):
            if pattern.search(line):
                msg = "'tftp' disabled in /etc/inet/inetd.conf, line %d" % line_nr
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                newline = '#' + line 
                change_record = line
            else:
                newline = line

            outfile.write(newline)

        infile.close()
        outfile.close()


        try:
            shutil.copymode(oldfile, newfile)
            shutil.copy2(newfile, oldfile)
            os.unlink(newfile)
        except OSError, err:
            msg = "Unable to replace %s with new version (%s)" % (newfile, str(err))
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1, change_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        # Is TFTP server package installed?
        if sb_utils.os.software.is_installed(pkgname='SUNWtftp') != True:
            msg = "TFTP Server (SUNWtftp) package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''

        if change_record == 'services':
            results = sb_utils.os.service.enable(svcname='tftp')
            if results == True:
                msg = "Undo Performed: TFTP service re-enabled"
                self.logger.notice(self.module_name, msg)
                return 1


        newfile = '/etc/inet/inetd.conf.new'
        oldfile = '/etc/inet/inetd.conf'

        tcs_utils.protect_file(oldfile)

        try:
            outfile = open(newfile, 'w')
            infile  = open(oldfile, 'r')
        except IOError, err:
            msg = str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        pattern = re.compile('^#tftp\s+.*/usr/sbin/in.tftpd')
        for line_nr, line in enumerate(infile.readlines()):
            if pattern.search(line):
                msg = "'tftp' re-enabled in /etc/inet/inetd.conf, line %d" % line_nr
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                newline = change_record
            else:
                newline = line

            outfile.write(newline)

        infile.close()
        outfile.close()

        try:
            shutil.copymode(oldfile, newfile)
            shutil.copy2(newfile, oldfile)
            os.unlink(newfile)
        except OSError, err:
            msg = "Unable to replace %s with new version (%s)" % (newfile, str(err))
            self.logger.info(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1
