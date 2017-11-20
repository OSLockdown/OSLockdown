#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.iniHandler
import sb_utils.SELinux

class ConfigureGDM_X11:

    def __init__(self):
        self.module_name = "ConfigureGDM_X11"
        self.__gdm_files = ['/etc/X11/gdm/gdm.conf' , '/etc/X11/gdm/custom.conf',
                            '/etc/gdm/gdm.conf', '/etc/gdm/custom.conf']
        self.logger = TCSLogger.TCSLogger.getInstance()


    ##########################################################################
    def validate_input(self, option):
        if option and option != 'None':
            return 1
        return 0

    def process_gdm_conf_file(self, filename):
        results = []
        changed = False
        lines = []
        
        if os.path.exists(filename):
            try:
                gdm_file = sb_utils.file.iniHandler.iniHandler()
                gdm_file.read_file(filename)
                disallowtcp = gdm_file.get_section_value(['security', 'DisallowTCP'])
                if disallowtcp in ['True', 'true']:
                    results.append(['ok', "Found 'DisallowTCP=%s' in 'security' section of %s" % (disallowtcp, filename) ])
                else:
                    gdm_file.set_section_value(['security', 'DisallowTCP', 'true'])
                    results.append(['problem', "Did not find 'DisallowTCP=true' or 'DisallowTCP=True' in 'security' section of %s" % filename ] )
                    results.append(['fix', "Added 'DisallowTCP=true' to 'security' section of %s" % filename ])
                    changed = True
                    lines = gdm_file.get_lines()
            except Exception, err:
                results.append(['error', "Unable to process %s (%s)" % (filename, str(err)) ])                         
        else:
            msg = "%s does not exist; skipping check" % filename
            results.append(['ok', msg])
    
        return changed, results, lines
            
    ##########################################################################
    def scan(self, option=None):

        messages = []
        changed = []
        results = []
        
        for filename in self.__gdm_files:
            c, r, l = self.process_gdm_conf_file(filename)
            changed.append(c)
            results.extend(r)
                
        for res in results:
            if res[0] == 'ok' :
                self.logger.notice(self.module_name, res[1])
                messages.append(res[1])
            elif res[0] in ['problem', 'error']:
                self.logger.warning(self.module_name, res[1])
                messages.append('Error: %s' % res[1])
        
        
        if True in changed:
            return False, '', {'messages':messages}
        else:
            return True, '', {'messages':messages}


    # write newlines to a scratch file, then generate a 'diff' record comparing the newfile 
    # to filename, suitable to later revert these changes.  Replace filename with the scratch
    # file
    ##########################################################################
    def generate_patch_entry(self, filename, newlines):

        try:
            tmpfile = open(self.__tmp_file, 'w')
        
        except IOError, err:
            msg = "Unable to create scratch file %s holding changes for %s: %s" % (self.__tmp_file, filename, err)
            self.logger.error(self.module_name, 'Apply Failed: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        tmpfile.writelines(newlines)
        tmpfile.close()

        change_record = tcs_utils.generate_diff_record(self.__tmp_file, filename)

        try:
            shutil.copymode(filename, self.__tmp_file)
            shutil.copy2(self.__tmp_file, filename)
            sb_utils.SELinux.restoreSecurityContext(filename)
            os.unlink(self.__tmp_file)
        except (IOError), err:
            msg = 'Apply Error: ' + str(err)
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        return change_record
        
    ##########################################################################
    def apply(self, option=None):

        change_record = []
        changed = []
        results = []
        messages = []
    
        for filename in self.__gdm_files:
            c, r, l = self.process_gdm_conf_file(filename)
            changed.append(c)
            results.extend(r)
            if c != False:
                change_record.append( self.generate_patch_entry(filename, l))

        for res in results:
            if res[0] == 'ok' :
                self.logger.notice(self.module_name, res[1])
                messages.append(res[1])
            elif res[0] in ['problem', 'fix', 'error']:
                self.logger.warning(self.module_name, res[1])
                messages.append('Error: %s' % res[1])
        
        if change_record == []: 
            return False, '', {'messages':messages}
        else:
            return True, ''.join(change_record), {'messages':messages}


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        result, reason, messages = self.scan()
        if result == 'Fail':
            return False, reason, messages

        if not change_record or change_record == "[]" or change_record == "":
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return False, '', {'messages':[msg]}

        try:
            tcs_utils.apply_patch(change_record)
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'GDM X11 startup scripts restored'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {'messages':[msg]}

