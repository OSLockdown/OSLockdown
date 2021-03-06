#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

"""
CorrectRcPathVars Module 
  Remove "." and "::" from PATH variables set in
  /etc/init.d/* Scripts
"""


import sys
import os
import glob
import re
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.SELinux

class CorrectRcPathVars:

    def __init__(self):
        self.module_name = "CorrectRcPathVars"
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def validate_input(self, option=None):
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):

        if option != None:
            option = None


        regex   = re.compile('(^"\.|^\.:|::|\.$|\."$)')
        path_re = re.compile('\s*PATH=')

        flag = False
        for rc_script in glob.glob('/etc/init.d/*'):
            if not os.path.isfile(rc_script):
                continue
            try:
                in_obj = open(rc_script, 'r')  
            except (IOError, OSError), err:
                msg = 'Unable to read %s: %s' % (rc_script, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                continue

            msg = """Scan: Checking %s for bad PATH assignments""" % rc_script
            self.logger.info(self.module_name, msg)

            for line_nr, line in enumerate(in_obj.xreadlines()):
                line = line.strip(' ')
                line = line.strip('\t')
                if line.startswith('#'):
                    continue 
                line = line.strip('\n')
                if path_re.search(line):
                    path_val = line.split('=')[1]

                    msg = """Scan: PATH currently set to "%s" at line %d in %s""" % (path_val, line_nr, rc_script)
                    self.logger.debug(self.module_name, msg)

                    if regex.search(path_val):
                        flag = True 
                        msg = 'Bad PATH assignment found in %s, %d' % (rc_script, line_nr)
                        self.logger.notice(self.module_name, 
                             'Scan Failed: ' + msg)

            in_obj.close()

        if flag == True: 
            return 'Fail', 'Bad PATH environment variables found'
            
        return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        if option != None:
            option = None


        regex   = re.compile('(^"\.|^\.:|::|\.$|\."$)')

        # Replace these with a single colon
        regex2  = re.compile('(:\.:|::)') 

        # Replace these with NULL
        regex3  = re.compile('(:\.$|:$|::$)')

        # Replace these with equalsign
        regex3a = re.compile('(=:|=::|=\.:)')

        # Replace these with Quotes
        regex4  = re.compile('(:\."$|:"$|::"$)')

        # Replace these with Equal sign and then Quotes
        regex5  = re.compile('(=":|="::|="\.:)')

        path_re = re.compile('\s*PATH=')

        change_record = ""

        for rc_script in glob.glob('/etc/init.d/*'):
            if not os.path.isfile(rc_script):
                continue

            made_change = False
            # Open rc file for input
            try:
                in_obj  = open(rc_script, 'r')
            except (IOError, OSError), err:
                msg = 'Unable to read %s : %s' % (rc_script, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                continue

            # Open temporary file for write
            tmpfile = '/tmp/.' + rc_script.split('/')[3]
            try:
                out_obj = open(tmpfile, 'w')
            except (IOError, OSError), err:
                msg = 'Unable to create /tmp/.%s : %s' % (rc_script, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                in_obj.close()
                continue

            msg = """Apply: Checking %s for bad PATH assignments""" % rc_script
            self.logger.info(self.module_name, msg)

            for line in in_obj.readlines():
                orig_line = line
                line = line.strip(' ')
                line = line.strip('\t')
                if line.startswith('#'):
                    out_obj.write(orig_line)
                    continue

                line = line.strip('\n')
                if path_re.search(line):
                    path_val = line.split('=')[1]
                    if regex.search(path_val):
                        orig_line = regex2.sub(':', orig_line)
                        orig_line = regex3.sub('', orig_line)
                        orig_line = regex3a.sub('=', orig_line)
                        orig_line = regex4.sub('\"', orig_line)
                        orig_line = regex5.sub('=\"', orig_line)
                        msg = "Removed . and :: from PATH in %s" \
                                     % rc_script
                        self.logger.notice(self.module_name, 
                                     'Apply Performed: ' + msg)
                        made_change = True

                out_obj.write(orig_line) 

            in_obj.close()
            out_obj.close()

            if made_change == True:
                change_record += tcs_utils.generate_diff_record(tmpfile, 
                                                             rc_script) + '\n'
                try:
                    shutil.copymode(rc_script, tmpfile)
                    shutil.copy2(tmpfile, rc_script)
                    sb_utils.SELinux.restoreSecurityContext(rc_script)
                except (OSError, IOError), err:
                    msg = "Unable to replace %s with new version: %s" % (rc_script, err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
            os.unlink(tmpfile)

        if change_record == '':
            return 0, ''
        else:
            return 1, change_record

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        try:
            result, reason = self.scan()
            if result == 'Fail':
                return 0, ''
        except tcs_utils.ScanNotApplicable, err:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            return 0, ''

        if not change_record or change_record == '' :
            msg = "Skipping Undo: No change record or empty change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0

        try:
            tcs_utils.apply_patch(change_record.lstrip())
        except tcs_utils.ActionError, err:
            msg = "Unable to undo previous changes (%s)." % err 
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'PATH environment variables in system RC scripts restored'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

