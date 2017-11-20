#!/usr/bin/env python
#
# Copyright (c) 2007-2017 by Forcepoint LLC
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#  
#

import sys
import urlparse
import re

logFile = '/var/log/oslockdown-dispatcher.log'
lastConsoleAddr=""
exitVal=1


regex = re.compile(r'(https?://\S+)')
try:
    for line in open(logFile):
        match = regex.search(line)
        if match:
            lastConsoleAddr=urlparse.urlparse(match.group(1))[1]
    if lastConsoleAddr:
        exitVal=0
except IOError:
    # If we can't open/read/process the file then assume no registration
    pass
except Exception,e:
    print >> sys.stderr, e
    print ""
    
print " at port ".join(lastConsoleAddr.split(':'))
sys.exit(exitVal)
