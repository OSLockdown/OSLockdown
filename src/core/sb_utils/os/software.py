#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import info

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils

MODULE_NAME = "OS.Software"

##############################################################################
def listAllFilesForPackage(pkgname=None):
    """Return a list of files that were installed by the package"""
    pkgList = []

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    if not is_installed(pkgname):
        return pkgList
    if info.is_solaris() == True:
        cmd = "/usr/sbin/pkgchk -l %s | grep 'Pathname:'" % pkgname
        if not os.path.isfile('/usr/sbin/pkginfo'):
            return None

        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] == 0:
            pkgList = [ thisfile[10:] for thisfile in output[1].splitlines() if  thisfile.startswith('Pathname: ') ]

        del output
        
    else:
        try:
            import rpm
        except ImportError:
            return None

        try:
            transet = rpm.TransactionSet()
        except Exception, err:
            logger.error(MODULE_NAME, err)
            return None

        ## First try, the Python RPM API....
        pkglist = transet.dbMatch('name', pkgname)    
        if type(pkglist).__name__ == 'mi':
            for hdr in pkglist:
                if hdr['name'] == pkgname:
                    pkgList = hdr['filenames']
                    break
        ## Okay, now try the old-fashioned method of using rpm(8) command
        else:
            msg = "Unable to determine if '%s' is installed using "\
                  "Python-RPM API, trying the rpm(8) utility" % pkgname
            logger.info(MODULE_NAME, msg)
            cmd = "/bin/rpm -q --list %s " % pkgname
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] == 0:
                pkgList = output[1].split()
            
    return pkgList

##############################################################################
def get_rpm_changelog(pkgname=None):

    changelog = ()

    if pkgname == None:
        return changelog

    try:
        import rpm
    except ImportError:
        return changelog

    try:
        transet = rpm.TransactionSet()
    except Exception, err:
        return changelog

    pkglist = transet.dbMatch('name', pkgname)    
    if type(pkglist).__name__ == 'mi':
        for hdr in pkglist:
            if hdr['name'] == pkgname:
                changelog = zip(hdr["changelogtime"], hdr["changelogname"], hdr["changelogtext"])
                break

    return changelog

        
##############################################################################
def is_installed(pkgname=None):
    """Determine if a package is installed"""

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    if pkgname == None:
        return None

    installed = False
        
    #==========================
    # Solaris check
    #==========================
    if info.is_solaris() == True:
        cmd = '/usr/bin/pkginfo %s' % pkgname
        if not os.path.isfile('/usr/bin/pkginfo'):
            return None

        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] == 0:
            installed = True

        del output

    #==========================
    # Linux check
    #==========================
    ## TODO: Ubuntu support will use 'dpkg-query -s'
    else:
        try:
            import rpm 
        except ImportError:
            return None

        try:
            transet = rpm.TransactionSet()
        except Exception, err:
            logger.error(MODULE_NAME, err)
            return None
 
        ## First try, the Python RPM API....
        pkglist = transet.dbMatch('name', pkgname)    
        if type(pkglist).__name__ == 'mi':
            for hdr in pkglist:
                if hdr['name'] == pkgname:
                    pkgname = "%s-%s-%s" % (str(hdr['name']), 
                                        str(hdr['version']), 
                                        str(hdr['release']) ) 
                    installed = True 
                    break
        ## Okay, now try the old-fashioned method of using rpm(8) command
        else:
            msg = "Unable to determine if '%s' is installed using "\
                  "Python-RPM API, trying the rpm(8) utility" % pkgname
            logger.info(MODULE_NAME, msg)
            cmd = "/bin/rpm -q %s " % pkgname
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] == 0:
                installed = True
            else:
                installed = False

    #=========================
    if installed == False:
        msg = """Package '%s' is NOT installed""" % pkgname
        logger.debug(MODULE_NAME, msg)
        return False
    else:
        msg = """Package '%s' is installed""" % pkgname
        logger.debug(MODULE_NAME, msg)
        return True

