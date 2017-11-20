#!/usr/bin/env python
  
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
  
# This module secures log files by making sure they do not
# have group write or world read/write. If the file does
# not meet that criteria, then it's permissions are set to
# 0640.
#
# Additionally, it examines /etc/syslog.conf (or /etc/rsyslog.conf)
# to determine where mail.* or mail.crit messages are being logged. If
# it doesn't find an entry, it defaults to /var/log/maillog
#
# On Solaris systems it examines /etc/security/audit_control,
# to see where audit files are being written. If it can't find
# a 'dir:' entry, it defaults to /var/audit.  On Linux systems, 
# it defaults to /var/log/audit. In either case, it expects
# the directory permissions to be 0700 and owned by root.
#
# When it comes to examining the user and group ownership
# of log files, it ensures each file is owned by a system 
# user (Solaris UID < 100 and Linux UID < 500)
#
# $Id: SysLogFilePerms.py 23917 2017-03-07 15:44:30Z rsanders $
#


#
# DISA STIG Requirements:
#    GEN001260 - System Log File Permissions
#        Most syslog messages are logged to /var/log, /var/log/syslog, 
#        or /var/adm directories.  Check the permissions by performing 
#        the following command: ls -lL <syslog directory>
#
#        If any of the log files permissions are greater than 640, this 
#        is a finding.
#
#    GEN002680 - Audit Logs Accessiblity
#    GEN002700 - Make sure audit files are ownly readable by root
#        Perform the following to determine the location of audit logs and 
#        then check the ownership:
#                       more /etc/security/audit_control
#                       ls -lLd <audit log dir>
#        The audit log directory needs to be owned by root and only readable
#        by him.
#
#    GEN004480 - Critical Sendmail Log File Ownership
#        Either /var/log/syslog or /var/log/maillog must be owned by root
#
#    GEN004500 - Critical Sendmail Log File Permissions
#        No greater than 644
#


import os
import sys
import pwd
import grp
import stat
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms



