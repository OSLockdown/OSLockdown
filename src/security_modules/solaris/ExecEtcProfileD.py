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
import re
sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms
import sb_utils.file.exclusion

class ExecEtcProfileD:

    def __init__(self):
        """
        MySQLHist Security Module handles removing the MYSQL
        history file.
        """
        self.module_name = "ExecEtcProfileD"
        self.logger = TCSLogger.TCSLogger.getInstance()
                            

    ##########################################################################
    def _update_master_profile(self, action, fileName, requiredMultiLineString):

        message = ""
        newText = None
        madeChange = False
        
        # if we can't read the file for any reason, punt
        try: 
            text = open(fileName, 'r').read()     
        except IOError, err:
            message = "Unable to read '%s': %s" % (fileName, str(err))
            self.logger.error(self.module_name, message)
            return madeChange, message
    
        
        if action == 'undo':
            #try to remove it...
            newText = re.compile(re.escape(requiredMultiLineString),re.MULTILINE|re.DOTALL).sub("", text)
            if newText != text:
                madeChange = True
                message = "Removing required text from '%s'" % fileName
                self.logger.info(self.module_name, message)
            else:
                message = "Did not find required text in '%s' to remove" % fileName
                self.logger.info(self.module_name, message)
        else:
            # is the *first* non-whitespace line already in our file?  If so assume the entirety is...
            searchLine = requiredMultiLineString.strip().splitlines()[0].strip()
            regex = re.compile(r"^\s*%s" % re.escape(searchLine), re.MULTILINE|re.DOTALL)
            match = regex.search(text)
        
            if match:
                if action in ['scan', 'apply']:
                    message = "Looks like required text may already be in '%s'" % fileName
                    self.logger.info(self.module_name, message)
            else:
                madeChange = True
                if action in ['scan']:
                    message = "Did not find required text in '%s'" % fileName
                    self.logger.info(self.module_name, message)
                elif action in ['apply']:
                    newText = text+requiredMultiLineString
                    message = "Adding required text to '%s'" % fileName
                    self.logger.info(self.module_name, message)

        if newText != text and newText != None and action != 'scan':
            try:    
                open(fileName, 'w').write(newText)     # since we *should* not be altering DACs/MACs, don't bother changing them.
                madeChange = True
            except IOError, err:
                message = "Unable to write '%s': %s" % (fileName, str(err))
                self.logger.error(self.module_name, message)
        
        return madeChange, message
   

    ##########################################################################
    def _update_master_profiles(self,action):


        madeChange = False
        # Check /etc/profile for code block to support profile.d
        anyChanges = False
        allMessages = []
        masterProfileList = {}
        sh_codeblock = """\n\nfor i in /etc/profile.d/*.sh ; do\n  if [ -r "$i" ]; then\n    . $i\n  fi\ndone\n"""
        csh_codeblock = """\n\nif ( -d /etc/profile.d ) then\n  set nonomatch\n  foreach i ( /etc/profile.d/*.csh )\n    if ( -r $i ) then\n        source $i\n    endif\n  end\n  unset i nonomatch\nendif"""

        masterProfileList['/etc/profile']  = sh_codeblock
        masterProfileList['/etc/.login']  = csh_codeblock

        if action != 'undo':
            if not os.path.isdir('/etc/profile.d'):
                if action == 'scan':
                    msg = "/etc/profile.d directory does not exist or is not a directory"
                    self.logger.error(self.module_name, msg)
                    allMessages.append(msg)
                else:
                    try:
                        os.mkdir('/etc/profile.d',0755)
                        msg = "Creating /etc/profile.d directory"
                        self.logger.notice(self.module_name, msg)
                    except Exception, err:
                        msg = "Unable to create /etc/profile.d directory : %s" % str(err)
                        raise tcs_utils.ActionError("%s %s" % (self.module_name, msg))
            else:
                msg = "/etc/profile.d directory exists"
                self.logger.notice(self.module_name, msg)
                
        for profile, requiredMultiLineString in masterProfileList.items():
            madeChange, message = self._update_master_profile(action, profile, requiredMultiLineString)
            allMessages.extend(message)
            if madeChange:
                anyChanges = True
        
        if action == "undo":
            #ok, try and remove the directory - silently catch a failure...
            try:
                os.rmdir('/etc/profile.d')
                msg = "Removed /etc/profile.d directory"
                self.logger.notice(self.module_name, msg)
            except Exception, err:
                pass
     
        return anyChanges,allMessages
        
    ##########################################################################
    def scan(self, option=None):

        allMessages = []
        allChanges = []
        retval = True

        anyChanges, messages = self._update_master_profiles('scan')
        if anyChanges:
            retval = False
        allMessages.extend(messages)

        if retval == False:
            msg = "Missing line(s) in shell startup files to execute scripts in /etc/profile.d"
        else:
            msg = "Required line(s) present in shell startup files to execute scripts in /etc/profile.d"
        return retval, msg, {'messages':allMessages}
        
    ##########################################################################
    def apply(self, option=None):

        allMessages = []
        allChanges = []
        retval = False
        changes = None
        
        anyChanges, messages = self._update_master_profiles('apply')
        if anyChanges:
            retval = True
        allMessages.extend(messages)

        msg = ""
        if retval:
            changes = "True"
        return retval, str(changes), {'messages':allMessages}
            



    ##########################################################################
    def undo(self, change_record=None):
        """
        Remove the scripts that were created in /etc/profile.d/
        Note that since SB did the creation, we're assuming that *NOONE* else would modify.  So our undo is to delete.
        """

        allMessages = []

        anyChanges, messages = self._update_master_profiles('undo')
        allMessages.extend(messages)

        msg = "Removed line(s) from shell startup files to execute scripts in /etc/profile.d"
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, {}, {'messages':allMessages}

