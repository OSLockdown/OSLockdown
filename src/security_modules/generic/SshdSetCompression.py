#!/usr/bin/env python
#
# Copyright (c) 2013-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")

import tcs_utils
import TCSLogger
import sb_utils.SELinux
import sb_utils.os.info
import sb_utils.os.software
import Ssh_Sshd_ConfigEditor

class SshdSetCompression(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):
    """
    """

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name    = "SshdSetCompression"
     
        self.configfile = '/etc/ssh/sshd_config'
        self.settings = [ ['Compression', 'no',self._isEqualTo], 
                        ]

        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshdr'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.package = 'openssh'
        else:
            self.package = 'openssh-server'

    def validate_options(self, optionsDict):
        if optionsDict['sshdCompressionMode'] == '1':
            comp = 'delayed'
        else :
            comp = 'no'
        self.settings = [ ['Compression', comp,self._isEqualTo], 
                        ]
    def scan(self,optionsDict=None):
        self.validate_options(optionsDict)
        return self.scanCfg(self.settings)
        
    def apply(self, optionsDict=None):
        self.validate_options(optionsDict)
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
      


if __name__ == '__main__':
    test = SshdSetCompression()
    print test.scan()
