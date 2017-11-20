#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.SELinux

class AccountLocks:
    """
    AccountLocks Security Module handles the guideline for locking
    user accounts after three unsuccessful login attempts.
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "AccountLocks"
        self.__target_files = ['/etc/pam.d/system-auth']
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__pam_entries = []
        self.__pam_service = ''
        self.__max_fails = 3
        
    def _init_fields(self, option=None ):
        # We need to do different stuff for RH4 platforms.  RH5 and Fedora seem use the same logic.  We make a few dictionaries here
        # so we can pass these through to the relevent routines.
        

        # we know '/etc/pam.d/system-auth' should *always* be there, but also look for potentially '/etc/pam.d/password-auth'
        # RH4/5 and F10 only used system-auth, but F11/12/13 and RH6 also reference /etc/pam.d/password-auth, so if we see it,
        # add it to the list of files to check for
        
        if os.path.exists('/etc/pam.d/password-auth'):
             self.__target_files.append('/etc/pam.d/password-auth')
             
        if type(option)==type("") and option.isdigit():
            option = int(option)
        elif type(option)!=type(3):
            option = 3 
            
        self.__max_fails = int(option)
        if self.is_rh4():
            pam_service = 'pam_tally.so'
            auth_entry = {'type' : 'auth', 'control' : 'required', 'service' : '/lib/security/$ISA/pam_tally.so', 
                          'fields' : [ 'onerr=fail', 'no_magic_root' ] }    
            account_entry = {'type' : 'account', 'control' : 'required', 'service' : '/lib/security/$ISA/pam_tally.so', 
                             'fields' : [ 'deny=\d', 'no_magic_root reset' ] }
        elif self.is_f12() or self.is_f13() or self.is_rh6():
            pam_service = 'pam_tally2.so'
            auth_entry = {'type' : 'auth', 'control' : 'required', 'service' : 'pam_tally2.so', 
                          'fields' : [ 'deny=\d', 'onerr=fail' ] }    
            account_entry = {'type' :'account' , 'control' : 'required', 'service' : 'pam_tally2.so',
                             'fields' : [] }
        else :   # RHEL5
            pam_service = 'pam_tally2.so'
            auth_entry = {'type' : 'auth', 'control' : 'required', 'service' : 'pam_tally2.so', 
                          'fields' : [ 'deny=\d' ] }    
            account_entry = {'type' :'account' , 'control' : 'required' , 'service' : 'pam_tally2.so' ,
                             'fields' : [] }

        # now that we've got the OS variable stuff resolved, finish with some pre-processing/initializing stuff...
        self.__pam_entries = [auth_entry, account_entry]
        self.__pam_service = pam_service
        for entry in self.__pam_entries:
            entry['desc'] = "%s %s" % (entry['type'], entry['control'])

            entry['sect_str'] = "^%s\s*%s" % (entry['type'], entry['control'])
            entry['sect_re' ] = re.compile (entry['sect_str'])

            entry['service_str'] = "^%s\s*%s\s*%s" % (entry['type'], entry['control'], entry['service'].replace('$','\$'))
            entry['service_re'] = re.compile (entry['service_str'])

            entry['defline_str'] = "%s\t%s\t%s\t%s\n" % (entry['type'], entry['control'], entry['service'], '\t'.join(entry['fields'] ))
            entry['defline'] = entry['defline_str'].replace('deny=\d', 'deny=%d' % option)

    ##########################################################################

    def is_rh4(self):
        """ Quickly see if we are a RH4 *based* box or anything else"""
        retval = False
        try:
            if sb_utils.os.info.is_LikeRedHat() and sb_utils.os.info.getOSMajorVersion() == '4':
                retval = True
        except Exception:
            pass
        return retval
    ##########################################################################

    def is_rh6(self):
        """ Quickly see if we are a RH4 *based* box or anything else"""
        retval = False
        try:
            if sb_utils.os.info.is_LikeRedHat() and sb_utils.os.info.getOSMajorVersion() == '6':
                retval = True
        except Exception:
            pass
        return retval
                
    ##########################################################################

    def is_f12(self):
        """ Quickly see if we are a RH4 *based* box or anything else"""
        retval = False
        try:
            if sb_utils.os.info.is_fedora() and sb_utils.os.info.getOSMajorVersion() == '12':
                retval = True
        except Exception:
            pass
        return retval

    def is_f13(self):
        """ Quickly see if we are a RH4 *based* box or anything else"""
        retval = False
        try:
            if sb_utils.os.info.is_fedora()  and sb_utils.os.info.getOSMajorVersion() == '13':
                retval = True
        except Exception:
            pass
        return retval


    def scan_for_pam_line(self, fileName, lines, pam_entry):
        """ Look through the text in lines, and do the following
            1) If the service for pam_entry isn't there, insert it as the first line for the appropriate 'control'
            2) If the service for pam_entry is there and mis-formed comment out the bad line and insert corrected line
            3) If the service is present and correct, make no changes
            In all cases return a dictionary with:
                 ['problems'] = a list of messages about problems detected
                 ['fixes']    = a list of messages about problems fixed
                 ['changes']  = a dictionary of line changes ( key is newline, value is oldline (or '' if line inserted
                 ['lines']    = the (potentially) modified list of lines
        """
        
        insert_line_at = 0
        problem_messages = []
        fixed_messages = []
        changes = {}
        found_service = False
        
#        self.logger.info(self.module_name, "sect_str    = %s" %    pam_entry['sect_str'])
#        self.logger.info(self.module_name, "service_str = %s" % pam_entry['service_str'])
#        self.logger.info(self.module_name, "defline_str = %s" % pam_entry['defline'])
#        for f in pam_entry['fields']:
#            self.logger.info(self.module_name, "fields      = %s" % f)

        for linenum in range(0, len(lines)):
            line = lines[linenum].rstrip()
#            self.logger.info(self.module_name, "Line %d - %s" % (linenum,line))
            if pam_entry['sect_re'].search(line) and insert_line_at==0:
                insert_line_at = linenum
            if pam_entry['service_re'].search(line):
                found_service = True
                fields_to_add = []
                new_deny = ''
                fields = ' '.join(line.split()[3:])  # ignore the first three fields now
                for req_field in pam_entry['fields']:
                    msg = ""
                    field_re = re.compile (req_field)
                    field_loc = field_re.search (fields)
                    if field_loc:
                        if req_field.startswith('deny=') == True:
                            denyfield = fields[field_loc.start(): field_loc.end()]
                            denycount = int(denyfield.split('=')[1])
                            if denycount > self.__max_fails:
                                new_deny = 'deny=%d' % self.__max_fails
                                msg = "%s: '%s' found on '%s' line, 'deny' limit is too permissive (%d with minimum acceptable limit of %d )" % \
                                                (fileName, self.__pam_service, pam_entry['desc'], denycount, self.__max_fails)
                                problem_messages.append("%s: Deny limit to permissive" % fileName)
                            else:
                                msg = "%s: '%s' found on '%s' line, 'deny' limit is acceptable (%d with minimum acceptable limit of %d)" % \
                                                (fileName, self.__pam_service, pam_entry['desc'], denycount, self.__max_fails)
                            self.logger.notice(self.module_name, msg)                                                                         
                    else:
                        if (req_field.startswith('deny=')):
                            fields_to_add.append('deny=%d' % self.__max_fails)
                        else:
                            fields_to_add.append(req_field)
                        
                        msg = "%s: '%s' found on '%s' line, missing required field '%s'" % \
                                       (fileName, self.__pam_service, pam_entry['desc'], req_field)
                        problem_messages.append("%s: Missing '%s' from '%s %s' line" %
                                            ( fileName, req_field, pam_entry['desc'], self.__pam_service)) 
                        self.logger.notice(self.module_name, msg )

                if fields_to_add or new_deny:
                    tmpline = lines[linenum].rstrip()
                    tmpline += ' '+' '.join(fields_to_add)+'\n'
                    fixed_line = re.sub('deny=\d+','deny=%d' % self.__max_fails, tmpline)
                    changes[fixed_line] = lines[linenum]
                    lines[linenum] = fixed_line
                    fixed_messages.append("%s: Corrected '%s %s' line to include required fields." %
                            (fileName, pam_entry['desc'], self.__pam_service))
        # if we never found a line to modify, then we'll have to insert it, so find the 'right' place....
        if found_service == False:
            for linenum in range (insert_line_at, len(lines)):
                if lines[linenum][0] != '#':
                    break                      
            lines.insert(linenum, pam_entry['defline'])
            changes[pam_entry['defline']] = None
            problem_messages.append("%s: Missing line for '%s %s' " % 
                                   (fileName, pam_entry['desc'], self.__pam_service))
            fixed_messages.append("%s: Inserted corrected line for '%s %s' " % 
                                   (fileName, pam_entry['desc'], self.__pam_service))
        
        
        return {'problems':problem_messages, 'fixes':fixed_messages, 'lines':lines, 'changes': changes}
        
    def parse_system_auth(self, fileName, option=None):
        """ Open the file parse it *looking* for lines that satisfy the required module entries 
            We look for cases where the lines are missing, where they are malformed, and where they are
            formed properly but the faillimit is set wrong.  Each requires a different approach to fix.
        """
        
        
        try:
            in_obj = open(fileName, 'r')
        except Exception, err:
            msg =  "Unable to open file for analysis (%s)" % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        in_obj.close()
        problems = []
        changes = {}
        fixes = []
        for pam_line in self.__pam_entries:
            ret_dict = self.scan_for_pam_line(fileName, lines, pam_line)
            problems.extend(ret_dict['problems'])
            fixes.extend(ret_dict['fixes'])
            lines = ret_dict['lines']
            changes.update(ret_dict['changes'])
          
        return {'problems' : problems, 'fixes': fixes, 'changes' : changes, 'lines' :lines}  

    ##########################################################################
    def scan(self, option=None):
        """ Check to see if account locks are in place.
            Looks to see if there is a line with 'pam_tally.so' (or pam_tally2.so for F12) and 'deny=[1-3]' on it,
        """

        self._init_fields(option)
        messages = {'messages' : [] }
        retval = True
        
        for fileName in self.__target_files:
            ret_dict = self.parse_system_auth(fileName, option)   
            if ret_dict['problems'] != [] :
                for msg in ret_dict['problems']:
                    self.logger.notice(self.module_name, msg)
                messages['messages'].extend(ret_dict['problems'])        
                retval = False
                
        return retval, '', messages


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def apply(self, option=None):
        """Enable account locking after 3 unsuccessful login attempts."""

        msg = None
        self._init_fields(option)
        messages = {'messages':[]}
        # Protect file
        changeDict = {}
        retval = False
        
        for fileName in self.__target_files:
            tcs_utils.protect_file(fileName)

            ret_dict = self.parse_system_auth(fileName,option)   
        
            if ret_dict['fixes'] == [] :
                continue
            else:
                for msg in ret_dict['fixes']:
                    self.logger.notice(self.module_name, msg)
                messages['messages'].extend(ret_dict['fixes'])        

            try:
                out_obj = open(fileName + '.new', 'w')
            except Exception, err:
                msg = "Unable to create temporary file (%s)" % str(err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
            for line in ret_dict['lines']:
                out_obj.write(line)
            out_obj.close()
        
            try:
                shutil.copymode(fileName, fileName + '.new')
                shutil.copy2(fileName + '.new', fileName)
                sb_utils.SELinux.restoreSecurityContext(fileName)
                os.unlink(fileName + '.new')
                changeDict[fileName] = ret_dict['changes']
            except OSError:
                msg = "Unable to replace %s with new version." % fileName 
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            msg = 'Added %s to authentication service' % self.__pam_service
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        if changeDict != {}:
            # prefix with 'files' to distinguish from older dictionaries....
            changeDict = {'files': changeDict}
            retval = True
        
            
        return retval, str(changeDict) , messages

    ##########################################################################
    def undo(self, change_record=None):
        """Disable account locking after 3 unsuccessful login attempts."""

        # we're not calling scan directly
        self._init_fields()
        if not change_record : 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        changes = {}
        if change_record != 'added':
            try:
                changes = tcs_utils.string_to_dictionary (change_record)
                try:
                    changes = changes['files']  
                except KeyError:
                    changes = {'/etc/pam.d/system-auth': changes} 
            except Exception, err:
                msg = "Unable to process change_record to perform undo.\n%s" % err
                self.logger.error(self.module_name, 'Undo Error: '+ msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            changes = {None:None}
        
        for fileName in changes:        
            newfile = "%s.new" % fileName
            thisChange = changes[fileName]
            try:
                origfile = open(fileName, 'r')
                workfile = open(newfile, 'w')
            except IOError, err:
                msg = 'Undo Error: %s' % err
                self.logger.error(self.module_name, msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
 
            origlines = origfile.readlines()
            for ch in thisChange.items():
                if ch[0] != None:
                    look_for = ch[0].strip()
                else:
                    look_for = ch[0]
                if ch[1] != None:
                    replace_with = ch[1].strip()
                replace_with = ch[1]

                for idx, line in enumerate(origlines):
                    # sanity check - look only for our changes
                    if not line or line[0] == '#' or line.find('pam_tally')<0:   
                        continue
                    if line.endswith("#Added by OS Lockdown\n") :
                        origlines.pop(idx)
                        break
                    elif look_for == line.strip():
                        if replace_with != None and replace_with != '':
                            origlines[idx] = replace_with
                        else:
                            origlines.pop(idx)
                        break
            workfile.writelines(origlines)
                
            origfile.close()
            workfile.close()

            try:
                shutil.copymode(fileName , newfile)
                shutil.copy2(newfile, fileName)
                sb_utils.SELinux.restoreSecurityContext(fileName)
                os.unlink(newfile)
            except Exception, err:
                msg = 'Undo Error: %s' % err
                self.logger.error(self.module_name, msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        msg = 'Removed %s as authentication service from /etc/pam.d/system-auth.' % self.__pam_service
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

 
