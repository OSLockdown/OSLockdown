#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import os
import sys
import re

import software
import info

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()

MODULE_NAME = "OS.Service"

##############################################################################
# Determine if service configured to start at boot 
##############################################################################
def is_enabled(svcname=None):
    """Determine if a service is enabled"""

    if svcname == None:
        return None

    #
    # Solaris Operating System (svcprop)
    #
    if info.is_solaris() == True:
       if not os.path.isfile('/usr/bin/svcprop'):
          return None

       cmd = '/usr/bin/svcprop -p restarter/state %s' % svcname
       msg = "Executing: %s" % cmd
       logger.info(MODULE_NAME, msg)

       output = tcs_utils.tcs_run_cmd(cmd, True)
       if output[0] != 0:
           msg = """Solaris: %s: %s """ % (svcname, output[2] )
           logger.debug(MODULE_NAME, msg)
           if "Couldn't find property group" in output[2]:
               msg = "No restarter/state property; using svcs(1) command instead."
               logger.debug(MODULE_NAME, msg)
               cmd = "/usr/bin/svcs %s" % svcname
               toutput = tcs_utils.tcs_run_cmd(cmd, True)
               if toutput[0] != 0:
                   return None
               else:
                   output = []
                   output.append('0')
                   output.append(toutput[1].split('\n')[1])
           else:
               return None

       if output[1].startswith('online'):
           msg = 'Solaris: %s is online' % (svcname)
           logger.info(MODULE_NAME, msg)
           return True

       if output[1].startswith('maintenance'):
           msg = 'Solaris: %s is in maintenance state' % (svcname)
           logger.info(MODULE_NAME, msg)
           return True

       # This is confusing but 'offline' means it is not
       # running but it is enabled.  Huh?!?
       #   Offline - "The service is enabled but has not yet reached the online 
       #   state. It is either in the process of starting up, or the dependencies 
       #   of the service are not yet online."
       if output[1].startswith('offline'):
           msg = 'Solaris: %s is offline' % (svcname)
           logger.info(MODULE_NAME, msg)
           return True

       if output[1].startswith('disabled'):
           msg = 'Solaris: %s is disabled' % (svcname)
           logger.info(MODULE_NAME, msg)
           return False

       if output[1].startswith('enabled'):
           msg = 'Solaris: %s is enabled' % (svcname)
           logger.info(MODULE_NAME, msg)
           return True

       if output[1].startswith('uninitialized'):
           msg = 'Solaris: %s is uninitialized' % (svcname)
           logger.info(MODULE_NAME, msg)
           return False

    #
    # Linux Operating System (chkconfig)
    #
    ## TODO: Ubuntu Support
    #    - NOTE: Ubuntu will use 'update-rc.d' utility
    #            to enable/disable however, we will need
    #            check the /etc/rcX.d/ directories.


    ##
    ## Red Hat 4.8 xinetd services report slighlty different
    ##
    cpe = info.getCpeName() 
    if float(cpe.split(':')[4]) == 4.8:
        cmd1 = "/sbin/chkconfig --list %s" % svcname
        rhel48_out = tcs_utils.tcs_run_cmd(cmd1, True)
        results = rhel48_out[1].strip()
        if results.endswith('\ton'):
            return True
        if results.endswith('\toff'):
            return False

    # Normal check
    cmd = "/sbin/chkconfig %s" % svcname
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        return False

    ## SUSE's chkconfig returns zero if the services is disabled
    ## or enabled despite what the man page says. So, we must
    ## parse the output which it sent.
    if info.is_LikeSUSE() == True:
        if output[1].endswith(' on\n'):
           msg = """Linux: chkconfig reports that '%s' is enabled (on)""" % (svcname)
           logger.info(MODULE_NAME, msg)
           return True
        if output[1].endswith(' off\n'):
           msg = """Linux: chkconfig reports that '%s' is disabled (off)""" % (svcname)
           logger.info(MODULE_NAME, msg)
           return False

        if output[1].endswith(' xinetd\n'):
            cmd = "/sbin/chkconfig -list %s" % svcname
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] != 0:
               return False

            if output[1].endswith(' on\n'):
                msg = """Linux: chkconfig reports that '%s' is enabled (on)""" % (svcname)
                logger.info(MODULE_NAME, msg)
                return True

            if output[1].endswith(' off\n'):
                msg = """Linux: chkconfig reports that '%s' is disabled (off)""" % (svcname)
                logger.info(MODULE_NAME, msg)
                return False

    else:
        msg = """Linux: chkconfig reports that '%s' is enabled""" % (svcname)
        logger.info(MODULE_NAME, msg)
        return True


