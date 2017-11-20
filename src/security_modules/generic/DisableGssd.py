#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disables Generic Security Service (GSS) daemon
#
# NOTE: We have to do something special for SUSE in this module.
#
##############################################################################

try:
    import Enable_Disable_Any_Service
except ImportError:
    raise

import sys
sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info

class DisableGssd:

    def __init__(self):

        self.module_name = self.__class__.__name__

        self.suse_msg = "The rpc.gssd(8) is integrated into the NFS server and client "\
             "services. It is controlled in the /etc/sysconfig/nfs but is "\
              "not started alone in SUSE therefore, this module is not applicable "\
              "on this system."

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    ###################
    ##     Scan      ##
    ###################
    def scan(self, option=None):

        if sb_utils.os.info.is_LikeSUSE() == False:
            return Enable_Disable_Any_Service.scan(self.module_name, enable=False)    

        results =  sb_utils.os.software.is_installed(pkgname='nfs-kernel-server')
        if results != True:
            msg = "'nfs-kernel-server' package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        self.logger.notice(self.module_name, 'Not Applicable: ' + self.suse_msg)
        raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, self.suse_msg))



    ###################
    ##    Apply      ##
    ###################
    def apply(self, option=None):

        if sb_utils.os.info.is_LikeSUSE() == False:
            return Enable_Disable_Any_Service.apply(self.module_name, enable=False)    

        messages = {}
        messages['messages'] = []
        results =  sb_utils.os.software.is_installed(pkgname='nfs-kernel-server')
        if results != True:
            msg = "'nfs-kernel-server' package is not installed" 
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            messages['messages'].append(msg)                 
        else:
            messages['messages'].append('nfs-kernel-server package is installed')
            messages['messages'].append(self.suse_msg)

        return False, 'empty', messages


    ###################
    ##     Undo      ##
    ###################
    def undo(self, change_record=None):

        if sb_utils.os.info.is_LikeSUSE() == False:
            return Enable_Disable_Any_Service.undo(self.module_name, change_record=change_record)    

        messages = {}
        messages['messages'] = []
        results =  sb_utils.os.software.is_installed(pkgname='nfs-kernel-server')
        if results != True:
            msg = "'nfs-kernel-server' package is not installed" 
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            messages['messages'].append(msg)                 
        else:
            messages['messages'].append('nfs-kernel-server package is installed')
            messages['messages'].append(self.suse_msg)

        return False, 'Not applicable', messages


if __name__ == '__main__':
    TEST = DisableGssd()
    print TEST.scan()
    (x, y, z) = TEST.apply()
    print z
    print TEST.undo(y)
