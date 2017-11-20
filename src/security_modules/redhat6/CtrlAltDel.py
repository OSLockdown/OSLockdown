#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# CtrlAltDel module provides the class for handling the security guidelines
# regarding a systems support for ctrl-alt-del key combinations.
#
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux
import sb_utils.gdm

class CtrlAltDel:
    """
    CtrlAltDel Security Module handles the guideline for disabling 
    ctrl-alt-del key sequence.
    
    """

    def __init__(self):
        self.module_name = "CtrlAltDel"
        
        self.__target_file = '/etc/init/control-alt-delete.conf'
        self.__pattern     = 'start on control-alt-delete'
        self.__tmp_file    = self.__target_file + '.new'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.CONFIG_SOURCE = ""

        
        self._gconf_key = "/apps/gnome_settings_daemon/keybindings/power"
        
        self.__cmd = "/usr/bin/gconftool-2"


    ##########################################################################
    def scan(self, option=None):
        """ Check to see if the ctrl-alt-del key combination is allowed."""

        messages = {'messages':[]}
        retval = True
        
        if not os.path.isfile(self.__target_file):
            msg = "%s does not exist" % self.__target_file
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open %s: %s" % (self.__target_file, str(err))
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
     
        
        msg = "Looking for lines starting with '%s' in %s" % (self.__pattern, self.__target_file)
        self.logger.info(self.module_name, 'Scan : ' + msg)

        lines = in_obj.readlines()
        in_obj.close()

        for line in lines:
            line = line.strip()
            if line.startswith(self.__pattern): 
                msg = "Ctrl-Alt-Delete not disabled in %s" % self.__target_file
                self.logger.notice(self.module_name, 'Scan Failed: %s' % msg)
                messages['messages'].append(msg)
                retval = False

        gconfVal = sb_utils.gdm.get(paramKey=self._gconf_key)
        if gconfVal != "":
            msg = "Mandatory '%s' setting is not ''" % self._gconf_key
            self.logger.notice(self.module_name, 'Scan Failed: %s' % msg)
            messages['messages'].append(msg)
            retval = False
            
        return retval, '', messages

    ##########################################################################
    def apply(self, option=None):
        """ Disable the ctrl-alt-del key combination."""

        change_record = {}
        result, reason, messages = self.scan()
        if result == True:
            return False, 'none', messages
         
        messages = {'messages':[]}
        retval = False
        
        # Protect file
        tcs_utils.protect_file(self.__target_file)

        search_pattern = re.compile(self.__pattern)
        try:
            in_obj = open(self.__target_file, 'r')
        except IOError, err:
            msg = "Unable to open file %s (%s)" % (self.__target_file, str(err))
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            out_obj = open(self.__target_file + '.new', 'w')
        except Exception, err:
            msg = "Unable to create temporary file (%s)." % str(err)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        lines = in_obj.readlines()
        for line in lines:
            if line.startswith('#'):
                continue
            if search_pattern.search(line):
                new_line = "#" + line
                out_obj.write(new_line)
                change_record['targetfile'] = 'added'
                retval = True
            else:
                out_obj.write(line)
        out_obj.close()
        in_obj.close()

        try:
            if change_record.has_key('targetfile'):
                shutil.copymode(self.__target_file, self.__target_file + '.new')
                shutil.copy2(self.__target_file + '.new', self.__target_file)
                sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__target_file + '.new')
        except OSError:
            msg = "Unable to replace %s with new version." % self.__target_file
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        oldValue = sb_utils.gdm.get(paramKey=self._gconf_key)
        if oldValue != "":
            newValue = ""
            retval = True
            sb_utils.gdm.set(paramKey=self._gconf_key, paramValue="", dataType="string")
            msg = 'Currently logged in users will need to logout and log back in to have ctrl-alt-del disabled'
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            messages['messages'].append(msg)
            change_record['gconf'] = [self._gconf_key, oldValue]
        
        if retval == True:
            msg = 'Ctrl-alt-del key combination disabled in %s' % self.__target_file
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return retval , str(change_record) , messages

    ##########################################################################
    def undo(self, change_record):
        """ Re-enable the ctrl-alt-del key combination."""


        messages = {'messages':[]}
        

        if change_record == 'added' :   # oldstyle change record
            change_record = {'targetfile' : 'added'}
        else:
            try:
                change_record = tcs_utils.string_to_dictionary (change_record)
            except Exception, err:
                msg = "Unable to process change_record to perform undo: %s" % str(err)
                self.logger.error(self.module_name, 'Undo Error: '+ msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                 
        if change_record.has_key('targetfile'):
            try:
                origfile = open(self.__target_file, 'r')
                workfile = open(self.__tmp_file, 'w')
            except IOError, err:
                self.logger.error(self.module_name, 'Undo Error: ' + str(err))
                raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))


            for line in origfile:
                if line.startswith("#exec /sbin/shutdown -r now") or line.startswith('#start on control-alt-delete'):
                    workfile.write(line[1:])
                else:
                    workfile.write(line)

            origfile.close()
            workfile.close()

            try:
                shutil.copy2(self.__tmp_file, self.__target_file)
                sb_utils.SELinux.restoreSecurityContext(self.__target_file)
                os.unlink(self.__tmp_file)
            except OSError, err:
                self.logger.error(self.module_name, 'Undo Error: ' + str(err))
                raise tcs_utils.ActionError('%s %s' % (self.module_name, str(err)))

            msg = 'Ctrl-alt-del key combination re-enabled in %s' % self.__target_file
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        
        if change_record.has_key('gconf'):
            keyName,oldValue = change_record['gconf']
            if oldValue == None or oldValue == 'unset':
                sb_utils.gdm.unset(paramKey=keyName)
            else:
                sb_utils.gdm.set(paramKey=self._gconf_key, paramValue=oldValue, dataType="string")
                              
            msg = 'Ctrl-alt-del key combination restored in %s' % self._gconf_key
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        
        return True, '', messages

