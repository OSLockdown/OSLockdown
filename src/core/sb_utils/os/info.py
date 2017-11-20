##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Determine Operating System information
# A generic wrapper for the platform module
#
##############################################################################
import platform
import sys
import os
import re

sys.path.append('/usr/share/oslockdown')
import sb_utils.os.software
import TCSLogger
import tcs_utils
logger = TCSLogger.TCSLogger.getInstance()

# Defined here so we can override if we need to for testing purposes...
# Look at the 'main' code below for details...

REDHAT_RELEASE_FILE       = "/etc/redhat-release"
NOVELL_SUSE_RELEASE_FILE  = "/etc/SuSE-release"
ORACLE_RELEASE_FILE       = "/etc/enterprise-release"
ORACLE_RELEASE_FILE_2     = "/etc/oracle-release"
FEDORA_RELEASE_FILE       = "/etc/fedora-release"

MODULE_NAME = "OS.Info"


##############################################################################
def is_solaris():
    """Determine of solaris operating system"""
    osname = platform.platform(aliased=1, terse=1)

    if osname.startswith('Solaris'):
        return True

    return False

def is_s390x():
    mach = platform.machine()

    msg = "platform.machine() returns: %s" % mach
    logger.log_debug(MODULE_NAME, msg)

    if mach.startswith('s390x'):
        return True

    return False
    

def is_x86():
    mach = platform.machine()

    msg = "platform.machine() returns: %s" % mach
    logger.log_debug(MODULE_NAME, msg)

    if mach.startswith('i86pc'):
        return True

    return False
    
def is_LikeRedHat():
    """Determine if the release is Red Hat or a 'derivative' that behaves the same
       such as CentOS, Oracle, or (eventually?) Scientific Linux
    """
    
    if getDistroName().lower() in ['red hat' , 'centos', 'oracle', 'scientific linux', 'xenserver'] :
        return True
    else:
        return False 
 
def is_suse():
    """redirect to is_LikeSUSE()"""
    return is_LikeSUSE()
              
def is_LikeSUSE():
    """Determine if SuSE/openSUSE Platform"""

    if getDistroName().lower() in ['novell', 'suse', 'opensuse']:
        return True
    else:
        return False

def is_fedora():
    """Determine if Fedora Platform"""

    if getDistroName().lower() in ['fedora', 'fedoraproject', 'fedora_project']:
        return True
    else:
        return False

def is_OracleEntLinux():
    
    if os.path.exists(ORACLE_RELEASE_FILE) or os.path.exists(ORACLE_RELEASE_FILE_2):
        return True
        
    if sb_utils.os.software.is_installed(pkgname='oracle-logos'):
        return True

    # Let's see if no one has altered the /etc/sysctl.conf
    try:
        infile = open('/etc/sysctl.conf', 'r')
        lines = infile.readlines()
        infile.close()
        if lines[0].strip().endswith('Oracle Enterprise Linux'):
            return True
    except:
        pass

    return False

##############################################################################
def getDistroFullname():
    return "%s %s" % (getDistroName(), getDistroVersion())

