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
import sb_utils.SELinux

class NFSanon:

    def __init__(self):
        self.module_name = "NFSanon"


        self.__target_file = '/etc/exports'
        self.__tmp_file = '/tmp/.exports.tmp'
        self.__mountopt = 'anonuid'

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
    def parse_exports(self, lines):
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


        try:
            infile = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, err)
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

        bad_entry = False
        for key in datadict.keys():
            hosts = datadict[key]
            for host in hosts:
                pos = host.find('(')
                if pos == -1:
                    # no options, just continue
                    continue
                options = host[pos+1:-1].split(',')
                if self.__mountopt in host[pos+1:-1] or 'anongid' in host[pos+1:-1]:
                    for opt in options:
                        if opt.startswith('anon'):
                            kkp, kkv = opt.split('=')
                            if int(kkv) not in self.__gooduids:
                                bad_entry = True
                                msg = "%s has bad option %s=%s" % (key, kkp, kkv)
                                self.logger.info(self.module_name, 'Scan Failed: ' + msg)

        del data
        del datadict

        if bad_entry == True:
            msg = "Anonymous user/group mapping not set to %s" % str(self.__gooduids)
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        return 'Pass', ''


    ##########################################################################            
    def apply(self, option=None):

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        try:
            infile = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s." % (self.__target_file, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = infile.readlines()
        infile.close()

        # Protect file
        tcs_utils.protect_file(self.__target_file)

        try:
            origfile = open(self.__target_file, 'r')
            workfile = open(self.__tmp_file, 'w')
        except IOError, err:
            msg = "%s" % (err)
            self.logger.error(self.module_name, 'Action Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        data = self.parse_exports(lines)

        for line in data:
            if line.startswith('#'):
                workfile.write(line + '\n')
                continue

            stuff = line.split()
            hosts = stuff[1:]
            hostlist = []
            for host in hosts:
                pos = host.find('(')
                if pos == -1:
                    # no options, just continue
                    hostlist.append(host)
                    continue
                else:
                    hoststr = host[:pos]
                    options = host[pos+1:-1].split(',')
                    if self.__mountopt in host[pos+1:-1] or 'anongid' in host[pos+1:-1]:
                        count = 0
                        for opt in options:
                            if opt.startswith('anon'):
                                kkp, kkv = opt.split('=')
                                if int(kkv) not in self.__gooduids:
                                    options[count] = kkp + '=-1'      
                                    msg = "%s : Setting %s to -1" % (line, kkp)
                            count = count + 1

                    hostlist.append(hoststr + '(' + ','.join(options) + ')')

            # now, write it all out
            workfile.write(stuff[0] + '\t' + ' '.join(hostlist) + '\n')

        origfile.close()
        workfile.close()

        action_record = tcs_utils.generate_diff_record(self.__tmp_file,
                                                       self.__target_file)

        try:
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        except (OSError, IOError), err:
            msg = "Unable to install new /etc/exports: %s" % err
            self.logger.notice(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        msg = "changed %s option for exported NFS filesystems" % self.__mountopt
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

        msg = 'Restored %s status to NFS mount points' % self.__mountopt
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

