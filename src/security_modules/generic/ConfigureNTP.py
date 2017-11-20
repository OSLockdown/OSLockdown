#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# This module enables the NTP service and ensures
# /etc/ntp.conf file matches what is provied in the profile.
#
# (1) Checks to see if the NTP service is enabled for boot using chkconfig.
#
# (2) Check to see if daemon is running (service <svc> status)
#
# (3) This module takes a SHA1 digest of the above file and
#     compares it to a SHA1 digest of the /etc/ntp.conf. If it 
#
#

import sha
import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.os.service
import sb_utils.file.fileperms

class ConfigureNTP:

    def __init__(self):
        self.module_name = "ConfigureNTP"

        # Config file/service details differ slightly between Solaris/Linux
        if sb_utils.os.info.is_solaris() == True:
            self.__ntpcond = '/etc/inet/ntp.conf'
            self.__pkgname = ['SUNWntpu', 'SUNWntpr']
            self.__svcname = 'ntpd'
        else:
            self.__ntpconf = '/etc/ntp.conf'
            self.__pkgname = ['ntp']
            self.__svcname = 'ntpd'
            

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


    ##########################################################################
    def checkStatus(self, optionDict={}):

        # assume true, and we'll set to false if needed
        status = True

        # Step 1: Check to see if NTP package(s) are installed.
        for pkg in self.__pkgnames:
            if sb_utils.os.software.is_installed(pkgname=pkg) == False:
                status = False
                msg = "'%s' package is not installed on the system" % self.__pkgname
                if optionDict['required'] == False:
                    self.logger.info(self.module_name, 'Not Applicable: ' + msg)
                    raise tcs_utils.ScanNotApplicable('%s %s' % 
                                              (self.module_name, msg))
                else:
                    self.logger.warning(self.module_name, 'Scan failed: ' + msg)

        # Step 2: Check to see if the NTP Service daemon is enabled.
        if sb_utils.os.service.is_enabled(svcname=self.__svcname) == False:
            status = False
            msg = "'%s' service is off. It is not configured to start "\
                  "during system startup." % self.__svcname
            self.logger.notice(self.module_name,  'Scan failed: ' + msg)
            
        # Step 3: Check to see if service is running.
        if sb_utils.os.service.status(svcname=self.__svcname) == False:
            status = False
            msg = "'%s' service is not running" % self.__svcname
            self.logger.notice(self.module_name,   'Scan failed: ' + msg)
            
        if optionDict['Required'] == True and not status:
            
            self.logger.info(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % 
                                              (self.module_name, msg))



    def checkConfigFile(self, option=None):
        # Now we go check the config file itself, looking for the 'server' lines.  
        pass
    
    def scan(self, option=None):
        pass
                    
    ##########################################################################
    def apply(self, option=None):
        

        action_record = []

        # Step 1: Check to see if NTP package is installed.
        results = sb_utils.os.software.is_installed(pkgname=self.__pkgname)
        if results == False:
            msg = "%s package is not installed on the system" % self.__pkgname
            self.logger.info(self.module_name, 'Not Applicable: ' + msg)
            return 0, ''

        # Did module receive ntp.conf text?
        if option == None or option == '':
            msg = "No ntp.conf text provided"
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg)) 

        # Capture current running status?
        results = sb_utils.os.service.status(svcname=self.__svcname)
        if results == True:
            action_record.append('RUNNING=yes\n') 
        else:
            action_record.append('RUNNING=no\n') 

        # Chkconfig status? Is it configured to be started during boot?
        results = sb_utils.os.service.is_enabled(svcname=self.__svcname)
        if results == True:
            action_record.append('CHKCONFIG=on\n') 
        else:
            sb_utils.os.service.enable(svcname=self.__svcname)
            action_record.append('CHKCONFIG=off\n') 
        

        # Replace contents of ntp.conf it doesn't match the provided content
        master_fingerprint = sha.new(option).hexdigest()
        apply_problem = False
        if self._sha1(self.__ntpconf) != master_fingerprint:
            if os.path.isfile(self.__ntpconf):
                # Capture ntp.conf contents
                try:
                    infile = open(self.__ntpconf, 'r')
                    lines = infile.readlines()
                    infile.close()
                except IOError, err:
                    msg = "Unable to read %s: %s" % (self.__ntpconf, err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                lines = "EMPTY\n"
        
            record = "NTPCONFIGFILE\n%s\n" % (''.join(lines))
            action_record.append(record)
                 

            # Copy provided content into ntp.conf
            try: 
                out_obj = open(self.__ntpconf, 'w')
                out_obj.write(option)
                out_obj.close()
                msg = "Apply Performed: %s updated." % (self.__ntpconf)
                self.logger.notice(self.module_name, msg)
            except (OSError, IOError), err: 
                apply_problem = True
                msg = "Unable to update %s: %s" % (self.__ntpconf, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)

            changes_to_make = {'owner':'root',
                               'group':'root',
                               'dacs':0444}
            ignore_results = sb_utils.file.fileperms.change_file_attributes(self.__ntpconf, changes_to_make)

        # Start the service. Stop if it is running then start it.
        results = sb_utils.os.service.status(svcname=self.__svcname)
        if results == True:
            sb_utils.os.service.stop(svcname=self.__svcname)
        sb_utils.os.service.start(svcname=self.__svcname)

        if apply_problem == True:
            return 0, ''

        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        if change_record == None :
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 0

        if change_record == "":
            msg = "Skipping Undo: Unknown change record in state file: '%s'" % change_record
            self.logger.error(self.module_name, 'Skipping undo: ' + msg)
            return 0


        #========================
        # Parse the change record
        NtpConf = []
        BeginFlag = False
        for record in change_record.split('\n'):
            if BeginFlag == True:
                NtpConf.append("%s\n" % record)
                continue

            if record == 'RUNNING=yes':   
                Running = True

            if record == 'RUNNING=no':    
                Running = False

            if record == 'CHKCONFIG=off': 
                Chkconfig = False

            if record == 'CHKCONFIG=on':  
                Chkconfig = True

            if record == 'NTPCONFIGFILE': 
                BeginFlag = True


        if Chkconfig == False:
            sb_utils.os.service.disable(svcname=self.__svcname)

        # Copy previous content into ntp.conf
        try: 
            out_obj = open(self.__ntpconf, 'w')
            out_obj.write(''.join(NtpConf))
            out_obj.close()
            msg = "Undo Performed: %s restored." % (self.__ntpconf)
            self.logger.notice(self.module_name, msg)
        except (OSError, IOError), err: 
            msg = "Unable to restore %s: %s" % (self.__ntpconf, err)
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        if Chkconfig == False:
            sb_utils.os.service.disable(svcname=self.__svcname)

        if Running == True:
            sb_utils.os.service.restart(svcname=self.__svcname)
        else:
            if  sb_utils.os.service.status(svcname=self.__svcname) == True:
                sb_utils.os.service.stop(svcname=self.__svcname)

        return 1


##############################################################################
# External (main) block provided because SB_Setup uses it
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s <NTPserver>" % sys.argv[0]
        sys.exit(1)

    if not os.path.isfile('/etc/ntp.conf-preSB_Setup'):
        try:
            shutil.copy2('/etc/ntp.conf', '/etc/ntp.conf-preSB_Setup')
            print >> sys.stdout, "Copied /etc/ntp.conf --> /etc/ntp.conf-preSB_Setup"
        except Exception, err:
            print >> sys.stderr, str(err)
            sys.exit(1)

    ConfigureIt = ConfigureNTP()
    NtpConf = "# Created by OS Lockdown Setup\nserver %s\ndriftfile /var/lib/ntp/drift\n" % str(sys.argv[1])
    (retVal, changeRecord) = ConfigureIt.apply(option=NtpConf)
    sys.exit(retVal)
    
