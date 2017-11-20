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

class ShellSessionTimeouts:

    def __init__(self):
        """
        ShellSessionTimeouts Security Module handles the guideline for 
		default timeout values in your shell environment and access 
		permissions on all associated files.
        """
        self.module_name = "ShellSessionTimeouts"
        self.__oldfiles = ["/etc/profile.d/sb-timeout.sh" , "/etc/profile.d/sb-timeout.csh"]
        self.__target_file1 = "/etc/profile.d/tmout.sh"
        self.__target_file2 = "/etc/profile.d/autologout.csh"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__sh_script  = ""
        self.__csh_script = ""

        # This is for bash, ksh, sh, stuff
        self.__sh_script  = ""

        # This is for CSH stuff
        self.__csh_script  = ""

        msg = ""
        if not os.path.exists('/etc/profile.d'):
            msg = "/etc/profile.d directory does not exist!  Consider adding 'Exec shell startups in /etc/profile.d' to Profile."
        elif not os.path.isdir('/etc/profile.d'):
            msg = "/etc/profile.d is not a directory!  This should be a directory.  Consider adding 'Exec shell startups in /etc/profile.d' to Profile afterward."
        if msg:
            raise tcs_utils.ManualActionReqd("%s %s" % (self.module_name, msg))
            
    def setTimeoutLines(self, seconds):
        # This is for bash, ksh, sh, stuff
        self.__sh_script  = "# Created by OS Lockdown\n"
        self.__sh_script += 'TMOUT=%d\n' % seconds
        self.__sh_script += 'readonly TMOUT\n' 
        self.__sh_script += 'export TMOUT\n'

        # This is for TCSH stuff (all supported linuxes have csh symlinked to tcsh)
        # and this variable expects the timeout in minutes, so divide by 60 
        self.__tcsh_script  = "# Created by OS Lockdown\n"
        self.__tcsh_script += 'set -r autologout=%d\n' % (seconds/60)
        

    ##########################################################################
    # Look for the older way this module use to write the files, and delete them if
    # so ordered.
    
    def handleOldFiles(self, deleteFlag):
        
        for oldFile in self.__oldfiles:
            if os.path.exists(oldFile):
                if deleteFlag:
                    os.unlink(oldFile)
                    msg = "Removing old OS Lockdown remediation file '%s'" % oldFile
                else:
                    msg = "Found old OS Lockdown remdiation file '%s'" % oldFile
                self.logger.notice(self.module_name, msg)


    def processFile(self, fileName, requiredText):
        if not os.path.isfile(fileName):
            msg = 'Missing %s' % fileName
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg

        try:
            fileContents = open(fileName, 'r').read()
        except IOError:
            msg = 'Unable to read %s' % self.__target_file1 
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
        
        if optionDict == None or not 'shellTimeout' in optionDict:
            msg = "Missing option value"
            self.logger.notice(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['shellTimeout']
        try:
            value = int(option)
        except ValueError, err:
            msg = "Bad option value: %s" % err
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        self.handleOldFiles(False)

        # Build Strings to represent what the files MUST
        # have in them
        self.setTimeoutLines(value)

        messages = {'messages' : []}
        retval = True

        ret1, message1 = self.processFile(self.__target_file1, self.__sh_script)
        if ret1 != True:
            retval = False
            messages['messages'].append(message1)        

        ret2, message2 = self.processFile(self.__target_file2, self.__tcsh_script)
        if ret2 != True:
            retval = False
            messages['messages'].append(message1)        
        
        if retval == True:
            msg = "Session Timeout Scripts correct"
        else:
            msg = "Session Timeout Scripts incorrect"

        self.handleOldFiles(False)
        
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
        Create the scripts in /etc/profile.d/ and assign the correct 
        permissions and ownership.
        """

        if optionDict == None or not 'shellTimeout' in optionDict:
            msg = "Missing option value"
            self.logger.error(self.module_name, 'Apply Failed: ' + msg)
            return 0, ''
        option = optionDict['shellTimeout']

        try:
            value = int(option)
        except ValueError:
            msg = 'Bad option value'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        files_created = [] 
        # Build what the file is supposed to have in MEMORY
        self.setTimeoutLines(value)

        ###################################
        # Bash, Bourne, and Korn stuff
        ###################################
        messages = {'messages' : []}
        
        ret1, message1 = self.processFile(self.__target_file1, self.__sh_script)
        if ret1 != True:
            messages['messages'].append(message1)        
            if self._write_shell_script(self.__target_file1, self.__sh_script) == True:
                files_created.append(self.__target_file1)
                messages['messages'].append("Wrote '%s'" % self.__target_file1)
        
        ret2, message2 = self.processFile(self.__target_file2, self.__tcsh_script)
        if ret2 != True:
            messages['messages'].append(message2)        
            if self._write_shell_script(self.__target_file2, self.__tcsh_script) == True:
                files_created.append(self.__target_file2)
                messages['messages'].append("Wrote '%s'" % self.__target_file2)
            

        self.logger.notice(self.module_name, 'Apply Performed')
        
        self.handleOldFiles(True)
        if files_created == [] :
            return False, 'No changes required', {}
        else:
            return True, '\n'.join(files_created), messages


    ##########################################################################
    def undo(self, change_record=None):
        """
        Remove the scripts that were created in /etc/profile.d/
        """
        
        # if 'oldstyle' change record found (record ends with ' created' delete both files
        if change_record == None or change_record.endswith == ' created':
            change_record = "%s\n%s" % ( self.__target_file1, self.__target_file2)
        
        for shfile in change_record.splitlines():
            try:
                os.unlink(shfile)
                self.logger.notice(self.module_name,'Undo : removed %s' % shfile)
            except IOError:
                msg = 'Unable to remove %s' % shfile
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        self.handleOldFiles(True)

        msg = 'Session timeout scripts removed from /etc/profile.d/'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

    ##########################################################################
    def validate_input(self, option=None):
        """
        Validate input 
        """
        if option == None:
            return 0


