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

class MySQLHist:

    def __init__(self):
        """
        MySQLHist Security Module handles removing the MYSQL
        history file.
        """
        self.module_name = "MySQLHist"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__targets = { "/etc/profile.d/sb-mysqlhist.sh" :
                            [ """MYSQL_HISTFILE=""\n""" ,'export MYSQL_HISTFILE\n' ] ,
                        "/etc/profile.d/sb-mysqlhist.csh" :
                            [ """setenv MYSQL_HISTFILE ""\n""" ]
                         }
                            
    ##########################################################################
    def _check_shell_script(self, action, fileName, lines):

        fileLines = []
        messages = []
        changes = []

        # generate exclusion list *early* to avoid cluttering log
        sb_utils.file.exclusion.exlist()
        
        try:
            fileLines = open(fileName, 'r').readlines()
        except IOError, err:
            msg = "Unable to read %s: %s" % (fileName, err)
            self.logger.info(self.module_name, msg)

        for thisLine in fileLines:
            if thisLine == lines[0]:
                msg = "Found '%s' in '%s'" % (lines[0].strip(), fileName)
                lines.pop(0)
                if not lines:
                    break
        if lines:
            changes = fileName
            if action == 'scan':
                for line in lines:
                    msg = "Missing '%s' from '%s':" % (line.strip(), fileName)
                    self.logger.info(self.module_name, "Scan Failed: "+ msg)
            elif action == 'apply':
                try: 
                    open(fileName,'w').writelines(fileLines+ lines)
                    sb_utils.SELinux.restoreSecurityContext(fileName)
                    for line in lines:
                        msg = "Writing '%s' to '%s':" % (line.strip(), fileName)
                        self.logger.info(self.module_name, msg)
                except IOError, err:
                    msg = "Unable to write %s: %s" % (fileName, err)
                    self.logger.info(self.module_name, msg)
                            
        # Set permissions - *IF WE CREATE TEH
        requiredChanges = {'owner':'root',
                           'group':'root',
                           'dacs': 0644}

        # prepare to process metadata (DACs/owner/ACLs)
        # we're doing this out of the goodness of our hearts, to do the 'right thing'.  Don't record for undo....
        if action == "scan":
            options = {'checkOnly':True}
        elif action == "apply":
            options = {'checkOnly':False}
  
        if os.path.exists(fileName) and changes:
            ignore =  sb_utils.file.fileperms.search_and_change_file_attributes(fileName, requiredChanges, options)
            
        return changes, messages

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
            if newText == text:
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

        for profile, requiredMultiLineString in masterProfileList.items():
            madeChange, message = self._update_master_profile(action, profile, requiredMultiLineString)
            allMessages.extend(message)
            if madeChange:
                anyChanges = True
                   
        return anyChanges,allMessages
        
    ##########################################################################
    def scan(self, option=None):

        allMessages = []
        allChanges = []
        retval = True
        for thisFile, theseLines in self.__targets.items():
            changes, messages = self._check_shell_script('scan', thisFile, theseLines)
#            print changes, messages
            allMessages.extend(messages)
            if changes:
                allChanges.append(changes)
                retval = False
        
#        if sb_utils.os.info.is_solaris() == True:
#        if not option:
#            anyChanges, messages = self._update_master_profiles('scan')
#            if anyChanges:
#                retval = False
#            allMessages.extend(messages)

        msg = ""
        if retval:
            msg = "One or more files did not exist, have correct contents, or correct permissions"
        
        return retval, msg, {'messages':allMessages}
        
    ##########################################################################
    def apply(self, option=None):

        allMessages = []
        allChanges = []
        retval = False
        for thisFile, theseLines in self.__targets.items():
            changes, messages = self._check_shell_script('apply', thisFile, theseLines)
            allMessages.extend(messages)
            if changes:
                retval = True
                allChanges.append(changes)
#        print allChanges
#        if sb_utils.os.info.is_solaris() == True:
#        if not option:
#            anyChanges, messages = self._update_master_profiles('apply')
#            if anyChanges:
#                retval = True
#            allMessages.extend(messages)
        msg = ""
        if retval:
            changes = "\n".join(allChanges)
        
        return retval, str(changes), {'messages':allMessages}
            



    ##########################################################################
    def undo(self, change_record=None):
        """
        Remove the scripts that were created in /etc/profile.d/
        Note that since SB did the creation, we're assuming that *NOONE* else would modify.  So our undo is to delete.
        """

        allMessages = []
        # if 'oldstyle' change record found (recorded as 'MYSQLHIST environment variable set' delete both files
        if change_record == None or change_record == 'MYSQLHIST environment variable set':
            change_record = "\n".join(self.__targets.keys())
        
        for shfile in change_record.splitlines():
            try:
                if os.path.exists(shfile):
                    os.unlink(shfile)
                    self.logger.notice(self.module_name,'Undo : removed %s' % shfile)
                else:
                    self.logger.warn(self.module_name,'Undo : file %s does not exist to remove' % shfile)
            except IOError:
                msg = 'Unable to remove %s' % shfile
                self.logger.error(self.module_name, 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
#        if sb_utils.os.info.is_solaris() == True:
#        if change_record == change_record:
#            anyChanges, messages = self._update_master_profiles('undo')
#            allMessages.extend(messages)

        msg = 'MYSQLHIST scripts removed from /etc/profile.d/'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, {}, {'messages':allMessages}

