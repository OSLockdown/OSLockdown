#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# List all PCI Devices
###############################################################################

import sha
import os
import libxml2
import sys

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.os.info
import sb_utils.os.solaris
import sb_utils.misc.tcs_utils

def collect(infoNode):

    report = infoNode.newChild(None, "content", None)
    mydigest = sha.new()

    if sb_utils.os.info.is_solaris() == True:
        if sb_utils.os.solaris.zonename() != 'global':
            mydigest.update('\nInformation not available in a non-global zone')
            report.addContent('\nInformation not available in a non-global zone')
            report.setProp("fingerprint", mydigest.hexdigest())
            return 
        else:
            cmd = "/usr/bin/perl /usr/share/oslockdown/tools/prtpci > /var/tmp/pciids"
            retval = os.system(cmd)
            report.addContent('\n')
            mydigest.update('\n')
            try:
                in_obj = open('/var/tmp/pciids', 'r')
                lines = ''.join(in_obj.readlines())
                scrubbed_data = unicode(lines, 'ascii', errors='ignore')
                in_obj.close()
                mydigest.update(scrubbed_data)
                report.addContent(scrubbed_data)
                os.unlink('/var/tmp/pciids')
            except Exception, err:
                pass

            report.setProp("fingerprint", mydigest.hexdigest())
            return

    ## Linux world
    else:
        cmd = "/sbin/lspci"
        if not os.path.isfile(cmd) or not os.path.isdir('/proc/bus/pci'):
            mydigest.update('\nInformation not available')
            report.addContent('\nInformation not available')
            report.setProp("fingerprint", mydigest.hexdigest())
            return 

        report.addContent('\n')
        mydigest.update('\n')
    
        results = sb_utils.misc.tcs_utils.tcs_run_cmd(cmd, True) 
        if results[0] == 0:
            scrubbed_data = unicode(''.join(results[1]), 'ascii', errors='ignore')
        else:
            scrubbed_data = unicode(''.join(results[2]), 'ascii', errors='ignore')
    
        mydigest.update(scrubbed_data)
        report.addContent(scrubbed_data)
        report.setProp("fingerprint", mydigest.hexdigest())
        return
