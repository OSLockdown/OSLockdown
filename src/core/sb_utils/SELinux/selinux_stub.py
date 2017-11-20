##############################################################################
# Copyright (c) 2010-2011 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
# This is a stub class for boxes that do not have the python bindings installed.  This may be because SELinux doesn't exist for that
# distro (Solaris, SUSE 10,..) or because the python bindings don't exist (RH4). 

# Note that we're providing thesecurity_getenforce() and security_getpolicytype() routines only here.  These are the only routines
# we need to use from the selinux Python api.  To simulate them we're spawning off a call to '/usr/sbin/sestatus' and parsing the 
# output to get the current state/policy entries.

import os, commands

class selinux_stub:

    def __init__(self) :
        """
        Parse the sestatus output to figure out our status
        If 'SELinux status:' is disabled, we don't need to do anything more, just force the 'disabled' values
        Otherwise we assume enabled, and parse for the remaining fields.   
        """
        
        if "getenforce_value" not in dir(selinux_stub):
            self.initValues()

    def initValues(self):
        # default values are for disabled, no policy
        selinux_stub.getenforce_value = -1
        selinux_stub.getpolicytype_value = [-1, "" ]
                
        SESTATUS = "/usr/sbin/sestatus"
        if os.path.exists(SESTATUS):
            status, output = commands.getstatusoutput(SESTATUS)
            for rawline in output.splitlines():
                line = rawline.strip()
                if line.startswith("SELinux status:"):
                    if line.split()[-1] == 'disabled':
                        selinux_stub.getenforce_value = -1
                        selinux_stub.getpolicytype_value = [-1, "" ]
                        break
                elif line.startswith("Current mode:"):
                    if line.split()[-1] == 'enforcing':
                        selinux_stub.getenforce_value = 1
                    else:
                        selinux_stub.getenforce_value = 0
                elif line.startswith("Policy from config file:"):
                    selinux_stub.getpolicytype_value = line.split()[-1]
                                                                        
       
    # Normally, -1 = Disabled/error, 0 = permissive, and 1 = enforcing
    
def security_getenforce():
    stub = selinux_stub()
    return stub.getenforce_value
  
def selinux_getpolicytype():
    stub = selinux_stub()
    return stub.getpolicytype_value
