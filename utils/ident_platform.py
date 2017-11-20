#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Determine Operating System information
# A generic wrapper for the platform module
#
#
# We should return a string like this
#
#   os:ver:platform
#
#   os = ubuntu/redhat/suse/opensuse/fedora/solaris
#      note - centos/oracle/scili = redhat
#   ver = maj_min     ie 10_3   5_2
#   platform = i86pc|sparc|s390x|i386|x86_64
##############################################################################

import platform
import sys
import os
import re
import commands

def getBuildString():
    platformdata = platform.platform().split('-')
    os_name = "unknown"
    os_ver = "unknown"
    os_arch = "unknown"
    
    if platformdata[0] == 'SunOS':
#        print len(platformdata),'-',platformdata
        os_name = "Solaris"
        os_ver  = platformdata[1].split('.')[1]
        os_arch = platformdata[2]
        if os_arch == 'Sun4u':
	    os_arch = 'sparc'
    else:
#        print len(platformdata),platformdata.index('with'),platformdata
        with_index = platformdata.index('with')
        os_name = platformdata[with_index+1]
        os_ver = platformdata[with_index+2]
        os_arch = platformdata[with_index-1]

        if os_arch.startswith('i'):
            os_arch = 'i386'
        
        if os_name == "SuSE":
            rel_lines = open('/etc/SuSE-release').readlines()
            os_name = rel_lines[0].split()[0].lower()
            if os_name == "opensuse":
                for line in rel_lines:
                    if line.startswith('VERSION'):
                        os_ver = line.split('=')[-1].strip()
                        break
            else:
                for line in rel_lines:
                    if line.startswith('VERSION'):
                        os_major = line.split('=')[-1].strip()
                    elif line.startswith('PATCH'):
                        os_minor = line.split('=')[-1].strip()
                os_ver = "%s_%s" % (os_major, os_minor)
                
    return "%s %s %s " % (os_name.lower(), os_ver.replace('.','_'), os_arch)


if __name__ == '__main__':
    bigstr = getBuildString()
    if len(sys.argv) > 1:
      outfields=[]
      os_name, os_rev, os_proc = bigstr.split()
      for arg in sys.argv[1:]:
        if arg == '-M' :   # Show our OS Minor software release
          outfields.append(os_rev.split('_')[0])
        elif arg == '-m' : # Show our OS Minor release number (or '-' if no minor number - like Fedora)
          revnums = os_rev.split('_')
          if len(revnums) > 0:
            outfields.append(revnums[1])
          else:
            outfields.append('-')
        elif arg == '-t' : # Show our 'lineage' IE solaris, redhat (inc centos/oracle) , fedora, suse, opensuse
          outfields.append(os_name)  
        elif arg == '-p' : # Show our 'processor' type (i386, x86_64, sparc, s390x)
          outfields(os_proc)
      print ' '.join(outfields)
    else:
      print bigstr