##############################################################################
# Disable Service
##############################################################################
def disable(svcname=None):

    if svcname == None:
        return None

    #
    # Solaris Operating System (svcadm)
    #
    if info.is_solaris() == True:
       if not os.path.isfile('/usr/sbin/svcadm'):
           return None

       cmd = '/usr/sbin/svcadm disable %s' % svcname
       output = tcs_utils.tcs_run_cmd(cmd, True)
       msg = 'Solaris: %s' % output[2]
       if output[0] != 0:
           logger.debug(MODULE_NAME, msg)
           return False
       else:
           msg = """Solaris: 'svcadm disable %s' successful""" % svcname
           logger.debug(MODULE_NAME, msg)
           return True

    #
    # Linux Operating System (chkconfig)
    #
    pattern = re.compile('insserv: Service .* has to be enabled')
    cmd = "/sbin/chkconfig %s off" % svcname
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = """Linux: %s """ % output[2]
        logger.debug(MODULE_NAME, msg)
        if info.is_LikeSUSE() != True:
           return False

        if not pattern.search(output[2]):
           return False

        msg = "Error detected, trying alternative insserv(8) utility with force option (-f)..."
        logger.debug(MODULE_NAME, msg)

        cmd = "/sbin/insserv -f -r -d %s " % svcname
        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] != 0:
            msg = """Linux: %s """ % output[2]
            logger.debug(MODULE_NAME, msg)
            return False
        else:
            msg = """Linux: 'insserv -f -r -d %s' was successful""" % svcname
            logger.debug(MODULE_NAME, msg)
            return True

    else:
        msg = """Linux: 'chkconfig %s off' successful""" % svcname
        logger.debug(MODULE_NAME, msg)
        return True

    return False

###############################################################################
# Enable Service
###############################################################################
def enable(svcname=None):

    if svcname == None:
        return None

    #
    # Solaris Operating System (svcadm)
    #
    if info.is_solaris() == True:
       if not os.path.isfile('/usr/sbin/svcadm'):
           return None

       cmd = '/usr/sbin/svcadm enable -r %s' % svcname
       output = tcs_utils.tcs_run_cmd(cmd, True)
       msg = 'Solaris: %s' % output[2]
       if output[0] != 0:
           logger.debug(MODULE_NAME, msg)
           return False
       else:
           msg = """Solaris: 'svcadm enable -r %s' was successful""" % svcname
           logger.debug(MODULE_NAME, msg)
           return True

    #
    # Linux Operating System (chkconfig)
    #
    pattern = re.compile('insserv: Service .* has to be enabled')
    cmd = "/sbin/chkconfig %s on" % svcname
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = """Linux: %s """ % output[2]
        logger.debug(MODULE_NAME, msg)
        if info.is_LikeSUSE() != True:
           return False

        if not pattern.search(output[2]):
           return False

        msg = "Error detected, trying alternative insserv(8) utility with force option (-f)..."
        logger.debug(MODULE_NAME, msg)

        cmd = "/sbin/insserv -f -d %s " % svcname
        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] != 0:
            msg = """Linux: %s """ % output[2]
            logger.debug(MODULE_NAME, msg)
            return False
        else:
            msg = """Linux: 'insserv -f -d %s' was successful""" % svcname
            logger.debug(MODULE_NAME, msg)
            return True

    else:
        msg = """Linux: 'chkconfig %s on' was successful""" % svcname
        logger.debug(MODULE_NAME, msg)
        return True

    return False


###############################################################################
# Get Solaris Service Property
###############################################################################
def getprop(svcname=None, property=None):

    if svcname == None or property == None:
        return None

    if info.is_solaris() == False:
        return None

    if not os.path.isfile('/usr/bin/svcprop'):
        return None

    cmd = '/usr/bin/svcprop -p %s %s' % (property, svcname)
    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        msg = "Solaris: '%s' failed: %s" % (cmd, output[2])
        logger.debug(MODULE_NAME, msg)
        return None
    else:
        msg = "Solaris: '%s' succeeded: %s" % (cmd, output[1])
        logger.debug(MODULE_NAME, msg)
        return output[1].rstrip('\n')


