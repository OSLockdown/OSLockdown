#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Set Security Settings in User's Firefox Preference file
#  >> Java
#
#
##############################################################################
import sys
sys.path.append("/usr/share/oslockdown")
import tcs_utils
from Firefox_utils import Firefox_utils

class FirefoxJava:

    def __init__(self):
        self.module_name = self.__class__.__name__
        self._ff_settings = {}


    ##########################################################################
    def scan(self, optionDict=None):
        if optionDict == None or not 'FirefoxJava' in optionDict:
            msg = "No module option provided"
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['FirefoxJava']
        option = int(option)
        if option < 0 or option > 1:
            msg = "Invalid option provided"
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
            
        ff_settings = self._ff_settings
        if option == 0:
            ff_settings['security.enable_java'] = 'false'
        else:
            ff_settings['security.enable_java'] = 'true'
        
        firefox_utils = Firefox_utils(ff_settings)
        return firefox_utils.scan()

    ##########################################################################
    def apply(self, optionDict=None):
        if optionDict == None or not 'FirefoxJava' in optionDict:
            msg = "No module option provided"
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['FirefoxJava']
        option = int(option)
        if option < 0 or option > 1:
            msg = "Invalid option type provided"
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        ff_settings = self._ff_settings
        if option == 0:
            ff_settings['security.enable_java'] = 'false'
        else:
            ff_settings['security.enable_java'] = 'true'
        
        firefox_utils = Firefox_utils(ff_settings)
        return firefox_utils.apply()


    ##########################################################################
    def undo(self, change_record=None):
        firefox_utils = Firefox_utils({})
        return firefox_utils.undo(change_record)


if __name__ == '__main__':
    Test = FirefoxJava()
    print Test.scan(option=1)
    #(flag, change_record, messages) = Test.apply()
    #print flag
    #print Test.undo(change_record)
    #print Test.scan()
