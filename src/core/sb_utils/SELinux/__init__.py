#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Security-Enhanced Linux (SELinux) Functions
#
#
#


import os
import sys
import stat
import commands

sys.path.append('/usr/share/oslockdown')

import TCSLogger

try:
    import selinux
except ImportError:
    import selinux_stub as selinux
       
MODULE_NAME = "SELinux"

# We might be able to be more efficient here by use a Class to get some invariant details only once.  Things
# like current SELinux status, policy, and are we even supporting SELinux here at all....

# True if OS Lockdown supports SELinux on the current platform - has nothing to do with current SELinux status on the box
# For now - we support:
#   RedHat 4/5/6 (and derivatives)
#   Fedora 10/11/12/13
#
#

def _getSecStatus():
    try:
        value = selinux.security_getenforce()
    except:
        value = -1
    return value

def isSELinuxSupportedOnBox():
    supported = False
    
    # Ok, we've got an import loop going on if we try and call sb_utils.os.info routines, so explicitly look for
    # one of the release files to see if we support SELinux on this platform.
    for distFile in ['/etc/redhat-release', '/etc/centos-release', '/etc/fedora-release', '/etc/enterprise-release']:
        if os.path.exists(distFile):
            supported = True
    import sb_utils.os.info
#    if sb_utils.os.info.is_LikeRedHat() or sb_utils.os.info.is_fedora():
#        supported = True
    
    return supported
              
##############################################################################
# True if  we are *NOT* in disabled mode
def isSELinuxEnabled():
    retval = False
    if _getSecStatus() >= 0:
        retval = True
    return retval
    


##############################################################################
# True only if enforcing mode is on 
def isEnforcing():
    retval = False
    if _getSecStatus() == 1:
        retval = True
    return retval
    

##############################################################################
def SELinuxMode():
# return N/A if SELinux not available, or 'disabled', 'permissive', or 'enforcing' as required
    z = _getSecStatus()
    if z == 1 :
        mode = "enforcing"
    elif z == 0:
        mode = "permissive"
    elif z == -1:
        mode = "disabled"
    else:
        mode = "N/A" 
    return mode


def SELinuxPolicy():
    try:
        poltype = selinux.selinux_getpolicytype()
    except:
        poltype = ""
    return poltype,
    
def restoreSecurityContext(path, recursive=False):
    if isSELinuxEnabled() and isSELinuxSupportedOnBox():
        if 'getfilecon' in dir(selinux):
            restoreSecurityContext_api(path, recursive)
        else:
            restoreSecurityContext_noapi(path, recursive)

def getContext(path):
    context=None
    if isSELinuxEnabled() and isSELinuxSupportedOnBox():
        if 'getfilecon' in dir(selinux):
            context=getContext_api(path)
        else:
            context=getContext_noapi(path)
    return context
    
##############################################################################
# Spawn off a command to do the 'ls -Zd', then grab the 4
def getContext_noapi(path):
    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    context = None 
    if os.path.exists(path):
        cmd = "ls -Zd '%s' " % path
        status, output = commands.getstatusoutput(cmd)
        if status != 0:
            msg = "Unable to run '%s'" % cmd
            logger.error(MODULE_NAME, msg)
        else:
            context = output.strip().split()[3]
    else:
        msg = """OS Lockdown trying to get context of '%s' which does not exist."""% (path)
        logger.warn (MODULE_NAME, msg)                

    return context
    
##############################################################################
# Use the Python API  
def getContext_api(path):
    """
    restorecon() wrapper.
      
      returns context if present or None if there was a problem - note: *empty* string == no context for RHEL4
    """
    context = None 
    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()
    
    if os.path.exists(path):
        contextCurrent = ""
        notes = ""
        rpath = os.path.realpath(path)
        if rpath != path:
            notes = "(%s)" % rpath
        myerror = None
        try:
            context = selinux.getfilecon(rpath)[1]
        except:
            pass
    else:
        msg = """OS Lockdown trying to get context of '%s' which does not exist."""% (path)
        logger.warn (MODULE_NAME, msg)                
        
        
    return context
                
##############################################################################
# Spawn off a command to do the restorecon
def restoreSecurityContext_noapi(path, recursive=False):
    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    cmd = "/sbin/restorecon -F %s" % path
    status, output = commands.getstatusoutput(cmd)
    if status != 0:
        msg = "Unable to run %s" % cmd
        logger.error(MODULE_NAME, msg)
       
##############################################################################
# Use the Python API to try and be smart about doing restorecon 
def restoreSecurityContext_api(path, recursive=False):
    """
    restorecon() wrapper.
      path - can be a single string or a list
      returns True if successful or False if there was a problem
    """
    
    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()
    
    if type(path).__name__ == 'str' :
        if os.path.exists(path):
            contextCurrent = ""
            notes = ""
            rpath = os.path.realpath(path)
            if rpath != path:
                notes = "(%s)" % rpath
            myerror = None
            try:
                contextCurrent = selinux.getfilecon(rpath)[1]
            except:
                pass
            try:
                # unfortunately not all RH5 boxes have 'restorecon' as part of the python bindings.  Since we never
                # do this recursively, we'll explicitly do the matchpathcon/lsetfilecon ourselves.  
                mode = os.stat(rpath)[stat.ST_MODE]
                status, contextRestore = selinux.matchpathcon(rpath, mode)
                
                if status == 0 :
                    # On the advice of our inhouse SELinux experts, we are intentially disregarding a potential 'user' mismatch
                    # We know that especially for daemon processes in targetted mode we could be either user_u or system_u 
                    # depending on how the daemon started.
                    
                    if contextRestore.split(':')[1:] != contextCurrent.split(':')[1:]:
                        selinux.lsetfilecon(rpath, contextRestore)
                        if notes:
                            msg = """OS Lockdown reset context of '%s' (actually '%s') to '%s'"""% (path, notes, contextRestore)
                        else:
                            msg = """OS Lockdown reset context of '%s' to '%s'"""% (path, contextRestore)
                        
                        logger.info (MODULE_NAME, msg)                
                else:
                    myerror = "Unable to get default context for '%s'" % path
                                    
            except OSError, err:
                myerror = err
                
            if myerror != None:
                logger.error(MODULE_NAME, str(myerror))
                return False
        else:
            msg = """OS Lockdown trying to restore context of '%s' which does not exist."""% (path)
            logger.warn (MODULE_NAME, msg)                
            
        
    return


