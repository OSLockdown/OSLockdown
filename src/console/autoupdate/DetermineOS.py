#!/usr/bin/env python
#########################################################################
# Copyright (c) 2012-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##########################################################################
#
#

import sys
import os
import commands
import platform
import re
import getopt
import base64
import exceptions
import zipfile
import tarfile
import StringIO
import shutil
import logging

    #
    # Additional processing for SUSE/OPENSUSE since they have a multiline release
    # file instead of a single line

def _process_suse_release(relFile):
    major_version = ""
    minor_version = ""
    
    version = ""
    distro = ""
    patch = ""
    for line in open(relFile):
        if line.startswith('VERSION'):
            version = line.split()[-1]
        elif line.startswith('PATCHLEVEL'):
            patch  = line.split()[-1]
        elif line.startswith('openSUSE'):
            distro = "opensuse"
        elif line.startswith('SUSE'):
            distro = "suse"

    if distro == "suse" and version and patch:
        major_version = version
        minor_version = patch
    elif distro == "opensuse" and version:
        # there wasn't a .0 release, but for safety sake...
        version += ".0."
        major_version, minor_version,slop = version.split('.',2)
    
        # need to consider 11.3 special (major version number on libraries)
        # need to consider 11.4 special (python version change)
        if major_version == "11" and minor_version in [ "3", "4"]:
            major_version = "11_%s" % minor_version 
            minor_version = "---"

    return distro, major_version, minor_version


#
#  Process the release file for distro major/minor version
#
#
def _process_release_file(relFile):
    # Look for the either 'Release X.Y' or 'Release X (Update Y)' using
    # regular expressions.
    major_version = ""
    minor_version = ""
    release_contents = open(relFile).read()
    rel = re.search(" release\s(\d+)\.*(\d+|\s)", release_contents)
    upd = re.search(" release\s(\d+).*\Update\s+(\d+)", release_contents)
            
    if upd:
        major_version = upd.group(1)
        minor_version = upd.group(2)
    elif rel:
        major_version = rel.group(1)
        minor_version = rel.group(2)

    return major_version, minor_version

#   
# Do a quick and dirty determination of the OS flavor.  For linux keep in mind
# that the /etc/*-release file is legacy, and many flavors default to populating
# /etc/redhat-release, so look for that *last*.

def get_os_info():
    uname = platform.uname()
    short_cpe = ""
    major_version = ""
    minor_version = ""
    arch = ""
    hostname = ""
    
    # for open source release, pkg_root is always 'Packages'
    pkg_root = "Packages"
    
    hostname = platform.node()
    
    if uname[0] == 'SunOS':
        short_cpe = 'solaris'
        major_version = uname[2].split('.')[1]
        minor_version = " "
        arch = uname[4]
        if arch == "sun4u":
            arch = "sparc"
        else:
            arch = "i86pc"
        
    else:
        # Ok, we're linux.  Start with distro specific release files
        # CentOS/Oracle are treated as 'redhat' flavors for our packaging
        
        if os.path.exists('/etc/enterprise-linux'):    # Oracle
            relFile = '/etc/enterprise-linux'
            short_cpe = "redhat"
            
        elif os.path.exists('/etc/fedora-release'):   # Fedora
            relFile = '/etc/fedora-release'
            short_cpe = "fedora"
            
        elif os.path.exists('/etc/SuSE-release'):     # SUSE/openSUSE
            relFile = '/etc/SuSE-release'
            short_cpe, major_version, minor_version = _process_suse_release(relFile)
        
        elif os.path.exists('/etc/centos-release'):   # explicit CentOS
            relFile = '/etc/centos-release'
            short_cpe = "redhat"
            
        elif os.path.exists('/etc/redhat-release'):   # fall back
            relFile = '/etc/redhat-release'
            short_cpe = "redhat"
            
        # bail if we can't figure out the short cpe name
        if not relFile or not short_cpe:
            logging.getLogger('AutoUpdate').error( "Unable to locate OS release file, unable to update")
            logging.getLogger('AutoUpdate').error( "Please contact product technical Support.")
            sys.exit(1)
        elif "suse" not in short_cpe:
            # Everyone else is a flat file with common syntax for releases so...
            major_version, minor_version = _process_release_file(relFile)

        machine = platform.machine()
        if machine in [ "s390x" ]:
            arch = "s390x"
            short_cpe += "_z"
        elif machine in [ "x86_64" ] :
            arch = "x86_64"
        elif machine in ["i386", "i486", "i586", "i686" ]:
            arch = "i386" 

    return pkg_root, short_cpe, major_version, minor_version, arch

if __name__ == "__main__":
    pkg_root, short_cpe, major_version, minor_version, arch = get_os_info()
    if "-s" in sys.argv[1:]:
        print "%s-%s-%s" % (short_cpe, major_version, arch)
    else:
        print "pkg_root      = %s " % pkg_root
        print "short_cpe     = %s " % short_cpe
        print "major_version = %s " % major_version
        print "minor_version = %s " % minor_version
        print "arch          = %s " % arch
