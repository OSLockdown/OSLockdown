#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#


import sys
import re
import pwd



sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.acctmgt.users
import sb_utils.acctmgt.shadow

class SetPassAgingOnAccts:
    """
    Set password aging on unlocked accounts with UID > 499
    """
    ##########################################################################
    def __init__(self):

        self.module_name = "SetPassAgingOnAccts"

        self.__pass_min = 0
        self.__pass_max = 0
        self.__pass_warn = 0
        self.__pass_inact = 0

        self.__exemptSystemAccounts = []
        self.__exemptSpecificAccounts = []       

        self.logger = TCSLogger.TCSLogger.getInstance()
        
    ##########################################################################
    ##########################################################################
    def scan(self, optionDict=None):
        """
        Find user accounts (uid > 499) with incorrect password aging.
        """
        self.validate_input(optionDict)

        msg =  'Getting lock status of each user'
        self.logger.info(self.module_name, msg)
        messages = []
        
        flag = 0
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            try:
                user = pwd.getpwnam(userName)
                shuser = sb_utils.acctmgt.shadow.getspnam(userName)
            except Exception, err:
                print str(err)    
                msg = "'%s' account not found in /etc/passwd or /etc/shadow. Password files are "\
                      "out of sync: recommend running pwconv(8)." % userName
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                messages.append(msg)
                continue
            aging_not_set = False

            if userName in self.__exemptSystemAccounts:       
                msg =  'Skipping password aging check for %s - system users exempted' % userName
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue
            if userName in self.__exemptSpecificAccounts:       
                msg =  'Skipping password aging check for %s - user specifically exempted' % userName
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue
            
            if sb_utils.acctmgt.users.is_locked(userName) == True:
                msg = "Skipping user '%s' because it is already locked" % (userName)
                self.logger.debug(self.module_name, msg)
                continue

            #  sp_expire  #days since 1970-01-01 until account is disabled
            #  sp_flag    reserved
            #  sp_inact   #days after pw expires until account is blocked
            #  sp_lstchg  date of last change
            #  sp_max     max #days between changes
            #  sp_min     min #days between changes
            #  sp_nam     login name
            #  sp_pwd     encrypted password
            #  sp_warn    #days before pw expires to warn user about it

            if shuser.sp_max  != self.__pass_max:    aging_not_set = True
            if shuser.sp_min  != self.__pass_min:    aging_not_set = True
            if shuser.sp_warn != self.__pass_warn:   aging_not_set = True
            if shuser.sp_inact != self.__pass_inact: aging_not_set = True

            if aging_not_set == True:
                msg = "Password aging not set on account '%s'" % userName
                messages.append(msg)
                self.logger.notice(self.module_name, 'Scan Failed:' + msg)
                flag = 1

        if flag == 1:
            return False, '', {'messages':messages}
        else:
            return True, '', {'messages':messages}


    ##########################################################################
    def apply(self, optionDict):

        self.validate_input(optionDict)

        msg =  'Getting lock status of each user'
        self.logger.info(self.module_name, msg)
        messages = []
        
        action_record = []
        flag = 0
        for userName in sb_utils.acctmgt.users.local_AllUsers():
            user = pwd.getpwnam(userName)
            aging_not_set = False

            try:
                user = pwd.getpwnam(userName)
                shuser = sb_utils.acctmgt.shadow.getspnam(userName)
            except:    
                msg = "'%s' account not found in /etc/passwd or /etc/shadow. Password files are "\
                      "out of sync: recommend running pwconv(8)." % userName
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                messages.append(msg)
                continue

            if userName in self.__exemptSystemAccounts:       
                msg =  'Skipping password aging check for %s - system users exempted' % userName
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue
            if userName in self.__exemptSpecificAccounts:       
                msg =  'Skipping password aging check for %s - user specifically exempted' % userName
                self.logger.debug(self.module_name, 'Scan: ' + msg)
                continue

            if sb_utils.acctmgt.users.is_locked(userName) == True:
                msg = "Skipping user '%s' because it is already locked" % (userName)
                self.logger.debug(self.module_name, msg)
                continue

            if shuser.sp_max  != self.__pass_max:    aging_not_set = True
            if shuser.sp_min  != self.__pass_min:    aging_not_set = True
            if shuser.sp_warn != self.__pass_warn:   aging_not_set = True
            if shuser.sp_inact != self.__pass_inact: aging_not_set = True

            if aging_not_set == True:
                change_rec = "%s|%d|%d|%d|%d\n" % (shuser.sp_nam, shuser.sp_max, shuser.sp_min, shuser.sp_warn, shuser.sp_inact)
                action_record.append(change_rec)
                cmd = "/usr/bin/chage -m %d -M %d -W %d -I %d %s" % \
                               (self.__pass_min, self.__pass_max, 
                                self.__pass_warn, self.__pass_inact, userName )
                output = tcs_utils.tcs_run_cmd(cmd, True)
                if output[0] != 0:
                    msg = "Unable to set password aging on '%s': %s" % (userName, output[2])
                    self.logger.error(self.module_name, 'Apply Failed: ' + msg)
                    continue
                else:
                    msg = "Password aging set on '%s'" % (userName)
                    self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        if action_record == []:
            return False, '', {'messages':messages}
        else:
            return True, ''.join(action_record), {'messages':messages}



    ##########################################################################
    def undo(self, change_record):

        if not change_record:
            return 0, 'No change record provided'

        fieldArgs = ['spaceholder','M', 'm', 'W', 'I']
        
        # Note - legacy RedHat/Fedora change records used a space as the record delimiter, and also had
        # the fields in slightly altered order.  So we need to detect if we have such a record and 
        # reorder it before proceeding.  Both change records will have 5 fields, with either ' ' or '|' as
        # the field delimiter.
        # The legacy RH/Fedora order is 'user sp_min sp_max sp_warn sp_inact', and current ordering
        # is                            'user sp_max sp_min sp_warn sp_inact'
        # The change record will record 'empty' fields if the setting in the shadow file for the account
        # in question was strict enough and did not require changing.
        
        changelist = change_record.split('\n')
        for record in changelist:
            # if we have a space, assume legacy Redhat/Fedora style and fix
            if not record: 
                continue
            if '|' in record:
                fields = record.split('|')
            else:
                fieldsRH = record.split(' ')
                fields = [ fieldsRH[elem] for elem in [0,2,1,3,4]]
            
            if len(fields) != 5: 
                msg = "Element of change record has incorect number of fields, skipping '%s'" % record
                self.logger.error(self.module_name, "Undo Error: " + msg)
                continue

            try:
                pwd.getpwnam(fields[0])
            except Exception, err:
                msg = "Unable to get information on account '%s' " % fields[0]
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                continue

            cmdArgs = []
            for i in range(1,len(fields)):
                if fields[i]:
                    cmdArgs.append("-%s %s" % (fieldArgs[i], fields[i]))
            cmd = "/usr/bin/chage %s %s" % (' '.join(cmdArgs), fields[0])
               
            output = tcs_utils.tcs_run_cmd(cmd, True)
            if output[0] != 0:
                msg = "Unable to undo password aging on '%s': %s" % (fields[0], output[2])
                self.logger.error(self.module_name, 'Undo Failed: ' + msg)
                continue
            else:
                msg = "Password aging reset on '%s'" % (fields[0])
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)


        return True,'',{}

    ##########################################################################
    # Verify each argument name is present in the diction, and is an integer
    # return the value or raise an exception
    
    def validate_argument(self, argName, optionDict):
        try:
            argValue = int(optionDict[argName],10)
        except:
            msg =  'Invalid option arg (%s) provided' % argName
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        return argValue

    ##########################################################################
    def validate_input(self, optionDict=None):
        """
        Validate optionDict has required args, within acceptable ranges
        """

        self.__pass_min   = self.validate_argument('passwordAgingMindays', optionDict)
        self.__pass_max   = self.validate_argument('passwordAgingMaxdays', optionDict)
        self.__pass_warn  = self.validate_argument('passwordAgingExpireWarning', optionDict)
        self.__pass_inact = self.validate_argument('passwordAgingInvalidate', optionDict)

        if optionDict['exemptSystemAccounts'] == '1':
            self.__exemptSystemAccounts = sb_utils.acctmgt.users.local_SystemUsers()
        else:
            self.__exemptSystemAccounts = []

        self.__exemptSpecificAccounts = tcs_utils.splitNaturally(optionDict['exemptSpecificAccounts'])
 
        flag = 0
        if self.__pass_min < 1 or self.__pass_max < 1 or \
               self.__pass_inact < 0 or self.__pass_warn < 1:
            flag = 1
    
        if self.__pass_max < self.__pass_min:
            flag = 1 
 
        if flag == 1:
            msg =  'Invalid option arg provided' 
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

 
