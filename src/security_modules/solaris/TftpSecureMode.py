#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import shutil
import re

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service

#
class TftpSecureMode:
    """
    Set TFTP into Secure mode (-s)
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'TftpSecureMode'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0



    ##########################################################################
    def scan(self, option=None):


        boot_pat = re.compile('-s /tftpboot') 

        # Is TFTP server package installed?
        if sb_utils.os.software.is_installed(pkgname='SUNWtftp') != True:
            msg = "TFTP Server (SUNWtftp) package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        prop = sb_utils.os.service.getprop(svcname='tftp', 
                                                    property='inetd_start/exec')
        if prop != None:
            prop = prop.replace('\\', '')
            if not boot_pat.search(prop):
                msg = "Tftp service 'inetd_start/exec' property (%s) does not "\
                      "contain '-s /tftpboot'" % prop
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg


        self.logger.debug(self.module_name, 'Checking /etc/inet/inetd.conf')

        try:
            infile = open('/etc/inet/inetd.conf', 'r')
        except IOError, err: 
            msg = "Unable to read /etc/inet/inetd.conf: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        pattern = re.compile('^(#t|t)ftp\s+.*/usr/sbin/in.tftpd')
        found_it = False
        is_disabled = False
        for line_nr, line in enumerate(infile.readlines()):
            if pattern.search(line):
                msg = "Found 'tftp' in /etc/inet/inetd.conf, line %d" % line_nr
                self.logger.debug(self.module_name, 'Scan Failed: ' + msg)
                options = line.split('\t')[-1]
                if not boot_pat.search(options):
                    if line.split('\t')[0][0] == '#':
                        is_disabled = True 
                    found_it = True
                    break

        infile.close()
        
        if found_it == False:
            return 'Pass', ''

        if is_disabled == False:
            msg = "Tftp is enabled and a secure directory (-s) is NOT specified"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        msg = "Tftp is disabled and a secure directory (-s) is NOT specified"
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
        return 'Fail', msg
           


    ##########################################################################
    def apply(self, option=None):

        results, reason = self.scan(option)
        if results == 'Pass':
            return 0, ''

        change_record = ''
        # Is TFTP server package installed?
        if sb_utils.os.software.is_installed(pkgname='SUNWtftp') != True:
            msg = "TFTP Server (SUNWtftp) package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''

        boot_pat = re.compile('-s /tftpboot') 
        prop = sb_utils.os.service.getprop(svcname='tftp',
                                                    property='inetd_start/exec')
        if prop != None:
            prop = prop.replace('\\', '')
            if not boot_pat.search(prop):
                args = "/usr/sbin/in.tftpd -s /tftpboot"
                cmd = """/usr/sbin/inetadm -m tftp exec="%s" """ % args
                results = tcs_utils.tcs_run_cmd(cmd, True)  
                if results[0] != 0:
                    msg = "Unable to execute: %s (%s)" % (cmd, results[2])
                    self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
                    return 0, ''
                else:
                    change_record = '|' + prop
                    msg = "Successfully executed: %s" % cmd
                    self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                    return 1, change_record


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

        pattern  = re.compile('^(#t|t)ftp\s+.*/usr/sbin/in.tftpd')
        for line_nr, line in enumerate(infile.readlines()):
            if pattern.search(line):
                msg = "'tftp' disabled in /etc/inet/inetd.conf, line %d" % line_nr
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                options = line.split('\t')[-1]
                if not boot_pat.search(options):
                    newline = '\t'.join(line.split('\t')[:-1]) + '\tin.tftpd -s /tftpboot'
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

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record[0] == '|':
            cmd = """/usr/sbin/inetadm -m tftp exec="%s" """ % change_record[1:]
            results = tcs_utils.tcs_run_cmd(cmd, True)
            if results[0] != 0:
                msg = "Unable to execute: %s (%s)" % (cmd, results[2])
                self.logger.notice(self.module_name, 'Undo Failed: ' + msg)
                return 0
            else:
                msg = "Successfully executed: %s" % cmd
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
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

        pattern = re.compile('^(#t|t)ftp\s+.*/usr/sbin/in.tftpd')
        for line_nr, line in enumerate(infile.readlines()):
            if pattern.search(line):
                msg = "'Tftp' configuration restored in /etc/inet/inetd.conf, line %d" % line_nr
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

