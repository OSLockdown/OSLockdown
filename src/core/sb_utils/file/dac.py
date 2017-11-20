#!/usr/bin/python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import stat
import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.file.exclusion
try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

MODULE_NAME = 'sb_utils.file.dac'

##############################################################################
def testFile(filepath):
    try:
        st = os.stat(filepath)
    except OSError, err:
        logger.log_err(MODULE_NAME, str(err)) 
        return False

    return True
    

def isGroupReadable(filepath):
    st = os.stat(filepath)
    return bool(st.st_mode & stat.S_IRGRP)



# For testing perms mode we can't rely on simple greater/lesser value, as each of the three bits for r,w,x must be considered
# independently of the others.  So when comparing permissions of X and Y, if Y has some access that X does not, then Y is considered
# 'more permissive'.  Remember that the perrmisions are indicated by a bit map, which is normally treated as an octal number for human 
# consumption.  We can not just take the absolute octal values for the comparisions.    Thus we need to consider the permission bits
# at each of the r, w, and x bits, to see if the current mode is granting something that the testmode would not.

def isUSR(curMode, testMode):
    """Is current user mode more permissive than test mode?"""
    mask = 0
    for bit in [stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR]:
        if (curMode & bit) and not (testMode & bit):
            mask |= bit    
    return mask
    

def isGRP(curMode, testMode):
    """Is current group mode more permissive than test mode?"""
    mask = 0
    for bit in [stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP]:
        if (curMode & bit) and not (testMode & bit):
            mask |= bit        
    return mask

def isOTH(curMode, testMode):
    """Is current other mode more permissive than test mode?"""
    mask = 0
    for bit in [stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH]:
        if (curMode & bit) and not (testMode & bit):
            mask |= bit    
    return mask

def isSpecial(curMode, testMode):
    """Check the suig/sgid/stick bits"""
    mask = 0
    for bit in [stat.S_ISUID, stat.S_ISGID, stat.S_ISVTX]:
        if (curMode & bit) and not (testMode & bit):
            mask |= bit    
    return mask
    
def findMaximumPermittedDACs(currentDACs, allowedDACs):
    """
    Restrict the bits in currentDACs to only those in allowedDACs.  Explicitly *IGNORE* any bits
    that are not in the 0777 range.
    """   
    newPerms = 0
    if type(currentDACs) == type(""):
        currentDACs = int(currentDACs,8)
    if type(allowedDACs) == type(""):
        allowedDACs = int(allowedDACs,8)
    
    otherMask = isOTH(currentDACs, allowedDACs)
    groupMask = isGRP(currentDACs, allowedDACs)
    userMask  = isUSR(currentDACs, allowedDACs)
    specialMask = isSpecial(currentDACs, allowedDACs)
    fullMask = otherMask|groupMask|userMask|specialMask
    
    newPerms = currentDACs & ~fullMask
    return newPerms
    
def isPermOkay(filepath='', testMode='', ignoreExcludes=False):
    """
    Given a filepath and a set of permissions, return if the
    currently assigned permissions are equal to or less restrictive
    that the 'testMode' permissions.  We can't just compare the values, but
    need to look at the actual bits.  A simple check would be to mask out the bits
    from testMode in the actual files permissions, and then see if anything is left.  If so, 
    the file is 'more permissive' (IE - allows something testMode doesn't).  The below does
    some explicit checks so we can indicate *what* is being allowed.
    """
   
    # assume we're ok, we'll flag otherwise explicitly
    retval = True 
    if testFile(filepath) == False or testMode == '':
        return None
        
    testMode = int(testMode,8)

    st = os.stat(filepath)
    curMode = stat.S_IMODE(st.st_mode)

    # if we are a *directory*, we need to make sure that *if* read is allowed for the directory, execute is
    if stat.S_ISDIR(st.st_mode):
        newModes=[]
        if (testMode & stat.S_IRUSR) and not (testMode & stat.S_IXUSR):
            testMode = testMode | stat.S_IXUSR
            newModes.append("owner")
        if (testMode & stat.S_IRGRP) and not (testMode & stat.S_IXGRP):
            testMode = testMode | stat.S_IXGRP
            newModes.append("group")
        if (testMode & stat.S_IROTH) and not (testMode & stat.S_IXOTH):
            testMode = testMode | stat.S_IXOTH
            newModes.append("other")
        if newModes:
            msg = "'%s' is a directory - adding execute permission because read permissions are allowed for %s" % (filepath, ', '.join(newModes))
            logger.log_notice(MODULE_NAME, msg) 
            
    #msg = "%s is currently set to '%s'" % (filepath, curMode)
    #logger.log_debug(MODULE_NAME, msg) 

    msg = "Checking to see if current permissions '%.3o' are equal to or more restrictive than '%.3o'" % (curMode, testMode)
    #logger.log_debug(MODULE_NAME, msg) 

    # Short circuit  - Are Permissions equal?
    if curMode == testMode:
        msg = "%s - Current permissions '%0.3o' are equal to the expected " \
              "permissions '%.3o'" % (filepath, curMode, testMode)
        logger.log_info(MODULE_NAME, msg) 
        return retval

    otherMask = isOTH(curMode, testMode)
    groupMask = isGRP(curMode, testMode)
    userMask  = isUSR(curMode, testMode)
    specialMask = isSpecial(curMode, testMode)
    fullMask = otherMask|groupMask|userMask|specialMask
          
    if fullMask:
        isExcluded = False
        if not ignoreExcludes:
            isExcluded, whyExcluded = sb_utils.file.exclusion.file_is_excluded(filepath)
        if isExcluded:
            msg = whyExcluded
            logger.log_info(MODULE_NAME, whyExcluded)
        else:
            msg = "%s - Current permissions '%3o' are more permissive "\
              "than '%3o'" % (filepath, curMode, testMode)
            logger.log_warn(MODULE_NAME, msg)
            retval = False
    else:
        msg = "%s - Current permissions '%3o' are more restrictive "\
              "than '%3o'" % (filepath, curMode, testMode)
        logger.log_debug(MODULE_NAME, msg) 
  
    return retval


