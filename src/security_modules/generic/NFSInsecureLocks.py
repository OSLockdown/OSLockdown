#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
#  NFSInsecureLocks 
#
#  This Security Module ensures that NFS-exported 
#  filesystems do not have the 'insecure_locks' option.
#

import sys
import shutil
import os
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.SELinux


class NFSInsecureLocks:
    """
    NFSInsecureLocks Security Module ensures that NFS-exported 
    filesystems do not have the 'insecure_locks' option.
    """

    def __init__(self):
        self.module_name = "NFSInsecureLocks"
        self.__target_file = '/etc/exports'
        self.__tmp_file = '/tmp/.exports.tmp'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def strip_comment(self, line):
        """Remove commented lines"""
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
    def parse_exports(self, lines):
        """Parse /etc/exports"""
        data = []
        i = 0
        line = ''
        while i < len(lines):
            line = line + self.strip_comment(lines[i]).strip()
            if line == '':
                i = i+1
                continue

            if not line.startswith('#') and line.endswith('\\'):
                # continued line - save it for the next iteration
                line = line.rstrip('\\')
                i = i+1
                continue

            # if we are here, we have a complete line
            data.append(line)
            line = ''
            i = i+1

        # data now contains either full-line comments or entire, non-broken
        # lines
        return data

    ##########################################################################
    def scan(self, option=None):

        if sb_utils.os.info.is_solaris() == True:
            msg = "This NFS mount option are not available in the "\
                  "standard Solaris distribution."
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.OSNotApplicable('%s %s' % (self.module_name, msg))


        msg = "Checking %s to see if the 'insecure_locks' option is set "\
              "on anything" %  self.__target_file
        self.logger.info(self.module_name, 'Scan: ' + msg)

        try:
            infile = open(self.__target_file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = infile.readlines()
        infile.close()

        if len(lines) == 0:
            # empty file - this is an automatic pass
            return 'Pass', ''

        data = self.parse_exports(lines)
        datadict = {}
        for line in data:
            if line.startswith('#'):
                continue
            d = line.split()
            datadict[d[0]] = d[1:]

        for key in datadict.keys():
            hosts = datadict[key]
            for host in hosts:
                # look at every option for this host and see if 'insecure_locks'
                # is one of them
                pos = host.find('(')
                if pos == -1:
                    # no options, just continue
                    continue
                options = host[pos+1:-1].split(',')
                if 'insecure_locks' in options:
                    msg = 'insecure_locks option found for host in %s' % self.__target_file
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    del data
                    del datadict
                    return 'Fail', msg

                if 'no_auth_nlm' in options:
                    msg = "'no_auth_nlm' (synonymous for 'insecure_locks') option "\
                          "found for host in %s" % self.__target_file
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    del data
                    del datadict
                    return 'Fail', msg

        # success if we haven't found an insecure_locks host at this point
        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        try:
            myfile = open(self.__target_file, 'r')
        except (IOError, OSError), err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = myfile.readlines()
        myfile.close()

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except (IOError, OSError), err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        data = self.parse_exports(lines)

        for line in data:
            if line.startswith('#'):
                workfile.write(line + '\n')
                continue

            stuff = line.split()
            hosts = stuff[1:]
            hostlist = []
            for host in hosts:
                # look at every option for this host and see if 'insecure_locks'
                # is one of them
                pos = host.find('(')
                if pos == -1:
                    # no options, just continue
                    hostlist.append(host)
                    continue
                else:
                    hoststr = host[:pos]
                    options = host[pos+1:-1].split(',')

                    if 'insecure_locks' in options:
                        options[options.index('insecure_locks')] = ''

                    if 'no_auth_nlm' in options:
                        options[options.index('no_auth_nlm')] = ''

                    hostlist.append(hoststr + '(' + ','.join(options) + ')')

            # now, write it all out
            newlist = re.sub(',,', ',', ' '.join(hostlist))
            newlist = re.sub('\(,', '(', newlist)
            newlist = re.sub(',\)', ')', newlist)
            workfile.write(stuff[0] + '\t' + newlist + '\n')

        origfile.close()
        workfile.close()

        action_record = tcs_utils.generate_diff_record(self.__tmp_file,
                                                       self.__target_file)

        try:
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except (IOError, OSError), err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "removed 'insecure_locks' option for exported NFS filesystems"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, action_record

            
    ##########################################################################
    def undo(self, change_record=None):
        """Undo previous change application."""

        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Restored insecure_locks status to NFS mount points'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1
