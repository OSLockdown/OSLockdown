#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Set idle timeout for ssh connections
#
#

import sys
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import sb_utils.os.info
import TCSLogger
import Ssh_Sshd_ConfigEditor


class SshdSetIdleTimeout(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name = "SshdSetIdleTimeout"
        
        self.configfile = '/etc/ssh/sshd_config'
        self.settings = []  # overridden in validate_input()

        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshdr'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.package = 'openssh'
        else:
            self.package = 'openssh-server'
        
        self.logger = TCSLogger.TCSLogger.getInstance()
        
        
    def validate_input(self, optionDict):
        if optionDict == None or not 'sshdIdleTimeout' in optionDict :
            return False
        try:
            value = int(optionDict['sshdIdleTimeout'])
        except ValueError:
            msg = "Invalid option value -> '%s'" % optionDict
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if value < 1:
            msg = "Invalid option value -> '%s'" % optionDict
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        self.settings = [ ['ClientAliveInterval', optionDict['sshdIdleTimeout'] , self._noLessThan ] , 
                            ['ClientAliveCountMax', '0' , self._isEqualTo ] ]

    def scan(self,optionDict=None):
        self.validate_input(optionDict)
        return self.scanCfg(self.settings)
        
    def apply(self, optionDict=None):
        self.validate_input(optionDict)
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
