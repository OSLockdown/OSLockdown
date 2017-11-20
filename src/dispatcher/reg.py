#!/usr/bin/env python
##############################################################################
# Copyright (c) 2014-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

# script to quickly register a number of clients
import os
import getopt
import platform
import sys

port = 6443
numthreads=1
offset = 0
server = 'localhost'

hostname = platform.node()
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hp:n:o:s:" )
except getopt.GetoptError, err:
    print >> sys.stderr, "Error: %s" % err
    sys.exit (1)
for o,a in opts:
    if o == '-p':
        port = int(a)
    elif o == '-n':
        numthreads = int(a)
    elif o == '-s':
        server = a
    elif o == '-o':
        offset = int(a)
    elif o == '-h':
        print "%s : [-h | [-n numthreads] [-p startingPort] ]" % sys.argv[0]
        sys.exit(1)    

for thnum in range(0,numthreads):
  cmd = "/usr/share/oslockdown/tools/RegisterClient -n -l -s %s -D %s_%d -A %s -P %d" % (server, hostname, thnum+offset+1, hostname, thnum+port+offset)
  os.system(cmd)

