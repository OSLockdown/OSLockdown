#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")


from sb_utils.misc import TCSLogger
from sb_utils.misc import tcs_utils
import sb_utils.SELinux

class KernelModuleUpdate(object):
    """
    Class representing abstracted kernel parameter testing and manipulation.
    """
    
    def __init__(self, kernel_parameter, value,       \
                 module_name, pretty_param_name=None, \
                 validate_boolean=False, fail_message=None):
        
        self.module_name        = module_name
        self.__kernel_parameter = kernel_parameter
        self.__value            = int(value)
        self.__validate_bool    = validate_boolean
        self.__target_file      = '/etc/sysctl.conf'
        self.__tmp_file         = '/tmp/.sysctl.conf.tmp'
        self.__sysctl_path      = '/sbin/sysctl'
        self.__analysis_results = None
        self.logger             = TCSLogger.TCSLogger.getInstance()
        
        # Configure pretty parameter name, if not specified
        if pretty_param_name:
            self.__pretty_param_name = pretty_param_name
        else:
            self.__pretty_param_name = self.__kernel_parameter
        
        # Create failure message, if not specified
        if fail_message:
            self.__fail_message     = fail_message
        else:
            if self.__value == 0:
                self.__fail_message = "%s is enabled" %  \
                                            self.__pretty_param_name
            else:
                self.__fail_message = "%s is disabled" % \
                                            self.__pretty_param_name

    ##########################################################################
    def scan(self, option=None):
        """
        Tests if proper kernel parameters are set.
        """
        
        if option == None:
            option = self.__value
        else:
            option = int(option)
        
        self.logger.log_debug(self.module_name, 'Initiating scan.')
        
        cmd = '%s -n %s' % (self.__sysctl_path, self.__kernel_parameter)
        self.logger.log_notice(self.module_name, 'Executing: ' + cmd)
        output_tuple = tcs_utils.tcs_run_cmd(cmd, True)
        
        # Check the current state kernel (from memory)
        if output_tuple[0] == 0:
            value = output_tuple[1].rstrip('\n')
            self.__analysis_results = value
            
            # Validate command output (will do more elegant multivalue checking
            # in the future)
            if (self.__validate_bool and (int(value) != 0 and int(value) != 1)):
                # Only 1 and 0 are valid values
                msg = "Unexpected return value (%s)" % value
                self.logger.log_err(self.module_name, 'Scan Error: ' + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
            else:
                # Failed scan: invalid memory parameters
                if int(value) != option:
                    self.logger.log_info(self.module_name, 'Scan Failed: ' + \
                                         self.__fail_message)
                    return 'Fail', self.__fail_message
        else:
            # The command failed to run properly so raise an exception
            msg = "Cannot determine state of the %s kernel parameter." % \
                  self.__pretty_param_name
            self.logger.log_err(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        if os.path.exists(self.__target_file):
            # Check the file configuration
            conf_file = open(self.__target_file, 'r')
            regex = re.compile("\s*%s\s*=\s*(\d+)\s*"% self.__kernel_parameter)
            invalid_value_found = False
            missing_entry       = True
      
            for line in conf_file:
                match = regex.match(line)
                if match:
                    missing_entry = False
                    if int(match.group(1)) != option:
                        invalid_value_found = True
                        break
            
            conf_file.close()
        
        
        else:
            # For missing configuration file
            msg = "Missing %s configuration file." % self.__target_file
            self.logger.log_info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        # Fail if entry is not in configuration
        if missing_entry:
            msg = "Parameter %s is not explicitly set correctly in %s" % \
                  (self.__pretty_param_name, self.__target_file)
            self.logger.log_info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        # Exit if found invalid entry
        if invalid_value_found:
            msg = "Parameter %s not set correctly in %s" % \
                  (self.__pretty_param_name, self.__target_file)
            self.logger.log_info(self.module_name, 'Scan Failed: ' + msg)
            return 'Fail', msg
        
        return 'Pass', ''
        
    
    ##########################################################################
    def apply(self, option=None):
        """
        Set kernel parameter to predefined setting
        """

        if not option:
            option = self.__value
        else:
            option = int(option)
        
        self.logger.log_debug(self.module_name, 'Initiating apply change.')
        result = self.scan(option)[0]
        if result == 'Pass':
            return 0, str(option)
        
        # Protect file
        tcs_utils.protect_file(self.__target_file)

        # make sure we have the original values from the system before we
        # start modifying them, so we can save them for the change record
        # (note: we don't bother checking to see whether the command
        # succeeded - it won't fail now if it didn't fail in the call
        # to scan() above)
        
        # NOTE: In order for undo to succeed, the parameter value in memory has
        #       to be the same as the parameter value stored in /etc/sysctl.conf
        #       This might be something TODO in the future.

        if not self.__analysis_results:
            cmd = '%s -n %s' % (self.__sysctl_path, self.__kernel_parameter)
            output_tuple = tcs_utils.tcs_run_cmd(cmd)
            self.__analysis_results = output_tuple[1].strip()

        # set the current system value
        cmd = '%s -w %s=%s' % (self.__sysctl_path, self.__kernel_parameter, \
                              option)

        self.logger.log_notice(self.module_name, 'Executing: ' + cmd)
        output_tuple = tcs_utils.tcs_run_cmd(cmd)
        if output_tuple[0] != 0:
            msg = "Unexpected return value (%s): %s" % (output_tuple[0], output_tuple[2])
            self.logger.log_info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        #
        # Modify the sysctl.conf file so the parameter is set on reboot
        #
        
        if os.access(self.__target_file, os.R_OK):
            origfile = open(self.__target_file, 'r')
            
        
        # Create /etc/sysctl.conf file if doesn't exist
        # NOTE: we do not undo this action
        elif not os.path.exists(self.__target_file):
            # Create the configuration file
            from sb_utils.file import TemplateStore
            
            store = TemplateStore.TemplateStore()
            if store.has_key(self.__target_file):
                store.write_to_path(self.__target_file)
            else:
                msg = "Error creating file (" + self.__target_file + ")."
                self.logger.log_err(self.module_name, 'Apply Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))            
            
            # Clean up after ourselves
            del store
            del TemplateStore
            
            origfile = open(self.__target_file, 'r')

        else:
            msg = "Cannot open source file (" + self.__target_file + ")."
            self.logger.log_err(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        try:
            workfile = open(self.__tmp_file, 'w')
        
        except OSError:
            msg = "Unable to create temporary file (" + self.__tmp_file + ")."
            self.logger.log_err(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        found = False
        regex = re.compile('\s*%s\s*=\s*\d+' % self.__kernel_parameter)
        correct_line = '    %s = %s\n' % (self.__kernel_parameter, option)
        old_match = ''
        
        for line in origfile:
            # NOTE: we ignore commented out lines
            if (not found and regex.match(line)):
                old_match = line
                workfile.write(correct_line)
                found = True

            # Strip out all other duplicate lines
            elif regex.match(line):
                pass

            else:
                workfile.write(line)
        
        # Stick the lines in if we didn't find them
        if not found:
            workfile.write(correct_line)

        origfile.close()
        workfile.close()
        
        # Ensure we replicate permissions off of original file (if exists)
        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)

            os.unlink(self.__tmp_file)
        
        except Exception, err:
            msg = "Unexpected error replacing original file (" + str(err) + ")."
            self.logger.log_err(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        # Finally, we want to save the original values for the action record.
        msg = 'Network parameter %s set to %s.' % (self.__kernel_parameter, \
                                                    option)
        self.logger.log_notice(self.module_name, 'Apply Performed: ' + msg)
        
        return 1, tcs_utils.packObjectIntoString([self.__analysis_results, \
                                                  correct_line,            \
                                                  old_match])
    
    
    ##########################################################################
    def undo(self, action_record=None):
        """Undo previous change application."""
        
        self.logger.log_debug(self.module_name, 'Initiating undo change.')
        
        # NOTE: not running analyze system in undo due to the ability to pass
        #       in custom parameters
        
        #result = self.scan()[0]
        #if result == 'Fail':
        #    return 0

        # Unpack action_record object
        action_record = tcs_utils.extractFromString(action_record)
        # set the current system value
        cmd = '%s -w %s=%s' % (self.__sysctl_path, self.__kernel_parameter, \
                               action_record[0])
        output_tuple = tcs_utils.tcs_run_cmd(cmd)
        if output_tuple[0] != 0:
            msg = "Unexpected return value (%s)" % output_tuple[0]
            self.logger.log_info(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        #
        # Modify the sysctl.conf file so the parameter is set on reboot
        #
        
        if os.access(self.__target_file, os.R_OK):
            origfile = open(self.__target_file, 'r')
        
        else:
            msg = "Cannot open source file (" + self.__target_file + ")."
            self.logger.log_err(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        try:
            workfile = open(self.__tmp_file, 'w')
        
        except OSError:
            msg = "Unable to create temporary file (" + self.__tmp_file + ")."
            self.logger.log_err(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        found = False
        
        # Search for corrected line
        regex = re.compile('^\s*%s\s*$' % action_record[1])
        
        for line in origfile:
            # NOTE: we ignore commented out lines
            if (not found and regex.match(line)):
                workfile.write(action_record[2])
                found = True

            # Strip out all other duplicate lines
            elif regex.match(line):
                pass

            else:
                workfile.write(line)

        origfile.close()
        workfile.close()

        # Ensure we replicate permissions off of original file (if exists)
        try:
            shutil.copymode(self.__target_file, self.__tmp_file)
            shutil.copy2(self.__tmp_file, self.__target_file)
            sb_utils.SELinux.restoreSecurityContext(self.__target_file)
            os.unlink(self.__tmp_file)
        
        except Exception, err:
            msg = "Unexpected error replacing original file (" + str(err) + ")."
            self.logger.log_err(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        msg = 'Network parameter %s has been reset to pre-apply memory state.' \
              % self.__kernel_parameter
        self.logger.log_notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

if __name__ == '__main__':
    # Test Variables used, replace later with command line arguments
    PARAM                = 'net.ipv4.conf.all.rp_filter'
    VALUE                = 1
    MODULE_NAME          = 'RPFilter'
    PARAM_NAME           = 'Reverse Path Source Validation'
    VALIDATE_BOOL        = True
    
    TESTOBJECT = KernelModuleUpdate(PARAM, VALUE, MODULE_NAME, PARAM_NAME, \
                                    VALIDATE_BOOL)
    
    print "Analysis result:            " + str(TESTOBJECT.scan())
    apply_str = TESTOBJECT.apply()
    print "Apply result:               " + str(apply_str)
    print "Post-apply analysis result: " + str(TESTOBJECT.scan())
    print "Undo result:                " + str(TESTOBJECT.undo(apply_str[1]))
    print "Post-undo analysis result:  " + str(TESTOBJECT.scan())

