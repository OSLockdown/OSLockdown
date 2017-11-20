#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Software packages and patches
#
###############################################################################

import sha
import os
import libxml2
import sys

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.os.info

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()


MODULE_NAME = "Baseline"
MODULE_REV  = "$Rev: 10108$".strip('$')

def collect(infoNode):
    logger.log_debug(MODULE_NAME, "Installed Software module (%s)" % MODULE_REV)
    logger.log_info(MODULE_NAME, "Inventorying installed software and packages")

    tt = infoNode.newChild(None, "subSection", None)
    tt.setProp("name", "Packages" )
    packageNode = tt.newChild(None, "packages", None)

    xx = infoNode.newChild(None, "subSection", None)
    xx.setProp("name", "Patches" )
    patchesNode = xx.newChild(None, "patches", None)

    sha1Patches = sha.new()
    sha1Packages = sha.new()

    sha1Packages.update('')
    sha1Patches.update('')

    if sb_utils.os.info.is_solaris() == True:
        import Software.Inventory_Solaris
        Software.Inventory_Solaris.collect(packageNode, patchesNode, sha1Packages, sha1Patches)    
    else:
        import Software.Inventory_Linux
        Software.Inventory_Linux.collect(packageNode, sha1Packages)    

        # The 'patches' element is only applicable to Solaris sytems
        patchesNode.setProp("fingerprint", "xx")

