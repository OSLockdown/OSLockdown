#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Identify Open TCP Ports
#
###############################################################################

import sha
import os
import libxml2
import sys
import socket

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.os.info
import sb_utils.misc.tcs_utils
import sb_utils.SELinux

SELinuxEnabled = sb_utils.SELinux.SELINUX_ENABLED

def collect(infoNode):

    if sb_utils.os.info.is_solaris() == True:
        _solaris(infoNode)
        return

    report = infoNode.newChild(None, "objects", None)
    mydigest = sha.new()

    if SELinuxEnabled == True:
        cmd = "/bin/netstat -tlnpZ"
    else:
        cmd = "/bin/netstat -tlnp"

    results = sb_utils.misc.tcs_utils.tcs_run_cmd(cmd, True)
    if results[0] != 0:
        mydigest.update('\n')
        report.setProp("fingerprint", mydigest.hexdigest())
        return

    report.setProp("numAttrs", "6")
    report.setProp("attr1", "TCP Port")
    report.setProp("attr2", "Listening Address")
    report.setProp("attr3", "Program")
    report.setProp("attr4", "SELinux Context")
    report.setProp("attr5", "IP Version")
    report.setProp("attr6", "IANA Well-Known Name")

    for line in results[1].split('\n'):
        if not line.startswith('tcp'):
            continue

        fields = line.split()
        tcpPort = fields[3].split(':')[-1]
        ifBound = fields[3].split(':')[0:-1]

        if fields[6].count('/') > 0:
            programName = fields[6].split('/')[1]
        else:
            programName = fields[6]

        if SELinuxEnabled == True:
            seContext = fields[-1]
        else:
            seContext = "-"

        try:
            svcName = socket.getservbyport(int(tcpPort), 'tcp')
        except:
            svcName = '-'

        # Grab IP Version
        ipVersion = "IPv4"
        # Handle IPv6 Addresses
        if len(ifBound) > 1:
            ifBound = fields[3].split(':')
            if len(ifBound) > 4:
                ifBound = "%s:%s:%s:%s" % (ifBound[0], ifBound[1], ifBound[2], ifBound[3])
                ipVersion = "IPv6"
            else:
                ifBound = "%s:%s:%s" % (ifBound[0], ifBound[1], ifBound[2])
        else:
            ifBound = ''.join(ifBound)

        portObject = report.newChild(None, "object", None)
        portObject.setProp("key", fields[3])
        portObject.setProp("attr1", tcpPort)
        portObject.setProp("attr2", ifBound)
        portObject.setProp("attr3", programName)
        portObject.setProp("attr4", seContext)
        portObject.setProp("attr5", ipVersion)
        portObject.setProp("attr6", svcName)

        mydigest.update(fields[3])
        mydigest.update(tcpPort)
        mydigest.update(ifBound)
        mydigest.update(programName)
        mydigest.update(seContext)
        mydigest.update(ipVersion)

    report.setProp("fingerprint", mydigest.hexdigest())
    return

##############################################################################
def _solaris(infoNode):
    """
    Solaris netstat results
    """
    report = infoNode.newChild(None, "objects", None)
    mydigest = sha.new()

    if socket.has_ipv6 == True:
        cmd = "/usr/bin/netstat -na -P tcp -f inet -f inet6"
    else:
        cmd = "/usr/bin/netstat -na -P tcp -f inet"

    results = sb_utils.misc.tcs_utils.tcs_run_cmd(cmd, True)
    if results[0] != 0:
        mydigest.update('\n')
        report.setProp("fingerprint", mydigest.hexdigest())
        return

    report.setProp("numAttrs", "6")
    report.setProp("attr1", "TCP Port")
    report.setProp("attr2", "Listening Address")
    report.setProp("attr3", "Program")
    report.setProp("attr4", "SELinux Context")
    report.setProp("attr5", "IP Version")
    report.setProp("attr6", "IANA Well-Known Name")

    ipVersion = "-"
    for line in results[1].split('\n'):
        line = line.strip()
        if not line: 
            continue

        if line.startswith('TCP:'):
            ipVersion = line.split(' ')[1]
            continue

        if line.startswith('Local Address'):
            continue
        if line.startswith('----------'):
            continue

        fields = line.split()
        if fields[-1] != 'LISTEN':
            continue

        tcpPort = fields[0].split('.')[-1]
        try:
            svcName = socket.getservbyport(int(tcpPort), 'tcp')
        except:
            svcName = "-"

        portObject = report.newChild(None, "object", None)
        portObject.setProp("key", "%s:%s" % (fields[0], ipVersion))
        portObject.setProp("attr1", tcpPort)
        ifBound = fields[0].split('.')[0:-1] 
        ifBound = '.'.join(ifBound)

        portObject.setProp("attr2", ifBound)
        portObject.setProp("attr3", "-")
        portObject.setProp("attr4", "-")
        portObject.setProp("attr5", ipVersion)
        portObject.setProp("attr5", svcName)

        mydigest.update(fields[0].split('.')[-1])
        mydigest.update(ifBound)
        mydigest.update(ipVersion)
        mydigest.update(svcName)


    report.setProp("fingerprint", mydigest.hexdigest())
    return
