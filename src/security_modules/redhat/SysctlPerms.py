#!/usr/bin/env python

#  Handles the guideline for file permissions
#  on the /etc/sysctl.conf file. Checks for existence of the file as well.
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

import os
import stat
import sys

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.file.fileperms

class SysctlPerms:
    """
    SysctlPerms Security Module handles the guideline for file permissions
    on the /etc/sysctl.conf file. Checks for existence of the file as well.
    """

    def __init__(self):
        self.module_name = "SysctlPerms"
        self.__target_file = '/etc/sysctl.conf'
        self.logger = TCSLogger.TCSLogger.getInstance()

        # Define default contents of /etc/sysctl.conf in case it is missing

        self.__sh_script  = """
# Created by OS Lockdown
# Kernel sysctl configuration file for Red Hat Linux
#
# For binary values, 0 is disabled, 1 is enabled.See sysctl(8) and
# sysctl.conf(5) for more details

# Controls IP packet forwarding
net.ipv4.ip_forward = 0

# Controls source route verification
net.ipv4.conf.default.rp_filter = 1

# Do not accept source routing
net.ipv4.conf.default.accept_source_route = 0

# Controls the System Request debugging functionality of the kernel
kernel.sysrq = 0

# Controls whether core dumps will append the PID to the core filename
# Useful for debugging multi-threaded applications
kernel.core_uses_pid = 1

# Controls the use of TCP syncookies
net.ipv4.tcp_syncookies = 1

# Controls the maximum size of a message, in bytes
kernel.msgmnb = 65536

# Controls the default maxmimum size of a mesage queue
kernel.shmmax = 4294967295

# Controls the maximum number of shared memory segments, in pages
kernel.shmall = 268435456
"""

    ##########################################################################        
    def validate_input(self, option):
        """valiate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################        
    def scan(self, option=None):
        """
        First checks for existence of the /etc/sysctl.conf file.
        Check the file permissions on /etc/sysctl.conf are not more permissive
        than 600.  Also check to see if owner/group is root:root.
        """

        if not os.path.isfile(self.__target_file):
            msg = 'Missing %s' % self.__target_file 
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        try:
            statinfo = os.stat(self.__target_file)
        except OSError: 
            reason = "Unable to stat file %s." % self.__target_file
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', msg

        if statinfo.st_mode & 0777 ^ 0600 != 0:
            reason = 'sysctl.conf has permissions of %o instead of 600' % \
                     stat.S_IMODE(statinfo.st_mode)
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        elif statinfo.st_uid != 0:
            reason = 'sysctl.conf has owner %d instead of 0 (root)' % \
                    statinfo.st_uid
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        elif statinfo.st_gid != 0:
            reason = 'sysctl.conf has group %d instead of 0 (root)' % \
                    statinfo.st_gid
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            return 'Fail', reason

        else:
            return 'Pass', ''

    ##########################################################################        
    def apply(self, option=None):
        """
        If absent creates an /etc/sysctl.conf
        Modify the file permissions on the file /etc/sysctl.conf to be 600,
        and the owner/group to be root:root.
        """
        
        result, reason = self.scan()
        change_record = {}
        if result == 'Pass':
            return 0, ''
        
     
        changes_to_make = {'owner':'root',
                           'group':'root',
                           'dacs':0600}
        change_record = sb_utils.file.fileperms.change_file_attributes( self.__target_file, changes_to_make)


#        action_record = '%d:%d:%d' % (stat.S_IMODE(statinfo.st_mode), statinfo.st_uid, statinfo.st_gid)


        if change_record == {}:
            return 0, ''
        else:
            return 1, str(change_record)
            
    ##########################################################################        
    def undo(self, change_record=None):
        """
        Reset the file permissions on the file /etc/sysctl.conf to previous
        value.
        """

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "mode|uid|gid\n"  - mode should be interpreted as decimal
        # If so, convert that into the new dictionary style, and we know the filename already
        if not change_record[0:200].strip().startswith('{') and len(change_record.split(':')) == 3:
            fspecs = change_record.split(':')
            change_record = {}
            if len(fspecs) == 3:
                change_record[self.__target_file] = {'owner':fspecs[1],
                                                     'group':fspecs[2],
                                                     'dacs':int(fspecs[0], 10)}
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

