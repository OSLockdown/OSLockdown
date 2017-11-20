#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Audit Configuration
#
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

    if sb_utils.os.info.is_solaris() == True:
        msg = 'Configuration and Rules are combined in /etc/security/audit_control'
        report.addContent(msg)
        mydigest.update(msg)
        report.setProp("fingerprint", mydigest.hexdigest() )
        return

    if os.path.isdir('/etc/audit'):
        auditconf_file = '/etc/audit/auditd.conf'
    else:
        auditconf_file = '/etc/auditd.conf'

    try:
        ar_fd = open(auditconf_file, 'r')
    except:
        report.addContent('Unable to retrieve audit configuration')
        mydigest.update('Unable to retrieve audit configuration')
        return
        
    report.addContent('\n# FILE: %s \n\n' % auditconf_file)
    mydigest.update('\n# FILE: %s \n\n' % auditconf_file)

    for line in ar_fd.readlines():
        scrubbed_data = unicode(line, 'ascii', errors='ignore')
        report.addContent(scrubbed_data)
        mydigest.update(scrubbed_data)

    ar_fd.close()
    report.setProp("fingerprint", mydigest.hexdigest() )
    return
