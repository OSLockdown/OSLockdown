#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import sha

import  xml.sax.saxutils

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.SELinux

class AuditRules:
    """
    Setup Audting to collect the right stuff
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "AuditRules"
        if os.path.isdir('/etc/audit'):
            self.__target_file = '/etc/audit/audit.rules'
        else:
            self.__target_file = '/etc/audit.rules'
        
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__content = ""


    ##########################################################################
    def validate_input(self, option):
        """Check input"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, optionDict=None):
        """Check to see if audit.rules file is correct"""

        results =  sb_utils.os.software.is_installed(pkgname='audit')
        if results != True:
            msg = "'audit' package is not installed on the system"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        if optionDict == None or not 'auditRules' in optionDict:
            msg = "No audit rules provided"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        try:
            option = xml.sax.saxutils.unescape(optionDict['auditRules'])
            if option[-1] != '\n':
                option = option + '\n'
        except UnicodeEncodeError, err:
            self.logger.error(self.module_name, 'Scan Error: ' + err)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, err))
            
        files2check = []
        files2check.append(self.__target_file)

        found = False
        for auditfile in files2check:
            msg = "Checking %s" % auditfile
            self.logger.info(self.module_name, msg)

            if not os.path.isfile(auditfile):
                msg = "%s is missing." % auditfile
                self.logger.info(self.module_name, msg)
                continue

            fingerprint = sha.new()
            try:
                in_obj = open(auditfile, 'r')
            except IOError:
                msg = 'Unable to read %s' % auditfile
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
            for line in in_obj.readlines():
                fingerprint.update(line)
            in_obj.close() 

    
            digest = sha.new()
            digest.update(str(option))
            
            #print auditfile, fingerprint.hexdigest(), digest.hexdigest()
            if digest.hexdigest() != fingerprint.hexdigest():
                msg = '%s do not match provided audit rules' % auditfile
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg
            else:
                found = True

        if found == False: 
            return 'Fail', ''
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict=None):
        """Create and replace the audit rules configuration."""

        action_record = []
        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, action_record

        option = xml.sax.saxutils.unescape(optionDict['auditRules'])
        if option[-1] != '\n':
            option = option + '\n'

        if os.path.exists(self.__target_file):
            # Protect file
            tcs_utils.protect_file(self.__target_file)

            try:
                out_obj = open(self.__target_file + '.new', 'w')
            except IOError, err:
                msg = "Unable to create temporary file (%s)." % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            out_obj.write(option)
            out_obj.close()

            action_record.append(tcs_utils.generate_diff_record(self.__target_file + '.new', self.__target_file))

            try:
                shutil.copymode(self.__target_file, self.__target_file + '.new')
                shutil.copy2(self.__target_file + '.new', self.__target_file)
                sb_utils.SELinux.restoreSecurityContext(self.__target_file)


                os.unlink(self.__target_file + '.new')

            except (IOError, OSError), err:
                msg = "Unable to replace %s with new version: %s" % (self.__target_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            try:
                open(self.__target_file, 'w').write(option)
            except IOError, err:
                msg = "Unable to create new audit rules file : (%s)" % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            action_record = "EMPTY"
            msg = "Audit rules configuration file (%s) was empty." % (self.__target_file)
            self.logger.notice(self.module_name, msg)
            
        msg = "Audit rules configuration file (%s) installed." % (self.__target_file)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Restore file to what it was before the apply
        if change_record == "EMPTY":
            os.unlink(self.__target_file)
            msg = "Removing '%s'" % self.__target_file
        else:
            try:
                tcs_utils.apply_patch(change_record)
            except tcs_utils.ActionError, err:
                msg = "Unable to undo previous changes (%s)." % err 
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = 'audit.rules file restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