##############################################################################
def getXttr(filepath):

    if testFile(filepath) == False:
        return ''

    if sb_utils.os.info.is_solaris() == True:
        msg = "Extended File Attributes - Not applicable in Solaris"
        logger.log_info(MODULE_NAME, msg) 
        return ''
 
    results = sb_utils.os.software.is_installed(pkgname='e2fsprogs')
    if results == False:
        msg = "'e2fsprogs' package is not installed"
        logger.log_err(MODULE_NAME, msg) 
        return ''
      

    if not os.path.exists('/usr/bin/lsattr'):
        msg = "'/usr/bin/lsattr' does not exist"
        logger.log_err(MODULE_NAME, msg) 
        return ''

    cmd = "/usr/bin/lsattr %s" % filepath
    out = tcs_utils.tcs_run_cmd(cmd, True)
    
    if out[0] != 0 or not out[1] :
        msg = "Unable to get file attributes: %s" % str(out[2])
        logger.log_err(MODULE_NAME, msg) 
        return ''

    return out[1].split()[0].strip()

##############################################################################
def setXttr(filepath, immutable = False):

    if testFile(filepath) == False:
        return False

    if sb_utils.os.info.is_solaris() == True:
        msg = "Extended File Attributes - Not applicable in Solaris"
        logger.log_info(MODULE_NAME, msg) 
        return False
 
    results = sb_utils.os.software.is_installed(pkgname='e2fsprogs')
    if results == False:
        msg = "'e2fsprogs' package is not installed"
        logger.log_err(MODULE_NAME, msg) 
        return False
      

    if not os.path.exists('/usr/bin/lsattr'):
        msg = "'/usr/bin/lsattr' does not exist"
        logger.log_err(MODULE_NAME, msg) 
        return False

    if immutable == True:
        cmd = "/usr/bin/chattr +i %s" % filepath
    else:
        cmd = "/usr/bin/chattr -i %s" % filepath

    out = tcs_utils.tcs_run_cmd(cmd, True)
    if out[0] != 0  :
        msg = "Unable to set file attributes: %s" % str(out[2])
        logger.log_err(MODULE_NAME, msg) 
        return False

    return True

def isImmutable(filepath):
    flags = getXttr(filepath)
    try:
        if flags[4] == 'i':
            msg = "%s - immutable attribute is ON" % (filepath)
            logger.log_info(MODULE_NAME, msg) 
            return True
        else:
            msg = "%s - immutable attribute is off" % (filepath)
            logger.log_info(MODULE_NAME, msg) 
            return False    
    except IndexError:
        msg = "%s - unable to determine immutable attribute state" % (filepath)
        logger.log_err(MODULE_NAME, msg) 
        return False

##############################################################################
def isACL(filepath):
    # Check to see if anything besides base ACLs are set...

    if testFile(filepath) == False:
        return None

    if sb_utils.os.info.is_solaris() == True:
        cmd = "/bin/getfacl -s %s" % filepath
    else:
        cmd = "/usr/bin/getfacl -c -s %s" % filepath

    out = tcs_utils.tcs_run_cmd(cmd, True)
    if out[0] != 0:
        msg = "Unable to get ACL: %s" % str(out[2])
        logger.log_err(MODULE_NAME, msg) 
        return None

    if len(out[1]) > 0:
        return True
    else:
        return False

##############################################################################
def getACL(filepath):
    # Check to see if anything besides base ACLs are set...

    if testFile(filepath) == False:
        return None

    aclDict = {}
    if sb_utils.os.info.is_solaris() == True:
        cmd = "/bin/getfacl -c %s" % filepath
    else:
        cmd = "/usr/bin/getfacl -c -e %s" % filepath

    out = tcs_utils.tcs_run_cmd(cmd, True)
    if out[0] != 0:
        msg = "Unable to get ACL: %s" % str(out[2])
        logger.log_err(MODULE_NAME, msg) 
        return None

    for aclEntry in out[1].split('\n'):
        if aclEntry == '':
            continue

        try:
            effectiveACL = aclEntry.split()[1].strip()
        except IndexError:
            effectiveACL = ''

        aclEntry = aclEntry.split()[0]

        (name, aclObject, perms) = aclEntry.split(':')
        if aclObject == '':
            aclObject = 'base'

        if effectiveACL != '':
            if effectiveACL.startswith('#effective'):
                try:
                    effectiveACL = effectiveACL.split(':')[1]
                except IndexError:
                    effectiveACL = perms
        else: 
            effectiveACL = perms 

        if not aclDict.has_key(name):
            aclDict[name] = {}

        aclDict[name][object] = "%s|%s" % (perms, effectiveACL)

    return aclDict


if __name__ == '__main__':
    logger.error("FOO","TEST")
    print isPermOkay('/tmp/zip1', '0740') 
    print "%.3o" % findMaximumPermittedDACs(currentDACs = "0440", allowedDACs = "0777")
    #print isImmutable(filepath='/etc/jamie')
    #print getACL(filepath='/etc/jamie')
