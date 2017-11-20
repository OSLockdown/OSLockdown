#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable Firefox browser if running vulnerable version
#
#
##############################################################################

import sys
import os
import re

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.file.fileperms


class DisableFirefox:

    def __init__(self):

        self.module_name = 'DisableFirefox'
        self.logger = TCSLogger.TCSLogger.getInstance()

        # This is the minimum version. >= is okay
        # eventually this *should* be a editable option and processed at runtime.
        self.__goodversion = "3.0.0"


        # The location/package differs between OS's, so try and figure it out
        firefoxCandidates = []
        
        if sb_utils.os.info.is_solaris() == True:
            firefoxCandidates.append( ('/opt/sfw/lib/firefox3/firefox', 'SUNfirefox') )
            firefoxCandidates.append( ('/usr/lib/firefox/firefox' , 'SUNWfirefox') )
            
        elif sb_utils.os.info.is_LikeSUSE() == True:
            firefoxCandidates.append( ("/usr/bin/firefox", "MozillaFirefox") )
        else:
            firefoxCandidates.append( ("/usr/bin/firefox", "firefox") )

        self.__firefox_path = None
        self.__firefox_package = None
        self.__firefox_version = None
        
        for candidate in firefoxCandidates:
            if os.path.exists(candidate[0]) and sb_utils.os.software.is_installed(candidate[1]):
                self.__firefox_path = candidate[0]
                self.__firefox_package = candidate[1]
                self.__firefox_version = sb_utils.os.software.version(pkgname=self.__firefox_package)[0]
                break
    
    # return an int we only contain numbers, a string otherwise
    def fixField(self, field):
	if field.isdigit():
            return int(field)
        else:
	    return field

    # basically split the passed version string, trying to keep sequences of digits or letters together.  
    def splitVersion(self, versionString):
        z=re.compile("(\d+|[a-zA-Z_]+|[-.+=]+)")
        # we could do this nicely as as one-line ternary expression, but old python won't handle it.  So do it
        # the ploddy way....
        # nice way = 
        #        fields = [ int(z) if z.isdigit() else z for z in z.findall(versionString)]
        # ploddy way
        fields = [ self.fixField(z) for z in z.findall(versionString)]
        return fields

    # compare found version (if any) with required minimum.  Return pass/fail, a message, and the permissions of the executable
    def versionOK(self):
        isOK = True
        msg = ""
        perms = None
        
        if not self.__firefox_path:
            msg = "Firefox does not appear to be installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        try:
            statinfo = os.stat(self.__firefox_path)
        except OSError, err:
            msg = "Unable to stat file %s" % (self.__firefox_path, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
        perms = statinfo.st_mode & 07777
        
        acceptableVersion = self.splitVersion(self.__goodversion)
        installedVersion = self.splitVersion(self.__firefox_version)
        
        if acceptableVersion < installedVersion:
            isOk = True
            msg = "Installed firefox version is %s, which is acceptable" % self.__firefox_version
        else:
            if perms != 0:
                isOk = False
                msg = "Found firefox version %s, which is unacceptable, and it is not disabled" %  self.__firefox_version
            else:
                isOk = True
                msg = "Found firefox version %s, which is unacceptable, but it is disabled" % self.__firefox_version
        return isOk, msg, perms
        
        
        


    ##########################################################################
    def scan(self, option=None):

        messages = {'messages': []}

        isOk, msg, perms = self.versionOK()
        if isOk:
            self.logger.info(self.module_name, 'Scan: ' + msg)
        else:
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            messages['messages'].append(msg)
        return isOk, msg, messages

    ##########################################################################
    def apply(self, option=None):

        messages = {'messages': []}
        isOk, msg, perms = self.versionOK()
        if isOk == True:
            self.logger.info(self.module_name, 'Scan: ' + msg)
            return False, '', msg
        
        self.logger.notice(self.module_name, 'Scan Failed: ' + msg)

        changes_to_make = {'dacs':0}
        change_record = sb_utils.file.fileperms.change_file_attributes( self.__firefox_path, changes_to_make)
        
        if change_record == {}:
            msg = "Firefox (%s) binary *NOT* disabled"
            self.logger.error(self.module_name, 'Apply Performed: ' + msg)
            messages['messages'].append(msg)
            return False, "", messages
        else:
            msg = "Firefox (%s) binary disabled by setting permissions " \
              "to zeros. You need to upgrade or remove package." % self.__firefox_path
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

            return True, str(change_record), messages


    ##########################################################################
    def undo(self, change_record=None):

        # we should never get an empty change record, but if we did...
        if change_record == "" :
            change_record = {}
            change_record[self.__firefox_path] = {'dacs':0755}
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)
        return True, '', {}

if __name__ == "__main__":
	test = DisableFirefox()
        test.logger.forceToStdout()
	print test.scan()
