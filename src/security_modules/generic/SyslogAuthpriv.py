#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#
#

import sys
import os

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.info
import sb_utils.os.syslog
import tcs_utils

class SyslogAuthpriv:

    def __init__(self):
        self.module_name = "SyslogAuthpriv"

        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.change_set = self.generate_changes(is_undo=False)
        


    ##########################################################################
    # Generate are search criteria, but only for config files that we see.
    # Note that for 'undo' we generate a change set for a change that we *would* have made,
    # if we needed to make it.  If the change actually isn't there (in the conf file) then
    # no harm/no foul.  In the generic 'undo' case (generated when 'is_undo' is passed),
    # we *explicitly* indicate that we're looking for a regex, as we're not exactly sure 
    # what may have been installed.  This 'undo' case is because some older versions of this
    # code did slightly different things depending on the OS.  This current code is designed
    # to work on all OS releases, so we loosen up the search case a bit to handle how the older
    # code may have made the changes. 
    
    def generate_changes(self, is_undo=False):

        change_set = {}
        
        logfile = '/etc/syslog-ng/syslog-ng.conf'
        if os.path.exists(logfile):
            ctm = []
            # do we want to *require* an exact match on the log location in the search string?
            search = [ '^filter\s+f_auth\s+\{\s+facility\(auth,authpriv\);\s+\}' ]
            replace = 'filter f_auth { facility(auth,authpriv); };'
            if is_undo == True:
                ctm.append( {'search'       : search, 'regex': True  })
            else:
                ctm.append( {'search'       : search , 'replace_with' : replace })
                
            search = [ '^destination\s+d_auth\s+\{\s+file\(\"/var/log/secure\"\);\s+\}' ]
            replace =  'destination d_auth { file("/var/log/secure"); };'
            if is_undo == True:
                ctm.append( {'search'       : search, 'regex': True  })
            else:
                ctm.append( {'search'       : search , 'replace_with' : replace })
        

            search = [ '^log\s+\{\s+source\(src\);\s+filter\(f_auth\); destination\(d_auth\);\s+\}' ]
            replace = 'log { source(src); filter(f_auth); destination(d_auth); };'

            if is_undo == True:
                ctm.append( {'search'       : search, 'regex': True  })
            else:
                ctm.append( {'search'       : search , 'replace_with' : replace })
        
            change_set[logfile] = ctm                         

        ctm = []
        
        for cfgfile in ['/etc/rsyslog.conf' , '/etc/syslog.conf']:
            if not os.path.exists(cfgfile):
                continue
            logfile = "/var/log/secure"              

            if sb_utils.os.info.is_solaris() == True:
                search = [ '^auth.info\s' ]
                replace = 'auth.info\t\t%s' % logfile 
            else:
                search = [ '^authpriv.\*\s' ]
                replace = 'authpriv.*\t\t%s' % logfile 
            
            if is_undo == True:
                ctm.append( {'search'       : search[0], 'regex': True })
            else:
                ctm.append( {'search'       : search , 'replace_with' : replace })
            change_set[cfgfile] = ctm
        return change_set

    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    def process_change_set(self, change_set, action):
        messages = []
        changes = {}
        for file_to_change in change_set:
            changes_to_make = change_set[file_to_change]
            
            m, c = sb_utils.os.syslog.process_arbitary_file(file_to_change, changes_to_make, action)

            messages.extend(m)
            if c != []:
                changes[file_to_change] = c
        
        return messages, changes
        
    ##########################################################################
    def scan(self, option=None):
    
        messages = []

        all_messages, changes = self.process_change_set(self.change_set, "scan")
        
        for level, text in all_messages:
            if level in ['ok']:
                self.logger.notice(self.module_name, text)
                messages.append(text)
            elif level in [ 'problem']:
                self.logger.info(self.module_name, text)
                messages.append(text)
            elif level in ['error' ]:
                self.logger.error(self.module_name, text)
                messages.append(text)
        if changes != {}:
            retval = False
        else: 
            retval = True
    
        return retval, "", {'messages':messages}
    
    
    ##########################################################################
    def apply(self, option=None):
        messages = []

        all_messages, changes = self.process_change_set(self.change_set, "apply")
        
        for level, text in all_messages:
            if level in ['ok']:
                self.logger.notice(self.module_name, text)
                messages.append(text)
            elif level in [ 'problem', 'fix']:
                self.logger.info(self.module_name, text)
                messages.append(text)
            elif level in ['error' ]:
                self.logger.error(self.module_name, text)
                messages.append(text)

        if changes == {}:
            retval = False
            changes = ""
        else: 
            retval = True
    
        return retval, str(changes), {'messages':messages}

        
    ##########################################################################
    def undo(self, option=None):
    
        messages = []
        # old style change record - we know what *might* have been applied, so construct an undo record
        # old generic used a patch set, old redhat6 used simply 'added', suse used 'applied', so 
        
        
        if option in ['added', 'applied'] or ( type(option)==type("") and option.startswith ("--- /etc")):
            # generate an default 'undo' set for any possible change we could have made
            change_set = self.generate_changes(is_undo=True)
        else:
            change_set = tcs_utils.string_to_dictionary(option)
        
        all_messages, changes = self.process_change_set(change_set, "undo")
        
        for level, text in all_messages:
            if level in ['ok']:
                self.logger.notice(self.module_name, text)
                messages.append(text)
            elif level in [ 'problem', 'fix']:
                self.logger.info(self.module_name, text)
                messages.append(text)
            elif level in ['error' ]:
                self.logger.error(self.module_name, text)
                messages.append(text)

        if changes == {}:
            retval = False
            changes = ""
        else: 
            retval = True
    
        return retval, str(changes), {'messages':messages}
