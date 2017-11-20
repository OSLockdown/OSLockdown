#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import Ssh_Sshd_ConfigEditor

class SshdMaxAuthTries(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name = "SshdMaxAuthTries"

        self.configfile = '/etc/ssh/sshd_config'
        self.settings = [ ]   # Overridden in validate_options()

        self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshdr'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.package = 'openssh'
        else:
            self.package = 'openssh-server'


        
    def validate_options(self, optionDict):
        
        if not optionDict or not 'MaxAuthTries' in optionDict :
            option = '3'
        else:
            option = optionDict['MaxAuthTries']
            
        self.settings = [ ['MaxAuthTries' , option, self._noGreaterThan]]
        
    def scan(self,optionDict=None):
        self.validate_options(optionDict)
        return self.scanCfg(self.settings)
        
    def apply(self, optionDict=None):
        self.validate_options(optionDict)
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
      

    