def getDistroVersion():
    if is_solaris() == True:
        return os.uname()[2]
    else:
        # We must use the getDistroName() function
        # to differentiate between Novell SUSE and openSUSE
        release_contents = None
        
        distroName = getDistroName()
        if distroName in ['SUSE', 'openSUSE'] :
            novell_details = getNovellSuSEDetails() 
            if novell_details[1] != '' and novell_details[2] != '':
                return "%s.%s" % (novell_details[1], novell_details[2])
            return novell_details[1]
            
        # *everyone* else uses a single line with 'release <ver>' in it.  Some have ver as x.y, others as x with an optional
        # 'update Y' field.  So key on release first, then look for any possible updates
        
        elif distroName in [ "Fedora" , "CentOS", "Red Hat" ]:
            release_contents = open(REDHAT_RELEASE_FILE).read()
        
        elif distroName == "Oracle":
            if os.path.exists(ORACLE_RELEASE_FILE):
                release_contents = open(ORACLE_RELEASE_FILE).read()
            elif os.path.exists(ORACLE_RELEASE_FILE_2):
                release_contents = open(ORACLE_RELEASE_FILE_2).read()
            
        else: # Ok, unknown release type - fall back to potentially flawed platform.dist() processing
            release_info = platform.dist()
            return release_info[1]
        
        # Look for the 'release X' line
        
        rel = re.search(" release\s+([\d.]+)", release_contents)
        upd = re.search(" Update\s+(\d+)", release_contents)
                
        if not upd:
            return rel.group(1)    
        else:
            return "%s.%s" %(rel.group(1),upd.group(1))
                
        release_info = platform.dist()
        if release_info[0] != 'redhat':
            return release_info[1]

        # Release version already contains minor (x.y)
        if len(release_info[1].split('.')) > 1:
            return release_info[1]
        
        try:
            return "%s.%s" % (release_info[1], m.group(1))        
        except:
            return release_info[1]

def getDistroName():

    # Step 1: Solaris is easy....
    osname = platform.platform(aliased=1, terse=1) 
    if osname.startswith('Solaris'):
        return "Solaris"

    # Step 2: Try to figure out proper "branding"
    # We're going to base this off of some explicit looking for various /etc/*-release files.  The python 'platform.dist()' code has some known
    # flaws - see OS Lockdown BugId 13229 for more details
    
    if os.path.exists(NOVELL_SUSE_RELEASE_FILE):        # Novell SUSE and OpenSUSE releases, read file to determine which
        try:
            in_obj = open(NOVELL_SUSE_RELEASE_FILE, 'r')
            xbuffer = in_obj.read(32).split()[0]
            in_obj.close()
            return xbuffer
        except IOError, err:
            return "SUSE"

    elif os.path.exists(FEDORA_RELEASE_FILE):    # Fedora
        return "Fedora"
    elif os.path.exists(REDHAT_RELEASE_FILE):    # CentOS/Oracle/Redhat all populate this, but we need to do some additional work

        if is_OracleEntLinux() == True:
            return "Oracle"

        try:
            in_obj = open(REDHAT_RELEASE_FILE, 'r')
            line = in_obj.read(32).split()
            in_obj.close()
            if line[0] == 'Red':
                distName = 'Red Hat'
            elif line[0] == 'Scientific':
                distName = 'Scientific Linux'
            elif line[0] == 'XenServer':
                distName = 'XenServer'
            else:
                distName = line[0]
         
            return distName
        except IOError, err:
            if dstver < 10.0:
                return "Red Hat"
            else:
                return "Fedora"


    # Step 3: Just give up and return whatever the platform module reports - this is a *PURE* fallback, as the platform.dist() code has 'issues'
    return platform.dist()[0]

##########################################################################
def getRedHatType():
    """Determine if install is 'server', 'as', 'es', etc..."""

    distro_type = ''
    try:
        in_obj = open(REDHAT_RELEASE_FILE, 'r')
        line = in_obj.read(32)
        fields = line.split()
        if line.startswith('Red Hat Enterprise Linux'):
            if fields[4] == 'Server':
                distro_type = 'server'

            if fields[4] == 'Desktop':
                distro_type = 'desktop'

            if fields[4] == 'ES':
                distro_type = 'es'

            if fields[4] == 'AS':
                distro_type = 'as'

        in_obj.close()

    except:
        pass

    return distro_type


