#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module disables USB (mass storage) and PCMCIA support.
# It's RedHat counterpart offers two options: 1 or 2. The first
# will disable all USB devices and the second (2) will disable
# only USB storage devices.
#
# This has caused problems with many customers so, we are making
# the default to only disable storage devices.
#
# The Solaris variant (the one you are reading now) will simply
# prevent the USBA (Solaris USB architecture) compliant nexus driver
# from loading. This is accomplished by added the following line to
# /etc/system in the global zone:
#
# exclude: scsa2usb
#
# We also exclude the PCMCIA nexus driver by adding the following
# to /etc/system:
#
# exclude: pcmcia
#
# For more information, see the following:
# - man page scsa2usb(7D) and 
# - man page pcmcia(7D)
# - http://docs.sun.com/app/docs/doc/816-5177/scsa2usb-7d?a=view
# 



import sys
import os
import shutil

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.solaris
import sb_utils.os.software

class DisableUSB:

    def __init__(self):
        self.module_name = 'DisableUSB'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option_str):

        return 0


    ##########################################################################
    def scan(self, optionDict=None):

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to check /etc/system parameters in a non-global zone"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        msg = "Checking /etc/system for directives to exclude scsa2usb and pcmcia"
        self.logger.info(self.module_name, msg)
        try:
            infile = open('/etc/system', 'r')
        except IOError, err:
            msg = "Unable to read /etc/system: %s" % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        found_it1 = False
        found_it2 = False
        for line_nr, line in enumerate(infile.readlines()):
            line = line.strip()
            if not line.startswith('exclude:'):
                continue 
            else:
                excl_module = line.split(':')[1].strip()
                
                # Check for USB Driver/module...
                if excl_module == 'scsa2usb':
                    msg = "Found 'exclude: %s' in /etc/system, line %d" % \
                          (excl_module, line_nr)
                    self.logger.info(self.module_name, msg)
                    found_it1 = True
                    continue

                # Check for PCMCIA Driver/module...
                if excl_module == 'pcmcia':
                    msg = "Found 'exclude: %s' in /etc/system, line %d" % \
                          (excl_module, line_nr)
                    self.logger.info(self.module_name, msg)
                    found_it2 = True
                    continue

        infile.close()

        if found_it1 == False or found_it2 == False: 
            msg = "/etc/system is missing exclusion directives to prevent "\
                  "the loading of 'scsa2usb' and 'pcmcia' kernel modules (drivers)"
            self.logger.notice(self.module_name, 'Scan Failed:' + msg)
            return 'Fail', msg


        return 'Pass', ''        


    ##########################################################################
    def apply(self, optionDict=None):

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to change /etc/system parameters in a non-global zone"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        action_record = []
        tcs_utils.protect_file('/etc/system')
        failure_flag = False

        try:
            infile  = open('/etc/system', 'r')
            outfile = open('/etc/system.new', 'w')
        except IOError, err:
            msg = str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        found_it1 = False
        found_it2 = False
        for line_nr, line in enumerate(infile.readlines()):
            orig_line = line
            line = line.strip()
            if not line.startswith('exclude:'):
                outfile.write(orig_line)
                continue
            else:
                excl_module = line.split(':')[1].strip()

                # Check for USB Driver/module...
                if excl_module == 'scsa2usb':
                    msg = "Found 'exclude: %s' in /etc/system, line %d" % \
                          (excl_module, line_nr)
                    self.logger.info(self.module_name, msg)
                    found_it1 = True
                    outfile.write(orig_line)
                    continue

                # Check for PCMCIA Driver/module...
                if excl_module == 'pcmcia':
                    msg = "Found 'exclude: %s' in /etc/system, line %d" % \
                          (excl_module, line_nr)
                    self.logger.info(self.module_name, msg)
                    found_it2 = True
                    outfile.write(orig_line)
                    continue

        infile.close()
        # If exclusion directives were not found, append them
        if found_it1 == False: 
            newline = "\n* Added by OS Lockdown\nexclude: scsa2usb\n\n"
            outfile.write(newline)
            action_record.append(newline)
            msg = "Added 'exclude: scsa2usb' to /etc/system"
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
              

        if found_it2 == False: 
            newline = "\n* Added by OS Lockdown\nexclude: pcmcia\n\n"
            outfile.write(newline)
            action_record.append(newline)
            msg = "Added 'exclude: pcmcia' to /etc/system"
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
 
        outfile.close()
        if found_it1 == False or found_it2 == False:
            try:
                shutil.copymode('/etc/system', '/etc/system.new')
                shutil.copy2('/etc/system.new', '/etc/system')
            except OSError:
                msg = "Unable to replace /etc/system with new version."
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                failure_flag = True

        try:
            os.unlink('/etc/system.new')
        except IOError, err:
            msg = "Unable to remove working file /etc/system.new"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
 
        if failure_flag == True:
            msg = "Unable to disable USB mass storage & PCMCIA support"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return 0, ''

        
        if found_it1 == False or found_it2 == False:
            msg = 'USB mass storage & PCMCIA support disabled'
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            return 1, ''.join(action_record)
        else:
            msg = "USB mass storage & PCMCIA support is already disabled in "\
                  "/etc/system. If subsequent scans with this module report a "\
                  "failure, then you must reboot the system for the apply to "\
                  "affect."
            self.logger.info(self.module_name, msg)
            return 0, ''


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        zonename = sb_utils.os.solaris.zonename()
        if zonename != 'global':
            msg = "Unable to change /etc/system parameters in a non-global zone"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ZoneNotApplicable('%s %s' % (self.module_name, msg))

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            infile  = open('/etc/system', 'r')
            lines = infile.readlines()
            infile.close()
        except IOError, err:
            msg = str(err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        linesToRemove = []
        for removeLine in change_record.split('\n'):
            if removeLine.strip() == '':
                continue
            linesToRemove.append(removeLine)

        try:
            outFile  = open('/etc/system', 'w')
        except IOError, err:
            msg = str(err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for line in lines:
            if line.strip() not in linesToRemove:
                outFile.write(line)
        
        outFile.close()

        msg = 'USB mass storage and PCMCIA support enabled'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
