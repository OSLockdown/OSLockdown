#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Enable ExecShield on Red Hat systems (kernel.exec-shield)
#

import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.config
import sb_utils.os.linux
import sb_utils.os.info

class EnableKernelExecShield:

    def __init__(self):
        self.module_name = "EnableKernelExecShield"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.__target_file = "/etc/sysctl.conf"

        self.__settings = { }

    def validate_options(self, optionDict):
        # parse our list to generate the 'lines_to_find'
        if not optionDict or not 'requiredLines' in optionDict:
           msg = "No options provided to look for"
           self.logger.warn(self.module_name, msg)
           raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        # populate the self.__settings dictionary to reuse existing code....
        for line in optionDict['requiredLines'].splitlines():
            param, value = [ field.strip() for field in line.split('=',1)]
            self.__settings[param] = value
            
    ##########################################################################
    def scan(self, optionDict=None):

        if sb_utils.os.info.is_LikeSUSE() == True:
            msg = "This module is not applicable to SUSE systems"
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
       
        messages = {}
        messages['messages'] = []

        self.validate_options(optionDict)
        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file, delim='=') 
        SysCtl = sb_utils.os.linux.sysctl()
        sysdict = SysCtl.getlist()

        if len(sysdict) == 0:
            msg = "Unable to get in-memory kernel setting using sysctl(8) utility"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        failure_flag = False

        msg = "Checking settings in %s" % (self.__target_file)
        self.logger.info(self.module_name, msg)

        for param in  self.__settings.keys():
            # Verify the parameter setting actually exists in /proc/sys/kernel - if not then the feature doesn't exist and shouldn't be set
            # via sysconfig 
            
            if not param.startswith('kernel.'):
                msg = "Found '%s' as the parameters, expected it to start with 'kernel.', skipping entire module..." % param
                raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
            kernelPath = "/proc/sys/kernel/" + param[7:]
            if not os.path.exists(kernelPath):
                msg = "Did not find %s for setting %s - feature not applicable for this kernel" % ( kernelPath, param)
                self.logger.info(self.module_name, msg)
                continue
                
            # Ok, got here, check for actual setting...
            if paramlist.has_key(param):
                if int(self.__settings[param]) != int(paramlist[param]):
                    msg = "'%s' is set to '%s' in %s; exepcted it to be set to '%s'" % \
                                 (param, paramlist[param], self.__target_file, self.__settings[param])
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    failure_flag = True
                    messages['messages'].append("Fail: %s" % msg)
                else:
                    msg = "Okay: '%s' is set to '%s' in %s" % (param, self.__settings[param], self.__target_file)
                    self.logger.info(self.module_name, msg)
                    messages['messages'].append(msg)
            else:
                msg = "'%s' not found in %s" % (param, self.__target_file)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append("Fail: %s" % msg)
                failure_flag = True

 
        msg = "Checking in-memory kernel settings using sysctl(8) utility"
        self.logger.info(self.module_name, msg)

        for param in  self.__settings.keys():
            if sysdict.has_key(param):
                if int(self.__settings[param]) != int(sysdict[param]):
                    msg = "'%s' is set to '%s' in the running kernel; expected it to be set to '%s'" % \
                              (param, sysdict[param], self.__settings[param])
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    messages['messages'].append("Fail: %s" % msg)
                    failure_flag = True
                else:
                    msg = "Okay: '%s' is set to '%s' in the running kernel" % (param, self.__settings[param])
                    messages['messages'].append(msg)
                    self.logger.info(self.module_name, msg)
            else:
                msg = "'%s' not found; skipping" % param
                self.logger.notice(self.module_name, msg)
                messages['messages'].append(msg)
        

        del paramlist
        del sysdict
        del SysCtl

        if failure_flag == True:
            return False, 'Settings in sysclt are not enabled', messages
        else:
            return True, 'Settings in sysclt are enabled', messages
  
    ##########################################################################
    def apply(self, optionDict=None):

        messages = {}
        messages['messages'] = []

        if sb_utils.os.info.is_LikeSUSE() == True:
            msg = "This module is not applicable to SUSE systems"
            return False, msg, {}

        self.validate_options(optionDict)
        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                delim='=')
        SysCtl = sb_utils.os.linux.sysctl()
        sysdict = SysCtl.getlist()
        change_record = ''
        mem_action_record = {}
        file_action_record = {}

        if len(sysdict) == 0:
            msg = "Unable to get in-memory kernel setting using sysctl(8) utility"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = "Checking settings in %s" % (self.__target_file)
        self.logger.info(self.module_name, msg)

        for param in self.__settings.keys():
            # Verify the parameter setting actually exists in /proc/sys/kernel - if not then the feature doesn't exist and shouldn't be set
            # via sysconfig 
            
            if not param.startswith('kernel.'):
                msg = "Found '%s' as the parameters, expected it to start with 'kernel.', skipping entire module..." % param
                raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
            kernelPath = "/proc/sys/kernel/" + param[7:]
            if not os.path.exists(kernelPath):
                msg = "Did not find %s for setting %s - feature not applicable for this kernel" % ( kernelPath, param)
                self.logger.info(self.module_name, msg)
                continue
            if paramlist.has_key(param):
                if int(self.__settings[param]) == int(paramlist[param]):
                    continue 

            results = sb_utils.os.config.setparam( \
                    configfile=self.__target_file, \
                    param=param, value=str(self.__settings[param]), delim='=')

            if results == False:
                msg = "Unable to set %s in %s" % (param, self.__target_file)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                file_action_record[param] = str(results)
                msg = "Apply Performed: %s set to '%s' in %s" % \
                          (param, self.__settings[param], self.__target_file)
                self.logger.notice(self.module_name, msg)
                messages['messages'].append(msg)



        ######################################################################
        msg = "Checking in-memory kernel settings using sysctl(8) utility"
        self.logger.info(self.module_name, msg)

        for param in  self.__settings.keys():
            if sysdict.has_key(param):
                if int(self.__settings[param]) != int(sysdict[param]):
                    results = SysCtl.setparam( paramname = param, paramval = self.__settings[param])
                    if results == True: 
                        mem_action_record[param] = str(sysdict[param])
                        msg = "Set '%s' to '%s' in running kernel" % (param, str(self.__settings[param]))
                        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
                        messages['messages'].append(msg)
                    else: 
                        msg = "Unable to set '%s' to '%s' in running kernel" % (param, str(self.__settings[param]))
                        self.logger.error(self.module_name, 'Apply Error: ' + msg)
                        messages['messages'].append(msg)


        del paramlist
        del sysdict
        del SysCtl

        if mem_action_record == {} and file_action_record == {}:
            return False, 'empty', messages
        else:
            change_record = "mem|%s\nfile|%s" % (str(mem_action_record), str(file_action_record))
            return True, change_record, messages
                                                            
            
    ##########################################################################
    def undo(self, change_record=None):


        if not change_record or change_record == '': 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        messages = {}
        messages['messages'] = []

        if not os.path.exists('/proc/sys/kernel/exec-shield'):
            msg = "Not Applicable: The ExecShield kernel module is not loaded."
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, msg)
            return False, 'Not Applicable', messages

        records = change_record.split('\n')
        if len(records) != 2:
            msg = "Unable to perform undo operation without a complete record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        mem_obj = None
        file_obj = None

        for line in records:
            try:
                (paramtype, jsonobj) = line.split('|')          
                if paramtype == 'mem':
                    mem_obj = eval(jsonobj)

                if paramtype == 'file':
                    file_obj = eval(jsonobj)
            except Exception:
                continue

        del change_record
        del records

        ######################################################################
        if len(file_obj) != 0:
            msg = "Reverting settings in %s" % (self.__target_file)
            self.logger.info(self.module_name, msg)

            for xparam in file_obj.keys():
                results = ''
                if file_obj[xparam] == '': 
                    results = sb_utils.os.config.unsetparam( \
                        configfile=self.__target_file, param=xparam, delim='=')
                else:
                    results = sb_utils.os.config.setparam( \
                        configfile=self.__target_file, \
                        param=xparam, value=str(file_obj[xparam]), delim='=')

                if results == False:
                    msg = "Unable to set %s in %s" % (xparam, self.__target_file)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                else:
                    if file_obj[xparam] == '':
                        msg = "'%s' removed from %s" % (xparam, self.__target_file)
                        messages['messages'].append(msg)
                    else:
                        msg = "'%s' set to '%s' in %s" % (xparam, file_obj[xparam], self.__target_file)
                        messages['messages'].append(msg)

                    self.logger.notice(self.module_name, "Undo Performed: " + msg)

        del file_obj

        ######################################################################
        if len(mem_obj) != 0:
            msg = "Reverting in-memory kernel settings using sysctl(8) utility"
            self.logger.info(self.module_name, msg)
            SysCtl = sb_utils.os.linux.sysctl()

            for param in  mem_obj.keys():
                results = SysCtl.setparam( paramname = param, paramval = mem_obj[param])
                if results == True:
                    msg = "Reset '%s' to '%s'" % (param, str(mem_obj[param]))
                    messages['messages'].append(msg)
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                else:
                    msg = "Unable to reset '%s' to '%s'" % (param, str(mem_obj[param]))
                    messages['messages'].append(msg)
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)

            del SysCtl
            del mem_obj


        return True, '', messages