##########################################################################
def getNovellSuSEDetails():
    """
     Novell SUSE Linux has a different release file structure:
     /etc/SuSE-release

     SUSE Linux Enterprise Server 10 (i586)
     VERSION = 10
     PATCHLEVEL = 3

    function will return tuple:
      (distro_type, release, service_pack)
    
      type = (Desktop or Server)
      release = 10 or 11
    """
    sp_ver = ''
    maj_ver = ''
    distro_type = ''
    try:
        in_obj = open(NOVELL_SUSE_RELEASE_FILE, 'r')
        for line in in_obj.readlines():
            if line.startswith('SUSE Linux Enterprise '):
                m = re.search("SUSE Linux Enterprise (\w+) \d+", line)
                if m:
                    distro_type = m.group(1).lower()

            if line.startswith('VERSION'):
                try:
                    maj_ver = line.split('=')[1].strip()
                except IndexError:
                    pass

            if line.startswith('PATCHLEVEL'):
                try:
                    sp_ver = line.split('=')[1].strip()
                except IndexError:
                    pass

        in_obj.close()
    except IOError:
        pass

    return (distro_type, maj_ver, sp_ver)
    
    

##########################################################################
def getCpeName():
    """ 
    Obtain the system's Common Platform Enumeration (CPE) string
    - See http://cpe.mitre.org/ for more information
    - Get current dictionary here: http://nvd.nist.gov/cpe.cfm
    """

    osName = getDistroName()
    dstVer = getDistroVersion()
    cpeName = "cpe:/o:"
    
    # Fedora's /etc/system-release-cpe file claims 
    # cpe://o:fedora_project instead of o:redhat however,
    # the official CPE v2.2 dictionary dated 5/12/2010
    # marks it as o:readhat.
    if osName == 'Fedora':
        cpeName = "cpe:/o:redhat:fedora:%s" % dstVer

    if osName == 'Ubuntu':
        cpeName = "cpe:/o:ubuntu:ubuntu:%s" % dstVer

    #----------------------------
    # Red Hat Systems (note - treat Scientific Linux as redhat for CPE
    if osName in [ 'Red Hat', 'Scientific Linux']:
        distro_type = getRedHatType() 
        if distro_type != '':
            distro_type = ":%s" % distro_type

        if len(dstVer.split('.')) < 2:
            cpeName = "cpe:/o:redhat:enterprise_linux:%s%s" % (dstVer, distro_type)
        else:
            if dstVer.split('.')[1] == '0':
                cpeName = "cpe:/o:redhat:enterprise_linux:%s:ga%s" % (dstVer.split('.')[0], distro_type)
            else:
                cpeName = "cpe:/o:redhat:enterprise_linux:%s:update%s%s" % (dstVer.split('.')[0], dstVer.split('.')[1], distro_type)

    # For now, treat XenServer *as* CentOS 5 - this is a temporary hardcode to keep us from having to add a full
    # CPE entry for *all* modules 
    if osName == 'XenServer':
        cpeName = "cpe:/o:centos:centos:5"

    if osName == 'CentOS':
        cpeName = "cpe:/o:centos:centos:%s" % dstVer

    if osName == 'XenServer':
        cpeName = "cpe:/o:centos:centos:5"

    if osName == 'openSUSE':
        cpeName = "cpe:/o:novell:opensuse:%s" % dstVer

    if osName == 'Oracle':
        cpeName = "cpe:/o:oracle:enterprise_linux:%s" % dstVer

    #----------------------------
    # SUSE Systems
    #
    # Prior to release 10, the CPE was o:suse not o:novell
    # Let's do some specific checks for Novell Systems
    if osName == 'SUSE':
        distro_type = ''
        novell_details = ('', '', '')
        try: 
            novell_details = getNovellSuSEDetails()
            if novell_details[0] != '':
                distro_type = ":%s" % novell_details[0]
        except:
            pass 

        if float(dstVer) < 10.0:
            cpeName = "cpe:/o:suse:suse_linux:%s" % dstVer
        else:
            if len(dstVer.split('.')) < 2:
                cpeName = "cpe:/o:novell:suse_linux:%s:-" % (dstVer, distro_type)
            else:
                if dstVer.split('.')[1] == '0':
                    cpeName = "cpe:/o:novell:suse_linux:%s:gm%s" % (dstVer.split('.')[0], distro_type)
                else:
                    cpeName = "cpe:/o:novell:suse_linux:%s:sp%s%s" % (dstVer.split('.')[0], dstVer.split('.')[1], distro_type)

    if osName == 'Solaris':
        cpeName = "cpe:/o:sun:sunos:%s" % dstVer


    return cpeName 

    
