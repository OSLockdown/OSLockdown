#!/usr/bin/python

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

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import tcs_utils
import sb_utils.os.validateFile
import sb_utils.acctmgt.users
import sb_utils.os.config
import sb_utils.os.info

class PwGrpCheck:

    def __init__(self):
        self.module_name = "PwGrpCheck"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    ##########################################################################
    def scan(self, option=None):

        msgs = []
        retval = True
        if option != None:
            option = None

        #---------------------------------
        # Check the format of /etc/passwd
        if sb_utils.os.validateFile.passwd('/etc/passwd') != True:
            msg = "/etc/passwd does not appear to be properly formatted"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            msgs.append(msg)
            
        else:
            self.logger.debug(self.module_name, "/etc/passwd structure is valid.")

        # Grab parameters separated by either a space or a tab - but only if /etc/login.defs exists (linux only feature)
        if not sb_utils.os.info.is_solaris():
            paramlist = sb_utils.os.config.get_list(configfile='/etc/login.defs', delim='\t') 
            paramlist.update(sb_utils.os.config.get_list(configfile='/etc/login.defs', delim=' '))
            if paramlist.has_key('MAX_MEMBERS_PER_GROUP'):
               msg = "Found MAX_MEMBERS_PER_GROUP in /etc/login.defs. This enables the split "\
                     "group feature (see group(5)). This module does not support this "\
                     "configuration, so it will skip the syntax check of /etc/group."
               self.logger.warn(self.module_name, msg)
            else:
                #---------------------------------
                # Check the format of /etc/group
                if sb_utils.os.validateFile.group('/etc/group') != True:
                    msg = "/etc/group does not appear to be properly formatted"
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    msgs.append(msg)
                else:
                    self.logger.debug(self.module_name, "/etc/group structure is valid.")
        

        # Get a list of shells identified in /etc/shells
        shells = sb_utils.os.info.validShells()

        # as per GEN002140 we will add /usr/bin/false, /dev/null, /sbin/nologin, to our list of 
        # acceptable shells.  Our list might already have them, so check first
        extra_shells = ['/usr/bin/false','/dev/null','/sbin/nologin' ]
        
        #-------------------------------------
        # Checking for duplicate user and uid
        self.logger.debug(self.module_name, "Checking for duplicate UIDs...")
        userlist = {}
        uidlist = {}
        lockedAccounts = []
        
        # While we can absolutely tell who is a local users, and we could derive
        # who is only a remote user (sub all users from localusers) there isn't a way
        # to detect users who are both local *and* remote short of editting /etc/nsswitch.conf and
        # repeating our queries - so limit ourselve to local users here...
        
        # look for duplicates including any external account sources
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            user = pwd.getpwnam(userName)

            # Is it a duplicate username?
            if userlist.has_key(user[0]):
                msg = "Duplicate username: %s" % (user[0])
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                msgs.append(msg)
            else:
                userlist[user[0]] = user[2]
        
            # Is it a duplicate UID?
            if uidlist.has_key('u'+str(user[2])):
                msg = "Duplicate UID %s: both %s and %s are assigned this UID" % (str(user[2]), user[0], uidlist['u'+str(user[2])])
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                msgs.append(msg)
            else:
                uidlist['u'+str(user[2])] = user[0]

            # Get account's status. Is it locked?
            isLocked = sb_utils.acctmgt.users.is_locked(user[0])

            # Does home directory exist? Only report a scan failure if the account is NOT locked.
            if not os.path.isdir(user[5]):
                msg = "%s assigned home directory (%s) does not exist" % (user[0], user[5])
                if isLocked != True:
                     self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                     msgs.append(msg)
                else:
                     self.logger.info(self.module_name, "%s but the account is locked." % msg)
                     lockedAccounts.append(user[0])

            # Does the account have a valid shell? Only report a scan failure if the account is NOT locked
            if user[6] == '' or user[6] not in shells:
                if user[6] in extra_shells:
                    msg = "%s has shell (%s) allowed by GEN002140 even if not in /etc/shells" %(user[0],user[6])
                    self.logger.info(self.module_name, "%s" % msg)
                else:
                    msg = "%s is not assigned a valid shell" % user[0]
                    if isLocked != True:
                        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                        msgs.append(msg)
                    else:
                        self.logger.info(self.module_name, "%s but the account is locked." % msg)
                        lockedAccounts.append(user[0])

            # Does the account have a valid primary group assigned?
            try:
                grpName = grp.getgrgid(int(user[3]))[0]

            except (KeyError, IndexError), err:
                msg = "%s is not assigned a valid primary group" % user[0]
                if isLocked != True:
                     self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                     msgs.append(msg)
                else:
                     self.logger.info(self.module_name, "%s but the account is locked." % msg)
                     lockedAccounts.append(user[0])
            except Exception, err:
                msg = "Unable to determine the primary group of %s: %s" % (user[0], err)          
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg)) 
                     
        del userlist
        del uidlist

        #------------------------------------
        # Verify Group information
        groupList = {}
        gidList = {}
        for groupName in sb_utils.acctmgt.users.local_AllGroups():
            group = grp.getgrnam(groupName)
            # Is it a duplicate group name?
            if groupList.has_key(group[0]):
                msg = "Duplicate group name: %s" % (group[0])
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                msgs.append(msg)
            else:
                groupList[group[0]] = group[2]
        
            # Is it a duplicate GID?
            if gidList.has_key('u'+str(group[2])):
                msg = "Duplicate GID %s: both %s and %s are assigned this GID" % (str(group[2]), group[0], gidList['u'+str(group[2])])
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                msgs.append(msg)
            else:
                gidList['u'+str(group[2])] = group[0]

            # Check secondary members of this group. If no members, then just skip.
            if len(group[3]) < 1:
                continue

            for testUser in group[3]:
                try:
                    pwd.getpwnam(testUser)

                except (KeyError, IndexError), err:
                    msg = "Group '%s' has user '%s' assigned to it but this is an invalid user account." % (group[0], testUser)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    msgs.append(msg)

                except Exception, err:
                    msg = "In group '%s', unable to determine the status of assigned user '%s': %s" % (group[0], testUser, err)          
                    self.logger.error(self.module_name, 'Scan Error: ' + msg)
                    raise tcs_utils.ScanError('%s %s' % (self.module_name, msg)) 

        del groupList
        del gidList

        if msgs:
            return False, 'One or more problems were found', {'messages':msgs}
        else:
            return True, '',{}


    ##########################################################################
    def apply(self, option=None):
        """
        Lock invalid users
        """

        accountsToBeLocked = {}
        msgs = []
        
        #---------------------------------
        # Check the format of /etc/passwd
        if sb_utils.os.validateFile.passwd('/etc/passwd') != True:
            msg = "/etc/passwd does not appear to be properly formatted"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg)) 
        else:
            self.logger.debug(self.module_name, "/etc/passwd structure is valid.")

        # Grab parameters separated by either a space or a tab - but only if /etc/login.defs exists (linux only feature)
        if not sb_utils.os.info.is_solaris():
            paramlist = sb_utils.os.config.get_list(configfile='/etc/login.defs', delim='\t') 
            paramlist.update(sb_utils.os.config.get_list(configfile='/etc/login.defs', delim=' '))
            if paramlist.has_key('MAX_MEMBERS_PER_GROUP'):
               msg = "Found MAX_MEMBERS_PER_GROUP in /etc/login.defs. This enables the split "\
                     "group feature (see group(5)). This module does not support this "\
                     "configuration, so it will skip the syntax check of /etc/group."
               self.logger.warn(self.module_name, msg)
            else:
                #---------------------------------
                # Check the format of /etc/group
                if sb_utils.os.validateFile.group('/etc/group') != True:
                    msg = "/etc/group does not appear to be properly formatted"
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg)) 
                else:
                    self.logger.debug(self.module_name, "/etc/group structure is valid.")


        # Get a list of shells identified in /etc/shells
        shells = sb_utils.os.info.validShells()

        #-------------------------------------
        # Checking for duplicate user and uid
        self.logger.debug(self.module_name, "Checking for duplicate UIDs...")
        userlist = {}
        uidlist = {}
        lockedAccounts = []
        # look for duplicates including any external account sources
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            user = pwd.getpwnam(userName)
            # Is it a duplicate username?
            if userlist.has_key(user[0]):
                msg = "Duplicate username: %s" % (user[0])
                self.logger.notice(self.module_name, msg)
                if not accountsToBeLocked.has_key(user[0]):
                    accountsToBeLocked[user[0]] = True
                 
            else:
                userlist[user[0]] = user[2]
        
            # Is it a duplicate UID?
            if uidlist.has_key('u'+str(user[2])):
                msg = "Duplicate UID %s: both %s and %s are assigned this UID" % (str(user[2]), user[0], uidlist['u'+str(user[2])])
                self.logger.notice(self.module_name, msg)
                if not accountsToBeLocked.has_key(user[0]):
                    accountsToBeLocked[user[0]] = True
            else:
                uidlist['u'+str(user[2])] = user[0]

            # Get account's status. Is it locked?
            isLocked = sb_utils.acctmgt.users.is_locked(user[0])

            # Does home directory exist? Only report a scan failure if the account is NOT locked.
            if not os.path.isdir(user[5]):
                msg = "%s assigned home directory (%s) does not exist" % (user[0], user[5])
                if isLocked != True:
                     self.logger.notice(self.module_name, msg)
                     if not accountsToBeLocked.has_key(user[0]):
                         accountsToBeLocked[user[0]] = True
                else:
                     self.logger.info(self.module_name, "%s but the account is locked." % msg)

            # Does the account have a valid shell? Only report a scan failure if the account is NOT locked
            if user[6] == '' or user[6] not in shells:
                msg = "%s is not assigned a valid shell" % user[0]
                if isLocked != True:
                     self.logger.notice(self.module_name, msg)
                     if not accountsToBeLocked.has_key(user[0]):
                         accountsToBeLocked[user[0]] = True
                else:
                     self.logger.info(self.module_name, "%s but the account is locked." % msg)

            # Does the account have a valid primary group assigned?
            try:
                grpName = grp.getgrgid(int(user[3]))[0]

            except (KeyError, IndexError), err:
                msg = "%s is not assigned a valid primary group" % user[0]
                if isLocked != True:
                     self.logger.notice(self.module_name, msg)
                     if not accountsToBeLocked.has_key(user[0]):
                         accountsToBeLocked[user[0]] = True
                else:
                     self.logger.info(self.module_name, "%s but the account is locked." % msg)
            except Exception, err:
                msg = "Unable to determine the primary group of %s: %s" % (user[0], err)          
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg)) 
                     
        del userlist
        del uidlist

        #------------------------------------
        # Verify Group information
        groupList = {}
        gidList = {}
        for groupName in sb_utils.acctmgt.users.local_AllGroups():
            group = grp.getgrnam(groupName)
            # Is it a duplicate group name?
            if groupList.has_key(group[0]):
                msg = "Duplicate group name: '%s', you will need to manually correct this configuration." % (group[0])
                self.logger.warn(self.module_name, msg)
            else:
                groupList[group[0]] = group[2]
        
            # Is it a duplicate GID?
            if gidList.has_key('u'+str(group[2])):
                msg = "Duplicate GID %s: both %s and %s are assigned this GID. You will need to manually correct this configuration." % (str(group[2]), group[0], gidList['u'+str(group[2])])
                self.logger.warn(self.module_name, msg)
            else:
                gidList['u'+str(group[2])] = group[0]

            # Check secondary members of this group. If no members, then just skip.
            if len(group[3]) < 1:
                continue

            for testUser in group[3]:
                try:
                    pwd.getpwnam(testUser)

                except (KeyError, IndexError), err:
                    msg = "Group '%s' has user '%s' assigned to it but this is an invalid user account. You will need to manually correct this configuration." % (group[0], testUser)
                    self.logger.notice(self.module_name, msg)

                except Exception, err:
                    msg = "In group '%s', unable to determine the status of assigned user '%s': %s" % (group[0], testUser, err)          
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg)) 

        del groupList
        del gidList
        lockedAccounts = []
        for user in accountsToBeLocked.keys():
            result = sb_utils.acctmgt.users.lock(user)
            msgs.append("Locked local users account '%s'" % user)
            
            if result == True:
                lockedAccounts.append(user)
        if len(lockedAccounts) > 0:
            return True, '\n'.join(lockedAccounts), {'messages':msgs}
        else:
            return False, '', {}


    ##########################################################################
    def undo(self, change_record=None):
        """
        Unlock previously locked accounts
        """
        
        if change_record == None:
            return 0, 'No change record provided'

        changelist = change_record.split(':')
        for user in changelist:
            if not user:
                continue
            result = sb_utils.acctmgt.users.unlock(user)
            msg = '%s user unlocked' % user
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        self.logger.notice(self.module_name, 'Undo Performed')
        return True,'',{}

    ##########################################################################
    def validate_input(self, option=None):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

if __name__ == "__main__":
    test = PwGrpCheck()
    test.logger.forceToStdout()
    print test.scan()
    
