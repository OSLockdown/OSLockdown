#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.acctmgt.acctfiles

class DisablePrelinking:
    """
    Disable Prelinking service and undo existing prelinks
    """

    def __init__(self):

        self.module_name = 'DisablePrelinking'
        self.__target_file = '/etc/sysconfig/prelink'
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__pkgname = "prelink"


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    def check_file(self, pkgname, filename, targetValue):
        """
        Check the lines in looking for the 'PRELINKING=' line.  If the value of 'PRELINKING=' isn't targetValue, then make it so.  While
        no explicit checks are being done, targetValue should be 'yes' or 'no'.
        """
        
        changeRec = {}
        
        lines = None
        msg = None
        
        results =  sb_utils.os.software.is_installed(pkgname)
        if results != True:
            msg = "'%s' package is not installed on the system" % pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        elif not os.path.isfile(filename):
            msg = "No such file '%s'" % filename
            self.logger.warning(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            lines = open(filename).readlines()    
            for ln in range(len(lines)):
                line = lines[ln].strip()
                if not line.startswith('PRELINKING='):
                    continue
                value = line.split('=',1)[1]
                if value == targetValue:
                    self.logger.info(self.module_name, "Found '%s' in '%s'" % (line, filename))                
                else:
                    msg = "Found '%s' in '%s', expected 'PRELINKING=%s'" % (line, filename, targetValue)
                    self.logger.warning(self.module_name, msg)
                    lines[ln] = line.split('=')[0]+'='+targetValue+'\n'
                    changeRec = value
                     
                break
        
        
        return lines, changeRec, msg
        
                        
    ##########################################################################
    def scan(self, option=None):
        """
        Check to see if prelink rpm is intalled and PRELINKING=no in /etc/sysconfig/prelink
        """
        
        retval = True
        messages = {'messages':[] }
        
        newLines, changeRec, msg = self.check_file(self.__pkgname, self.__target_file, targetValue = 'no')
        if msg :
            messages['messages'].append(msg)
            retval = False   

        return retval, '',messages

    ##########################################################################
    def apply(self, option=None):

        changeRec = {}

        messages = {'messages':[]}
        retval = False
        
        targetValue = 'no'
        newLines, changeRec, msg = self.check_file(self.__pkgname, self.__target_file, targetValue = targetValue)
        
        if msg:
            msg = "Setting 'PRELINKING=%s' in '%s'" % (targetValue, self.__target_file)
            self.logger.info(self.module_name, msg)
            retval = True
            try:
                open(self.__target_file,'w').writelines(newLines)
            except IOError:
                msg = "Unable to write to %s " % self.__target_file
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            self.logger.info(self.module_name, "Calling '/usr/sbin/prelink' to undo all prelinks...")

            # allow up to 5 minutes for this to complete
            cmd = '/usr/sbin/prelink -ua'
            output = tcs_utils.tcs_run_cmd(cmd, True, cmdTimeout=300)
            if output[0] != 0 :
                self.logger.warning(self.module_name, "Command returned error code %d" % output[0])
            if output[2]:
                for lines in output[2].splitlines():
                    self.logger.warning(self.module_name, lines)   
        else:
            changeRec = ''
        return retval, str(changeRec), messages

    ##########################################################################
    def undo(self, changeRec=None):
        """Undo the previous action."""


        messages = {'messages':[]}
        retval = False

        newLines, scratch, msg = self.check_file(self.__pkgname, self.__target_file, targetValue = changeRec)
        
        if msg:
            msg = "Setting 'PRELINKING=%s' in '%s'" % (changeRec, self.__target_file)
            self.logger.info(self.module_name, msg)
            retval = True
            try:
                open(self.__target_file,'w').writelines(newLines)
            except IOError:
                msg = "Unable to write to %s " % self.__target_file
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            changeRec = ''
        return retval, "Undo Performed: Prelinking will occur the next time '/etc/cron.daily/prelink' is executed.", messages


