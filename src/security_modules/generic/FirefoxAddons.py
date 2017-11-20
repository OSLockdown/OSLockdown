#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Set Security Settings in User's Firefox Preference file
#  >> Add-Ons Settings
#
#
##############################################################################
from Firefox_utils import Firefox_utils

class FirefoxAddons:

    def __init__(self):
        self.module_name = self.__class__.__name__
        ff_settings = { 'xpinstall.whitelist.add' : '\"\"',
                        'xpinstall.whitelist.add.103' : '\"\"',
                        'xpinstall.whitelist.required': 'true'}
        self.__firefox_utils = Firefox_utils(ff_settings)


    def scan(self, option=None):
        return self.__firefox_utils.scan()


    def apply(self, option=None):
        return self.__firefox_utils.apply()


    def undo(self, change_record=None):
        return self.__firefox_utils.undo(change_record)


if __name__ == '__main__':
    Test = FirefoxAddons()
    print Test.scan()
    #(flag, change_record, messages) = Test.apply()
    #print flag
    #print Test.undo(change_record)
    #print Test.scan()
