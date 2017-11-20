#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Collect Firewall Information (iptables)
###############################################################################

import sha
import os
import libxml2
import sys

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.os.info


def collect(infoNode):
    """ Iptables Firewall Configuration """

    iptables_report = infoNode.newChild(None, "content", None)

    mydigest = sha.new()
    if sb_utils.os.info.is_solaris() == True:
        if sb_utils.os.solaris.zonename() == 'global':
            pipe = os.popen('/usr/sbin/ipfstat -io 2>&1', 'r')
        else:
            line = '\nInformation not available in a non-global zone'
            mydigest.update(line)
            iptables_report.addContent(line)
            return True
    else:
        if sb_utils.os.info.is_LikeSUSE() == True:
            pipe = os.popen('/usr/sbin/iptables --list', 'r')
        else:
            pipe = os.popen('/sbin/iptables --list', 'r')

    # Ensure lines are ASCII Characters for XML reasons
    iptables_report.addContent('\n')
    mydigest.update('\n')
    for line in pipe.readlines():
        scrubbed_line = unicode(line, 'ascii', errors='ignore')
        mydigest.update(scrubbed_line)
        iptables_report.addContent(scrubbed_line)

    iptables_report.setProp("fingerprint", mydigest.hexdigest())
    pipe.close()

    return True
