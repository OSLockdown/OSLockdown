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
import Ssh_Sshd_ConfigEditor
import sb_utils.os.info

class SshdLogLevel(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name = "SshdLogLevel"

        self.__log_levels = [ 'QUIET', 'FATAL',  'ERROR', 'INFO', 'VERBOSE', 
                             'DEBUG', 'DEBUG1', 'DEBUG2', 'DEBUG3' ]

        self.configfile = '/etc/ssh/sshd_config'
        self.settings = [ ['LogLevel', 'VERBOSE',self._isEqualTo], 
                        ]

        self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshdr'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.package = 'openssh'
        else:
            self.package = 'openssh-server'


    def validate_options(self, optionDict):
        if not optionDict or not 'sshdLogLevel' in optionDict:
            option = 'VERBOSE'
        else:
            option = optionDict['sshdLogLevel']
            
        if option.upper() not in self.__log_levels:
            msg = "Invalid LogLevel provided. Defaulting to 'VERBOSE'"
            self.logger.warn(self.module_name, msg)
            messages['messages'].append(msg)
    
        self.settings = [['LogLevel', option, self._isEqualTo]]
    
    def scan(self,optionDict=None):
        self.validate_options(optionDict)
        return self.scanCfg(self.settings)
        
    def apply(self, optionDict=None):
        self.validate_options(optionDict)
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
      





    

if __name__ == '__main__':
    TEST = SshdLogLevel()
    print TEST.scan('VERBOSE')
    #print TEST.apply('VERBOSE')
    #print TEST.undo('INFO')
