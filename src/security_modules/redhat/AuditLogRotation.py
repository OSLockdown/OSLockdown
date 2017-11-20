#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.SELinux

class AuditLogRotation:
    """
    Rotate audit logs daily
    """
    ##########################################################################
    def __init__(self):
        """Constructor"""
        self.module_name = "AuditLogRotation"

        self.__target_file = '/etc/logrotate.d/audit'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """Verify option input"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):
        """
        Scan system to see if /etc/logrotate.d/audit is 
        rotating audit logs daily
        """

        results =  sb_utils.os.software.is_installed(pkgname='logrotate')
        if results != True:
            msg = "logrotate is not installed on the system; you should install"\
                  "this package."
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if not os.path.isfile(self.__target_file):
            msg = "%s does not exist" % (self.__target_file)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Checking %s for daily rotation" % self.__target_file
        self.logger.info(self.module_name, msg)

        daily_pattern = re.compile('daily')
        audit_pattern = re.compile('audit.log')
        lines = in_obj.readlines()
        in_obj.close()

        audit_found = False
        daily_found = False
        for line in lines:
            # Skip commented lines
            if line.lstrip().startswith('#'):
                continue
            if audit_pattern.search(line):
                audit_found = True
            if daily_pattern.search(line):
                daily_found = True

        if audit_found and daily_found:
            return 'Pass', ''

        msg = "%s not configured correctly." % self.__target_file
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
        return 'Fail', msg


    ##########################################################################
    def apply(self, option=None):
        """Create and replace the audit configuration for logrotate."""

        
        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''
        
        action_record = ''
        

        new_lines = """/var/log/audit/audit.log {                                                                                        
    daily                                                                                                                                
    rotate 14                                                                                                                            
    compress                                                                                                                             
    notifempty                                                                                                                           
    missingok                                                                                                                            
    postrotate                                                                                                                           
    /sbin/service auditd restart 1>/dev/null 2>&1 || true                                                                                
    endscript                                                                                                                            
}                                                                                                                                        
""" 
        if not os.path.isfile(self.__target_file):

            # Create logrotate audit file if missing
            action_record = "empty"
            try:                                                                                                                             
                out_obj = open(self.__target_file, 'w')                                                                             
                out_obj.write(new_lines)
                out_obj.close() 
            except Exception, err:                                                                                                           
                msg = "Unable to create temporary file (%s)." % str(err)                                                                     
                self.logger.error(self.module_name, 'Apply Error: ' + msg)                                                                 
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))  


        else:

            # If file exists, create a temporary one and then generate a 
            # diff record to be used to restore it during an undo
            tcs_utils.protect_file(self.__target_file)

            newfile = self.__target_file + '.new'
            oldfile = self.__target_file

            try:
                out_obj = open(newfile, 'w')
                out_obj.write(new_lines)
                out_obj.close() 
            except IOError, err:
                msg = "Unable to create temporary file: %s" % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            action_record = tcs_utils.generate_diff_record(newfile, oldfile)

            try:
                shutil.copymode(oldfile, newfile)
                shutil.copy2(newfile, oldfile)
                sb_utils.SELinux.restoreSecurityContext(newfile)
                os.unlink(newfile)
            except (OSError, IOError), err:
                msg = "Unable to replace %s with new version: %s" % (newfile, str(err))
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = '%s configuration file created' % self.__target_file
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        # Remove file if it did not exist before the apply
        if change_record == 'empty':
            if not os.path.isfile(self.__target_file):
                msg = "Was going to remove %s but it does not exist; undo "\
                      "not necessary." % self.__target_file
                self.logger.notice(self.module_name, msg)

            else:

                try:
                    os.unlink(self.__target_file)  
                except OSError, err:
                    msg = "Unable to remove %s: %s" % (self.__target_file, str(err))
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            return 1

        # Restore file to what it was before the apply
        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = '/etc/logrotate.d/audit configuration file reset'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

