#!/usr/bin/env python

# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

"""
  Processes configuraiton files in the 
  following format:

  [section]
    option = value
    option = value
    ...

  [section]
    option = value
    option = value
    ...
"""

import ConfigParser
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.SELinux

class SMB_Conf:
    """
    Configure SMB Settings
    """
    def __init__(self):
        """
        Constructor - Initialize dictionary which need
        to be set /etc/samba/smb.conf
        """
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.module_name = 'SMB_conf'

        if sb_utils.os.info.is_solaris() == True:
            self.__smb_ini = '/etc/sfw/smb.conf'
            self.__pkgname = 'SUNWsmbar'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.__smb_ini = '/etc/samba/smb.conf'
            self.__pkgname = 'samba'
        else:
            self.__smb_ini = '/etc/samba/smb.conf'
            self.__pkgname = 'samba-common'

        self.__newfile = self.__smb_ini + '.new'
        
        self.__smb_settings = {}
        self.__smb_settings['global'] = { 'security' : 'user',
                                          'smb passwd file' : '/etc/samba/passwd', 
                                          'encrypt passwords' : 'yes', 
                                          'client lanman auth' : 'no', 
                                          'client ntlmv2 auth' : 'yes', 
                                          'server signing' : 'mandatory', 
                                          'client signing' : 'mandatory', 
                                          'guest ok' : 'no' }

    ##########################################################################
    def scan(self, option=None):
        """
        Examine /etc/samba/smb.conf for missing or invalid values
        """  
        if option != None:
            option = None
         
        messages = {'messages':[]}
        
        results =  sb_utils.os.software.is_installed(pkgname=self.__pkgname)

        if results == False:
            msg = "%s package is not installed" % self.__pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        if not os.path.isfile(self.__smb_ini):
            msg = "Missing %s but samba is installed" % self.__smb_ini
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__smb_ini, 'r')
        except (IOError, OSError), err:
            msg = "Unable to read %s: %s" % (self.__smb_ini, err) 
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
           
        try:
            out_obj = open(self.__newfile, 'w')
        except (IOError, OSError), err:
            in_obj.close()
            msg = "Unable to create %s: %s" % (self.__newfile, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        lines = in_obj.xreadlines()
        for line in lines:
            line = line.strip(' ')
            line = line.strip('\t')
            out_obj.write(line)
        
        in_obj.close()
        out_obj.close()
        
        config = ConfigParser.ConfigParser()
        config.read(self.__newfile)

        try:
            os.unlink(self.__newfile)
        except (OSError, IOError), err:
            msg = "Unable to remove %s: %s" % (self.__newfile, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)

        okay_flag = True
        for section in self.__smb_settings.keys():
            subpair = self.__smb_settings[section]
            for subkey in subpair.keys():    
                subvalue = self.__smb_settings[section][subkey].lower()
                if config.has_option(section, subkey):
                    curvalue = config.get(section, subkey).lower()
                else:
                    msg = "Scan Failed: '%s' '%s' parameter is not "\
                          "configured"  % (section, subkey)
                    messages['messages'].append(msg)
                    self.logger.notice(self.module_name, msg)
                    okay_flag = False
                    continue

                if subvalue != curvalue:
                    msg = "Scan Failed: '%s' '%s' parameter is not set "\
                          "to '%s'" % (section, subkey, subvalue)
                    messages['messages'].append(msg)
                    self.logger.notice(self.module_name, msg)
                    okay_flag = False
          
        if okay_flag == False:
            msg = "Missing or incorrect parameters"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            messages['messages'].append(msg)
            return False, '', messages
        
        return True, '', messages


    ##########################################################################
    def apply(self, option=None):

        messages = {'messages':[]}
        self.validate_input(option)

        results =  sb_utils.os.software.is_installed(pkgname=self.__pkgname)

        if results == False:
            msg = "%s package is not installed" % self.__pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        already_done = {}
        change_record = ""
        for subkey in self.__smb_settings.keys():
            already_done[subkey] = {}
            for subsubkey in self.__smb_settings[subkey].keys():
                already_done[subkey][subsubkey] = False

        if not os.path.isfile(self.__smb_ini): 
            msg = "%s does not exist" % self.__smb_ini
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''
 
        try:  
            in_obj = open(self.__smb_ini, 'r')
        except (OSError, IOError), err:
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        try:  
            out_obj = open(self.__newfile, 'w')
        except (OSError, IOError), err:
            in_obj.close()
            self.logger.error(self.module_name, 'Apply Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        lines = in_obj.xreadlines()
        section = None
        for line in lines:
            line = line.strip(' ')
            line = line.strip('\t')
            if line.startswith('['):
                if already_done.has_key(section):
                    for skey in already_done[section].keys():
                       
                        if already_done[section][skey] == False:
                            out_obj.write(skey + ' = ')
                            out_obj.write(self.__smb_settings[section][skey])
                            out_obj.write('\n')
                            msg = "Setting Section '%s', '%s' to '%s'" % \
                                  (section, skey, 
                                           self.__smb_settings[section][skey])
                            messages['messages'].append(msg)
                            self.logger.notice(self.module_name, 
                                                   'Apply Performed: ' + msg)
                            change_record += section + '|' + skey + '|null\n'

                section = line.rstrip('\n')
                section = section.strip(' ')
                section = section.lstrip('[')
                section = section.rstrip(']')
                out_obj.write(line)
                continue

            newline = line
            if not line.startswith(';') and not line.startswith('\n')\
                       and not line.startswith('#') and not line.startswith('['):
                line = line.rstrip('\n')
                opt, curvalue = line.split('=', 1)
                opt = opt.strip(' ')
                if curvalue != None:
                    curvalue = curvalue.strip(' ')  

                if self.__smb_settings.has_key(section):
                    subkey = self.__smb_settings[section]
                    if subkey.has_key(opt):
                        if subkey[opt] != curvalue:
                            # Ignore duplicates
                            if already_done[section][opt] == True:
                                continue

                            already_done[section][opt] = True
                            change_record += section + '|' + opt + '|' + curvalue + '\n'
                            newline = opt + ' = ' + subkey[opt] + '\n'
                            msg = "Apply Performed: Section '%s', set '%s' "\
                                  "to '%s'" % (section, opt, subkey[opt])
                            messages['messages'].append(msg)
                            self.logger.notice(self.module_name, msg)

                        else:
                            if already_done[section][opt] == True:
                                continue
                            already_done[section][opt] = True

            out_obj.write(newline)

        in_obj.close()
        out_obj.close()

        # Switch old file with new one while preserving permissions
        try:
            shutil.copymode(self.__smb_ini, self.__newfile)
            shutil.copy2(self.__newfile, self.__smb_ini)
            sb_utils.SELinux.restoreSecurityContext(self.__smb_ini)
            os.unlink(self.__newfile)
        except (IOError, OSError), err:
            msg = "Unable to replace %s with new version: %s" % (self.__smb_ini, err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if change_record == '':
            return False, '', messages
        else:
            return True, change_record, messages

    ##########################################################################
    def undo(self, change_record=None):

        messages = {'message':[]}
        if not change_record or change_record == '': 
            return False , "", "" 

        lines = change_record.rstrip('\n').split('\n')
        old_smb_settings = {}
        already_done = {}
        for line in lines:
            fields = line.split('|')
            if len(fields) != 3:
                continue

            section = fields[0].strip(' ')
            if not old_smb_settings.has_key(section):
                old_smb_settings[section] = {}
                already_done[section] = {}
            subkey = fields[1].strip(' ')
            old_smb_settings[section][subkey] = fields[2].strip(' ')
            already_done[section][subkey] = False

        try:  
            in_obj = open(self.__smb_ini, 'r')
        except (IOError, OSError), err:
            self.logger.info(self.module_name, 'Undo Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        try:  
            out_obj = open(self.__newfile, 'w')
        except (IOError, OSError), err:
            in_obj.close()
            self.logger.info(self.module_name, 'Undo Error: ' + err)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, err))

        lines = in_obj.xreadlines()
        section = None
        for line in lines:
            line = line.strip(' ')
            if line.startswith('['):
                if already_done.has_key(section):
                    for skey in already_done[section].keys():
                        if already_done[section][skey] == False:
                            out_obj.write(skey + ' = ')
                            out_obj.write(old_smb_settings[section][skey])
                            out_obj.write('\n')
                            msg = "Section '%s', restored '%s' to '%s'" % \
                                (section, skey, old_smb_settings[section][skey])
                            messages['messages'].append(msg)
                            self.logger.notice(self.module_name, 
                                                    'Undo Performed: ' + msg)
                section = line.rstrip('\n')
                section = section.strip(' ')
                section = section.lstrip('[')
                section = section.rstrip(']')
                out_obj.write(line)
                continue

            newline = line
            if not line.startswith(';') and not line.startswith('#') \
                                                 and not line.startswith('\n'):
                line = line.rstrip('\n')
                opt, curvalue = line.split('=', 1)

                opt = opt.strip(' ')
                if curvalue != None:
                    curvalue = curvalue.strip(' ')  

                if old_smb_settings.has_key(section):
                    subkey = old_smb_settings[section]
                    if subkey.has_key(opt):
                        if subkey[opt] != curvalue:
                            # Ignore duplicates
                            if already_done[section][opt] == True:
                                continue

                            already_done[section][opt] = True
                            if subkey[opt] != 'null':
                                newline = opt + ' = ' + subkey[opt] + '\n'
                            else:
                                newline = ''

                        else:
                            if already_done[section][opt] == True:
                                continue
                            already_done[section][opt] = True
            
            if newline != '':
                out_obj.write(newline)

        out_obj.close()
        in_obj.close()

        # Switch old file with new one while preserving permissions
        try:
            shutil.copymode(self.__smb_ini, self.__newfile)
            shutil.copy2(self.__newfile, self.__smb_ini)
            sb_utils.SELinux.restoreSecurityContext(self.__smb_ini)
            os.unlink(self.__newfile)
        except (IOError, OSError), err:
            msg = "Unable to replace %s with new version: %s" % (self.__smb_ini, err)
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return True, "", messages


    ##########################################################################
    def validate_input(self, option=None):
        """Validate input - This class has no options"""
        if option != None:
            option = None
        return 0