##########################################################################
# return the 'major Version' number of the OS
def getOSMajorVersion():
    return getDistroVersion().split('.')[0]
    
##########################################################################
# return the 'minor Version'  number of the OS or '' if none (like for Fedora)
def getOSMinorVersion():
    try:
        minVer = getDistroVersion().split('.')[1]
    except:
        minVer = ''
    return minVer

##########################################################################
# Return a list of the valid shells as per /etc/shells
# If file unreadable, log said and create a default list hardcoded from 
# man pages of getusershell().  Wish python had a nice way to call getusershell()
# directly...
 
def validShells():
    """Get a list of valid shells from /etc/shells"""

    shells = []
    try:
        in_obj = open('/etc/shells', 'r')
        for line in in_obj.readlines():
            shells.append(line.strip())
        in_obj.close()
    except IOError, err:
        msg = "Unable to open /etc/shells: %s" % err
        logger.log_err("sb_utils.os.info.validShells", msg)
        msg = "Using default shells as per getusershell()"
        logger.log_err("sb_utils.os.info.validShells", msg)
        # Ok, for sanity we'll 'create' the approved shells (as per linux/solaris man pages)
        # but *only* if we can't read the file 
        if not is_solaris():
            shells = [ "/bin/sh", "/bin/csh" ]
        else:
            shells = [ "/bin/bash", "/bin/csh", "/bin/jsh", "/bin/ksh",
                       "/bin/pfcsh", "/bin/pfksh", "/bin/pfsh", "/bin/sh",
                       "/bin/tcsh", "/bin/zsh", "/sbin/jsh", "/sbin/pfsh",
                       "/sbin/sh", "/usr/bin/bash", "/usr/bin/csh", "/usr/bin/jsh",
                       "/usr/bin/ksh", "/usr/bin/pfcsh", "/usr/bin/pfksh", "/usr/bin/pfsh",
                       "/usr/bin/sh", "/usr/bin/tcsh", "/usr/bin/zsh", "/usr/sfw/bin/zsh",
                       "/usr/xpg4/bin/sh" ]
       
    return shells 
    

if __name__ == '__main__':
    if len(sys.argv) >1:
        try:
            altSys = sys.argv[1]
            oldprefix = "/etc/"
            newprefix = "/data/shared/etc_releases/%s/" % altSys
            REDHAT_RELEASE_FILE      = REDHAT_RELEASE_FILE.replace(oldprefix, newprefix)     
            NOVELL_SUSE_RELEASE_FILE = NOVELL_SUSE_RELEASE_FILE.replace(oldprefix, newprefix)  
            ORACLE_RELEASE_FILE      = ORACLE_RELEASE_FILE.replace(oldprefix, newprefix)       
            FEDORA_RELEASE_FILE      = FEDORA_RELEASE_FILE.replace(oldprefix, newprefix)       
            
        except:
            print "OOPS, I need valid arguments"
    
#    print "REDHAT_RELEASE_FILE      = %s" % REDHAT_RELEASE_FILE     
#    print "NOVELL_SUSE_RELEASE_FILE = %s" % NOVELL_SUSE_RELEASE_FILE
#    print "ORACLE_RELEASE_FILE      = %s" % ORACLE_RELEASE_FILE     
#    print "FEDORA_RELEASE_FILE      = %s" % FEDORA_RELEASE_FILE     

    print "getDistroName() = %s " % getDistroName()

    print "getCpeName()       = %s " % getCpeName()
    print "getDistroVersion() = %s " % getDistroVersion()
    print "is_solaris()       = %s " % is_solaris()
    print "is_x86()           = %s " % is_x86()
    print "is_LikeSUSE()      = %s " % is_LikeSUSE()
    print "is_fedora()        = %s " % is_fedora()
    print "is_LikeRedHat()    = %s " % is_LikeRedHat()
    print
