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


class SshRestrictCiphers(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name = "SshRestrictCipher"
        
        self.configfile = '/etc/ssh/ssh_config'
        # Settings here don't matter, the scan/apply will override to correct values
        
        self.settings = [ ['Ciphers', 'foo' , self._restrictCiphers  ] ]

        # defaultCiphers taken from sshd_config man page(s) and manually restricted to valid ciphers
        
        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshcr'
            self.defaultCiphers = "aes128-ctr,aes128-cbc,arcfour,3des-cbc,blowfish-cbc"
        else:
            self.package = 'openssh'
            self.defaultCiphers = "aes128-ctr,aes192-ctr,aes256-ctr,arcfour256,arcfour128,aes128-cbc,3des-cbc,blowfish-cbc,cast128-cbc,aes192-cbc,aes256-cbc,arcfour"
        
        self.logger = TCSLogger.TCSLogger.getInstance()
            
    def scan(self,optionDict=None):
        restrictions = {}
        for key in ['mustStartWith', 'mustEndWith', 'mustContain']:
            if key in optionDict:
                restrictions[key] = optionDict[key]

        self.settings = [['Ciphers', restrictions, self._restrictCiphers]]
        return self.scanCfg(self.settings)
        
    def apply(self, optionDict=None):
        restrictions = {}
        for key in ['mustStartWith', 'mustEndWith', 'mustContain']:
            restrictions[key] = None
            try:
                restrictions[key] = optionDict[key]
            except KeyError:
                pass
        self.settings = [['Ciphers', restrictions, self._restrictCiphers]]
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)

if __name__ == "__main__":
    myLog = TCSLogger.TCSLogger.getInstance()
    myLog.force_log_level (7)
    myLog._fileobj = sys.stdout
    test = SshRestrictCiphers()
    print test.scan()
