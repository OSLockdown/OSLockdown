#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable SELinux Restorecon Service (restorecond)
#
# NOTE: The restorecond daemon monitors a list of files which are frequently 
#       created or modified on running systems, and whose SELinux contexts are 
#       not set correctly. It looks for creation events related to files listed 
#       in /etc/selinux/restorecond.conf, and sets the contexts of those files 
#       when they are discovered. 
#
#
##############################################################################

try:
    import Enable_Disable_Any_Service
except ImportError:
    raise

class DisableRestorecond:

    def __init__(self):

        self.module_name = self.__class__.__name__


    def scan(self, option=None):
        return Enable_Disable_Any_Service.scan(self.module_name, enable=False)    


    def apply(self, option=None):
        return Enable_Disable_Any_Service.apply(self.module_name, enable=False)    


    def undo(self, change_record=None):
        return Enable_Disable_Any_Service.undo(self.module_name, change_record=change_record)    
        


if __name__ == '__main__':
    TEST = DisableRestorecond()
    print TEST.scan()
    (x, y, z) = TEST.apply()
    print TEST.undo(y)
