#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# System Logging Configuration - syslog.conf, rsyslog.conf, and syslog-ng.conf
###############################################################################

import sha
import os
import libxml2
import sys

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.hardware
import sb_utils.os.info
import sb_utils.misc.tcs_utils

def collect(infoNode):

    report = infoNode.newChild(None, "content", None)
    mydigest = sha.new()

    if os.path.isfile('/etc/syslog.conf'):
        syslog_file = '/etc/syslog.conf'

    if os.path.isfile('/etc/rsyslog.conf'):
        syslog_file = '/etc/rsyslog.conf'

    if os.path.isfile('/etc/syslog-ng/syslog-ng.conf'):
        syslog_file = '/etc/syslog-ng/syslog-ng.conf'

    try:
        syslog_fd = open(syslog_file, 'r')
    except:
        report.addContent('Unable to retrieve syslog configuration.')
        mydigest.update('Unable to retrieve syslog configuration.')
        return
        
    report.addContent('\n# FILE: %s \n\n' % syslog_file)
    mydigest.update('\n# FILE: %s \n\n' % syslog_file)

    for line in syslog_fd.readlines():
        scrubbed_data = unicode(line, 'ascii', errors='ignore')
        report.addContent(scrubbed_data)
        mydigest.update(scrubbed_data)

    syslog_fd.close()
    report.setProp("fingerprint", mydigest.hexdigest() )
    return
