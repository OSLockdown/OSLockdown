#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import platform

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class DisableUSB:
    """
    Disable the USB and PCMCIA subsystems.
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'DisableUSB'
        self.__target_file = '/boot/grub/grub.conf'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, optionDict):
        """Expect either a one or a two"""

        if not optionDict or not 'usbDevices' in optionDict:
            return 1
        try:
            value = int(optionDict['usbDevices'])
        except ValueError:
            return 1
        if value < 1 or value > 2:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict=None):
        """
        Analyze grub.conf for proper USB and PCMICA kernel settings
        """
        test_arch = platform.machine()
        if test_arch == 's390x':
            msg = "GRand Unified Bootloader (GRUB) not used on S390 hardware, "\
                  "unable to inform the kernel not to load USB support."
            self.logger.warn(self.module_name, "Not Applicable: " + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['usbDevices']
        option = int(option)

        # For RHEL4/FC4 check for PCMCIA module...
        # NOTE: We don't check for kernel-pcmcia-cs because we won't remove it
        #       anyways (cannot undo remove)
        #       RHEL5 uses pcmciautils which can only be disabled by
        #       uninstalling the package (udev workaround possible)
 
        cmd = '/bin/grep "release 5" /etc/redhat-release'
        output = tcs_utils.tcs_run_cmd(cmd, True)
        
        # RHEL 4 PCMCIA check
        # NOTE: This requires testing on RHEL4
        if output[0] != 0:
            cmd = "/bin/rpm -q pcmcia-cs"
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] == 0:
                cmd = "/sbin/chkconfig pcmcia"
                output = tcs_utils.tcs_run_cmd(cmd, True)
                if output[0] == 0:
                    msg = 'Scan Failed: chkconfig reports pcmcia is on'
                    self.logger.info(self.module_name, msg)
                    return 'Fail', msg
        
        # RHEL 5 PCMCIA check
        # NOTE: This might work with RHEL4 as well. Need to verify with RedHat
        #       if this way of disabling PCMCIA is valid
        else:
            cmd = "/sbin/grubby --info=`/sbin/grubby --default-kernel` "
            cmd += "| /bin/grep nopcmcia=1"
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] != 0:
                msg = "PCMCIA not disabled in kernel"
                self.logger.warn(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

        # Checking if USB is disabled in default kernel
        if option == 1:
            cmd = "/sbin/grubby --info=`/sbin/grubby --default-kernel` | /bin/grep nousb"
        else:
            cmd = "/sbin/grubby --info=`/sbin/grubby --default-kernel` | /bin/grep nousbstorage"

        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] != 0:
            msg = "USB not disabled in kernel"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''        


    ##########################################################################
    def apply(self, optionDict=None):
        """
        Update grub.conf with correct parameters
        """

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, ''
        option = optionDict['usbDevices']

        # Note: Not that this case can even exist, but keeping it for
        #       standard's sake
        
        cmd = '/bin/grep "release 5" /etc/redhat-release'
        output = tcs_utils.tcs_run_cmd(cmd, True)
        
        # RHEL 4 PCMCIA
        # NOTE: This requires testing on RHEL4
        if output[0] != 0:
            cmd = "/bin/rpm -q pcmcia-cs"
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] == 0:
                cmd = "/sbin/chkconfig pcmcia off"
                output = tcs_utils.tcs_run_cmd(cmd, True)
                if output[0] != 0:
                    msg = 'Failed to disable pcmcia'
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        # Checking if USB is disabled in default kernel
        cmd = "/sbin/grubby --info=`/sbin/grubby --default-kernel` "
        cmd += "| /bin/grep nousb"
        output = tcs_utils.tcs_run_cmd(cmd, True)
        if output[0] != 0:
            opt = str(option) 
            if opt == '1':
                cmd = "/sbin/grubby --update-kernel=`/sbin/grubby --default-kernel` "
                cmd += "--args='nousb nopcmcia=1'"
                output = tcs_utils.tcs_run_cmd(cmd, True)
            elif opt == '2':
                cmd = "/sbin/grubby --update-kernel=`/sbin/grubby --default-kernel` "
                cmd += "--args='nousbstorage nopcmcia=1'"
                output = tcs_utils.tcs_run_cmd(cmd, True)
            else:
                msg = 'You must supply either a 1 or 2 as the option for %s' \
                % self.module_name
                raise tcs_utils.ActionError(msg)
            if output[0] != 0:
                msg = 'Failed to disable usb'
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        sb_utils.SELinux.restoreSecurityContext(self.__target_file)    
        msg = 'USB & PCMCIA disabled'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, 'disabled'


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        
        if not change_record or change_record != 'disabled':
            msg = 'unable to undo without valid change record'
            self.logger.error(self.module_name, 'Undo Error: ' +  msg)
            return 0
                   
        cmd = '/bin/grep "release 5" /etc/redhat-release'
        output = tcs_utils.tcs_run_cmd(cmd, True)
        
        # RHEL 4 PCMCIA
        # NOTE: This requires testing on RHEL4
        if output[0] != 0:
            cmd = "/bin/rpm -q pcmcia-cs"
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] == 0:
                cmd = "/sbin/chkconfig pcmcia on"
                output = tcs_utils.tcs_run_cmd(cmd, True)
                if output[0] != 0:
                    msg = 'Failed to enable pcmcia'
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        cmd = "/sbin/grubby --update-kernel=`/sbin/grubby --default-kernel` "
        cmd += "--remove-args 'nopcmcia=1 nousb nousbstorage'"
        output = tcs_utils.tcs_run_cmd(cmd, True)
        sb_utils.SELinux.restoreSecurityContext(self.__target_file)    
        if output[0] != 0:
            msg = 'Failed to remove disable USB/PCMCIA kernel arguments'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0
        
        msg = 'USB/PCMCIA service enabled'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
