#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module configures the Gnome display manager and X11
# server to disallow remote X connections over TCP.
#
# If neither SUNWgnome-display-mgr-root or SUNWxwplt
# packages are installed, the module is not applicable.
#
# If the Gnome display manager is installed, this module
# will ensure that 'DisallowTCP' is set true under the [security]
# section and that 'Enable' is set to false in the [xdmcp]
# section. This is done in the /etc/X11/gdm/gdm.conf file.
#
# For the X11 Server, this module will set the tcp_listen property
# of the x11-server service:
#
# svccfg -s  svc:/application/x11/x11-server setprop options/tcp_listen = false
#
#

import sys
import os
import ConfigParser
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.service
import sb_utils.os.software

class RemoteXClients:

    def __init__(self):
        self.module_name = "RemoteXClients"

        self.logger = TCSLogger.TCSLogger.getInstance()

        self.__gdm_file = '/etc/X11/gdm/gdm.conf'

        self.__gdm_settings = {}
        self.__gdm_settings['security'] = { 'DisallowTCP' : 'true'}
        self.__gdm_settings['xdmcp'] = { 'Enable' : 'false'}
 
    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        na_count = 0

        #
        # Analyze GDM (Gnome) Configuration File
        #
        gdm_pkg_installed = sb_utils.os.software.is_installed(
                                         pkgname='SUNWgnome-display-mgr-root')

        if gdm_pkg_installed != True:
            msg = "Gnome display manager not installed; skipping check of "\
                  "%s" % (self.__gdm_file)
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            na_count += 1
        else:
            try:
                in_obj = open(self.__gdm_file, 'r')
            except IOError, err:
                msg = "Unable to read %s: %s " % (self.__gdm_file, err)
                self.logger.error(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

            newfile = self.__gdm_file + '.new'
            try:
                out_obj = open(newfile, 'w')
            except IOError, err:
                msg = "Unable to create temp file %s: %s" % (newfile, err)
                self.logger.error(self.module_name, 'Scan Failed: ' + msg)
                return 'Fail', msg

            out_obj = open(newfile, 'w')
            lines = in_obj.xreadlines()
            for line in lines:
                line = line.lstrip(' ')
                out_obj.write(line)
        
            in_obj.close()
            out_obj.close()
        
            msg = 'Analyzing %s' % self.__gdm_file
            self.logger.notice(self.module_name, msg)
            config = ConfigParser.ConfigParser()
            config.read(newfile)
            try:
                os.unlink(newfile)
            except IOError, err:
                msg = "Unable to remove temp file %s: %s" % (newfile, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)

            okay_flag = True
            for section in self.__gdm_settings.keys():
                subpair = self.__gdm_settings[section]
                for subkey in subpair.keys(): 
                    msg = "Checking value of '%s' in section '%s'" % \
                          (subkey, section)
                    self.logger.info(self.module_name, 'Scan: ' + msg)
                    subvalue = self.__gdm_settings[section][subkey].lower()
    
                    if config.has_option(section, subkey):
                        curvalue = config.get(section, subkey).lower()
                    else:
                        okay_flag = False
                        msg = "Scan Failed: Section '%s', '%s' option "\
                              "is missing." % (section, subkey)
                        self.logger.notice(self.module_name, msg)
                        continue
    
                    if subvalue != curvalue:
                        msg = "Scan Failed: Section '%s', option '%s' is "\
                              "NOT set to '%s'" % (section, subkey, subvalue)
                        self.logger.notice(self.module_name, msg)
                        okay_flag = False
                    else:
                        msg = "Scan Passed: Section '%s', option '%s' is "\
                              "set to '%s'" % (section, subkey, subvalue)
                        self.logger.notice(self.module_name, msg)
              
            if okay_flag == False:
                msg = "GDM configuration is missing or has incorrect parameters"
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
    
    
        #
        # X11-Server - tcp_listen property should be set to false.
        #
        x11_installed = sb_utils.os.software.is_installed(pkgname='SUNWxwplt')

        if x11_installed != True:
            msg = "X Window System platform software (SUNWxwplt) not "\
                  "installed; skipping tcp_listen property check of x11-server"
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)

            if na_count > 0:
                msg = "Neither SUNWxwplt or SUNWgnome-display-mgr-root "\
                      "packages are installed."
                raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


        results = sb_utils.os.service.getprop(
                          svcname='svc:/application/x11/x11-server', 
                          property='options/tcp_listen' )


        if results == 'true':        
            msg = 'X11-server tcp_listen is set to true'
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            okay_flag = False
        else:
            msg = 'X11-server tcp_listen is NOT set to true'
            self.logger.notice(self.module_name, 'Scan Passed: ' + msg)


        if okay_flag == False:
            return 'Fail', ''
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        result, reason = self.scan()
        if result == 'Pass':
            return 0,''
            

        #
        # Update GDM  (Gnome) Configuration File
        #
        already_done = {}
        change_record = ""

        # Initialize record-keeping dictionary to know which params 
        # we've already set
        for subkey in self.__gdm_settings.keys():
            already_done[subkey] = {}
            for subsubkey in self.__gdm_settings[subkey].keys():
                already_done[subkey][subsubkey] = False

        # If file does not exist, create one:
        if not os.path.isfile(self.__gdm_file): 
            try:
                out_obj = open(self.__gdm_file, 'w')
            except IOError, err:
                msg = 'Unable to create new %s: %s' % (self.__gdm_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                return 0, msg

            out_obj.write('; Created by OS Lockdown\n')
            for section in self.__gdm_settings.keys():
                out_obj.write('[' + section + ']\n')
                subpair = self.__gdm_settings[section]
                for subkey in subpair.keys():    
                    subvalue = self.__gdm_settings[section][subkey]
                    out_obj.write(subkey + ' = ' + subvalue + '\n')
                out_obj.write('\n')
            out_obj.close()  


        else: 
            newfile = self.__gdm_file + '.new'
            try:  
                in_obj = open(self.__gdm_file, 'r')
                out_obj = open(newfile, 'w')
            except IOError, err:
                msg = 'Unable to create temp %s: %s' % (newfile, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
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
                                out_obj.write(self.__gdm_settings[section][skey])
                                out_obj.write('\n')
                    section = line.rstrip('\n')
                    section = section.strip(' ')
                    section = section.lstrip('[')
                    section = section.rstrip(']')
                    out_obj.write(line)
                    continue
    
                newline = line
                if not line.startswith('#') and not line.startswith('\n'):
                    line = line.rstrip('\n')
                    opt, curvalue = line.split('=', 1)
                    opt = opt.strip(' ')
                    if curvalue != None:
                        curvalue = curvalue.strip(' ')  
    
                    if self.__gdm_settings.has_key(section):
                        subkey = self.__gdm_settings[section]
                        if subkey.has_key(opt):
                            if subkey[opt] != curvalue:
                                # Ignore duplicates
                                if already_done[section][opt] == True:
                                    continue
    
                                already_done[section][opt] = True
                                newline = opt + '=' + subkey[opt] + '\n'
                                msg = 'Apply Performed: Set ' + opt + ' = ' + subkey[opt]
                                self.logger.info(self.module_name, msg)
    
                            else:
                                if already_done[section][opt] == True:
                                    continue
                                already_done[section][opt] = True
    
                out_obj.write(newline)
    
            out_obj.close()
    
            change_record = tcs_utils.generate_diff_record(newfile, self.__gdm_file)

            # Switch old file with new one while preserving permissions
            try:
                shutil.copymode(self.__gdm_file, newfile)
                shutil.copy2(newfile, self.__gdm_file)
                os.unlink(newfile)
            except OSError, err:
                msg = "Unable to replace %s with new version: %s" % \
                      (self.__gdm_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


        #
        # X11-Server - tcp_listen property should be set to false.
        #
        x11results = sb_utils.os.service.getprop(
                          svcname='svc:/application/x11/x11-server',
                          property='options/tcp_listen' )

        if x11results == 'true':
            results = sb_utils.os.service.setprop(
                          svcname='svc:/application/x11/x11-server', 
                          property='options/tcp_listen', 
                          propval='false')

            if results == True:
                msg = 'Apply Performed: x11-server tcp_listen set to false'
                self.logger.notice(self.module_name, msg)
            else:
                msg = "Apply Failed: Unable to set x11-server's tcp_listen "\
                      "property to false"
                self.logger.error(self.module_name, msg)


        msg = "Remote X clients are now disallowed"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return 1, change_record


    ##########################################################################
    def undo(self, change_record=None):

        # Check to see if packages or installed
        x11_installed     = sb_utils.os.software.is_installed(
                                         pkgname='SUNWxwplt')

        gdm_pkg_installed = sb_utils.os.software.is_installed(
                                         pkgname='SUNWgnome-display-mgr-root')


        # Neither package is installed, so just quit
        if x11_installed == False and gdm_pkg_installed == False:
            msg = 'module is not applicable for this system'
            self.logger.notice(self.module_name, 'Undo: ' + msg)
            return 1

        # GDM installed but I was not given a change record to restore file
        if not change_record and gdm_pkg_installed == True:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
 
        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # X11 is installed 
        if x11_installed == 'true':
            results = sb_utils.os.service.setprop(
                          svcname='svc:/application/x11/x11-server',
                          property='options/tcp_listen',
                          propval='true')

            if results == True:
                msg = 'Undo Performed: x11-server tcp_listen set to true'
                self.logger.notice(self.module_name, msg)
            else:
                msg = "Undo Failed: Unable to set x11-server's tcp_listen "\
                      "property to true"
                self.logger.error(self.module_name, msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        return 1
