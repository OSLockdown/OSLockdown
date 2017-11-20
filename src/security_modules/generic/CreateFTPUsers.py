#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.misc.unique

import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info

class CreateFTPUsers:

    def __init__(self):
        self.module_name = "CreateFTPUsers"

        self.usernames = []

        # Solaris Systems
        if sb_utils.os.info.is_solaris() == True: 
            self.usernames.append('nobody')
            self.usernames.append('nobody4')
            self.usernames.append('noaccess')
            self.__maxuid = 100
            self.__target_file = '/etc/ftpd/ftpusers'
            self.__target_file2 = ''
            self.__pkgName = 'SUNWftpr'

        # Linux Systems
        else:
            self.usernames.append('nfsnobody')
            self.__maxuid = 500
            self.__target_file = '/etc/ftpusers'

            # Of course, SUSE uses a different package ( sarcasm )
            if sb_utils.os.info.is_LikeSUSE() != True:
                self.__pkgName = 'vsftpd'
                self.__target_file2 = '/etc/vsftpd.ftpusers'
            else:
                self.__pkgName = 'netcfg'
                self.__target_file2 = ''

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        self.get_ftpusers()

    ##########################################################################
    def get_ftpusers(self):
        """  
        create the list of users who will appear in the ftpusers file -
        these are the users who are NOT allowed to use FTP
        """

        self.usernames = []

        theusers = pwd.getpwall()
        for usracct in theusers:
            if usracct[2] < self.__maxuid:
                self.usernames.append(usracct[0])


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):


        results =  sb_utils.os.software.is_installed(pkgname=self.__pkgName)
        if results != True:
            msg = "'%s' package is not installed." % self.__pkgName
            self.logger.info(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        # first, check to see whether the target file exists at all
        if not os.path.isfile(self.__target_file):
            msg = "File %s does not exist" % self.__target_file
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        # now check its contents to be sure it contains what we want
        if not os.path.isfile(self.__target_file):
            msg = "%s does not exist" % self.__target_file
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        try:
            infile = open(self.__target_file, 'r')
        except (OSError, IOError), err:
            msg = "Unable to open file %s: %s" % (self.__target_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))


        lines = infile.readlines()
        infile.close()

        orig_ftpusers = []
        for line in lines:
            orig_ftpusers.append(line.strip())

        fail_flag = False
        for user in self.usernames:
            if user not in orig_ftpusers:
                msg = "User '%s' not in %s" % (user, self.__target_file)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                fail_flag = True

        if fail_flag == True:
            msg = "Not all system users appear in %s" % self.__target_file
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg


        # OK, now do the exact same thing for vsftpd.ftpusers
        if self.__target_file2 != '':
            if not os.path.isfile(self.__target_file2):
                msg = "File %s does not exist" % self.__target_file2
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg
    
            try:
                infile = open(self.__target_file2, 'r')
            except IOError:
                msg = "Unable to open file %s" % self.__target_file2
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                return 'Fail', msg

            lines = infile.readlines()
            infile.close()

            orig_ftpusers = []
            for line in lines:
                orig_ftpusers.append(line.strip())
    
            for user in self.usernames:
                if user not in orig_ftpusers:
                    msg = "%s not found in %s" % (user, self.__target_file2)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    return 'Fail', msg

        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):
        """Create and replace the audit rules configuration."""
        action_record = ''

        result, reason = self.scan()
        if result == 'Pass':
            return 0, ''

        results =  sb_utils.os.software.is_installed(pkgname=self.__pkgName)
        if results != True:
            msg = "'%s' package is not installed." % self.__pkgName
            return 0, action_record

        created_files = []

        # now get a list of existing users in /etc/ftpusers
        orig_ftpusers = []
        if not os.path.isfile(self.__target_file):
            rest_ftpusers = ['-1']
            orig_ftpusers = []
        else: 
            rest_ftpusers = []
            orig_ftpusers = []
            try:
                infile = open(self.__target_file, 'r')
                lines = infile.readlines()
                infile.close()
                for line in lines:
                    orig_ftpusers.append(line.strip())
                    rest_ftpusers.append(line.strip() + '|')

            except (OSError, IOError, TypeError), err:
                pass

        combo_list = self.usernames + orig_ftpusers
        try:
            unique_list = list(set(combo_list))
        except NameError:
            unique_list = sb_utils.misc.unique.unique(combo_list)
   
        combo_list = unique_list
    

        try:
            outfile = open(self.__target_file, 'w')
        except (OSError, IOError), err:
            msg = "Unable to write to %s: %s" % (self.__target_file, err)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for user in self.usernames:
            outfile.write('%s\n' % user)

        outfile.close()
        msg = '%s file updated' % (self.__target_file)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        created_files.append(self.__target_file + '|' + ''.join(rest_ftpusers) + '\n')



        # now get a list of existing users in VSFTP Users
        if self.__target_file2 != '':
            if not os.path.isfile(self.__target_file2):
                orig_ftpusers = []
                rest_ftpusers = ['-1']
            else:
                orig_ftpusers = []
                rest_ftpusers = []

            try:
                infile = open(self.__target_file2, 'r')
                lines = infile.readlines()
                infile.close()
    
                for line in lines:
                    orig_ftpusers.append(line.strip())
                    rest_ftpusers.append(line.strip() + '|')
            except (IOError, OSError, TypeError):
                pass
    
            combo_list = self.usernames + orig_ftpusers
            try:
                unique_list = list(set(combo_list))
            except NameError:
                unique_list = sb_utils.misc.unique.unique(combo_list)
    
            combo_list = unique_list
            try:
                outfile = open(self.__target_file2, 'w')
            except (IOError, OSError), err:
                msg = "Unable to open file %s: %s" % (self.__target_file2, err)
                self.logger.info(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
    
            for user in self.usernames:
                outfile.write('%s\n' % user)
    
            outfile.close()
            created_files.append(self.__target_file2 + '|' + ''.join(rest_ftpusers) + '\n')

            msg = '%s file updated' % (self.__target_file2)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        if created_files == []:
            return 0, ''
        else :
            return 1, ''.join(created_files)

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        results =  sb_utils.os.software.is_installed(pkgname=self.__pkgName)
        if results != True:
            msg = "'%s' package is not installed." % self.__pkgName
            return 0

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for myfile in change_record.split('\n'):

            if not myfile:
                continue

            myfile = myfile.lstrip()
            fields = myfile.split('|')
            try:
                if fields[1] == '-1':
                    try:
                        os.unlink(fields[0])
                    except OSError:
                        msg = 'Undo Error:  Failed to remove file %s' % file
                        self.logger.error(self.module_name, msg)
                        raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                    msg = "%s removed." % fields[0]
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

                else:
                    junk = os.umask(022)
                    try: 
                        outfile = open(fields[0], 'w') 
                        for line in fields:
                            if line == fields[0] or not line:  
                                continue
                            outfile.write(line + '\n')
                        outfile.close()
                    except IOError, err:
                        msg = "Unable to restore %s: " % (fields[0], err)
                        self.logger.error(self.module_name, msg)
                        raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                    msg = "%s restored." % fields[0]
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
            except Exception, err:
                msg = "Invalid change record; ignoring: %s" % err
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                pass
               
        return 1


if __name__ == '__main__':
    TEST = CreateFTPUsers()
    print TEST.scan()
    
