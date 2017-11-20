#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable CUPS Printer Config Daemon
#
# RH4/5 and F10/11 use hal-cups-utils package and the cups-config-daemon service
#  - To disable just turn the service off
# RH6 and F12+ use system-config-printers-udev and udev rules in /lib/udev/rules.d and /etc/udev/rules.d
#  - To disable write a blank file in /etc/udev/rules.d with name ##-printers.rules, where ## is higher than any
#    other file ending in 'printers.rules' in the /etc/udev.rules or /lib/udev.rules directories.
#
#
##############################################################################

import sys
import os

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger


import sb_utils.os.config
import sb_utils.os.info
import sb_utils.os.software

try:
    import Enable_Disable_Any_Service
except ImportError:
    raise



class DisablePrinterConfig_halCupsUtils:

    def __init__(self, module_name):
        self.module_name = module_name
    
    def scan(self, option):
        return Enable_Disable_Any_Service.scan(self.module_name, enable=False)    
    
    def apply(self, option):
        return Enable_Disable_Any_Service.apply(self.module_name, enable=False)    
    
    def undo(self, change_record):
        return Enable_Disable_Any_Service.undo(self.module_name, change_record=change_record)    

class DisablePrinterConfig_udev:
    """
    The default rules are located in '/lib/udev/rules.d/70-printers.rules', but are subject to override
    by '/etc/udev/rules.d/70-printers.rules'.  To override we need to ensure that the contents of the /etc/
    version are empty, or the file has nothing but comments and blank lines.
    We'll pass if neither file exists, or we are overridden.
    """
    def __init__(self, module_name):
        
        self.module_name = module_name
        self.libFile = "/lib/udev/rules.d/70-printers.rules"
        self.etcFile = "/etc/udev/rules.d/70-printers.rules"
        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        self.etcLines = []
        self.libLines = []
        
    def _readFile(self, fileName):
        lines = None
        isEmpty = True
        if not os.path.exists(fileName):
            self.logger.info(self.module_name, "'%s' does not exist" % fileName)
        else:
            try :
                lines = open(fileName).readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        isEmpty = False
                        break
            except Exception, e:
                print >> sys.stderr,str(e)
                self.logger.warning(self.module_name, "Unable to read '%s'" % fileName)
        
#        if lines:
#            print "%s -> %d -> %s" % (fileName, len(lines), isEmpty)
#        else :
#            print "%s -> empty -> %s" % (fileName, isEmpty)
            
        return lines, isEmpty
        
    
    def scan(self, option):
        """
        If we see etcFile non-empty/non-commented we fail
        If etcFile doesn't exist and libFile is non-empty/non-commented we fail
        Otherwise we pass
        """
        retval = True
        messages = {'messages':[]}
        
        self.etcLines, self.etcLinesEmpty = self._readFile(self.etcFile)
        self.libLines, self.libLinesEmpty = self._readFile(self.libFile)
                
        if not self.etcLines and not self.libLines:
            msg = "Neither '%s' or '%s' exists" % (self.etcFile, self.libFile)
        elif self.etcLines != None and self.etcLinesEmpty :
            msg = "'%s' file exists, and is either blank or contains empty lines and comments only" % self.etcFile
        elif self.etcLines != None and not self.etcLinesEmpty :
            msg = "'%s' file exists, and contains line that are uncommented or not blank" % self.etcFile
            retval = False
        elif self.libLines != None and self.libLinesEmpty :
            msg = "'%s' file exists, and is either blank or contains empty lines and comments only" % self.libFile
        elif self.libLines and not self.libLinesEmpty :
            msg = "'%s' file exists, and contains line that are uncommented or not blank" % self.libFile
            retval = False
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        return retval, msg, messages
    
    def apply(self, option):
        retval , reason, messages = self.scan(option)
        if retval == True:
            return False, reason, messages

        retval = True
        changerec = "commented"
        messages = {'messages':[]}

        if self.etcLines:
            etcFile = open(self.etcFile,"w")
            for line in self.etcLines:
                if line and not line.strip().startswith('#'):
                    etcFile.write("#SB_COMMENT#%s" % line)
                else:
                    etcFile.write(line)
            etcFile.close()
            changerec = "commented"
            msg = "Rewrote '%s' with all lines commented or empty to override '%s'" % (self.etcFile, self.libFile)
            messages['messages'].append(msg)
        else:
            open(self.etcFile,"w").write("")
            msg = "Created empty file '%s' to override '%s'" % (self.etcFile, self.libFile)
            messages['messages'].append(msg)
            changerec = "blank"
        
        self.logger.info(self.module_name, msg)
            
