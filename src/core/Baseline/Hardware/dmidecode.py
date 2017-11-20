#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# DMI/SMBIOS Table Information
###############################################################################

import sha
import os
import libxml2
import sys

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.hardware
import sb_utils.misc.tcs_utils

def collect(infoNode):

    report = infoNode.newChild(None, "content", None)
    mydigest = sha.new()
    if sb_utils.hardware.is_xen_paravirt_domu() == True:
        mydigest.update('\nInformation not available\n')
        report.addContent('\nInformation not available\n')
    elif os.path.isfile('/usr/sbin/dmidecode'):
        report.addContent('\n')
        mydigest.update('\n')
        cmd = "/usr/sbin/dmidecode"
        results = sb_utils.misc.tcs_utils.tcs_run_cmd(cmd, True) 
        if results[0] == 0:
            scrubbed_data = unicode(''.join(results[1]), 'ascii', errors='ignore')
        else:
            scrubbed_data = unicode(''.join(results[2]), 'ascii', errors='ignore')

        mydigest.update(scrubbed_data)
        report.addContent(scrubbed_data)

    else:
        mydigest.update('\nInformation not available\n')
        report.addContent('\nInformation not available\n')

    report.setProp("fingerprint", mydigest.hexdigest() )