###############################################################################
# Is it a Solaris service?
###############################################################################
def is_service(svcname=None):

    if svcname == None:
        return None

    if info.is_solaris() == False:
        return None

    if not os.path.isfile('/usr/bin/svcs'):
        return None

    pattern = re.compile('svcs: Pattern .* doesn\'t match any instances')
    cmd = '/usr/bin/svcs %s' % (svcname)
    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        if pattern.search(output[2]):
            return False
    else:
        return True

###############################################################################
# Starting, stopping, restarting, and getting status services
# - Unable the disable/enable functions which only use chkconfig to configure
#   a Linux service for boot time, these functions actually perform the function
#   rather than waiting for a reboot.
###############################################################################
def start(svcname=None):
    """Start a service: return True if successful or False if failed"""

    if svcname == None:
        return False

    if info.is_solaris() == True:
        return enable(svcname=svcname)

    if not os.path.isfile('/sbin/service'):
        msg = "Could not find the /sbin/service command."
        logger.error(MODULE_NAME, msg)
        return False

    cmd = '/sbin/service %s start' % (svcname)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Unable to start '%s': %s" % (svcname, output[2])
        logger.error(MODULE_NAME, msg)
        return False
    else:
        msg = "Successfully started service '%s': %s" % (svcname, output[1].rstrip())
        logger.notice(MODULE_NAME, msg)
        return True

def stop(svcname=None):
    """Stop a service: return True if successful or False if failed"""

    if svcname == None:
        return False

    if info.is_solaris() == True:
        return disable(svcname=svcname)

    if not os.path.isfile('/sbin/service'):
        msg = "Could not find the /sbin/service command."
        logger.error(MODULE_NAME, msg)
        return False

    cmd = '/sbin/service %s stop' % (svcname)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Unable to stop '%s': %s" % (svcname, output[2])
        logger.error(MODULE_NAME, msg)
        return False
    else:
        msg = "Successfully stopped service '%s': %s" % (svcname, output[1].rstrip())
        logger.notice(MODULE_NAME, msg)
        return True

def restart(svcname=None):
    """Restart a service: return True if successful or False if failed"""

    if svcname == None:
        return False

    if info.is_solaris() == True:
        disable(svcname=svcname)
        return enable(svcname=svcname)

    if not os.path.isfile('/sbin/service'):
        msg = "Could not find the /sbin/service command."
        logger.error(MODULE_NAME, msg)
        return False

    cmd = '/sbin/service %s restart' % (svcname)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Unable to stop '%s': %s" % (svcname, output[2])
        logger.error(MODULE_NAME, msg)
        return False
    else:
        msg = "Successfully restarted service '%s': %s" % (svcname, output[1].rstrip())
        logger.notice(MODULE_NAME, msg)
        return True

def status(svcname=None):
    """Status of  service: return True if successful or False if failed"""

    if svcname == None:
        return None

    if info.is_solaris() == True:
        return None

    if not os.path.isfile('/sbin/service'):
        msg = "Could not find the /sbin/service command."
        logger.error(MODULE_NAME, msg)
        return False

    cmd = '/sbin/service %s status' % (svcname)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Status of service '%s': (Return Code=%s) %s" % (svcname, output[0], output[2].rstrip())
        logger.notice(MODULE_NAME, msg)
        return False
    else:
        msg = "Status of service '%s': (Return Code=%s) %s" % (svcname, output[0], output[1].rstrip())
        logger.notice(MODULE_NAME, msg)
        return True


###############################################################################
# Set Solaris Service Property
###############################################################################
def setprop(svcname=None, property=None, propval=None):
    """
    Set a Solaris service property, return the following:
        None  - if it couldn't do anything (missing params or commands) 
        True  - Successful
        False - Unsuccessful
    """

    if svcname == None or property == None or propval == None:
        return None

    if info.is_solaris() == False:
        return None

    if not os.path.isfile('/usr/sbin/svccfg'):
        return None

    # Example format of command:
    # svccfg -s service_fmri setprop property = value

    cmd = """/usr/sbin/svccfg -s %s setprop %s = "%s" """ % \
               (svcname, property, propval)

    output = tcs_utils.tcs_run_cmd(cmd, True)

    if output[0] != 0:
        msg = "Solaris: '%s' failed: %s" % (cmd, output[2])
        logger.debug(MODULE_NAME, msg)
        return False
    else:
        msg = "Solaris: '%s' succeeded: %s" % (cmd, output[1])
        logger.debug(MODULE_NAME, msg)
        return True

if __name__ == '__main__':
    print is_enabled(svcname='xinetd')
    print is_enabled(svcname='gssftp')