#        print retval, changerec, messages
        return retval, changerec, messages    
    
    def undo(self, change_record):
        
        if change_record == "commented":
            self.etcLines, self.etcLinesEmpty = self._readFile(self.etcFile)
            etcFile = open(self.etcFile,"w")
            for line in self.etcLines:
                if line.startswith('#SB_COMMENT#'):
                    etcFile.write(line[12:])
                else:
                    etcFile.write(line)
            etcFile.close()
            msg = "Rewrote '%s' removing lines that were commented out in previous 'apply'" % (self.etcFile)
        
        else:
            try:
                os.unlink(self.etcFile)
                msg = "Removed empty '%s' " % (self.etcFile)
            except OSError,e:
                msg = "Unable to remove '%s' : %s" % (self.etcFile, str(e))
                self.logger.error(self.module_name, msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        self.logger.info(self.module_name, msg)
        
        return True , msg, {}  

class DisablePrinterConfig_cupsAutoConfig:
    def __init__(self, module_name):
        self.module_name = module_name
        self.__config_file = "/etc/cups-autoconfig.conf"

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()
    
    def scan(self, option):
        messages = {'messages':[]}
        
        msg = "Looking to see if 'ConfigureNewPrinters'  is to "\
              "'no' in %s " % (self.__config_file)
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)
    
        paramlist = sb_utils.os.config.get_list(configfile=self.__config_file,
                                                delim='=') 

        if not paramlist.has_key('ConfigureNewPrinters'):
            msg = "'ConfigureNewPrinters' option is NOT set in %s" % (self.__config_file)
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            messages['messages'].append(msg)
            return False, "Printer auto-configuration is not disabled", messages

        if paramlist['ConfigureNewPrinters'] != 'no':
            msg = "'ConfigureNewPrinters' option is not set to 'no' in  %s" % (self.__config_file)
            messages['messages'].append(msg)
            self.logger.info(self.module_name, 'Scan Failed: ' + msg)
            return False, "Printer auto-configuration is not disabled", messages

        return True, "Printer auto-configuration is disabled", messages

    def apply(self, option):
        results, reason, messages = self.scan(option)
        if results == True:
            return False, reason, messages
        messages = {'messages':[]}
            
        results = sb_utils.os.config.setparam(configfile=self.__config_file,
                                                param='ConfigureNewPrinters',
                                                value='no', delim='=')
        if results == False:
            msg = "Unable to set 'ConfigureNewPrinters' in %s" % (self.__config_file)
            self.logger.info(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        else:
            action_record = results
    
        msg = "Set 'ConfigureNewPrinters' in %s" % (self.__config_file)
        messages['messages'].append(msg)
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
    
        msg = "'ConfigureNewPrinters' set to 'no'"
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
        return True, action_record, messages

    def undo(self, change_record):
        messages = {'messages':[]}
        if change_record not in ['no', 'yes']:
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            return False, msg, {}
             
        results = sb_utils.os.config.setparam(configfile=self.__config_file,
                                                param='ConfigureNewPrinters',
                                                value=change_record, delim='=')
        if results == False:
            msg = "Unable to set 'ConfigureNewPrinters' to '%s' " % change_record
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
        msg = "'ConfigureNewPrinters' set to '%s' " % change_record
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        return True, msg, {}
    
class DisablePrinterConfig:

    def __init__(self):

        self.module_name = 'DisablePrinterConfig'
        self.uses_Udev = False
        self.subclass = None
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.software.is_installed(pkgname='hal-cups-utils'):            
            self.subclass = DisablePrinterConfig_halCupsUtils(self.module_name)
        elif sb_utils.os.software.is_installed(pkgname='system-config-printer-udev'):
            self.subclass = DisablePrinterConfig_udev(self.module_name)
        elif sb_utils.os.software.is_installed(pkgname='udev-configure-printer'):
            self.subclass = DisablePrinterConfig_udev(self.module_name)
        elif sb_utils.os.software.is_installed(pkgname='cups-autoconfig'):
            self.subclass = DisablePrinterConfig_cupsAutoConfig(self.module_name)
        else:
            msg = "Unable to identify any loaded printer autoconfiguration package"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable("%s %s" % (self.module_name, msg))

         

    ##########################################################################
    def scan(self, option=None):

        return self.subclass.scan(option)


    ##########################################################################
    def apply(self, option=None):

        return self.subclass.apply(option)
    
    
    ##########################################################################
    def undo(self, change_record=None):

        return self.subclass.undo(change_record)



