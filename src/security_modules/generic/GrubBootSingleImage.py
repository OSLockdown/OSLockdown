#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Ensure that Grub only has a single boot definition.  If more than one are
# found, enforce that the default image is the only bootable image
#
#
##############################################################################

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.grub
import sb_utils.os.software

class GrubBootSingleImage:

    def __init__(self):
        self.module_name = "GrubBootSingleImage"
  
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
            messages['messages'].extend(self._grubHandler.readGrub())
            numDefs = self._grubHandler.numBootDefs()
            msg = "%s : found %d boot definitions" % (self.module_name, numDefs)
            if numDefs == 1:
                self.logger.info(self.module_name, msg)
                retval = True
            else:
                msg += ", expected only a single definition"
                self.logger.warning(self.module_name, msg )
                messages['messages'].append(msg)
                
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

        # Ok, we got to here, so we have more than one image.  
               
        messages = {}
        messages['messages'] = []

        bootDefault = self._grubHandler.getDefaultSection()
        changerec, msgs  = self._grubHandler.setSingleBootSection(bootDefault)

        msg = "Setting '%s' as the default boot image - others removed" % (bootDefault)
        self.logger.info(self.module_name, msg)
        
        # if the write fails it raises an action error, we trap it and reraise for documentation
        try:
            self._grubHandler.writeGrub()
        except Exception, err:
            raise    
        return True, str(changerec), messages

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
            messages['messages'].extend(self._grubHandler.readGrub())
            for section in changeDict['sectionNames']:
                self._grubHandler.restoreSectionLines(changeDict['sections'][section])
            
            msg = "Alternate boot definition lines restored"
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

