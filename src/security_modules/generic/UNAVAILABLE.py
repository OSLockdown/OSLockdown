#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This is an empty module to handle modules which could not
# be imported. Import problems could stem from a profile
# listing a module which the system does not have a corresponding 
# python module

import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class UNAVAILABLE:

    def __init__(self):
        self.module_name = "UNAVAILABLE"

        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option):

        msg = "Missing module"
        raise tcs_utils.ScanError("%s %s" % (self.module_name, msg))


    ##########################################################################
    def apply(self, option):

        msg = "Missing module"
        raise tcs_utils.ActionError("%s %s" % (self.module_name, msg))


    ##########################################################################
    def undo(self, change_record):

        msg = "Missing module"
        raise tcs_utils.ActionError("%s %s" % (self.module_name, msg))

