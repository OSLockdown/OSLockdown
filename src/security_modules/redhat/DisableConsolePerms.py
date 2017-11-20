#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

"""
  DisableConsolePerms
  If /etc/security/console.perms exists, rename it

"""

import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class DisableConsolePerms:
    """
    Class to rename an existing /etc/security/console.perms to 
      /etc/security/console.perms.disabled
    """

    def __init__(self):
        """Constructor"""
        self.module_name = "DisableConsolePerms"
        self.__target_file = '/etc/security/console.perms'
        self.__new_file = self.__target_file + '.disabled'
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """See if /etc/secure/console.perms exists"""

        if os.path.isfile(self.__target_file):
            msg = "%s exists" % self.__target_file
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, '', {'messages':msg}
        else:    
            msg = "%s does not exist" % self.__target_file
            self.logger.debug(self.module_name, 'Scan Passed: ' + msg)
            return True, '', {'messages':msg}

    ##########################################################################
    def apply(self, option=None):
        """Apply changes."""

        change_record = ''

        if not os.path.isfile(self.__target_file):
            return False, '', {'messages':'%s does not exist' % self.__target_file}
        else:    
            try:
                os.rename(self.__target_file, self.__new_file)
                change_record = 'renamed'
            except Exception, e:
                msg = "Unable to rename %s to %s: %s" % (self.__target_file, self.__new_file, e)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                

        msg = '%s renamed to %s' % ( self.__target_file, self.__new_file)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, change_record, {'messages':msg}


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record or change_record != 'renamed':
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if os.path.isfile (self.__target_file):
            msg = "Unable to perform undo, %s already exists." % self.__target_file
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if not os.path.isfile (self.__new_file):
            msg = "Unable to perform undo, renamed original file %s does not exist." % self.__new_file
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            os.rename(self.__new_file, self.__target_file)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'The %s configuration file has been restored.' % self.__target_file
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {'messages':msg}
