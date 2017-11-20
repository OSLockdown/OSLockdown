#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import shutil
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info
import sb_utils.SELinux

class DaemonUmask:
    """
    DaemonUmask Security Module sets the daemon umask to 027
    """

    def __init__(self):
        self.module_name = "DaemonUmask"

        if sb_utils.os.info.is_solaris() == True:
            self.__target_file = '/etc/default/init'
            self.__tmp_file = '/tmp/.init.tmp'
        else:
            if sb_utils.os.info.is_LikeSUSE():
                self.__target_file = '/etc/rc.status'
                self.__tmp_file = '/tmp/.rc.status'
            else:
                self.__target_file = '/etc/init.d/functions'
                self.__tmp_file = '/tmp/.funcions.tmp'

        self.logger = TCSLogger.TCSLogger.getInstance()

        self.orig_umask = "None"

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """
        Check the system's daemon umask
        """

        try:
            infile = open(self.__target_file, 'r')
        except IOError, err:
            msg = 'Scan Error: Unable to read %s: %s' % (self.__target_file, str(err))
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = 'Scanning %s for daemon umask of 027...' % (self.__target_file)
        self.logger.notice(self.module_name, msg)

        foundit = False

        if sb_utils.os.info.is_solaris() == True:
            pattern = "CMASK"
            delim   = '='
        else:
            pattern = "umask"
            delim   = ' '

        # We don't break out of the for loop after the first find
        # because we must find that last entry in the file.
        line_count = 0
        for inline in infile.readlines():
            line_count += 1
            line = inline.strip()

            if line.startswith(pattern):
                try:
                    self.orig_umask = line.split(delim)[1].rstrip('\n')
                    msg = "Scan: Found '%s' in %s, line number %d" % \
                       (line, self.__target_file, line_count)
                    self.logger.info(self.module_name, msg )
                    foundit = True
                except IndexError:
                    pass
                    

        infile.close()

        if foundit:
            # compare the digits of the umask with 027
            if self.orig_umask != '027':
                msg = 'daemon umask %s is insufficient' % self.orig_umask
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg
        else:
            msg = 'no daemon umask found'
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        return 'Pass', ''

    ##########################################################################
    def apply(self, option=None):
        """
        Set daemon umask to 027
        """


        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = 'Apply Error: %s' % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        foundit = False
        is_solaris = sb_utils.os.info.is_solaris()
        for line in origfile:
            if is_solaris == True:
                if str(line).startswith('CMASK'):
                    self.orig_umask = line.split('=')[1].rstrip('\n')
                    line = str('CMASK=027\n')
                    foundit = True
                    workfile.write(line)
                else:
                    workfile.write(line)
            else:
                if str(line).startswith('umask'):
                    self.orig_umask = line.split(' ')[1].rstrip('\n')
                    line = str('umask' + str(' 027') + ' \n')
                    foundit = True
                    workfile.write(line)
                else:
                    workfile.write(line)

        # stick the umask in if we didn't find it
        if not foundit:
            if sb_utils.os.info.is_solaris() == True:
                workfile.write('CMASK=027\n')
            else:
                workfile.write('umask 027\n')

        origfile.close()
        workfile.close()

        try:
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except (IOError, OSError), err:
            msg = "Apply Failed: %s" % err
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # save the original umask for the action record
        msg = 'daemon umask set to 027'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, str(self.orig_umask)
            
    ##########################################################################
    def undo(self, action_record=None):
        """Undo previous change application."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        try:
            origfile = open(self.__target_file, 'r')
        except (IOError, OSError), err:
            msg = "Undo Error: Unable to read %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = "Undo Error: Unable to create %s: %s" % (self.__tmp_file, err)
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        foundit = False
        is_solaris = sb_utils.os.info.is_solaris()
        for line in origfile:
            if is_solaris == True:
                if line.strip().startswith('CMASK'):
                    # found it
                    if action_record != "None":                    
                        workfile.write('CMASK=%s\n' % action_record)
                        foundit = True
                else: 
                    workfile.write(line)

            else:

                if line.strip().startswith('umask'):
                    # found it
                    if action_record != "None":
                        workfile.write('umask %s\n' % action_record)
                        foundit = True
                else:
                    workfile.write(line)


        # file didn't have the line - stick one in
        if not foundit and action_record != "None":
            if sb_utils.os.info.is_solaris() == True:
                workfile.write('CMASK=%s' % action_record)
            else:
                workfile.write('umask %s' % action_record)

        origfile.close()
        workfile.close()

        try:
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError, err:
            msg = "Unable to restore %s: %s" % (self.__tmp_file, str(err))
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            

        msg = 'reset daemon umask to original value of %s' % action_record
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

