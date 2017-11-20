#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# This module is present to indicate that FirefoxPrefs has been retired.


import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class FirefoxPrefs:

    def __init__(self):
        self.module_name = "FirefoxPrefs"
        self.msg = "Retired: The 'FirefoxPrefs' Module has been removed and replaced by the \
                    'FirefoxPrivacy', 'FirefoxAddons', FirefoxDynamicContent', and \
                    'FirefoxEncryption' modules.  Please refer to the Modules Guide \
                    for more information."
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option):

        raise tcs_utils.ScanError("%s %s" % (self.module_name, self.msg))


    ##########################################################################
    def apply(self, option):

        raise tcs_utils.ActionError("%s %s" % (self.module_name, self.msg))


    ##########################################################################
    def undo(self, change_record):

        raise tcs_utils.ActionError("%s %s" % (self.module_name, self.msg))

