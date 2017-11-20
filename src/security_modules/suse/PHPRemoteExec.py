#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import ConfigParser
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info


class PHPRemoteExec:

    def __init__(self):
        """
        Constructor - Initialize dictionary which need
        to be set /etc/php.ini
        """
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.module_name = 'PHPRemoteExec'

        self.__pkgname = 'apache2-mod_php5'
        self.__php_ini = '/etc/php5/apache2/php.ini'
        self.__newfile = '/etc/php5/apache2/php.ini.new'

        self.__php_settings = {}
        self.__php_settings['PHP'] = { 
                 'register_globals' : 'Off',
                 'magic_quotes_gpc' : 'Off',
                  'allow_url_fopen' : 'Off' }

    ########################################################################## 
    def scan(self, option=None):
        """
        Examine /etc/php.ini for missing or invalid values
        """  
        if option != None:
            option = None
         
        results = sb_utils.os.software.is_installed(pkgname=self.__pkgname)
        if results == False:
            msg = "'%s' is not installed on the system" % self.__pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        if not os.path.isfile(self.__php_ini):
            msg = "%s not found. Is PHP installed?" % self.__php_ini
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        self.logger.info(self.module_name, 'Checking %s' % self.__php_ini)
        try:
            in_obj = open(self.__php_ini, 'r')
        except IOError, err:
            msg = "Unable to read %s (%s)" % (self.__php_ini, err)
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        try:
            out_obj = open(self.__newfile, 'w')
        except IOError:
            msg = "Unable to create temp file %s" % self.__newfile
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg

        out_obj = open(self.__newfile, 'w')
        lines = in_obj.xreadlines()
        for line in lines:
            line = line.lstrip(' ')
            out_obj.write(line)
        
        in_obj.close()
        out_obj.close()
        
        config = ConfigParser.ConfigParser()
        config.read(self.__newfile)
        try:
            os.unlink(self.__newfile)
        except IOError:
            msg = "Unable to remove temp file %s" % self.__newfile
            self.logger.info(self.module_name, 'Scan Error: ' + msg)

        okay_flag = True
        for section in self.__php_settings.keys():
            subpair = self.__php_settings[section]
            for subkey in subpair.keys():    
                subvalue = self.__php_settings[section][subkey].lower()
                if config.has_option(section, subkey):
                    curvalue = config.get(section, subkey).lower()
                else:
                    okay_flag = False
                    continue

                if subvalue != curvalue:
                    msg = "%s.%s is not set to %s" % (section, subkey, subvalue)
                    self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                    okay_flag = False
          
        if okay_flag == False:
            msg = "Missing or incorrect parameters"
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        return 'Pass', ''

    
    ##########################################################################
    def apply(self, option=None):
        """
        Set parameters in /etc/php.ini
        Change record line is: <section>|<option>|<value>
        """
        self.validate_input(option)

        results = sb_utils.os.software.is_installed(pkgname=self.__pkgname)
        if results == False:
            msg = "'%s' is not installed on the system" % self.__pkgname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if not os.path.isfile(self.__php_ini):
            msg = "%s not found. Is PHP installed?" % self.__php_ini
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        already_done = {}
        change_record = ""
        for subkey in self.__php_settings.keys():
            already_done[subkey] = {}
            for subsubkey in self.__php_settings[subkey].keys():
                already_done[subkey][subsubkey] = False

        # Create new /etc/php.ini if it is missing
        if not os.path.isfile(self.__php_ini): 
            try:
                out_obj = open(self.__php_ini, 'w')
            except IOError:
                msg = 'Unable to create new %s' % self.__php_ini
                self.logger.info(self.module_name, 'Apply Error: ' + msg)
                return 0, msg

            out_obj.write('; Created by OS Lockdown\n')
            for section in self.__php_settings.keys():
                out_obj.write('[' + section + ']\n')
                subpair = self.__php_settings[section]
                for subkey in subpair.keys():    
                    subvalue = self.__php_settings[section][subkey]
                    out_obj.write(subkey + ' = ' + subvalue + '\n')
                out_obj.write('\n')
            out_obj.close()  
            return 0, '\n'
       
 
        self.logger.info(self.module_name, 'Checking %s' % self.__php_ini)
        try:  
            in_obj = open(self.__php_ini, 'r')
            out_obj = open(self.__newfile, 'w')
        except IOError:
            msg = 'Unable to create temp %s' % self.__newfile
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            return 0, msg

        lines = in_obj.xreadlines()
        section = None
        for line in lines:
            line = line.strip(' ')
            if line.startswith('['):
                if already_done.has_key(section):
                    for skey in already_done[section].keys():
                        if already_done[section][skey] == False:
                            out_obj.write(skey + ' = ')
                            out_obj.write(self.__php_settings[section][skey])
                            out_obj.write('\n')
                section = line.rstrip('\n')
                section = section.strip(' ')
                section = section.lstrip('[')
                section = section.rstrip(']')
                out_obj.write(line)
                continue

            newline = line
            if not line.startswith(';') and not line.startswith('\n'):
                line = line.rstrip('\n')
                opt, curvalue = line.split('=', 1)
                opt = opt.strip(' ')
                if curvalue != None:
                    curvalue = curvalue.strip(' ')  

                if self.__php_settings.has_key(section):
                    subkey = self.__php_settings[section]
                    if subkey.has_key(opt):
                        if subkey[opt] != curvalue:
                            # Ignore duplicates
                            if already_done[section][opt] == True:
                                continue

                            already_done[section][opt] = True
                            change_record += section + '|' + opt + \
                                '|' + curvalue + '\n'
                            newline = opt + ' = ' + subkey[opt] + '\n'
                            msg = 'Apply Performed: Set ' + opt + ' = ' + subkey[opt]
                            self.logger.info(self.module_name, msg)

                        else:
                            if already_done[section][opt] == True:
                                continue
                            already_done[section][opt] = True

            out_obj.write(newline)

        out_obj.close()

        # Switch old file with new one while preserving permissions
        try:
            shutil.copymode(self.__php_ini, self.__newfile)
            shutil.copy2(self.__newfile, self.__php_ini)
            os.unlink(self.__newfile)
        except OSError:
            msg = "Unable to replace %s with new version." % self.__php_ini 
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1, change_record 

    ##########################################################################
    def undo(self, change_record=None):
        """Reverse settings in /etc/php.ini"""

        if change_record == None:
            return 0, 'Missing change record'

        lines = change_record.rstrip('\n').split('\n')
        old_php_settings = {}
        already_done = {}
        for line in lines:
            fields = line.split('|')
            if len(fields) != 3:
                continue
            section = fields[0].strip(' ')
            if not old_php_settings.has_key(section):
                old_php_settings[section] = {}
                already_done[section] = {}
            subkey = fields[1].strip(' ')
            old_php_settings[section][subkey] = fields[2].strip(' ')
            already_done[section][subkey] = False

        try:  
            in_obj = open(self.__php_ini, 'r')
            out_obj = open(self.__newfile, 'w')
        except IOError:
            msg = 'Unable to create temp %s' % self.__newfile
            self.logger.info(self.module_name, 'Undo Error: ' + msg)
            return 0, msg

        lines = in_obj.xreadlines()
        section = None
        for line in lines:
            line = line.strip(' ')
            if line.startswith('['):
                if already_done.has_key(section):
                    for skey in already_done[section].keys():
                        if already_done[section][skey] == False:
                            out_obj.write(skey + ' = ')
                            out_obj.write(old_php_settings[section][skey])
                            out_obj.write('\n')
                section = line.rstrip('\n')
                section = section.strip(' ')
                section = section.lstrip('[')
                section = section.rstrip(']')
                out_obj.write(line)
                continue

            newline = line
            if not line.startswith(';') and not line.startswith('\n'):
                line = line.rstrip('\n')
                opt, curvalue = line.split('=', 1)
                opt = opt.strip(' ')
                if curvalue != None:
                    curvalue = curvalue.strip(' ')  

                if old_php_settings.has_key(section):
                    subkey = old_php_settings[section]
                    if subkey.has_key(opt):
                        if subkey[opt] != curvalue:
                            # Ignore duplicates
                            if already_done[section][opt] == True:
                                continue

                            already_done[section][opt] = True
                            change_record += section + '|' + opt + \
                                '|' + curvalue + '\n'
                            newline = opt + ' = ' + subkey[opt] + '\n'

                        else:
                            if already_done[section][opt] == True:
                                continue
                            already_done[section][opt] = True

            out_obj.write(newline)

        out_obj.close()
        in_obj.close()

        # Switch old file with new one while preserving permissions
        try:
            shutil.copymode(self.__php_ini, self.__newfile)
            shutil.copy2(self.__newfile, self.__php_ini)
            os.unlink(self.__newfile)
        except OSError:
            msg = "Unable to replace %s with new version." % self.__php_ini
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1


    ##########################################################################
    def validate_input(self, option=None):
        """Validate input - This class has no options"""
        if option != None:
            option = None
        return 0

