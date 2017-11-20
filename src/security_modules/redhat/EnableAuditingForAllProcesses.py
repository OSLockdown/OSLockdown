#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# For all 'kernel' options in the grub conf ensure that the 'audit=1' flag is
# also on that line, so that all processes are auditable, even those that are
# started prior to auditd on a boot.
# If there are more than one boot definition in the file, issue a warning and
# make the change to *all* of them.
#
#
##############################################################################

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.grub
import sb_utils.os.software

class EnableAuditingForAllProcesses:

    def __init__(self):
        self.module_name = "EnableAuditingForAllProcesses"
  
        self.logger = TCSLogger.TCSLogger.getInstance()
        self._grubHandler = None
        
    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []
        msg = ""
        self._grubHandler = sb_utils.os.grub.GrubHandler()
        retval = False
        try:
            self._grubHandler.readGrub()
            numDefs = self._grubHandler.numBootDefs()
            msg = "%s : found %d boot definitions" % (self.module_name, numDefs)
            if numDefs == 1:
                self.logger.info(self.module_name, msg)
            else:
                msg += ", expected only a single definition"
                self.logger.warning(self.module_name, msg )
                messages['messages'].append(msg)
                
            msgs = self._grubHandler.checkLines(None,"kernel","audit=1", reportMissing=True)
            if len(msgs) == 0:
                retval = True
                msg = "All boot definitions have 'audit=1' as a kernel boot argument"
            else:
                for msg in msgs:
                    self.logger.warning(self.module_name, msg )
                    messages['messages'].append(msg)
                msg = "One or more boot definitions do not have 'audit=1' as a kernel boot argument"
                
        except tcs_utils.OSNotApplicable,err:
            msg = "%s" % str(err)
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            raise
        except tcs_utils.ScanNotApplicable,err:
            msg = "%s" % str(err)
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
            raise
            
        return retval, msg, messages

    ##########################################################################
    def apply(self, option=None):

        
        (result, reason, messages) = self.scan()           
        if result == True:
            return False, reason, messages

        # Ok, we got to here, so we need to add it.  
        messages['messages'] = []
        numDefs = self._grubHandler.numBootDefs()
        if numDefs > 1:
            msg = "%s : found %d boot definitions, expected only a single definition" % (self.module_name, numDefs)
            messages['messages'].append(msg)

        changeRec, msgs = self._grubHandler.addToLines(None,"kernel","audit=1")
        messages['messages'].extend(msgs)
        if changeRec == {}:
            for sect in changeRec.keys():
                msg = "Adding 'kernel=1' to kernel args for image '%s'" % sect
                self.logger.info(self.module_name, msg)

        # if the write fails it raises an action error, we trap it and reraise for documentation
        try:
            self._grubHandler.writeGrub()
        except Exception, err:
            raise    
        return True, str(changeRec), messages

    ##########################################################################
    def undo(self, change_record=None):


        retval = False
        msg = ""
        messages = {}
        messages['messages'] = []
        if not change_record :
            msg = 'Unable to undo without valid change record'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return False, msg, {'messages': ["Error: %s" % msg]}
        changeDict = tcs_utils.string_to_dictionary(change_record)    

        self._grubHandler = sb_utils.os.grub.GrubHandler()
        try:
            self._grubHandler.readGrub()
            numDefs = self._grubHandler.numBootDefs()
            if numDefs > 1:
                msg = "%s : found %d boot definitions, expected only a single definition" % (self.module_name, numDefs)
                messages['messages'].append(msg)
                self.logger.warning(self.module_name, msg )

            for section in changeDict.keys():
                for tag, data in changeDict[section].items():
                    rec, msgs = self._grubHandler.removeFromLines(section, tag, data)
            
            messages['messages'].extend(msgs)
            msg = "Kernel boot lines restored"
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            # writeGrub raises an exception on error
            self._grubHandler.writeGrub()
            retval = True
        except tcs_utils.OSNotApplicable,err:
            msg = "%s" % str(err)
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
        except tcs_utils.ScanNotApplicable,err:
            msg = "%s" % str(err)
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)
        except Exception, err:
            raise   
                        
        return retval, msg, messages

