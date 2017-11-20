#!/usr/bin/env python
#
# Copyright (c) 2008-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import sha

import  xml.sax.saxutils

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.file.fileperms

class AuditRulesSolaris:

    def __init__(self):
        self.module_name = "AuditRulesSolaris"

        self.__auditRulesFile = "/etc/security/audit_control"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, option):
        """Check input"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, optionDict=None):

        results =  sb_utils.os.software.is_installed(pkgname='SUNWcsr')
        if results != True:
            msg = "'SUNWcsr' package is not installed on the system"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        if optionDict == None or 'auditRules' not in optionDict:
            msg = "No audit rules provided"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        option = optionDict['auditRules']
        try:
            option = xml.sax.saxutils.unescape(option)
            if option[-1] != '\n':
                option = option + '\n'
        except UnicodeEncodeError, err:
            self.logger.error(self.module_name, 'Scan Error: ' + err)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, err))
            
        files2check = []
        files2check.append(self.__auditRulesFile)

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

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''

        # Run run a quick scan to determine if an apply is warranted
        option = xml.sax.saxutils.unescape(optionDict['auditRules'])
        if option[-1] != '\n':
            option = option + '\n'

        # The action record should just be the contents of the old file
        if not os.path.isfile(self.__auditRulesFile):
            action_record = 'empty'
        else:
            try:
                inFile = open(self.__auditRulesFile, 'r')
                action_record = ''.join(inFile.readlines())
                inFile.close()
            except IOError, err:
                msg = "Unable to read %s : %s" % (self.__auditRulesFile, str(err))
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Write "option" value to audit rules file
        msg = "Writing new audit rules to %s ..." % self.__auditRulesFile
        self.logger.debug(self.module_name, msg)
        try:
            outFile = open(self.__auditRulesFile, 'w')
            outFile.write(option)
            outFile.close() 
        except (IOError, OSError), err:
            msg = "Unable to update %s : %s" % (self.__auditRulesFile, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Set Discretionary Access Controls
        msg = "Setting ownership to root:sys and mode to 0640 on %s" % self.__auditRulesFile
        self.logger.info(self.module_name, msg)
        changes_to_make = {'owner':'root',
                            'group':'root',
                            'dacs': 0640}
        ignore_changes = sb_utils.file.fileperms.change_file_attributes( self.__auditRulesFile, changes_to_make)

        msg = "Audit rules file (%s) installed." % (self.__auditRulesFile)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record == 'empty':
            change_record = ''

        # Write "change_record" value to audit rules file
        msg = "Restoring audit rules file %s ..." % self.__auditRulesFile
        self.logger.debug(self.module_name, msg)
        try:
            outFile = open(self.__auditRulesFile, 'w')
            outFile.write(change_record)
            outFile.close() 
        except (IOError, OSError), err:
            msg = "Unable to restore %s : %s" % (self.__auditRulesFile, str(err))
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Set Discretionary Access Controls
        msg = "Setting ownership to root:sys and mode to 0640 on %s" % self.__auditRulesFile
        self.logger.info(self.module_name, msg)
        changes_to_make = {'owner':'root',
                            'group':'root',
                            'dacs': 0640}
        ignore_changes = sb_utils.file.fileperms.change_file_attributes( self.__auditRulesFile, changes_to_make)
        msg = '%s file restored.' % self.__auditRulesFile 
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
