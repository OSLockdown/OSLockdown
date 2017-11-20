#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
# Set Umask to 077 for GSS FTP Server
# Modify the /etc/xinetd.d/gssftp 
#

import sys
import os
import shutil

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.SELinux

#
class GssftpUmask:
    """
    Set umask to 077 for Ftp Server
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'GssftpUmask'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Check for rpm and file permissions"""
        if option != None:
            option = None


        results =  sb_utils.os.software.is_installed(pkgname='krb5-workstation')
        if results != True:
            msg = "'krb5-workstation' package (/usr/kerberos/sbin/ftpd) not installed"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        
        if not os.path.isfile('/etc/xinetd.d/gssftp'):
            msg = "'/etc/xinetd.d/gssftp' does not exist"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        try:
            myfile = open('/etc/xinetd.d/gssftp', 'r')
        except IOError, err: 
            msg = "Unable to open /etc/xinetd.d/gssftp: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Looking for 'server_args' to have the option '-u 077' in  /etc/xinetd.d/gssftp"
        self.logger.info(self.module_name, msg)

        foundit = False 
        for line in myfile.xreadlines():
            line = line.strip('\n')
            line = line.strip(' ')
            line = line.strip('\t')
            if '=' in line:
                line = line.strip('\t')
                param, thevalue = line.split('=')
                param    = param.strip(' ')
                param    = param.strip('\t')
                thevalue = thevalue.strip(' ')
                if param == 'server_args':
                    if '-u 077' in thevalue:
                        foundit = True
                        break

        myfile.close()

        if foundit != True:
            msg = "Could not find -u 077 in /etc/xinetd.d/gssftp"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''
 
    
    ##########################################################################
    def apply(self, option=None):
        """Set GSS Ftp umask to 077"""

        change_record = ''
        try:
            result, reason = self.scan()
            if result == 'Pass':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        try:
            shutil.copy2('/etc/xinetd.d/gssftp', '/tmp/.gssftp.new')
            out_obj = open('/etc/xinetd.d/gssftp', 'w')
            sb_utils.SELinux.restoreSecurityContext('/etc/xinetd.d/gssftp')
            in_obj  = open('/tmp/.gssftp.new', 'r')
        except (OSError, IOError), err:
            msg = "Unable to create temp file: %s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        foundit = False 
        for line in in_obj.xreadlines():
            if line.startswith('#'):
                continue
            line = line.strip('\n')
            tline = line.strip('\t')
            tline = tline.strip(' ')
            if not tline.startswith('server_args'):
                if line.endswith('}') and foundit == False:
                    out_obj.write('\tserver_args     = -l -a -u 077\n')
                out_obj.write(line + '\n')
            else:
                param, thevalue = tline.split('=')
                param    = param.strip(' ')
                param    = param.strip('\t')
                thevalue = thevalue.strip(' ')
                if '-u' not in thevalue:
                    foundit = True
                    change_record = thevalue
                    out_obj.write(line + ' -u 077\n')
                else:
                    brokenout = thevalue.split()
                    idx = brokenout.index('-u')
                    try:
                        brokenout[idx+1] = '077'
                    except IndexError:
                        brokenout[idx] = '-u 077'
                    out_obj.write('\t' + param + '     = ')
                    for things in brokenout:
                        out_obj.write(things + ' ')
                    out_obj.write('\n')
                    foundit = True
                    change_record = thevalue
   
        out_obj.close()
        in_obj.close()
        try:
            os.unlink('/tmp/.gssftp.new')
        except (OSError, IOError), err:
            msg = "Unable to remove /tmp/.gssftp.new: %s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
        
        return 1, change_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        if change_record == None:
            msg = 'No change record provided'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0
     
        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0

        try:
            shutil.copy2('/etc/xinetd.d/gssftp', '/tmp/.gssftp.new')
            out_obj = open('/etc/xinetd.d/gssftp', 'w')
            sb_utils.SELinux.restoreSecurityContext('/etc/xinetd.d/gssftp')
            in_obj  = open('/tmp/.gssftp.new', 'r')
        except (OSError, IOError):
            msg = "Unable to create temp file"
            self.logger.error(self.module_name, 'Undo Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' %
                                              (self.module_name, msg))

        for line in in_obj.xreadlines():
            tline = line.strip()
            if tline.startswith('server_args'):
                out_obj.write('\tserver_args     = ' + change_record + '\n')
            else:
                out_obj.write(line)

        out_obj.close()
        in_obj.close()
        try:
            os.unlink('/tmp/.gssftp.new')
        except (OSError, IOError):
            msg = "Unable to remove /tmp/.gssftp.new: %s" % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
        
        return 1, ''


