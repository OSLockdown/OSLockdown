#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Device Files - /dev -- Collect permissions and information on files
###############################################################################

import sha
import os
import libxml2
import sys

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.filesystem.fingerprint


def collect(infoNode):

    if sb_utils.os.info.is_solaris() == True:
        thedirs = ['/usr/bin', '/usr/sfw/bin', '/usr/local/bin' ]
    else:
        thedirs = ['/bin', '/usr/bin', '/usr/local/bin' ]

    for captureDir in thedirs:
        targetDir = []
        targetDir.append(captureDir)
        fileslist = infoNode.newChild(None, "files", None)
        fileslist.setProp("path", captureDir )
        results, fingerprint = sb_utils.filesystem.fingerprint.perform(start_dirs=targetDir, xmlnode=fileslist)
        fileslist.setProp("fingerprint", fingerprint )
