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


class SshdRestrictHMAC(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name = "SshdRestrictHMAC"
        
        self.configfile = '/etc/ssh/sshd_config'
        self.settings = [ ['MACs', 'hmac-sha1' , self._isEqualTo ] ]

        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshdr'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.package = 'openssh'
        else:
            self.package = 'openssh-server'
        
        self.logger = TCSLogger.TCSLogger.getInstance()
    

    def scan(self,optionDict=None):
        return self.scanCfg(self.settings)
        
    def apply(self, optionDict=None):
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
