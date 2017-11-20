#!/usr/bin/env python
#
# Copyright (c) 2013 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import sha

import  xml.sax.saxutils

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms

class NoHashesInPasswdGroup:
    ##########################################################################
    def __init__(self):
        self.module_name = "NoHashesInPasswdGroup"
        
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.hashIndicators = ["x"]
        if sb_utils.os.info.is_solaris() == False:
            self.hashIndicators.append("*")  # not valid for Solaris officially, so only apply for linux

    ##########################################################################
    def scan(self, optionDict={}):
        messages = []
        
        results = True
        lineNumber = 0
        for fileName in sb_utils.file.fileperms.splitStringIntoFiles(optionDict['fileList']):
            extraCheck = []
            
            # have some 'extra' allowed fields for /etc/gshadow - ! = locked group, ""(emptyfield) = only group members have access
            if fileName == "/etc/gshadow" :
                extraCheck = ["!",""]
            
            lineNumber = 0
            try:
                fileText = open(fileName)
            except IOError, err:
                if not os.path.exists(fileName):
                    msg = "No such file '%s'" % fileName
                    self.logger.notice(self.module_name, msg)
                else:
                    msg = "Unable to read '%s' : %s " % (fileName, err)
                    self.logger.warn(self.module_name, msg)


            for line in fileText:
                
                try:
                    lineNumber = lineNumber + 1
                    line = line.strip()
                    if line.startswith('#'):
                        continue
                    fields = line.split(':')
            
                    firstChar = ""
                    if fields[1] :
                        firstChar = fields[1][0]
                    if firstChar in self.hashIndicators + extraCheck:
                        continue


                    msg = "%s : entry for '%s' contains an unhashed password" % (fileName, fields[0])
                    messages.append(msg)
                    self.logger.warn(self.module_name, msg)
                    result = False     
                except IOError, err:
                    if not os.path.exists(fileName):
                        msg = "No such file '%s'" % fileName
                        self.logger.notice(self.module_name, msg)
                    else:
                        msg = "Unable to read '%s' : %s " % (fileName, err)
                        self.logger.warn(self.module_name, msg)
                    continue
                except IndexError, err:
                    msg = "Unable to process line %d of '%s'" % (lineNumber, fileName)
                    self.logger.warn(self.module_name, msg)
                    continue

        if results == False:
            msg = "One or more users/groups has unhashed passwords - Manual action required to remediate"
        msg = ''
        return results, msg, {'messages':messages}
    ##########################################################################
    def apply(self, optionDict={}):

        results, msg, messages = self.scan(optionDict)
        if results == False:
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))
        
        return False, '',{}
        
    ##########################################################################
    def undo(self, change_record=None):

        return False, "Module is manual action, will not make changes", {}

if __name__ == "__main__":
    test = NoHashesInPasswdGroup()
    myLog = TCSLogger.TCSLogger.getInstance()
    myLog.force_log_level (7)
    myLog._fileobj = sys.stdout

    optionDict = {}
    optionDict['fileList'] = "/etc/passwd /etc/group /etc/gshadow"
    print test.scan(optionDict)
