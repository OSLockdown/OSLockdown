#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Set Security Settings in User's Firefox Preference file
#  >> Encryption Related Settings
#
#
##############################################################################
from Firefox_utils import Firefox_utils

class FirefoxEncryption:

    def __init__(self):
        self.module_name = self.__class__.__name__
        ff_settings = { 'security.enable_ssl2' : 'false',
                        'security.enable_ssl3' : 'false',
                        'security.enable_tls' : 'true',
                        'security.warn_viewing_mixed'  : 'true',
                        'security.warn_entering_weak' : 'true',
                        'security.OCSP.enabled' : '1',
                        'security.default_personal_cert': '\"Ask Every Time\"' }
        self.__firefox_utils = Firefox_utils(ff_settings)


    def scan(self, option=None):
        return self.__firefox_utils.scan()


    def apply(self, option=None):
        return self.__firefox_utils.apply()


    def undo(self, change_record=None):
        return self.__firefox_utils.undo(change_record)


if __name__ == '__main__':
    Test = FirefoxEncryption()
    print Test.scan()
    #(flag, change_record, messages) = Test.apply()
    #print flag
    #print Test.undo(change_record)
    #print Test.scan()
