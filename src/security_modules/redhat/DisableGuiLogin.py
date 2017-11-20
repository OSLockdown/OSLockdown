#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

#
# inittab(5) format:
#   id:runlevels:action:process
#   id:5:initdefault:
#
import sys
import re
import traceback

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger


class DisableGuiLogin:
    """
    DisableGuiLogin Security Module handles the guideline for disabling 
    the graphical user interface login (run-level 5)
    """

    def __init__(self):
        self.module_name = "DisableGuiLogin"
        self.__target_file = '/etc/inittab'
        self.logger = TCSLogger.TCSLogger.getInstance()


    def process_inittab(self, newlevel, action):
        try:
            return self.process_inittab2(newlevel, action)
        except Exception, e:
            print traceback.print_exc(file=sys.stderr)
            

    def process_inittab2(self, newlevel='3', action='scan'):
        """
        Read in the targetfile. 
        Look through lines looking for a line *staring* with 'id:#:initdefault:'
        If action = 'scan':
            if '#' == newlevel then return # - DO NOT WRITE CHANGES
        If action = 'apply':
            if '#' == newlevel then return # - DO NOT WRITE CHANGES
            if '#' != newlevel then replace # with newlevel, return # - WRITE CHANGES
        """
        
        if newlevel not in [ '1', '2', '3', '4', '5' ] :
            msg = "Requested to set unacceptable default run level : %s" % newlevel
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        oldlevel = -1
        try:
            lines = open(self.__target_file, 'r').readlines()
        except IOError, err:
            msg = "Unable to open file %s (%s)" % (self.__target_file, str(err))
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
         
        match_count = 0
        pat = re.compile ('^id:\d:initdefault:')
        repl = 'id:%s:initdefault:' % newlevel
        for linenum in range(0, len(lines)):
            if pat.match(lines[linenum]):
                match_count += 1
                oldlevel = lines[linenum].split(':')[1]
                lines[linenum] = pat.sub(repl, lines[linenum])

        if match_count > 1:
            msg = "%d duplicate entries found for initdefaults line: " % (match_count)
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                     
        if action == 'apply':
            try:
                inittab = open(self.__target_file, 'w')
                inittab.write(''.join(lines))
                inittab.close()
            except IOError, err:
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                        
        return oldlevel

    ##########################################################################
    def scan(self, option='3'):
        """ 
        Check to see if run-level 5 (X11) is the default
        """
        
        if not option:
            option = '3'

        oldlevel = self.process_inittab(option, 'scan')
        if oldlevel != option :
            retval = False
            msg = 'Default run-level set to %s in /etc/inittab' % oldlevel
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
        else:
            retval = True
            msg = 'Default run-level already set to %s in /etc/inittab' % oldlevel 
        
        return retval, '', {'messages':[msg]}                        

    ##########################################################################
    def apply(self, option='3'):
        """ 
        Set default system run-level to 3
        """

        if not option:
            option = '3'

        oldlevel = self.process_inittab(option, 'apply')
        if oldlevel != option:
            msg = 'Default run-level set to %s in /etc/inittab' % option
            retval = True
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        else:
            msg = 'Default run-level already set to %s in /etc/inittab' % oldlevel 
            retval = False

        return retval, oldlevel, {'messages':[msg]}

    ##########################################################################
    def undo(self, action_record):
        """ Re-enable the ctrl-alt-del key combination."""

        if not action_record: 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        desired_level = '5'
        
        # if the first line makes it look like a 'patch' then this is an older
        # change record, manually rip through the record looking for the 'old'
        # line that looks like '-id:#:initdefault:
        # A new style change record is simply the old value for the id: line
        pat = re.compile('^-id:\d:initdefault:')
        if action_record.startswith('--- /etc/inittab.new') :
            lines = action_record.splitlines()
            for thisline in lines:
                if pat.match(thisline):
                    desired_level = thisline.split(':')[1]
        elif action_record.isdigit():        
            desired_level = action_record
            
        oldlevel = self.process_inittab(desired_level, 'apply')            

        if oldlevel != desired_level:
            retval = True 
            msg = 'Default run-level restored to %s in /etc/inittab' % desired_level
            self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        else:
            retval = False
            msg = 'Default run-level already set to %s in /etc/inittab' % desired_level
        return retval , '', {'messages':[msg]}

