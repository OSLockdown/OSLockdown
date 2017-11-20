#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import stat
import sys
import pwd

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.exclusion
import sb_utils.file.fileperms
import sb_utils.acctmgt.users

class InvalidUserID (Exception):
    pass
    
class HomeDirPerms:

    def __init__(self):
        self.module_name = "HomeDirPerms"
        self.logger = TCSLogger.TCSLogger.getInstance()

        # List of directories to NEVER, NEVER change ownership on!
        if sb_utils.os.info.is_solaris() == False:        
            self.__excl_dirs = ['/usr', '/etc', '/lib', '/proc', '/opt', '/sbin',
                                '/usr/bin', '/usr/sbin', '/', '/var/lib/nfs']
            self.__userid_min = 100
            self.__userid_max = 4290000000
        else:
            self.__excl_dirs = [ '/', '/cdrom', '/dev', '/devices', '/etc', '/export',
                                 '/home', '/kernel', '/lib', '/mnt', '/net', '/opt', 
                                 '/platform', '/proc', '/sbin', '/system', '/tmp',
                                 '/usr', '/usr/bin', '/usr/lib', '/usr/sbin', 
                                 '/usr/share/lib', '/var/lib', '/var/lib/nfs', '/vol' ]
            self.__userid_min = 500
            self.__userid_max = 65535

    ##########################################################################
    def validate_input(self, option=None):
        if option and option != 'None':
            return 1
        return 0

    def is_valid_userid(self, pw_entry):
    
        retmsg = ""
        try:    
            homedir = pw_entry.pw_dir
            if not os.path.isdir(homedir): 
                msg = "User account '%s' home directory (%s) does not "\
                      "exist; ignoring..." % (pw_entry.pw_name, homedir)
                self.logger.info(self.module_name, msg)
                raise InvalidUserID(msg)  
    
            if homedir in self.__excl_dirs or pw_entry.pw_name in ('nfsnobody', 'nobody'):
                msg = "User account '%s' home directory (%s) is on the "\
                      "exclusion list for safety reasons; ignoring..." % \
                           (pw_entry.pw_name, homedir)

                self.logger.info(self.module_name, msg)
                raise InvalidUserID(msg)  

            is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(homedir)
            if is_excluded == True:
                self.logger.notice(self.module_name, why_excluded)
                raise InvalidUserID(why_excluded)  
        
        except InvalidUserID, why:
            retmsg = str(why)    
            
        return retmsg

    ##########################################################################
    def scan(self, option=None):
        result = True
        if option != None:
            option = None

        messages = {'messages':[]}
        
        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            user = pwd.getpwnam(userName)
            msg = self.is_valid_userid(user)
            if msg :
                if "not within userid range" not in msg:
                    messages['messages'].append(msg)
                continue

            try:
                statinfo = os.stat(user.pw_dir)
            except OSError, err:
                msg = "Unable to stat directory %s: %s" % (user.pw_dir, err)
                self.logger.warning(self.module_name, 'Scan Warning: ' \
                  + msg)
                messages['messages'].append(msg)
                continue
                
            if (statinfo.st_mode & 0020) or (statinfo.st_mode & 0007):
                result = False
                msg = '%s has permissions of %o' % \
                     (user.pw_dir, stat.S_IMODE(statinfo.st_mode))
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        return result, '', messages


    ##########################################################################
    def apply(self, option=None):
        if option != None:
            option = None

        change_record = {}
        messages = {'messages':[]}

        for userName in sb_utils.acctmgt.users.local_RegularUsers():
            user = pwd.getpwnam(userName)
            msg = self.is_valid_userid(user)
            if msg:
                messages['messages'].append(msg)
                continue
                
            try:
                statinfo = os.stat(user.pw_dir)
            except OSError, err:
                msg = "Unable to stat directory %s: %s" % (user.pw_dir, err)
                self.logger.warning(self.module_name, 'Scan Warning: ' \
                  + msg)
                messages['messages'].append(msg)
                continue

            if (statinfo.st_mode & 0020) or (statinfo.st_mode & 0007):
                newperms = statinfo.st_mode & 0750

                changes_to_make = {'dacs' : newperms}
                change_record.update(sb_utils.file.fileperms.change_file_attributes( user.pw_dir, changes_to_make))
                   
        if change_record == {}:
            return False, '', messages
        else:
            return True, str(change_record), messages

    ##########################################################################
    def undo(self, change_record=None):

        messages = {'messages':[]}
        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # check to see if this might be an oldstyle change record, which is a string of entries
        #   of "filename mode\n"  - mode should be interpreted as decimal
        # If so, convert that into the new dictionary style
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split(' ')
                if len(fspecs) != 2:
                    continue
                new_rec[fspecs[0]] = {'dacs':int(fspecs[1], 10)}
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)


        return True, '', messages
        

