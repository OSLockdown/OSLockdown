#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import pwd
import grp
import stat
import glob

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.dac
import sb_utils.file.fileperms

class SysConfigFilePerms:

    def __init__(self):
        self.module_name = "SysConfigFilePerms"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__log_analyze = 1

        self.replacementModules = {
            'Root Console Only Logins' : ['/etc/securetty'],
            'System Logging Configuration File Permissions' : [ '/etc/syslog.conf', '/etc/rsyslog.conf', '/etc/syslog-ng/syslog-ng.conf'],
            'Boot Loader Configuration File Permissions' : [ '/etc/lilo.conf', '/boot/grub/grub.conf', '/boot/grub/menu.lst'],
            'Inetd/Xinetd Configuration File Permissions' : [ '/etc/xinetd.d/', '/etc/xinetd.conf','/etc/xinetd.d/*'],
            'Skeleton File Permissions' : [ '/etc/skel/*'],
            'Global Initialization File Permissions' : [ '/etc/.login', '/etc/profile', '/etc/csh.cshrc', '/etc/csh.login','/etc/environment',
                                                '/etc/security/environ', '/etc/hosts', '/etc/login.defs', '/etc/profile.d/*','/etc/profile.d'],
            'SNMP Configuration File Permissions' : ['/etc/snmp/snmp.conf' , '/etc/snmp/snmpd.conf', 'etc/snmp/conf/snmpd.conf', 'etc/snmp/snmp.local.conf' ],
            'Kernel Core Dump Directory Permissions': ['/var/crash'], 
            'At Directory Permissions': ['/var/spool/at'],
            'At/Cron Access File Permissions': ['/etc/at.allow', '/etc/at.deny', '/etc/cron.allow', '/etc/cron.deny'],  # note - should happen *after* RestrictAtCron (which will *set* perms if content altered)
            'NIS/NIS+/YP Configuration File Permissions': ['/etc/yp', '/var/yp', '/etc/yp.conf'], 
            'NFS Export Configuration File Permissions': ['/etc/exports'],
            'Mail Agent Aliases Files Permissions': ['/etc/aliases', '/etc/aliases.db' ],
            'Samba Configuration File Permissions': ['/etc/samba/smb.conf' ],
            'Samba Password File Permissions': ['/etc/samba/smbpasswd' ],
            'Management Information Base (MIB) File Permissions': ['/usr/share/snmp/mibs/*.txt', '/usr/share/snmp/mibs/*.my' ,'/usr/share/dirsrv/mibs/redhat-directory.mib']  ,   # *.my ?!?
            'Services File Permissions' : ['/etc/services'],
            'FTP Configuration File Permissions' : ['etc/ftpusers', '/etc/vsftpd/ftpusers'] ,
            'LDAP Configuration File Permissions' : ['/etc/ldap.conf'], 
            'Security access.conf File Permisssions' : ['/etc/security/access.conf']     
        }
        self.file_data = {
            '/etc/inittab': '600,root,root,0',                                #  ignore - not referenced specifically
            '/etc/login.access': '640,root,root,0',                           # ignore - not referenced specifically
            
             }

        if sb_utils.os.info.is_solaris() == True:
            self.file_data['/boot/grub/menu.lst'] = '600,root,sys,0'
            self.file_data['/etc/audit/audit.rules'] = '640,root,root,0'
            self.file_data['/etc/ftpd/ftpusers'] = '640,root,root,0'
            self.file_data['/usr/aset/userlist'] = '600,root,bin,0'
            self.file_data['/etc/security/audit_user'] = '640,root,sys,0'
            self.file_data['/etc/default/cron'] = '555,root,bin,0'
            self.file_data['/etc/default/devfsadm'] = '444,root,sys,0'
            self.file_data['/etc/default/fs'] = '444,root,bin,0'
            self.file_data['/etc/default/kbd'] = '444,root,sys,0'
            self.file_data['/etc/default/keyserv'] = '444,root,sys,0'
            self.file_data['/etc/default/nss'] = '644,root,sys,0'
            self.file_data['/etc/default/syslogd'] = '444,root,sys,0'
            self.file_data['/etc/default/tar'] = '444,root,sys,0'
            self.file_data['/etc/default/utmpd'] = '444,root,sys,0'
            self.file_data['/etc/default/init'] = '644,root,sys,0'
            self.file_data['/etc/default/login'] = '600,root,sys,0'
            self.file_data['/etc/default/su'] = '444,root,sys,0'
            self.file_data['/etc/default/passwd'] = '600,root,sys,0'
            self.file_data['/etc/default/dhcpagent'] = '644,root,sys,0'
            self.file_data['/etc/default/inetinit'] = '444,root,sys,0'
            self.file_data['/etc/default/ipsec'] = '444,root,sys,0'
            self.file_data['/etc/default/mpathd'] = '444,root,sys,0'
            self.file_data['/etc/default/telnetd'] = '444,root,sys,0'
            self.file_data['/etc/default/nfs'] = '644,root,sys,0'
            self.file_data['/etc/default/power'] = '444,root,sys,0'
            self.file_data['/etc/default/sys-suspend'] = '644,root,sys,0'
            self.file_data['/etc/default/rpc.nisd'] = '644,root,sys,0'
            self.file_data['/etc/default/yppasswdd'] = '444,root,sys,0'
            self.file_data['/etc/default/lu'] = '644,root,sys,0'
            self.file_data['/etc/default/autofs'] = '444,root,sys,0'
            self.file_data['/etc/default/ftp'] = '644,root,sys,0'
            self.file_data['/etc/default/metassist.xml'] = '644,root,sys,0'
            self.file_data['/etc/default/nfslogd'] = '444,root,bin,0'
            self.file_data['/etc/default/ndd'] = '640,root,bin,0'
            self.file_data['/etc/default/x'] = '644,root,root,0'
            self.file_data['/etc/inet/inetd.conf'] = '440,root,root,0'
            self.file_data['/etc/inet/hosts'] = '444,root,sys,0'
            self.file_data['/etc/inet/ipaddrsel.conf'] = '444,root,sys,0'
            self.file_data['/etc/inet/netmasks'] = '444,root,sys,0'
            self.file_data['/etc/inet/networks'] = '444,root,sys,0'
            self.file_data['/etc/inet/protocols'] = '444,root,sys,0'
            self.file_data['/etc/inet/secret'] = '700,root,sys,0'
            self.file_data['/etc/inet/datemsk.ndpd'] = '444,root,sys,0'
            self.file_data['/etc/inet/ipsecalgs'] = '444,root,sys,0'
            self.file_data['/etc/inet/sock2path'] = '444,root,sys,0'
            self.file_data['/etc/inet/ntp.client'] = '644,root,sys,0'
            self.file_data['/etc/inet/ntp.server'] = '644,root,sys,0'
            self.file_data['/etc/inet/ntp.conf'] = '644,root,root,0'
            self.file_data['/etc/inet/routing.conf'] = '644,root,root,0'
            self.file_data['/etc/sma/snmp/mibs/*mib'] = '640,root,sys,0'
            self.file_data['/etc/sma/snmp/mibs/*txt'] = '640,root,sys,0'
            self.file_data['/var/snmp/mib/*mib'] = '640,root,sys,0'



    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scanFiles(self, action):

        changes = {}
        for testfile in self.file_data.keys():
            desired_changes = {}
            options = {}
            if testfile.find('*') != -1:
                options ['globNames'] = True

            
            fspecs = self.file_data[testfile].split(',')

            desired_changes['dacs'] = int(fspecs[0], 8)
            desired_changes['owner'] = fspecs[1]
            desired_changes['group'] = fspecs[2]
            
            # set flags for the permissions checks...

            if action == "scan":
                options ['checkOnly'] = True
            elif action == "apply":
                options ['checkOnly'] = False

            changes.update( sb_utils.file.fileperms.search_and_change_file_attributes(testfile, desired_changes, options))
            
            
        return changes
        
    def scanOld(self, option=None):
        changes = self.scanFiles(action='scan')
        if changes != {}:
            msg = "System configuration files are not secured."
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        else:
            return 'Pass', ''
        
    ##########################################################################
    def applyOld(self, option=None):

        changes = self.scanFiles(action='apply')
        
        if changes == {}:
            msg = "No changes requird"
            return 'Fail', msg
        else:
            return 'Pass', str(changes)
        change_record = {}

    def scan(self, option=None):
        raise tcs_utils.ManualActionReqd('This module is obsolete, and has been replaced with the following modules: %s' % ', '.join(self.replacementModules.keys()))
    
    def apply(self, option=None):
        raise tcs_utils.ManualActionReqd('This module is obsolete, and has been replaced with the following modules: %s' % ', '.join(self.replacementModules.keys()))
            
    ##########################################################################
    def undo(self, change_record=None):

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


if __name__ == '__main__':
    TEST = SysConfigFilePerms()
    print TEST.scan()
    # results, change_record = TEST.apply()
