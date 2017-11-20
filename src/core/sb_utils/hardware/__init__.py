#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Get generic hardware information
#

import sys
import platform
import re
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
from sb_utils.os.info import *
import sbProps

import TCSLogger

logger = TCSLogger.TCSLogger.getInstance()


################################################################################
def getTotalMemory():
     """Report Memory on system in MB"""

     # Memory = Page size multiplied by the number of physical pages
     memoryPages = 1.0*(os.sysconf("SC_PHYS_PAGES")*os.sysconf("SC_PAGESIZE"))
     return int(round((memoryPages/1024)/1024))
 

################################################################################
def getCpuInfo():

    ###################
    ## Solaris check ##
    ###################
    if is_solaris() == True:
        cmd = '/usr/platform/%s/sbin/prtdiag' %  platform.machine()
        if not os.path.isfile(cmd):
            return None

        searchPattern = re.compile('^System Configuration:.*\((.*) X (.*)\)')
        vmwarePattern = re.compile('^System Configuration: VMware')
        output = tcs_utils.tcs_run_cmd(cmd, True)
        vmware_flag = False
        if output[0] == 0:
            for line in output[1].split('\n'):
                cpuInfo = searchPattern.match(line.strip())
                if cpuInfo and vmware_flag == False:
                    try:
                        del output
                        return {cpuInfo.group(2) : int(cpuInfo.group(1))}
                    except:
                        return {'unknown': 1}

                cpuInfo = vmwarePattern.search(line)
                if cpuInfo or vmware_flag == True:
                     vmware_flag = True
                     break
        del output
        # If VMware, we'll try the kstat chain.
        if vmware_flag == False:
            return {'unknown': 1}
        else:
            ds_pattern = re.compile(r'\s+')
            cmd = "/usr/bin/kstat -m cpu_info  -s brand -p"
            output = tcs_utils.tcs_run_cmd(cmd, True)
            cpuInfo = {}
            if output[0] == 0:
                for line in output[1].split('\n'):
                    if line.startswith('cpu_info:'):
                        cpuItem = line.split('\t')[-1]
                        cpuItem = cpuItem.strip()
                        cpuItem = re.sub(ds_pattern, ' ', cpuItem) 
                        if cpuInfo.has_key(cpuItem):
                            cpuInfo[cpuItem] = cpuInfo[cpuItem] + 1
                        else:
                            cpuInfo[cpuItem] = 1
            return cpuInfo

    ##################
    ## zSeries Check##
    ##################

    if platform.machine() == 's390x':
        try:
            infile = open('/proc/cpuinfo', 'r')
        except IOError, err:
            msg = "Unable to open /proc/cpuinfo %s" % (err)
            logger.log_err('sb_utils.hardware', msg)
            return {}
            
        cpuInfo = {}
        cpuItem = ""
        cpuCount = ""
        for line in infile.readlines():
            if line.startswith('vendor_id'):
                cpuItem = line.rstrip().split(':')[1].lstrip()
            elif line.startswith('# processors'):
                cpuCount = int(line.rstrip().split(':')[1].strip())
        infile.close()
        if cpuItem and cpuCount :
            cpuInfo[cpuItem] = cpuCount
        return cpuInfo
    

    #################
    ## Linux Check ##
    #################
    try:
        infile = open('/proc/cpuinfo', 'r')
    except IOError, err:
        msg = "Unable to open /proc/cpuinfo %s" % (err)
        logger.log_err('sb_utils.hardware', msg)
        return {}
        
    cpuInfo = {}
    for line in infile.readlines():
        if line.startswith('model name'):
            cpuItem = line.rstrip().split(':')[1].lstrip()
            while "  " in cpuItem:
                cpuItem = re.sub('  ', " ", cpuItem)
            if cpuInfo.has_key(cpuItem):
                cpuInfo[cpuItem] = cpuInfo[cpuItem] + 1
            else:
                cpuInfo[cpuItem] = 1

    infile.close()
    return cpuInfo 
 
##############################################################################
def is_xen_paravirt_domu():
    """
    Try and detect that we're running a paravirt domU xen instance, as certain
    utilities (dmidecode, biosdecode) don't run correctly there.  Return True if 
    we're a xen paravirt domU, False otherwise.   Basic code for the below was found the
    Red Hat virtualization support documentation. 
    """
    is_domu = False
    try:
        xencaps = open("/proc/xen/capabilities")
        for capline in xencaps.readlines():
            if capline.strip() == "control_d":
                raise IOError
        is_domu = True
        xencaps.close()
    except IOError:
        pass

    return is_domu
