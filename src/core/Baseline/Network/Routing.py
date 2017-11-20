#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Collect Routing Information
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


def collect(infoNode):
    """ Routing Table """

    routing_report = infoNode.newChild(None, "content", None)

    mydigest = sha.new()
    if sb_utils.os.info.is_solaris() == True:
        pipe = os.popen('/bin/netstat -rn; /usr/bin/echo; /usr/sbin/routeadm -p', 'r')
    else:
        pipe = os.popen('/bin/netstat -rn', 'r')

    routing_report.addContent('\n')
    mydigest.update('\n')
    for line in pipe.readlines():
        scrubbed_line = unicode(line, 'ascii', errors='ignore')
        mydigest.update(scrubbed_line)
        routing_report.addContent(scrubbed_line)

    routing_report.setProp("fingerprint", mydigest.hexdigest())
    pipe.close()
