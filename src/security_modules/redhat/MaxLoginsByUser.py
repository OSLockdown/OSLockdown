#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sha
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms

class MaxLoginsByUser:

    def __init__(self):
        """
        Set the maximum number of logins by a specific user.
        """
        self.module_name = "MaxLoginsByUser"
        self.__target_file = "/etc/security/limits.d/MaxLoginsByUser"
        self.logger = TCSLogger.TCSLogger.getInstance()


    def setMaxLoginLines(self, maxLogins):
        # One option
        self.__lines1 = '* - maxlogins %d\n' % maxLogins
        
        self.__lines2 = '* hard maxlogins %d\n' % maxLogins


    def processFile(self, fileName, requiredText):

        try:
            fileContents = open(fileName, 'r').read()
        except IOError:
            msg = 'Unable to read %s' % self.__target_file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
        # See if the desired lines are 'contained' in the actual file.  This file counld have been altered (by SetMesgN for example).
        
        if requiredText not in fileContents:
            msg = '%s is incorrect' % fileName 
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg
    
        return True, "Found required lines"
        
    ##########################################################################
    def scan(self, optionDict=None):
        """
        Analyze system
        """

        if optionDict == None or not 'maxLoginsByUser' in optionDict:
            msg = "Missing option value"
            self.logger.error(self.module_name, 'Apply Failed: ' + msg)
            return 0, ''
        option = optionDict['maxLoginsByUser']

        try:
            value = int(option)
        except ValueError:
            msg = 'Bad option value'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        

        # Build Strings to represent what the files MUST
        # have in them
        self.setMaxLoginLines(value)

        messages = {'messages' : []}
        retval = False

        if not os.path.isdir(os.path.dirname(self.__target_file)):
            msg = "Required path does not exist - OS may not support the '%s' file" % self.__target_file
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if not os.path.isfile(self.__target_file):
            msg = 'Missing %s' % self.__target_file
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
        else:
            ret1, message1 = self.processFile(self.__target_file, self.__lines1)
            if ret1 == True:
                retval = True
                messages['messages'].append(message1)        
            else:
                ret2, message2 = self.processFile(self.__target_file, self.__lines2)
                if ret2 == True:
                    retval = True
                    messages['messages'].append(message1)        
        
        if retval == True:
            msg = "Maximum number of per user logins correct"
        else:
            msg = "Maximum number of per user logins incorrect"

        
        return retval, '', {'messages':messages}


    ##########################################################################
    def _write_shell_script(self, filename, filecontents):
        try:
            out_obj = open(filename, 'w')
        except IOError, err:
            msg = "Unable to create %s: %s" % (filename, err)
            self.logger.info(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        out_obj.write(filecontents)
        out_obj.close()

        msg = "%s created" % filename
        self.logger.notice(self.module_name, msg)

        changes_to_make = {'owner':'root',
                           'group':'root',
                           'dacs':0644}
        ignore_results = sb_utils.file.fileperms.change_file_attributes(filename, changes_to_make)
        return True

    ##########################################################################
    def apply(self, optionDict=None):
        """
        """

        results, reason, messages = self.scan(optionDict)
        if results == True:
            return False, reason,messages
            
        ###################################
        # Bash, Bourne, and Korn stuff
        ###################################
        messages = {'messages' : []}
        files_created = []
        
        if self._write_shell_script(self.__target_file, self.__lines1) == True:
            files_created.append(self.__target_file)
            messages['messages'].append("Wrote '%s'" % self.__target_file)
        
        self.logger.notice(self.module_name, 'Apply Performed')
        
        if files_created == [] :
            return False, 'No changes required', {}
        else:
            return True, '\n'.join(files_created), messages


    ##########################################################################
    def undo(self, change_record=None):
        """
        """
        
        for shfile in change_record.splitlines():
            try:
                os.unlink(shfile)
                self.logger.notice(self.module_name,'Undo : removed %s' % shfile)
            except IOError:
                msg = 'Unable to remove %s' % shfile
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            

        msg = 'Maximum logins by user removed from %s' % self.__target_file
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

    ##########################################################################
    def validate_input(self, option=None):
        """
        Validate input 
        """
        if option == None:
            return 0

if __name__ == "__main__":
    test = MaxLoginsByUser()
    options = {'maxLoginsByUser':10}
    print test.scan(options)
#    print test.apply(options)
