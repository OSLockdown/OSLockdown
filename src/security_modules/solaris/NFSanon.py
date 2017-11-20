#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module ensures that NFS shares specified in /etc/dfs/dfstab
# map anononmous uid/gid map to either 65534/65535 or disable it
# completely by setting anon to -1.
#
# If a share line in /etc/dfs/dfstab has something like '-o anon=100'
# then it fail. Because anon needs to be -1, 60001, 65534, or 65535.
#
# If no 'anon' option is set at all, it will pass but log the fact
# that system defaults are being used.
#
# Of course, if there are no NFS shares then the module will pass.
#
# Finally, if an absolute path for the share command is not specified
# the module will log it during scan and correct it during apply.
#

import sys
import shutil
import os
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class NFSanon:

    def __init__(self):
        self.module_name = "NFSanon"


        self.__target_file = '/etc/dfs/dfstab'
        self.__tmp_file = '/tmp/.dfs.tmp'

        # anon option can be set to one of these:
        self.__gooduids = [-1, 60001, 65534, 65535]

        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def strip_comment(self, line):
        if line.startswith('#'):
            # if the entire line is a comment, just return it so that we
            # can preserve these in the file
            return line
        pos = line.find('#')
        if pos == -1:
            return line
        else:
            return line[:pos].strip()
    

    ##########################################################################            
    def scan(self, option=None):

        try:
            infile = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        failure_flag = False
        pattern = re.compile('anon=')
        line_count = 0
        for line in infile.readlines():
            line = line.strip()
            line_count += 1

            if line.startswith('#') or not line:
                continue

            # Check for the share command used without absolute path
            if line.startswith('share'):
                msg = "%s: Line %d starts with 'share' but the absolute "\
                      "path (/usr/sbin/share) should be used instead." % \
                         (self.__target_file, line_count)
                self.logger.info(self.module_name, 'Scan Passed: ' + msg)


            # Look for the -o (Option) argument
            fields = line.split()

            marker = -1
            for idx, xfield in enumerate(fields):
                if xfield == '-o':
                    marker = idx
                    try:
                        options = fields[idx+1]
                        if not pattern.search(options):
                            marker = -1
                            break

                        for opts in options.split(','):
                            param  = opts.split('=')[0]
                            parval = opts.split('=')[1]
                            if param == 'anon' and int(parval) not in self.__gooduids: 
                                msg = "Scan Failed: %s line %d, anon=%s;" \
                                      " expecting anon to be set to %s" % \
                                      (self.__target_file, line_count, 
                                              parval, self.__gooduids)
                                self.logger.notice(self.module_name, msg)
                                failure_flag = True
                                break

                    except IndexError:
                        msg = "Scan Error: %s: malformed line %d" % \
                                            (self.__target_file, line_count)
                        self.logger.error(self.module_name, msg)
                    break

            if marker == -1:
                msg = "%s: 'anon' share option (-o) NOT specified on line %d. "\
                      "Ignoring because by default, unknown users are "\
                      "given the effective user ID UID_NOBODY." % \
                                              (self.__target_file, line_count)
                self.logger.warn(self.module_name, 'Scan Passed: ' + msg)
                continue

            
          
        if failure_flag == True:
            return 'Fail', ''

        else:
            return 'Pass', ''


    ##########################################################################            
    def apply(self, option=None):

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        try:
            infile = open(self.__target_file, 'r')
            outfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = "File %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        failure_flag = False
        pattern = re.compile('anon=')
        line_count = 0
        for line in infile.readlines():
            orig_line = line
            line = line.strip()
            line_count += 1

            if line.startswith('#') or not line:
                outfile.write(orig_line)
                continue

            # Check for the share command used without absolute path
            if line.startswith('share'):
                line = "/usr/sbin/%s" % orig_line.strip()
                msg = "%s: Line %d starts with 'share' but the absolute "\
                      "path (/usr/sbin/share) should be used instead." % \
                         (self.__target_file, line_count)
                self.logger.info(self.module_name, 'Apply: ' + msg)


            # Look for the -o (Option) argument
            fields = line.split()

            for idx, xfield in enumerate(fields):
                if xfield == '-o':
                    marker = idx
                    try:
                        options = fields[idx+1]
                        if not pattern.search(options):
                            break

                        for opts in options.split(','):
                            param  = opts.split('=')[0]
                            parval = opts.split('=')[1]
                            if param == 'anon' and int(parval) not in self.__gooduids:
                                msg = "Scan Failed: %s line %d, anon=%s;" \
                                      " expecting anon to be set to %s" % \
                                      (self.__target_file, line_count, 
                                              parval, self.__gooduids)
                                self.logger.notice(self.module_name, msg)
                                line = line.replace(opts, 'anon=-1')
                                failure_flag = True
                                break

                    except IndexError:
                        msg = "Apply Error: %s: malformed line %d" % \
                                            (self.__target_file, line_count)
                        self.logger.error(self.module_name,  msg)

                    break

            outfile.write(line + '\n') 


        infile.close()
        outfile.close()
  
        action_record = tcs_utils.generate_diff_record(self.__tmp_file, 
                                                       self.__target_file)

        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            os.unlink(self.__tmp_file)
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1, action_record

    ##########################################################################            
    def undo(self, change_record=None):
        """Undo previous change application."""

        result, reason = self.scan() 
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Restored %s" % self.__target_file
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

