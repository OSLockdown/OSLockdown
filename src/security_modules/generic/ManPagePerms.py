#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.exclusion
import sb_utils.file.fileperms

import pwd
import grp
import GenericPerms


class ManPagePerms:

    def __init__(self):
        self.module_name = "ManPagePerms"
        self.logger = TCSLogger.TCSLogger.getInstance()

# Commented and retained for legacy....
#        # fspec : octal mode MASK, owner, group, recursive
#        # owner/group: use -1 for "leave as is"
#        self.__man_dirs = { '/usr/share/man/': '0644,root,root',
#                            '/usr/share/info/': '0644,root,root',
#                            '/usr/share/infopage/': '0644,root,root' }
#
#        if sb_utils.os.info.is_solaris() == True: 
#
#            self.__man_dirs['/etc/webmin/man']      = '0644,root,root'
#            self.__man_dirs['/opt/SUNWrtvc/man']    = '0644,root,root'
#            self.__man_dirs['/usr/apache2/man']     = '0644,root,root'
#            self.__man_dirs['/usr/apache/man']      = '0644,root,bin'
#            self.__man_dirs['/usr/demo/link_audit/man'] = '0644,root,root'
#            self.__man_dirs['/usr/dt/share/man']    = '0644,root,root'
#            self.__man_dirs['/usr/j2se/man']        = '0644,root,root'
#            self.__man_dirs['/usr/jdk/instances/jdk1.5.0/man'] = '0644,root,root'
#            self.__man_dirs['/usr/lib/cc-ccr/man'] = '0644,root,root'
#            self.__man_dirs['/usr/local/man'] = '0644,root,root'
#            self.__man_dirs['/usr/openwin/share/man'] = '0644,root,root'
#            self.__man_dirs['/usr/perl5/5.6.1/man'] = '0644,root,root'
#            self.__man_dirs['/usr/perl5/5.8.3/man'] = '0644,root,root'
#            self.__man_dirs['/usr/perl5/5.8.4/man'] = '0644,root,root'
#            self.__man_dirs['/usr/sfw/lib/webmin/caldera/man'] = '0644,root,root'
#            self.__man_dirs['/usr/sfw/lib/webmin/man'] = '0644,root,root'
#            self.__man_dirs['/usr/sfw/lib/webmin/mscstyle3/man'] = '0644,root,root'
#            self.__man_dirs['/usr/sfw/lib/webmin/perlmod/man'] = '0644,root,root'
#            self.__man_dirs['/usr/sfw/share/man']   = '0644,root,bin'
#            self.__man_dirs['/usr/share/man'] = '0644,root,root'
#            self.__man_dirs['/usr/share/webconsole/man'] = '0644,root,root'
#            self.__man_dirs['/usr/SUNWale/share/man']          = '0644,root,root'
#            self.__man_dirs['/usr/X11/share/man']   = '0644,root,bin'


    ##########################################################################
    def scan(self, optionDict={}):

        return GenericPerms.scan(optionDict=optionDict)


    ##########################################################################
    def apply(self, optionDict={}):

        return GenericPerms.apply(optionDict=optionDict)

    ##########################################################################
    def undo(self, change_record=None):

        return GenericPerms.undo(change_record=change_record)

