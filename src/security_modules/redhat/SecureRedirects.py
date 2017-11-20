#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.config
import sb_utils.os.linux


class SecureRedirects:
    def __init__(self):

        self.module_name = "SecureRedirects"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.__target_file = "/etc/sysctl.conf"

        self.__settings = {'net.ipv4.conf.all.secure_redirects': 0,
                           'net.ipv4.conf.default.secure_redirects': 0 }

    ##########################################################################
    def validate_input(self, option):
        return


    ##########################################################################
    def scan(self, option=None):


        paramlist = sb_utils.os.config.get_list(configfile=self.__target_file,
                                                delim='=') 
        SysCtl = sb_utils.os.linux.sysctl()
        sysdict = SysCtl.getlist()

        if len(sysdict) == 0:
            msg = "Unable to get in-memory kernel setting using sysctl(8) utility"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        ipv6_enabled = False
        if sysdict.has_key('net.ipv6.conf.default.forwarding'):
            ipv6_enabled = True
        else:
            msg = "IPv6 support not enabled in the OS; skipping IPv6 tests."
            self.logger.info(self.module_name, msg)

        failure_flag = False

        msg = "Checking settings in %s" % (self.__target_file)
        self.logger.info(self.module_name, msg)

        for param in  self.__settings.keys():
            if paramlist.has_key(param):
                if int(self.__settings[param]) != int(paramlist[param]):
                    msg = "'%s' is set to '%s' in %s; exepcted it to be set to '%s'" % \
                                 (param, paramlist[param], self.__target_file, self.__settings[param])
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    failure_flag = True
                else:
                    msg = "Okay: '%s' is set to '%s' in %s" % (param, self.__settings[param], self.__target_file)
                    self.logger.info(self.module_name, msg)
            else:
                if 'ipv6' in param.split('.') and ipv6_enabled == False:
                    msg = "Skipping - '%s' not found in %s" % (self.__target_file, param)
                    self.logger.info(self.module_name, msg)
                else:
                    msg = "'%s' not found in %s" % (param, self.__target_file)
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    failure_flag = True

 
        msg = "Checking in-memory kernel settings using sysctl(8) utility"
        self.logger.info(self.module_name, msg)

        for param in  self.__settings.keys():
            if sysdict.has_key(param):
                if int(self.__settings[param]) != int(sysdict[param]):
                    msg = "'%s' is set to '%s' in the running kernel; expected it to be set to '%s'" % \
                              (param, sysdict[param], self.__settings[param])
                    self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                    failure_flag = True
                else:
                    msg = "Okay: '%s' is set to '%s' in the running kernel" % (param, self.__settings[param])
                    self.logger.info(self.module_name, msg)
            else:
                msg = "'%s' not found; skipping" % param
                self.logger.notice(self.module_name, msg)
        

        del paramlist
        del sysdict
        del SysCtl

        if failure_flag == True:
            return 'Fail', ''
        else:
            return 'Pass', ''
  
    ##########################################################################
    def apply(self, option=None):


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

        ipv6_enabled = False
        if sysdict.has_key('net.ipv6.conf.default.forwarding'):
            ipv6_enabled = True
        else:
            msg = "IPv6 support not enabled in the OS; skipping IPv6 tests."
            self.logger.info(self.module_name, msg)

        ######################################################################
        msg = "Checking settings in %s" % (self.__target_file)
        self.logger.info(self.module_name, msg)

        for xparam in self.__settings.keys():
            if paramlist.has_key(xparam):
                if int(self.__settings[xparam]) == int(paramlist[xparam]):
                    continue 
            else:
                if 'ipv6' in xparam.split('.') and ipv6_enabled == False:
                    msg = "Skipping - '%s' not found in %s" % (self.__target_file, xparam)
                    self.logger.info(self.module_name, msg)
                    continue

            results = sb_utils.os.config.setparam( \
                    configfile=self.__target_file, \
                    param=xparam, value=str(self.__settings[xparam]), delim='=')

            if results == False:
                msg = "Unable to set %s in %s" % (xparam, self.__target_file)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                file_action_record[xparam] = str(results)
                msg = "Apply Performed: %s set to '%s' in %s" % \
                          (xparam, self.__settings[xparam], self.__target_file)
                self.logger.notice(self.module_name, msg)



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
                    else: 
                        msg = "Unable to set '%s' to '%s' in running kernel" % (param, str(self.__settings[param]))
                        self.logger.error(self.module_name, 'Apply Error: ' + msg)


        del paramlist
        del sysdict
        del SysCtl

        if mem_action_record == {} and file_action_record == {}:
            return 0, ''
        else:
            change_record = "mem|%s\nfile|%s" % (str(mem_action_record), str(file_action_record))
            return 1, change_record
                                                            
            
    ##########################################################################
    def undo(self, change_record=None):


        if not change_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

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
                    else:
                        msg = "'%s' set to '%s' in %s" % (xparam, file_obj[xparam], self.__target_file)

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
                    self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
                else:
                    msg = "Unable to reset '%s' to '%s'" % (param, str(mem_obj[param]))
                    self.logger.error(self.module_name, 'Undo Error: ' + msg)

            del SysCtl
            del mem_obj


        return 1

