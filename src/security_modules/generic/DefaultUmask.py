#!/usr/bin/env python
#########################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##########################################################################

import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.SELinux
import sb_utils.file.dac
import re

class DefaultUmask:

    def __init__(self):

        self.module_name = "DefaultUmask"

        self.__umaskStr = '077'
        self.__umaskVal = 077

        # This isn't an exhaustive way of finding the command, but we're not writing a $(SHELL) parser here
        # Look for the simple case of umask on a line by itself, but allow for the argument not being 
        # processable
        # look for any lines that don't have a '#' as the leading non-whitespace character
        # ... the exact work 'umask' followed by at least one whitespace and a 
        # and then a whitespace separated argument.  If the argument is numeric and can be treated as octal
        # great, otherwise we need to highlight this for the user via a module message.  Not sure if we want
        # to treat such as a true 'failure', or perhaps make sure we can *everything* first and only
        # make changes if we can clearly locate such
        
        shell_pattern = "^(\s*[^#]umask\s+)(\S+)"
        shell_regex=re.compile(shell_pattern)

        self.__filesToCheck = []
        self.__filesToCheck.append( ('/etc/profile',            'umask', shell_regex, 'umask '))
        self.__filesToCheck.append( ('/etc/.login',             'umask', shell_regex, 'umask '))
        self.__filesToCheck.append( ('/etc/skel/local.cshrc',   'umask', shell_regex, 'umask '))
        self.__filesToCheck.append( ('/etc/skel/local.cshrc',   'umask', shell_regex, 'umask '))
        self.__filesToCheck.append( ('/etc/skel/local.login',   'umask', shell_regex, 'umask '))
        self.__filesToCheck.append( ('/etc/skel/local.profile', 'umask', shell_regex, 'umask '))

        if sb_utils.os.info.is_solaris() != True:
            self.__filesToCheck.append( ('/etc/bashrc',         'umask', shell_regex, 'umask '))
            self.__filesToCheck.append( ('/etc/csh.cshrc',      'umask', shell_regex, 'umask '))
            self.__filesToCheck.append( ('/etc/csh.login',      'umask', shell_regex, 'umask '))
        else:
            defLogin_pattern = "^(\s*[^#]UMASK=)(\S+)"
            defLogin_regex = re.compile(defLogin_pattern)
            self.__filesToCheck.append( ('/etc/default/login',  'UMASK', defLogin_regex, 'UMASK='))
            
        self.logger = TCSLogger.TCSLogger.getInstance()        
        

    ##########################################################################
    def validate_input(self, optionDict):
        if optionDict == None or not 'defaultUmask' in optionDict :
            return False
        
        # the umask must be an string representing an octal value, so try to convert to octal and 
        # check the range for validity.  If it passes, use as is.  Otherwise fail with an invalid
        # parameter message
        
        try:
            value = int(optionDict['defaultUmask'],8)
            if value < 0 or value > 0777:
                raise ValueError
        except ValueError:
            msg = "Invalid umask -> '%s'" % optionDict
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        self.__umaskVal = value
        self.__umaskStr = optionDict['defaultUmask']
        

    def isUmaskAcceptable(self, foundUmask):
        """
        Borrowed from sb_utils.file.dac.isPermOkay, modified to:
            look only at lower 3 octal digits of dacs
            allow for unprocessable mask
        Returns : True  = value found is acceptable
                : False = value found is inacceptable (i.e. value found is too permissive)
                : None  = unable to process value found (i.e. value can't be processed as octal)
        """
        try:
            if type(foundUmask) == type(""):
                foundUmask = int(foundUmask,8)
                if foundUmask < 0 or foundUmask > 0777:
                    raise ValueError
        except ValueError, err:
            return None
        
        # locate any bit with issues (IE set in foundUmask but not in maxiumValue
        otherMask = sb_utils.file.dac.isOTH(self.__umaskVal, foundUmask)
        groupMask = sb_utils.file.dac.isGRP(self.__umaskVal, foundUmask)
        userMask  = sb_utils.file.dac.isUSR(self.__umaskVal, foundUmask)

        fullMask = otherMask|groupMask|userMask
              
        if fullMask == 0:
            retval = True
        else:
            retval = False
        return retval
      

    ##########################################################################
    def _change_one_file(self, action, filename, fieldName, fieldRegex, fieldMissing):
        # Protect file
        tcs_utils.protect_file(filename)
        messages=[]
        action_record=""
        fileAcceptable = True
        
        try:
            lines = open(filename, 'r').readlines()
        except (IOError, OSError), err:
            msg = "Unable to open %s: %s" % (filename, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        umask_found = False
        for ln in range(len(lines)):
            line = lines[ln]
            match = fieldRegex.search(line)
            if not match:
                continue
            umask_found = True
            umask_found = match.group(2)
            
            isAcceptable = self.isUmaskAcceptable(umask_found)
            if isAcceptable == True:
                msg=  "Found acceptable '%s' value of '%s' in %s(%d) -> %s" % (umask_found, fieldName, filename, ln+1, line.strip())
                self.logger.debug(self.module_name,msg)
            elif isAcceptable == False:
                fileAcceptable = False
                msg = "Found unacceptable '%s' value of '%s' in %s(%d) -> %s" % (umask_found, fieldName, filename, ln+1, line.strip())
                self.logger.debug(self.module_name,msg)
                lines[ln] =  fieldRegex.sub('\g<1>%s' % self.__umaskStr, line)
                messages.append(msg)
            elif isAcceptable == None:
                msg = "Found UNPROCESSABLE '%s' value of '%s' in %s(%d) -> %s" % (umask_found, fieldName, filename, ln+1, line.strip())
                self.logger.warn(self.module_name,msg)
                messages.append(msg)
           
        if action == 'scan':
            if fileAcceptable == False:
                action_record = "False"
        else:
            try:
                out_obj = open(filename + '.new', 'w').writelines(lines)
            except Exception, err:
                msg = "Unable to create temporary file (%s)." % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
            action_record = tcs_utils.generate_diff_record(filename + '.new', 
                                                           filename)

            try:
                shutil.copymode(filename, filename + '.new')
                shutil.copy2(filename + '.new', filename)
                sb_utils.SELinux.restoreSecurityContext(filename)
                os.unlink(filename + '.new')
            except (OSError, IOError), err:
                msg = "Unable to replace %s with new version (%s)." % \
                     (filename, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = "'%s' set to '%s' in %s" % (fieldName, self.__umaskStr, filename)
            
        return action_record, messages

    ##########################################################################
    def scan(self, optionDict=None):

        allMessages = []
        action_record = ""

        self.validate_input(optionDict)
        for fileName, fieldName, fieldRegex, fieldMissing in self.__filesToCheck:
            if os.path.isfile(fileName): 
                change_record, messages = self._change_one_file('scan', fileName, fieldName, fieldRegex, fieldMissing)
                action_record += change_record 
                allMessages.extend(messages)

        self.logger.notice(self.module_name, 'Scan Performed: ')
        if not action_record:
            return True, '', {'messages':allMessages}
        else:
            return False, "One or more files has an unacceptable umask",{'messages':allMessages}

    ##########################################################################
    def apply(self, optionDict=None):

        action_record = ""
        allMessages = []

        self.validate_input(optionDict)
        for fileName, fieldName, fieldRegex, fieldMissing in self.__filesToCheck:
            if os.path.isfile(fileName): 
                change_record, messages = self._change_one_file('apply', fileName, fieldName, fieldRegex, fieldMissing)
                action_record += change_record 
                allMessages.extend(messages)

        if not action_record:
            return False, '', {'messages':allMessages}

        self.logger.notice(self.module_name, 'Apply Performed: ' )
        return True, "%s\n" % action_record, {'messages':allMessages}

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            self.logger.debug(self.module_name, 'Undo: No change record provided')
            return False, 'No change record provided', {}

        try:
            tcs_utils.apply_patch(change_record.lstrip())
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Umask setting reverted in shell resource files.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, msg, {}

if __name__ == "__main__":
    test = DefaultUmask()
    optionDict = {'defaultUmask':'077'}
    print test.scan(optionDict)