class SysLogFilePerms:

    def __init__(self):
        self.module_name = "SysLogFilePerms"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__log_analyze = 1

        self.__syslog   = '/etc/syslog.conf'
        
        self.__logdirs   = ['/var/adm',    '/var/log',      '/var/saf/zsmon',
                            '/var/sadm/pkg/SUNWcsr/save/pspool/SUNWcsr/reloc/var/log',
                            '/var/sadm/pkg/SUNWcsr/save/pspool/SUNWcsr/reloc/var/saf' ]
        self.__auditdirs = ['/var/audit',  '/var/log/audit' ]

        self.__excl_logs = ['/var/log/btmp', '/var/log/wtmp' ]

        if sb_utils.os.info.is_solaris():
            self.__maxugid = 99
        else:
            self.__maxugid = 499
        
        if sb_utils.os.info.is_fedora() or sb_utils.os.info.is_LikeSUSE():
            self.__syslog = '/etc/rsyslog.conf'

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):
        """
        Check the file permissions on system log files.
        """

        fail_flag = False
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # First, check auditing directory permissions
        #
        dirs_to_check = self.__logdirs
        audit_dir = self._get_auditdir()

        # Add it to the list of all directories to check
        audit_stat = False
        if audit_dir != None:
            dirs_to_check.append(audit_dir) 
            try:
                statinfo = os.stat(audit_dir)
                audit_stat = True
            except OSError, err:
                msg = "Scan Error: %s: %s" % (audit_dir, err)
                self.logger.error(self.module_name, msg)
                
            # I was able to stat file so, now check ownership and perms
            if audit_stat == True:
                testfile_mode  = int(oct(stat.S_IMODE(statinfo.st_mode)))
                testfile_owner = pwd.getpwuid(statinfo.st_uid)[0]
                testfile_group = grp.getgrgid(statinfo.st_gid)[0]
                statemsg = "found %d perms, owned by %s, group %s" % \
                               (testfile_mode, testfile_owner, testfile_group)

                # Is audit directory owner and group okay?
                if statinfo.st_uid > self.__maxugid or \
                                             statinfo.st_gid > self.__maxugid:
                    msg = "Scan Failed: %s is not owned by a system " \
                          "account; %s" % (audit_dir, statemsg)
                    self.logger.notice(self.module_name, msg)
                    fail_flag = True

                if testfile_mode != 700:
                    msg = "Scan Failed: %s permissions are not 700; %s" % \
                          (audit_dir, statemsg) 
                    self.logger.notice(self.module_name, msg)
                    fail_flag = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Second, check log which stores critical sendmail messages
        #
        maillog = self._get_maillog() 
        if os.path.isfile(maillog):
            maillog_checked = False
        else:
            maillog_checked = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Third, check all standard log directories and files within
        #
        for logdir in dirs_to_check:
            msg = "Scan: Checking %s directory..." % logdir
            self.logger.info(self.module_name, msg)

            for root, dirs, files in os.walk(logdir):
        
                if maillog_checked == False:
                    files.append(maillog)
                    maillog_checked = True

                for logfile in files:
                    testfile = os.path.join(root, logfile)
                    if testfile in self.__excl_logs:
                        msg = "Ignoring %s..." % testfile
                        self.logger.info(self.module_name, msg)
                        continue

                    try:
                        statinfo = os.stat(testfile)
                    except OSError, err:
                        msg = "Scan Error: %s: %s" % (testfile, err)
                        self.logger.error(self.module_name, msg)
                        continue
           
                    testfile_mode  = int(oct(stat.S_IMODE(statinfo.st_mode)))
                    try:
                        testfile_owner = pwd.getpwuid(statinfo.st_uid)[0]
                        testfile_group = grp.getgrgid(statinfo.st_gid)[0]
                    except KeyError:
                        msg = "Scan Failed: %s is unowned" % testfile
                        self.logger.notice(self.module_name, msg)
                        fail_flag = True
                        continue
                        
                   
                    statemsg = "found %d perms, owned by %s, group %s" % \
                               (testfile_mode, testfile_owner, testfile_group)


                    # Owner of file okay?
                    if statinfo.st_uid > self.__maxugid:
                        msg = "Scan Failed: %s is not owned by a system " \
                              "account; %s" % (testfile, statemsg)
                        self.logger.notice(self.module_name, msg)
                        fail_flag = True
                        continue

                    # Group owner of file okay?
                    if statinfo.st_gid > self.__maxugid:
                        msg = "Scan Failed: %s group owner is not a system " \
                              "group; %s" % (testfile, statemsg)
                        self.logger.notice(self.module_name, msg)
                        fail_flag = True
                        continue
                        
                    # Group or world writeable
                    if statinfo.st_mode & stat.S_IWGRP or \
                                              statinfo.st_mode & stat.S_IWOTH:
                        msg = "Scan Failed: %s should only be writable by "\
                              "owner; %s" % (testfile, statemsg)
                        self.logger.notice(self.module_name, msg)
                        fail_flag = True
                        continue

                    # World readable?
                    if statinfo.st_mode & stat.S_IROTH:
                        msg = "Scan Failed: %s should not have world "\
                              "read permissions; %s" % (testfile, statemsg)
                        self.logger.notice(self.module_name, msg)
                        fail_flag = True
                        continue

                    # Execute bits, log files don't need them!
                    if statinfo.st_mode & stat.S_IXUSR or \
                                          statinfo.st_mode & stat.S_IXGRP or \
                                          statinfo.st_mode & stat.S_IXOTH:
                        msg = "Scan Failed: %s do not need execute "\
                              "permissions; %s" % (testfile, statemsg)
                        self.logger.notice(self.module_name, msg)
                        fail_flag = True
                        continue

                    msg = "Scan: %s is okay; %s" % (testfile, statemsg)
                    self.logger.debug(self.module_name, msg)

        # Now return status
        if fail_flag == True:
            return 'Fail', 'Some system log files have insecure permissions'
        else:
            return 'Pass', ''
    

    ##########################################################################
    def _get_auditdir(self):
        """Determine where auditing files are written"""

        # If linux, default to /var/log/audit. If Solaris check the
        # audit configuration file or just default to /var/audit

        if sb_utils.os.info.is_solaris() != True:
            audit_dir = '/var/log/audit'
        else:
            audit_dir = None
            try:
                infile = open('/etc/security/audit_control', 'r')
            except IOError, err:
                msg = "Unable to read /etc/security/audit_control: %s" % err
                self.logger.error(self.module_name, msg)
                msg = "Defaulting to /var/audit as the auditing directory"
                self.logger.info(self.module_name, msg)
                audit_dir = '/var/audit'

            if audit_dir == None:
                audit_dir = '/var/audit'
                for line in infile.readlines():
                    if line.startswith('dir:'):
                        fields = line.strip('\n').split(':')
                        try:
                            audit_dir = fields[1]
                            if not os.path.isdir(audit_dir):
                                audit_dir = '/var/audit'
                        except:
                            pass
    
                        break                         

            infile.close()
                  

        return audit_dir

    ##########################################################################
    def _get_maillog(self):
        """Determine where auditing files are written"""

        # If linux, default to /var/log/audit. If Solaris check the
        # audit configuration file or just default to /var/audit

        maillog = None
        pattern = re.compile('^mail\.(\*|crit)')
        try:
            infile = open(self.__syslog, 'r')
        except IOError, err:
            msg = "Unable to read %s: %s" % (self.__syslog, err)
            self.logger.error(self.module_name, msg)

            msg = "Defaulting to /var/log/maillog as the mail log"
            self.logger.info(self.module_name, msg)
            maillog = '/var/log/maillog'

        if maillog == None:
            maillog = '/var/log/maillog'
            for line in infile.readlines():
                line = line.strip('\n')
                if pattern.search(line):
                    fields = line.strip('\n').split('\t')
                    try:
                        maillog = fields[-1]
                        if maillog[0] == '-':
                            maillog = fields[-1][1:]
                        if not os.path.isfile(maillog):
                            maillog = '/var/log/maillog'
                    except:
                        pass

                    break

            infile.close()

        return maillog


    ##########################################################################
    def apply(self, option=None):

        fail_flag = False
        action_record = {}
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # First, check auditing directory permissions
        #
        dirs_to_check = self.__logdirs
        audit_dir = self._get_auditdir()

        # Add it to the list of all directories to check
        audit_stat = False
        changes_to_make = {}
        if audit_dir != None:
            dirs_to_check.append(audit_dir) 
            try:
                statinfo = os.stat(audit_dir)
                audit_stat = True
            except OSError, err:
                msg = "Scan Error: %s: %s" % (audit_dir, err)
                self.logger.error(self.module_name, msg)
                
            # I was able to stat file so, now check ownership and perms
            if audit_stat == True:
                testfile_mode  = int(oct(stat.S_IMODE(statinfo.st_mode)))
             
                # Is audit directory owner and group okay?
                if statinfo.st_uid > self.__maxugid or \
                                             statinfo.st_gid > self.__maxugid:
                    changes_to_make.update({'owner':'root',
                                            'group':'root'})

                # Is Audit Directory perms set to 0700?
                if testfile_mode != 700:
                    changes_to_make.update({'dacs':0700})


            # Create an undo record!
            if len(changes_to_make) > 0 :
                action_record.update(sb_utils.file.fileperms.change_file_attributes(audit_dir, changes_to_make))



        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Second, check log which stores critical sendmail messages
        #
        maillog = self._get_maillog() 
        if os.path.isfile(maillog):
            maillog_checked = False
        else:
            maillog_checked = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Third, check all standard log directories and files within
        #
        for logdir in dirs_to_check:
            for root, dirs, files in os.walk(logdir):
        
                if maillog_checked == False:
                    files.append(maillog)
                    maillog_checked = True

                for logfile in files:
                    changes_to_make = {}
                    testfile = os.path.join(root, logfile)
                    if testfile in self.__excl_logs:
                        msg = "Ignoring %s..." % testfile
                        self.logger.info(self.module_name, msg)
                        continue

                    try:
                        statinfo = os.stat(testfile)
                    except OSError, err:
                        msg = "Apply Error: %s: %s" % (testfile, err)
                        self.logger.error(self.module_name, msg)
                        continue
           
                    testfile_mode  = int(oct(stat.S_IMODE(statinfo.st_mode)))
                   
                    # Owner of file okay?
                    if statinfo.st_uid > self.__maxugid or \
                                              statinfo.st_gid > self.__maxugid:
                        changes_to_make.update({'owner':'root',
                                                'group':'root'})


                    # Check permissions of file...
                    # Group or world writeable
                    bad_perms = False
                    if statinfo.st_mode & stat.S_IWGRP or \
                                              statinfo.st_mode & stat.S_IWOTH:
                        bad_perms = True

                    # World readable?
                    if statinfo.st_mode & stat.S_IROTH:
                        bad_perms = True

                    # Execute bits, log files don't need them!
                    if statinfo.st_mode & stat.S_IXUSR or \
                                          statinfo.st_mode & stat.S_IXGRP or \
                                          statinfo.st_mode & stat.S_IXOTH:
                        bad_perms = True

                    # Change Permissions if they are bad
                    if bad_perms == True:
                        changes_to_make.update({'dacs':0640})

                    if len(changes_to_make) > 0 :
                        action_record.update(sb_utils.file.fileperms.change_file_attributes(testfile, changes_to_make))
                    # Create an undo record!
#                    if bad_owner == True or bad_perms == True:
#                        record = "%s|%d|%s|%s\n" % (testfile, testfile_mode,
#                                          statinfo.st_uid, statinfo.st_gid)
#                        action_record.append(record)

        if action_record == {}:
            return 0, ''
        else:
            return 1, str(action_record)

            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the file permissions on system log files.
        """

        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record == '': 
            msg = "Unable to perform undo operation with empty change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename|mode|uid|gid\n"  - mode should be interpreted as octal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split('|')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[0]] = {'owner':fspecs[2],
                                      'group':fspecs[3],
                                      'dacs':int(fspecs[1], 8)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return 1