##############################################################################
def buildtime(pkgname=None):
    
    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    if info.is_solaris() == True:
        return None

    if pkgname == True:
        return None

    try:
        import rpm 
        import time
    except ImportError:
        return None, None

    try:
        transet = rpm.TransactionSet()
    except Exception, err:
        logger.error(MODULE_NAME, err)
        return None, None

    pkgBuildtime = None
    local_date_string = None

    ## First try, the Python RPM API....
    pkglist = transet.dbMatch('name', pkgname)    
    if type(pkglist).__name__ == 'mi':
        for hdr in pkglist:
            if hdr['name'] == pkgname:
                pkgBuildtime = hdr['buildtime']
                break

    ## Okay, now try the old-fashioned method of using rpm(8) command
    if pkgBuildtime == None:
        msg = "Unable to determine build time of '%s' using "\
              "Python-RPM API, trying the rpm(8) utility" % pkgname
        logger.info(MODULE_NAME, msg)
        cmd = """/bin/rpm -q %s --queryformat "%%{BUILDTIME}" """ % pkgname

        results = tcs_utils.tcs_run_cmd(cmd, True)
        if results[0] != 0:
            msg = """Unable to get buildtime of %s: %s""" % (pkgname, results[2])
            logger.error(MODULE_NAME, msg)
            pkgBuildtime = None
        else:
            pkgBuildtime = results[1]
            
    if pkgBuildtime != None:
        local_date_string = time.strftime("%a %b %d %T %Z %Y", time.localtime(int(pkgBuildtime)))

    return pkgBuildtime

 

##############################################################################
def version(pkgname=None):
    """
    Determine version and release of software package
    Return a tuple: [version, release]
    """

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    if pkgname == None:
        return None

    if info.is_solaris() == True:
        if not os.path.isfile('/usr/bin/pkgparam'):
            return None
        cmd = '/usr/bin/pkgparam %s VERSION' % pkgname
    else:
        if not os.path.isfile('/bin/rpm'):
            return None
        cmd = """/bin/rpm -q %s --queryformat "%%{VERSION},%%{RELEASE}" """ % pkgname

    results = tcs_utils.tcs_run_cmd(cmd, True)
    if results[0] != 0:
        msg = """Unable to get version of %s: %s""" % (pkgname, results[2])
        logger.error(MODULE_NAME, msg)
        return None

    msg = """Package '%s' is installed""" % pkgname
    logger.debug(MODULE_NAME, msg)
    return results[1].rstrip('\n').split(',')

##############################################################################
def isVersionRange(test_version = None, ver_a = None, ver_b = None):
    """
    Determine if a test_version is within ver_a and ver_b

       test_version >= vera and test_version <= ver_b
    """
        
    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    try:
        import distutils.version
    except ImportError:
        # don't have much choice here but to complain and return None
        logger.error(MODULE_NAME,"Unable to import distutils.version - are the devel libraries loaded?")
        return None
        
    if test_version == None or ver_a == None or ver_b == None:
        return None

    min_ver = distutils.version.LooseVersion("None:%s" % str(ver_a))
    max_ver = distutils.version.LooseVersion("None:%s" % str(ver_b))
    sw_ver  = distutils.version.LooseVersion("None:%s" % str(test_version))

    if sw_ver >= min_ver and sw_ver <= max_ver:
        return True
    else:
        return False


##############################################################################
def in_rpm_changelog(pkgname=None, regex=None):
    """
    Search an RPM's changelog for a certain pattern. This is useful when
    searching for a CVE reference.
    """

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    if pkgname == None or regex == None:
        return None

    if info.is_solaris() == True:
        return None

    try:
        import re
    except ImportError:
        return None

    try:
        search_pat = re.compile(regex)    
    except Exception, err:
        msg = "Unable to compile regular expression '%s': %s", (regex, str(err)) 
        logger.error(MODULE_NAME, msg)
        del logger
        return None

    cmd = "/bin/rpm -q --changelog %s" % pkgname
    results = tcs_utils.tcs_run_cmd(cmd, True)
    if results[0] != 0:
        msg = """Unable to retrieve changelog of '%s': %s""" % (pkgname, results[2])
        logger.error(MODULE_NAME, msg)
        del logger
        return None

    msg = "Searching '%s' package changelog for regular expression: '%s'" % (pkgname, regex)
    logger.debug(MODULE_NAME, msg)
    del logger
    for line in results[1].split('\n'):
        if search_pat.search(line):
            del results
            return True

    return False



if __name__ == '__main__':
    print isVersionRange(test_version='2.2.32a', ver_a='2.2.0', ver_b='2.2.32')
