#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

import os
import sys

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

import sb_utils.os.software
import sb_utils.os.service
import sb_utils.os.info
import sb_utils.gdm
import sb_utils.file.iniHandler

##############################################################################
class CreatePreLoginGUIBanner:

    def __init__(self):
        self.module_name = "CreatePreLoginGUIBanner"
        self.logger = TCSLogger.TCSLogger.getInstance() 

        if sb_utils.os.info.is_solaris():
            self.gdm_pkgname = 'SUNWgnome-display-mgr-root'
            self.gdm_servicename = 'gdm2-login'
            self.dt_servicename = 'cde-login'
            self.gdm_custom_conf = '/etc/X11/gdm/gdm.conf'
            self.gdm_settings = [ ['daemon',  'Greeter',        '/usr/bin/gdmlogin' ]]
        elif self.is_rh4():
            self.gdm_pkgname = 'gdm'
            self.gdm_servicename = ''
            self.gdm_custom_conf = '/etc/X11/gdm/gdm.conf'
            self.gdm_settings = [ ['daemon',  'Greeter',        '/usr/bin/gdmlogin' ]]
        elif sb_utils.os.info.is_LikeSUSE() and sb_utils.os.info.getOSMajorVersion() == '10':  # SUSE/OpenSUSE V10 does it this way, V11 is like fedora
            self.gdm_pkgname = 'gdm'
            self.gdm_servicename = ''
            if os.path.exists('/etc/gdm'):
                self.gdm_custom_conf = '/etc/gdm/custom.conf'
                self.gdm_settings = [ ['daemon',  'Greeter',        '/usr/lib/gdm/gdmlogin' ] ,
                              ['greeter', 'DefaultWelcome', 'false' ]]
            elif os.path.exists('/etc/opt/gnome/gdm'):
                self.gdm_custom_conf = '/etc/opt/gnome/gdm/gdm.conf'
                self.gdm_settings = [ ['daemon',  'Greeter',        '/opt/gnome/lib/gdm/gdmlogin' ] ,
                              ['greeter', 'DefaultWelcome', 'false' ]]

        else:
            self.gdm_pkgname = 'gdm'
            self.gdm_servicename = ''
            self.gdm_custom_conf = '/etc/gdm/custom.conf'
            self.gdm_settings = [ ['daemon',  'Greeter',        '/usr/libexec/gdmlogin' ] ,
                              ['greeter', 'DefaultWelcome', 'false' ]]

        self.kdm_pkgname = 'kdebase'
        self.kdm_custom_conf = '/usr/share/config/kdm/kdmrc'

        self.kdm_settings = [ ['X-*-Greeter', 'UseTheme',       'false' ] ]
        
    ##########################################################################

    def is_rh4(self):
        """ Quickly see if we are a RH4 *based* box or anything else"""
        retval = False
        try:
            if sb_utils.os.info.is_LikeRedHat() and sb_utils.os.info.getOSMajorVersion() == '4':
                retval = True
        except Exception:
            pass
        return retval

    ##########################################################################


    def uses_simple_greeter(self):
        """
        If we're a Fedora, or like RH6, then return true, otherwise false
        """
        retval = False
        if sb_utils.os.info.is_fedora(): 
            retval = True
        elif sb_utils.os.info.is_LikeRedHat() and sb_utils.os.info.getOSMajorVersion() == '6' :
            retval = True
        elif sb_utils.os.info.is_LikeSUSE() and sb_utils.os.info.getOSMajorVersion() == '11' :
            retval =  True
        return retval


    ########################################################################## 
    # For FEDORA linux
    def gdm_banner_simple_greeter(self, action, option):
    
        status = 'Pass'
        changes = []
        messages = {'messages':[]}
        
        if action == 'scan':
            results = sb_utils.gdm.get('/apps/gdm/simple-greeter/banner_message_enable')
            if results != 'true':
                msg = "GDM banner_message_enable not set to 'true'"
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append(msg)
                status = 'Fail'
            else:
                msg = "GDM banner_message_enable set to 'true'"
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                
            results = sb_utils.gdm.get('/apps/gdm/simple-greeter/banner_message_text')
            if results != option:
                msg = "GDM banner_message_text not set to correct text"
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append(msg)
                status = 'Fail'
            else:
                msg = "GDM banner_message_text set to correct text"
                self.logger.info(self.module_name, 'Scan : ' + msg)

        elif action == 'apply':
            msgState = sb_utils.gdm.get('/apps/gdm/simple-greeter/banner_message_enable') 
            if msgState == None:
                msgState = 'unset'

            msgText  = sb_utils.gdm.get('/apps/gdm/simple-greeter/banner_message_text')
            if msgText == None:
                msgText = 'unset'

            if msgState == "true" and msgText == option:
                msg = "No changes required: GDM banner status is correct"
                status = 'Fail'
            else:
                changes = "/apps/gdm/simple-greeter/banner_message_enable|%s\n" \
                          "/apps/gdm/simple-greeter/banner_message_text|%s" % \
                          (msgState, msgText)

                msgState = sb_utils.gdm.set(paramKey='/apps/gdm/simple-greeter/banner_message_enable',
                                            paramValue='true', dataType='bool') 
                if msgState == False:
                    msg = "Unable to set /apps/gdm/simple-greeter/banner_message_enable"
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))   

                msgText = sb_utils.gdm.set(paramKey='/apps/gdm/simple-greeter/banner_message_text',
                                            paramValue=option, dataType='string') 
                
                if msgText == False:
                    msg = "Unable to set /apps/gdm/simple-greeter/banner_message_text"
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))   

        elif action == 'undo':
            for gdmParam in option.split('\n'):
                if not gdmParam:
                    continue
                
                try:
                    (paramKey, paramValue) = gdmParam.split('|')
                except Exception, err:
                    self.logger.debug(self.module_name, str(err))
                    continue

                if paramValue == 'unset':
                    results = sb_utils.gdm.unset(paramKey=paramKey)
                    continue

                dType = ''
                if paramKey.endswith('message_text'):
                    dType = 'string'
                else:
                    dType = 'bool'

                results = sb_utils.gdm.set(paramKey = paramKey,
                                         paramValue = paramValue, 
                                           dataType = dType )
        return status, changes, messages
    ########################################################################## 
    # For all non-fedora Linuxes
    def gdm_banner(self, action, changes_to_make):
            
        status, changes, messages = self.conf_settings("GDM", action, self.gdm_custom_conf, changes_to_make)
        if action in ["apply", "undo"] and changes != {} :
            restarted = False
            restart_cmd = None
            for cmd in ['/usr/sbin/gdm-safe-restart', '/usr/sbin/gdm-restart', 
                        '/opt/gnome/sbin/gdm-safe-restart', '/opt/gnome/sbin/gdm-restart' ]:
                if os.path.exists(cmd):
                  restart_cmd = cmd
                  break

            if os.path.exists("/var/gdm/.gdmfifo"):
                try:
                    fifofile = open("/var/gdm/.gdmfifo", "w")
                    fifofile.write("HUP_ALL_GREETERS\nSOFT_RESTART\n")
                    fifofile.close()
                    restarted = True
                except Exception, err:
                    msg = "Failed to soft-restart GDM, could not write to /var/gdm/.gdmfifo.  GDM must restart to pick up changes."
                    messages['messages'].append(msg)
                    self.logger.error(self.module_name, msg)
            elif restart_cmd :
                results = tcs_utils.tcs_run_cmd(restart_cmd, True)
                if results[0] == 0 and results[1] != "Not supported":
                    restarted = True 

            if not restarted :
                msg = "Unable to soft-restart GDM, either fifo not found or the gdm-restart/gdm-safe-restart commands not effective.  GDM must restart to pick up changes."
                messages['messages'].append(msg)
                self.logger.warn(self.module_name, msg)
             
        return status, changes, messages

    ########################################################################## 
    def kdm_banner(self, action, changes_to_make):
        
        status = "N/A"
        changes = []
        messages = {'messages':[]}
        
        status, changes, messages = self.conf_settings("KDM", action, self.kdm_custom_conf, changes_to_make)
                
        return status, changes, messages

    ########################################################################## 
    def conf_settings(self, flavor, action, cfg_filename, changes_to_make):
        status = "N/A"
        changes = []
        messages = {'messages':[]}
        
        status = "Pass"
        if os.path.exists(cfg_filename):
            cfg_file = sb_utils.file.iniHandler.iniHandler()
            cfg_file.read_file(cfg_filename)
            for entry in changes_to_make:
                section, field, required_value = entry 
                file_value = cfg_file.get_section_value([section, field])
               
                if action == "scan" :
                    if required_value != file_value:
                        msg = '%s - [%s]%s - did not find required text' % ( flavor, section, field)
                        messages['messages'].append(msg)
                        self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                        status = "Fail"
                    else:
                        msg = '%s - [%s]%s - found required text' % (flavor, section, field)
                        messages['messages'].append(msg)
                        self.logger.info(self.module_name, "Scan : %s" % msg)
                elif action == "apply" :
                    if required_value != file_value:
                        this_change = cfg_file.set_section_value([section, field, required_value])
                        if this_change != None:
                            changes.append(this_change)
                        msg = '%s - [%s]%s - set required text' % ( flavor, section, field)
                        messages['messages'].append(msg)
                        self.logger.notice(self.module_name, "Apply: %s" % msg)
                    else:
                        msg = '%s - [%s]%s - required text already present' % ( flavor, section, field)
                        messages['messages'].append(msg)
                        self.logger.info(self.module_name, "Apply: %s" % msg)
                elif action == "undo":
                    if required_value != file_value: 
                        this_change = cfg_file.set_section_value([section, field, required_value])
                        if this_change != None:
                            changes.append(this_change)
                        msg = '%s - [%s]%s - restored original text' % ( flavor, section, field)
                        messages['messages'].append(msg)
                        self.logger.notice(self.module_name, "Undo: %s" % msg)
                    else:
                        msg = '%s - [%s]%s - required text already present' % ( flavor, section, field)
                        messages['messages'].append(msg)
                        self.logger.info(self.module_name, "Undo: %s" % msg)
        
            if action in [ "apply", "undo" ] and changes != {} :
                cfg_file.write_file(cfg_filename)
           
        return status, changes, messages

           
    ########################################################################## 
    def scan(self, optionDict=None):
         
        retval = True
        option = optionDict['preLoginBanner']
        
        messages = {'messages':[]}
        
        # bail if neither of GDM or KDM is installed
        gdm_installed = sb_utils.os.software.is_installed(pkgname = self.gdm_pkgname)
        kdm_installed = sb_utils.os.software.is_installed(pkgname = self.kdm_pkgname)
        
        if sb_utils.os.info.is_solaris() and sb_utils.os.service.is_enabled(self.dt_servicename) == True:
            self.logger.info(self.module_name,"Scan: Solaris %s is is enabled, but is not supported" % self.gdm_servicename)
        
        if not gdm_installed and not kdm_installed:
            raise tcs_utils.ScanNotApplicable("GDM and KDM display managers are not installed, nothing to do.")
             
        # start with GDM
        gdm_prelogin_status = "N/A"        
        gdm_prelogin_changes = []
        gdm_prelogin_messages = {'messages':[]}
        if gdm_installed:
            if self.uses_simple_greeter():
                prelogin_text = option.strip()
                gdm_prelogin_status, gdm_prelogin_changes, gdm_prelogin_messages = self.gdm_banner_simple_greeter("scan", prelogin_text)            
            else:
                # we need to process the rawtext we're given into a line with the newlines escaped...
                prelogin_text = option.strip().replace('\n', r'\\n')
                self.gdm_settings.append(['greeter', 'Welcome', prelogin_text])
                self.gdm_settings.append(['greeter', 'RemoteWelcome', prelogin_text])
                gdm_prelogin_status, gdm_prelogin_changes, gdm_prelogin_messages = self.gdm_banner("scan", self.gdm_settings)        
            
            messages.update(gdm_prelogin_messages)
                              
            if gdm_prelogin_status == 'Fail' :
                msg = "GDM is not setup for displaying a pre-login notification message"
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append(msg)
                retval = False     
        else:
            msg = "Package %s not installed, skipping 'SCAN' actions for GDM prelogin banner" % (self.gdm_pkgname)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, msg)        
        
        # then to KDM
        kdm_prelogin_status = "N/A"        
        kdm_prelogin_changes = []
        kdm_prelogin_messages = {'messages':[]}

        if kdm_installed:
            # we need to process the rawtext we're given into a line with the newlines escaped...
            prelogin_text = option.replace('\n', r'\n')
            self.kdm_settings.append(['X-*-Greeter', 'GreetString', prelogin_text])
        
            kdm_prelogin_status, kdm_prelogin_changes, kdm_prelogin_messages = self.kdm_banner("scan", self.kdm_settings)        
            messages.update(kdm_prelogin_messages)
                              
            if kdm_prelogin_status == 'Fail' :
                msg = "KDM is not setup for displaying a pre-login notification message"
                self.logger.info(self.module_name, 'Scan Failed: ' + msg)
                messages['messages'].append(msg)
                retval = False
        else:
            msg = "Package %s not installed, skipping 'SCAN' actions for KDM prelogin banner" % (self.kdm_pkgname)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, msg)        
        
        return retval, '', messages


    ########################################################################## 
    def apply(self, optionDict=None):
        """
        Change record line is: <section>|<option>|<value>
        """
    
        retval = True
        option = optionDict['preLoginBanner']
        messages = {'messages':[]}
    
        # bail if neither of GDM or KDM is installed
        
        gdm_installed = sb_utils.os.software.is_installed(pkgname = self.gdm_pkgname)
        kdm_installed = sb_utils.os.software.is_installed(pkgname = self.kdm_pkgname )
        if sb_utils.os.info.is_solaris() and sb_utils.os.service.is_enabled(self.dt_servicename) == True:
            self.logger.info(self.module_name,"Scan: Solaris %s is is enabled, but is not supported" % self.gdm_servicename)
        
        if not gdm_installed and not kdm_installed:
            raise tcs_utils.ScanNotApplicable("GDM and KDM display managers are not installed, nothing to do.")
        
        # start with GDM
        gdm_prelogin_status = "N/A"        
        gdm_prelogin_changes = []
        gdm_prelogin_messages = {'messages':[]}
        if gdm_installed:
            if self.uses_simple_greeter():
                prelogin_text = option.strip()
                gdm_prelogin_status, gdm_prelogin_changes, gdm_prelogin_messages = self.gdm_banner_simple_greeter("apply", prelogin_text)
            else:              
                # we need to process the rawtext we're given into a line with the newlines escaped...
                prelogin_text = option.strip().replace('\n', r'\\n')
                self.gdm_settings.append(['greeter', 'Welcome', prelogin_text])
                self.gdm_settings.append(['greeter', 'RemoteWelcome', prelogin_text])
                gdm_prelogin_status, gdm_prelogin_changes, gdm_prelogin_messages = self.gdm_banner("apply", self.gdm_settings)        

            messages.update(gdm_prelogin_messages)
        else:
            msg = "Package %s not installed, skipping 'APPLY' actions for GDM prelogin banner" % (self.gdm_pkgname)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, msg)        
                  
            if gdm_prelogin_status == 'Fail' :
                msg = "GDM is not setup for displaying a pre-login notification message"
                self.logger.info(self.module_name, 'Apply Failed: ' + msg)
                messages['messages'].append(msg)
                retval = False
                
        # then to KDM
        kdm_prelogin_status = "N/A"        
        kdm_prelogin_changes = []
        kdm_prelogin_messages = {'messages':[]}
        if kdm_installed:

            # we need to process the rawtext we're given into a line with the newlines escaped...
            prelogin_text = option.replace('\n', r'\n')
            self.kdm_settings.append(['X-*-Greeter', 'GreetString', prelogin_text])
            
            kdm_prelogin_status, kdm_prelogin_changes, kdm_prelogin_messages = self.kdm_banner("apply", self.kdm_settings)        
            messages.update(kdm_prelogin_messages)
                              
            if kdm_prelogin_status == 'Fail' :
                msg = "kdm is not setup for displaying a pre-login notification message"
                self.logger.info(self.module_name, 'Apply Failed: ' + msg)
                messages['messages'].append(msg)
                retval = False
        else:
            msg = "Package %s not installed, skipping 'APPLY' actions for KDM prelogin banner" % (self.kdm_pkgname)
            messages['messages'].append(msg)
            self.logger.notice(self.module_name, msg)        
                 
        change_record = {}
        if gdm_prelogin_changes != [] :
            change_record['gdm'] = gdm_prelogin_changes
        if kdm_prelogin_changes != [] :
            change_record['kdm'] = kdm_prelogin_changes
            
        if change_record != {}:
            retval = True
        else :
            retval = False
            
        return retval, str(change_record), messages
        
    ########################################################################## 
    def undo(self, change_record=None):
        """Reverse settings in /etc/php.ini"""

        retval = True 
        # convert back from string to dictionary
        change_record = tcs_utils.string_to_dictionary(change_record)
        messages = {'messages':[]}
        gdm_prelogin_status = "N/A"
        kdm_prelogin_status = "N/A"
        
        if change_record.has_key('gdm'):
            if self.uses_simple_greeter():
                gdm_prelogin_status, gdm_prelogin_changes, gdm_prelogin_messages = self.gdm_banner_simple_greeter("undo", change_record['gdm'])
            else:
                gdm_prelogin_status, gdm_prelogin_changes, gdm_prelogin_messages = self.gdm_banner("undo", change_record['gdm'])
            messages.update(gdm_prelogin_messages)
        if change_record.has_key('kdm'):
            kdm_prelogin_status, kdm_prelogin_changes, kdm_prelogin_messages = self.kdm_banner("undo", change_record['kdm'])
            messages.update(kdm_prelogin_messages)

        if gdm_prelogin_status == 'Fail' or kdm_prelogin_status == 'Fail':
            retval = False
        return retval, '', {'messages':[]}
if __name__ == '__main__':
	test = CreatePreLoginGUIBanner()
	test.scan('This is a test')
