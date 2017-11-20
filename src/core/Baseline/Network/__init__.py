#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
###############################################################################

import datetime
import os
import sha
import re
import sys
import shutil
import time
import cgi
import pwd


sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sbProps
import sb_utils.os.info
import sb_utils.os.solaris
import sb_utils.filesystem.fingerprint
import sb_utils.hardware
from sb_utils.misc.tcs_utils import find_xml_attr
try:
    import sb_utils.misc.unique
except ImportError:
    pass


# libxml2 may not be installed so we need to check
try:
    import libxml2
except ImportError:
    LOGGER = TCSLogger.TCSLogger.getInstance()
    MSG = 'Unable to import libxml2 module'
    LOGGER.log_err('BaselineReporting', MSG)
    sys.exit(1)


##############################################################################
class Report:
    def __init__(self,  xmlnode=None):
        """
        Report constructor
        """
        if xmlnode == None:
            return None

        self.__xml_node = xmlnode

    def create_report(self):
        """Create Network Report"""

        # Run report subsections
        self._iptables()
        self._routing()
         
    def _iptables(self):
        """ Iptables Firewall Configuration """
        # Update XML Document Tree
        tt = self.__xml_node.newChild(None, "subSection", None)
        tt.setProp("name", "IPtables")
        tt.setProp("fullname", "Network access controls such as firewall rules.")

        iptables_report = tt.newChild(None, "content", None)

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

    def _routing(self):
        """ Routing Table """

        # Update XML Document Tree
        tt = self.__xml_node.newChild(None, "subSection", None)
        tt.setProp("name", "Routing")
        msg = "Network configuration such as default route. "\
              "See netstat(8) and netstat(1M)."
        tt.setProp("fullname", msg)
        routing_report = tt.newChild(None, "content", None)

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
        return True
