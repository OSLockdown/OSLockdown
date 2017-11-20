#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.filesystem.scan
import sb_utils.file.fileperms

class SecureWorldWritableDevices:
    """
    SecureWorldWritableDevices Security Module handles the guidelines 
    for securing world-writable devices.
    """

    def __init__(self):
        self.module_name = "SecureWorldWritableDevices"
        self.__target_file = sb_utils.filesystem.scan.SCAN_RESULT
        self.__specialFiles = []
        self.__requiredPerms = 0666
        self.__requiredOwner = 0
        self.__requiredGroup = 0

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    ##########################################################################
    def validate_input(self, optionDict):
        try:
            self.__specialFiles      = sb_utils.file.fileperms.splitStringIntoFiles(optionDict['specialDevices'])
        except ValueError:
            msg = "Invalid option value -> '%s'" % optionDict
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

    ##########################################################################
    def scan(self, optionDict=None):
        """
        Initiating File System Scan to find world-writable devices
        """
        specialDevices = {}
        messages = []
        retval = True
        retmsg = ''
          
        self.validate_input(optionDict)
        # Only run FS scan if it hasn't been run this scan
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        secure_world_writable_devices = True
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        device_list = []

        for line in lines:
            if not line.startswith('c|') and not line.startswith('b|'):
                continue

                                
            fields = line.rstrip('\n').split('|')
            if len(fields) != 6:
                continue
            
            # build a line of file to be handled separately
            if fields[5] in self.__specialFiles:
                msg = "Device '%s' is in list of 'special' device files - will be checked seperately" % fields[5] 
                self.logger.notice(self.module_name,  msg)
                specialDevices[fields[5] ] = { 'dacs':0666, 'owner':'root'}
                continue

            if fields[1][6] == 'X':
                try:
                    statinfo = os.stat(fields[5])
                except OSError, err:
                    msg = "Unable to stat %s: %s" % (fields[5], err)
                    self.logger.error(self.module_name, 'Scan Error: ' + msg)
                    continue

                if stat.S_IWOTH & statinfo.st_mode :
                    device_list.append(fields[5])
                    secure_world_writable_devices = False
                    msg = "%s is world-writeable" % fields[5]
                    self.logger.notice(self.module_name, "Scan Failed: " + msg)

            del fields
            
        change_record = {}
        for testdevice in device_list:

            try:
                statinfo = os.stat(testdevice)
                changes_to_make = {'dacs':statinfo.st_mode & ~stat.S_IWOTH}
                change_record.update(sb_utils.file.fileperms.change_file_attributes( testdevice, changes_to_make, options= {'checkOnly': True}))
                
            except (OSError, IOError), err:
                msg = "Unable to change mode on %s: %s" % (testdevice, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                continue

        if specialDevices:
            change_record.update(sb_utils.file.fileperms.change_bulk_file_attributes(specialDevices, options = {'checkOnly':True, 'exactDACS':True}))

        if change_record:
            retval = False
            retmsg = 'Insecure world-writable devices exist'
            
        return retval, retmsg, {'messages':messages}

    ##########################################################################
    def apply(self, optionDict=None):
        """Remove world-writable status"""

        specialDevices = {}
        messages = []
        retval = False


        # Only run FS scan if it hasn't been run this scan
        self.validate_input(optionDict)
        if tcs_utils.fs_scan_is_needed():
            sb_utils.filesystem.scan.perform()
            if not os.path.isfile(self.__target_file):
                msg = "Unable to find %s" % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            # let others know we ran the fs scanner
            tcs_utils.update_fs_scanid()

        secure_world_writable_devices = True

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()

        device_list = []
        for line in lines:
            if not line.startswith('c|') and not line.startswith('b|'):
                continue

            fields = line.rstrip('\n').split('|')
            if len(fields) != 6:
                continue

            # build a line of file to be handled separately
            if fields[5]  in self.__specialFiles:
                msg = "Device '%s' is in list of 'special' device files - will be checked seperately" % fields[5] 
                self.logger.notice(self.module_name,  msg)
                specialDevices[fields[5] ] = { 'dacs':0666, 'owner':'root'}
                continue

            if fields[1][6] == 'X':
                try:
                    statinfo = os.stat(fields[5])
                except OSError, err:
                    msg = "Unable to stat %s: %s" % (fields[5], err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    continue

                if stat.S_IWOTH & statinfo.st_mode:
                    device_list.append(fields[5])
                    secure_world_writable_devices = False

            del fields

        change_record = {}

        # Remove world-writable status
        for testdevice in device_list:

            try:
                statinfo = os.stat(testdevice)
                changes_to_make = {'dacs':statinfo.st_mode & ~stat.S_IWOTH}
                change_record.update(sb_utils.file.fileperms.change_file_attributes( testdevice, changes_to_make))
                
            except (OSError, IOError), err:
                msg = "Unable to change mode on %s: %s" % (testdevice, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                continue

        if specialDevices:
            change_record.update( sb_utils.file.fileperms.change_bulk_file_attributes(specialDevices, options = {'checkOnly':False, 'exactDACS':True}))

        if change_record :
            retval = True

        return retval, str(change_record), {'messages':messages}
    ##########################################################################
    def undo(self, change_record=None):
        """Undo removal of world-writable status on devices"""

        retval = False
        messages = []
        msg = ''
        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
        
        # old style change record only had a list of device names, so we'll have to walk through this 
        # getting the current status of the device and adding the S_IWOTH bits
        else:
            if not change_record[0:200].strip().startswith('{') : # does it look like the start of a dictionary?
                changelist = change_record.split('\n')
                change_record = {}
                # remove empty last entry
                if not changelist[len(changelist)-1]:
                    del changelist[len(changelist)-1]

                for testdevice in changelist:
                    testdevice = testdevice.lstrip()
                    if not testdevice:
                        continue
 
                    try:
                        statinfo = os.stat(testdevice)
                        change_record[testdevice] = {'dacs':statinfo.st_mode|stat.S_IWOTH}
                        
                    except OSError:
                        msg = "Unable to stat device %s." % testdevice
                        self.logger.error(self.module_name, 'Undo Error: ' + msg)
                        continue

            sb_utils.file.fileperms.change_bulk_file_attributes(change_record)
            retval = True
            
        return retval, msg, {'messages':messages}

if __name__ == "__main__":
    test = SecureWorldWritableDevices()
    prof={'specialDevices':"/dev/null /dev/full /dev/random /dev/ptmx /dev/vsock /dev/tty /dev/X0R /dev/zero /selinux/null"}
    test.scan(prof)
