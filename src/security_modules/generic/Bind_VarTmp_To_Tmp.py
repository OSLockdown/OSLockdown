#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Bind-mount /var/tmp to /tmp using restrictive options 
# Note - explicit match to options required, not 'equivelence checking done'
#
#
#############################################################################

import sys
import re
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.acctmgt.acctfiles

class Bind_VarTmp_To_Tmp:

    def __init__(self):
        self.module_name = "Bind_VarTmp_To_Tmp"
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()
    
        self.__required_fields = ["/tmp", "/var/tmp", "none", "rw,noexec,nosuid,nodev,bind", "0", "0" ]
        self.__field_names = ["fs_spec", "fs_file", "fs_vfstype", "fs_mntops", "fs_freq", "fs_passno"]
        

    def check_fields(self, actual_fields) :            
        """
        Check the fields 2 through 5 for values (remember, field index starts at 0), and return an array of any differences
        """
    
        msgs = []
        for fn in range(2,6):
            if actual_fields[fn] != self.__required_fields[fn]:
                msg = "Field %d(%s) is '%s' when it should be '%s'" % (fn, self.__field_names[fn], 
                                                                   actual_fields[fn], self.__required_fields[fn])
                msgs.append(msg)
        return msgs
    
    ##########################################################################
    def scan(self, option=None):

        messages = {'messages' : [] }
        retval = False
        
        msg = "Checking to see if /var/tmp is mounted as /tmp with restrictive options" 
        self.logger.info(self.module_name, msg)
    
        required_fields = ["/tmp", "/var/tmp", "none", "rw,noexec,nosuid,nodev,bind", "0", "0" ]
        field_names = ["fs_spec", "fs_file", "fs_vfstype", "fs_mntops", "fs_freq", "fs_passno"]

        lines = open('/etc/fstab').readlines()
        
        have_line = None
        have_tmp = None
        have_vartmp = None

        #quick preprocess...
        line_fields = []
        
        for ln in range(len(lines)):
            fields = lines[ln].strip().split()
            if fields and not fields[0].startswith('#'):
                line_fields.append(fields)
                if fields[0] == "/tmp" and fields[1] == "/var/tmp":
                    have_line = ln
                if fields[1] == "/tmp" :
                    have_tmp = ln
                elif fields[1] == "/var/tmp" :
                    have_vartmp = ln
            else:
                line_fields.append([""])
        
#        print have_line, have_tmp, have_vartmp

        if have_line:   # found line mounting /tmp on /var/tmp, so check options:
            msgs = self.check_fields(line_fields[have_line])
            if msgs:
                for msg in msgs:
                    self.logger.warning(self.module_name, msg)
                    messages['messages'].append(msg)
                msg = "Found required mount, but options are incorrect"
            else:
                msg = "Found required line in /etc/fstab"
                self.logger.info(self.module_name, msg)
                retval = True
        elif have_tmp or have_vartmp:
            m1 = "Did not find required mount line in '/etc/fstab'"
            messages['messages'].append("Warning: %s" % m1)
            if have_tmp and have_vartmp:
                m1 = "'/var/tmp' and '/tmp' are explicitly different mountpoints, checking mount options"
                self.logger.info(self.module_name, m1)
                messages['messages'].append("Warning: %s " % m1)
            todo = {}
            wrong = []
            
            if have_tmp:
                todo['/tmp'] = line_fields[have_tmp]
            else:
                todo['/tmp'] = None
            
            if have_vartmp:
                todo['/var/tmp'] = line_fields[have_vartmp]
            else:
                todo['/var/tmp'] = None
                
            for key in todo.keys():
                if todo[key] == None:
                    m1 = "'%s' does not have an explicit mountpoint, so it is mounted on '/'" % key
                    self.logger.warning(self.module_name, m1)
                    messages['messages'].append("Warning: %s " % m1)
#                    wrong.append(key)
                else:
                    m1 = "'%s' has an explicit mountpoint, checking options" % key
                    self.logger.warning(self.module_name, m1)
                    msgs = self.check_fields(todo[key])
                    if msgs:
                        wrong.append(key)
                        for m1 in msgs:
                            self.logger.warning(self.module_name, "'%s' : %s" % (key, m1))
                            messages['messages'].append("Warning: '%s' : %s" % (key, m1))
                    else:
                            m1 = "Mount options appear correct"
                            self.logger.info(self.module_name, "'%s' : %s" % (key, m1))
                        
            if wrong:
                msg = "Incorrect mount flags for '%s'" % ("', '".join(wrong))
                self.logger.info(self.module_name, msg)
            
        else:
            msg = "No mountpoints found for '/tmp' or '/var/tmp'"
            self.logger.warning(self.module_name, msg);
            messages['messages'].append("Warning: %s" % msg);
            retval = False
            
        return retval, msg, messages

    ##########################################################################
    def apply(self, option=None):

        messages = {}
        action_record = 'none'
        try:
            (result, reason, messages) = self.scan()
            if result == False:
                msg = "Manual Action: You must make any change to /etc/fstab manually." 
                self.logger.info(self.module_name, msg)
                raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        except tcs_utils.ScanError, err:
            self.logger.error(self.module_name, err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))


        return False, action_record, messages

    ##########################################################################
    def undo(self, change_record=None):
        return False, "Nothing to undo", {}




#if __name__ == '__main__':
#    Test = Bind_VarTmp_To_Tmp()
#    Test.setFile('/tmp/fstab_tmp')

#    SCAN_RES = None
#    APPLY_RES = None
#    UNDO_RES = None
    
#    if '-s' in sys.argv[1:] :
#        SCAN_RES = Test.scan()
#        print "SCAN->",SCAN_RES,"\n\n"
#    if '-a' in sys.argv[1:] :
#        APPLY_RES = Test.apply()
#        print "APPLY->",APPLY_RES,"\n\n"
#    if '-u' in sys.argv[1:] :
#        if not APPLY_RES :
#            print "Must do -a with -u"
#        elif APPLY_RES[0] != True:
#           print "Apply wasn't required, nothing to undo"
#        else:
#            UNDO_RES = Test.undo(APPLY_RES[1])
#            print "UNDO->",UNDO_RES,"\n\n"
