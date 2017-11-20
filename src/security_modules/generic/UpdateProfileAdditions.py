#!/usr/bin/env python
#
# Copyright (c) 2013 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import tcs_utils
import sbProps
try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

def writeFile(fileBase, fileList):
    fileName = fileBase + ".profile"
    if not fileList:
        return True, 'No Profile additions for %s' % fileBase

    try:
        open(fileName, "w").write(fileList)
        msg = "wrote %s" % fileName
        logger.log_debug('UpdateProfileAdditions.writeFile', msg)
	if fileBase in [ sbProps.EXCLUSION_DIRS, sbProps.INCLUSION_FSTYPES ]:
		import sb_utils.file.exclusion
		sb_utils.file.exclusion.exlist(refresh=True)
        elif fileBase in [ sbProps.SUID_WHITELIST, SGID_WHITELIST] :
		import sb_utils.file.whitelist
		sb_utils.file.whitelists.whlists(refresh=True)

    except Exception,err:
        raise tcs_utils.AbortProfile("Unable to write to '%s' - aborting Profile" % fileName)
        
    return True, "Wrote Profile additions to '%s' file." % os.path.basename(fileName)

def removeFile(fileBase):
    fileName = fileBase + ".profile"
    try:
        if os.path.exists(fileName):
            msg = "removed %s" % fileName
            logger.log_debug('UpdateProfileAdditions.removeFile', msg)
            os.unlink(fileName)
    except Exception,err:
        raise tcs_utils.AbortProfile("Unable to erase to '%s' - aborting Profile" % fileName)
        
    return True, "Removed '%s' file." % os.path.basename(fileName)
