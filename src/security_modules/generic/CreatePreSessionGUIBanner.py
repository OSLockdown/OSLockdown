#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
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
import sb_utils.file.fileperms

##############################################################################
class CreatePreSessionGUIBanner:

    def __init__(self):
        self.module_name = "CreatePreSessionGUIBanner"
        self.logger = TCSLogger.TCSLogger.getInstance() 

        self.banner_filename = "/etc/oslockdown_gui_banner"

        # GDM/KDM settings
        if sb_utils.os.info.is_solaris():
            self.script_conf_file = "/etc/X11/gdm/PreSession/Default"
            self.script_file      = "/etc/X11/gdm/SB_BannerDisplay"
        elif self.is_rh4():
            self.script_conf_file = "/etc/X11/xdm/Xsession"
            self.script_file =      "/etc/X11/xdm/SB_BannerDisplay"
        else:
            self.script_conf_file = "/etc/X11/xinit/Xsession"
            self.script_file =      "/etc/X11/xinit/SB_BannerDisplay"

        self.invocation = ". %s # Inserted by OS Lockdown to display banner" % self.script_file

    # Solaris needs a slightly different banner script for the login text, due to using strict borne shell vice bash by default
        if sb_utils.os.info.is_solaris():
            self.banner_script = """#!/bin/sh 
BANNERFILE="BANNERFILEVAR"
BANNERTYPE="BANNERTYPEVAR"
ZENITY_EXISTS=0
KDIALOG_EXISTS=0

LOGGER=""
for LOG_CANDIDATE in /usr/sbin/logger /sbin/logger /usr/bin/logger /bin/logger ; 
do
  if [ -x ${LOG_CANDIDATE} ] ; then
     LOGGER=${LOG_CANDIDATE}
     break
  fi
done

if [ -x /usr/bin/zenity ] ; then
  ZENITY_EXISTS=1
fi

if [ -x /usr/bin/kdialog ] ; then 
  KDIALOG_EXISTS=1
fi
if [ -f ${BANNERFILE} ] ; then
  BANNERTEXT=`cat ${BANNERFILE}`
  if [ ${ZENITY_EXISTS} ] ; then
    if [ ${BANNERTYPE} = "REQUIRE_CONSENT" ] ; then
      /usr/bin/zenity --title="Consent Banner" --question --text="${BANNERTEXT}"
      if [ $? -eq 1 ] ; then
        if [ -x ${LOGGER} ] ; then
	  ${LOGGER} -p auth.notice "declined Consent banner - login denied"
	fi
	/usr/bin/zenity --title="Login denied" --info --text="Consent not given, logging out in 10 seconds..." &
        sleep 10
        exit 1
      fi
      if [ -x ${LOGGER} ] ; then
        ${LOGGER} -p auth.notice "accepted Consent banner - login allowed"
      fi
    else
      /usr/bin/zenity --title="Information Bannner" --info --text="${BANNERTEXT}"
    fi
  elif [ ${KDIALOG_EXISTS} ] ; then
    if [ ${BANNERTYPE} = "REQUIRE_CONSENT" ] ; then
      /usr/bin/kdialog --title="Consent Banner" --yesno="${BANNERTEXT}"
      if [ $? -eq 1 ] ; then
        if [ -x ${LOGGER} ] ; then
	  ${LOGGER} -p auth.notice "declined Consent banner - login denied"
	fi
        /usr/bin/kdialog --title="Login denied" --msgbox="Consent not given, logging out in 10 seconds..." &
        sleep 10
        exit 1
      fi
      if [ -x ${LOGGER} ] ; then
        ${LOGGER} -p auth.notice "accepted Consent banner - login allowed"
      fi
    else
      /usr/bin/kdialog --title="Information Bannner"  --msgbox="${BANNERTEXT}"
    fi
  fi
fi
"""    
        else:
            self.banner_script = """#!/bin/sh 
BANNERFILE="BANNERFILEVAR"
BANNERTYPE="BANNERTYPEVAR"
ZENITY_EXISTS=0
KDIALOG_EXISTS=0

LOGGER=""
for LOG_CANDIDATE in /usr/sbin/logger /sbin/logger /usr/bin/logger /bin/logger ; 
do
  if [ -x ${LOG_CANDIDATE} ] ; then
     LOGGER=${LOG_CANDIDATE}
     break
  fi
done


if [ -x /usr/bin/zenity ] ; then
  ZENITY_EXISTS=1
fi

if [ -x /usr/bin/kdialog ] ; then 
  KDIALOG_EXISTS=1
fi

if [ -f ${BANNERFILE} ] ; then
  if [ ${ZENITY_EXISTS} ] ; then
    if [ ${BANNERTYPE} = "REQUIRE_CONSENT" ] ; then
      /usr/bin/zenity --title="Consent Banner" --question --text="$(cat ${BANNERFILE})"
      if [ $? -eq 1 ] ; then
        if [ -x ${LOGGER} ] ; then
	  ${LOGGER} -p authpriv.notice "declined Consent banner - login denied"
	fi
	/usr/bin/zenity --title="Login denied" --info --text="Consent not given, logging out in 10 seconds..." &
        sleep 10
        exit 1
      fi
      if [ -x ${LOGGER} ] ; then
        ${LOGGER} -p authpriv.notice "accepted Consent banner - login allowed"
      fi
    else
      /usr/bin/zenity --title="Information Bannner" --info --text="$(cat ${BANNERFILE})"
    fi
  elif [ ${KDIALOG_EXISTS} ] ; then
    if [ ${BANNERTYPE} = "REQUIRE_CONSENT" ] ; then
      /usr/bin/kdialog --title="Consent Banner" --yesno="$(cat ${BANNERFILE})"
      if [ $? -eq 1 ] ; then
        if [ -x ${LOGGER} ] ; then
	  ${LOGGER} -p authpriv.notice "declined Consent banner - login denied"
	fi
        /usr/bin/kdialog --title="Login denied" --msgbox="Consent not given, logging out in 10 seconds..." &
        sleep 10
        exit 1
      fi
      if [ -x ${LOGGER} ] ; then
        ${LOGGER} -p authpriv.notice "accepted Consent banner - login allowed"
      fi
    else
      /usr/bin/kdialog --title="Information Bannner"  --msgbox="$(cat ${BANNERFILE})"
    fi
  fi
fi
"""    


        self.dt_script_filename = "/usr/dt/config/Xsession.d/0005.SB_BannerDisplay"
        self.dt_conf_dir        = "/usr/dt/config/Xsession.d"
        
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
    def preformat_text(self, lines_in):
        lines_out = []
        this_line = ""
        for line in lines_in:
            line = line.strip()
            if line == "":
                this_line = this_line.rstrip()
                lines_out.append(this_line+"\n")
                this_line = ""
            else:
                this_line += line + ' '
                if line.endswith('.'):
                    this_line += ' '

        if this_line != "":
            lines_out.append(this_line)
        
        return lines_out
        
        
    ########################################################################## 
    def set_banner_text(self, action, banner_filename, banner_text):
        
        status = "Pass"
        messages = {'messages':[]}
        changes = None
        
            
        current_banner_text = False
        if os.path.exists(banner_filename):
            current_banner_text = open(banner_filename).readlines()
        
        if action == "Scan":
            if banner_text != current_banner_text:
                msg = "Presession Banner does not match required text"
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, "Scan Failed: %s" % msg)
                status = False
            else:
                msg = "Presession Banner matches required text" 
                messages['messages'].append(msg)
                self.logger.info(self.module_name, "%s" % msg)
        elif action == "Apply":
            if banner_text != current_banner_text:
                try:
                    open(banner_filename,"w").writelines(banner_text)
                    # Verify permissions
                    changes_to_make = {'dacs':0444}
                    ignore_results = sb_utils.file.fileperms.change_file_attributes(banner_filename, changes_to_make, options={'exactDACs':True, 'checkOnly':False})
                    msg = "Replacing Presession Banner text"
                    self.logger.info(self.module_name, "Apply: %s" % msg)
                    changes = current_banner_text
                except Exception, err:
                    msg = "Unable to replace Presession Banner text - %s(%s)" % (banner_filename, str(err))
                    status = False
                    self.logger.error(self.module_name, "Apply Failed: %s" % msg)
                messages['messages'].append(msg)
            else:
                msg = "Presession Banner matches required text"
                messages['messages'].append(msg)
                self.logger.info(self.module_name, "%s" % msg)
                        
        elif action == "Undo":
            if not os.path.exists(banner_filename):
                msg = "Presession Banner text does not exist - %s" % (banner_filename)
                self.logger.info(self.module_name, "Undo: %s" % msg)
            elif banner_text == False:
                try:
                    os.unlink(banner_filename)
                    msg = "Removing Presession Banner text"
                    self.logger.info(self.module_name, "Undo: %s" % msg)
                except Exception, err:
                    msg = "Problem removing Pressession Banner text - %s" % (banner_filename)
                    self.logger.info(self.module_name, "Undo Failed: %s" % msg)
                    messages['messages'].append(msg)
                    status = False
            else:
                try:
                    open(banner_filename, "w").writelines(banner_text)
                    # Verify permissions
                    changes_to_make = {'dacs':00444}
                    ignore_results = sb_utils.file.fileperms.change_file_attributes(banner_filename, changes_to_make, options={'exactDACs':True, 'checkOnly':False})
                    msg = "Replacing Presession Banner text"
                    self.logger.info(self.module_name, "Undo: %s" % msg)
                except Exception, err:
                    msg = "Unable to replace Presession Banner text - %s (%s)" % ( banner_filename, str(err))
                    status = False
                    self.logger.error(self.module_name, "Undo Failed: %s" % msg)
                messages['messages'].append(msg)
        return status, changes, messages
            
    

    def set_script_text (self, action, flavor, banner_filename, new_banner_text):
        
        messages = {'messages':[]}
        status = ""
        changes = None
           
        # Try to read our custom display file to see what is present.
        current_banner_text = False
        if os.path.exists(banner_filename):
            current_banner_text = open(banner_filename).readlines()
        else:
            self.logger.notice(self.module_name,"%s : %s Banner display script (%s) does not exist" % (action, flavor, banner_filename))            

        if action == "Scan":
            if current_banner_text != new_banner_text:
                msg = "%s Banner display script does not match" % flavor
                self.logger.notice(self.module_name, "%s Failed: %s " % (action, msg))
                messages['messages'].append(msg)
                status = False
            else:
                msg = "%s Banner display script matches" % flavor
                self.logger.info(self.module_name, "%s : %s " % (action, msg))

        elif action == "Apply":
            if current_banner_text != new_banner_text:
                msg = "Setting required %s banner display script" % flavor
                self.logger.info(self.module_name, "%s : %s " % (action, msg))                
                changes = current_banner_text
                current_banner_text = new_banner_text
            else:
                msg = "%s Banner display script matches" % flavor
                self.logger.info(self.module_name, "%s : %s " % (action, msg))                

        elif action == "Undo":
            if new_banner_text == False:
                try:
                    os.unlink(banner_filename)
                    msg = "Deleted %s banner display script - %s" % (flavor, banner_filename)
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))
                except Exception, err:
                    msg = "Unable to delete %s banner display script - %s" % ( flavor, banner_filename)
                    self.logger.notice(self.module_name, "%s : %s " % (action, msg))
                    status = False

            elif current_banner_text != new_banner_text :
                changes = current_banner_text
                current_banner_text = new_banner_text
            else:
                msg = "%s Banner display script matches" % flavor
                self.logger.info(self.module_name, "%s : %s " % (action, msg))                
            

        if changes != None:
            try:
                open(banner_filename, "w").writelines(current_banner_text)
                # Verify permissions
                changes_to_make = {'dacs':0555}
                ignore_results = sb_utils.file.fileperms.change_file_attributes(banner_filename, changes_to_make, options={'exactDACs':True, 'checkOnly':False})
                msg = "Wrote %s Banner display script to %s" % (flavor, banner_filename)
                self.logger.info(self.module_name, "%s : %s " % (action, msg))
                messages['messages'].append(msg)
            except Exception, err:
                changes = None
                msg = "Unable to write new %s banner display script to %s - %s" % (flavor, banner_filename, str(err))
                self.logger.notice(self.module_name, "%s Failed: %s " % (action, msg))
                messages['messages'].append(msg)
                status = False

        return status, changes, messages



    def set_conf_settings(self, action, conf_filename, invocation_line):
        
        messages = {'messages':[]}
        status = ""
        changes = None

        
        current_display_script = []
        if os.path.exists(conf_filename):
            try:
                current_display_script = open(conf_filename).readlines()
            except Exception, err:
                msg = "Unable to access '%s' , module unable to continue" % conf_filename
                self.logger.notice(self.module_name, '%s Error: %s' % (action,  msg))
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
            # Preprocess the file looking for 
            # First non-commented line
            # The line we'd insert
            
            first_exec_line = -1
            sb_line = -1
            
            for linenum in range(len(current_display_script)):
                line = current_display_script[linenum].strip()
                if not line or line.startswith('#'):
                    continue

                if first_exec_line < 0 :
                    first_exec_line = linenum
                    
                if line.endswith("# Inserted by OS Lockdown to display banner"):
                    sb_line = linenum
            
                if first_exec_line >= 0 and sb_line >= 0 :
                    break
        
            if action == "Scan":

                if sb_line == -1:
                    msg = "Banner display invocation not found in %s" % conf_filename
                    self.logger.notice(self.module_name, "%s Failed: %s " % (action, msg))
                    messages['messages'].append(msg)
                    status = False
                elif current_display_script[sb_line].strip() != invocation_line:
                    msg = "Matching Banner display invocation not found in %s" % conf_filename
                    self.logger.notice(self.module_name, "%s Failed: %s " % (action, msg))
                    messages['messages'].append(msg)
                    status = False
                else:
                    msg = "Found banner display invocation"
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))

            elif action == "Apply":

                if sb_line == -1 :
                    changes = False
                    current_display_script.insert(first_exec_line, invocation_line+"\n")
                    msg = "Adding invocation line found in %s " % conf_filename
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))                
                elif current_display_script[sb_line].strip() != invocation_line:
                    msg = "Fixing invocation line found in %s " % conf_filename
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))                
                    changes = current_display_script[sb_line]
                else:
                    msg = "Invocation line found in %s " % conf_filename
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))                
                    status = False
                    
            elif action == "Undo":
                if sb_line == -1:
                    msg = "Invocation line not present in %s" % conf_filename
                    self.logger.notice(self.module_name, "%s Failed: %s " % (action, msg))
                    messages['messages'].append(msg)
                elif invocation_line == False:
                    changes = sb_line
                    current_display_script.pop(sb_line)
                    msg = "Removed invocation line from %s" % conf_filename
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))
                elif invocation_line != current_display_script(sb_line):
                    changes = sb_line
                    msg = "Removed invocation line from %s" % conf_filename
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))
                else:                                                          
                    msg = "No change needed to invocation line in %s" % conf_filename
                    self.logger.info(self.module_name, "%s : %s " % (action, msg))
        else:
            msg = "'%s' file does not exist, module unable to continue" % conf_filename
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            status = False
            changes = None

        if changes != None:
            try:
                open(conf_filename, "w").writelines(current_display_script)
                # Verify permissions
                changes_to_make = {'dacs':0555}
                ignore_results = sb_utils.file.fileperms.change_file_attributes(conf_filename, changes_to_make, options={'exactDACs':True, 'checkOnly':False})
                msg = "Wrote Banner text to %s" % conf_filename
                self.logger.info(self.module_name, "%s : %s " % (action, msg))
                messages['messages'].append(msg)
            except Exception, err:
                changes = None
                msg = "Unable to write new banner text to %s" % conf_filename
                self.logger.notice(self.module_name, "%s Failed: %s " % (action, msg))
                messages['messages'].append(msg)
                status = False

        return status, changes, messages
        

    ########################################################################## 
    def scan(self, optionDict=None):
         
        retval = True
        messages = {'messages':[]}

        gdm_kdm_avail = False
        dt_avail = False

        banner_status = True
        banner_changes = None
        banner_messages = {}
        
        script_status = True
        script_changes = None
        script_messages = {}

        conf_status = True
        conf_changes = None
        conf_messages = {}
        
        dt_status = True
        dt_changes = None
        dt_messages = {}
        
        # get the desired banner text
        if optionDict['bannerSrc'] == "0" :
            banner_text = open("/etc/motd","r").readlines()
        elif optionDict['bannerSrc']:
            banner_text = optionDict['bannerText'].splitlines()
            
        # reformat if asked
        if optionDict['formatBanner'] == "1":
            banner_text = self.preformat_text(banner_text)
        
        if optionDict['requireAssent'] == "0":  # Information only, no assent required
            bannertype = "INFO_ONLY"
        else:
            bannertype = "REQUIRE_CONSENT"
        banner_script = self.banner_script.replace("BANNERFILEVAR", self.banner_filename)  
        banner_script =      banner_script.replace("BANNERTYPEVAR", bannertype)  
        script_text = banner_script.splitlines(True)

        if os.path.exists(self.script_conf_file) :
            gdm_kdm_avail = True 

            # verify desired banner text is present and correct
            banner_status, banner_changes, banner_messages = self.set_banner_text("Scan", self.banner_filename, banner_text)
            messages.update(banner_messages)
        
            # verify script to display banner text is present and correct, including INFO_ONLY or REQUIRE_CONSENT options
            script_status , script_changes, script_messages = self.set_script_text("Scan", "GDM/KDM", self.script_file, script_text)
            messages.update(script_messages) 
        
            # verify extra line in the config file is present and correct
            conf_status, conf_changes, conf_messages = self.set_conf_settings("Scan", self.script_conf_file, self.invocation)
            messages.update(conf_messages)
        
            if banner_status == False or script_status == False or conf_status == False:
                retval = False            
        
        if os.path.exists(self.dt_conf_dir):
            dt_avail = True
            
            dt_status, dt_changes, dt_messages = self.set_script_text("Scan", "Dtlogin", self.dt_script_filename, script_text)
            if dt_status == False:
                retval = False
            
        if not gdm_kdm_avail and not dt_avail:
            raise tcs_utils.ScanNotApplicable("No supported display managers are installed, nothing to do.")
        
        return retval, '', messages


    ########################################################################## 
    def apply(self, optionDict=None):
        
        retval = True
        messages = {'messages':[]}
        change_record = {}
        
        gdm_kdm_avail = False
        dt_avail = False
        
        banner_status = False
        banner_changes = None
        banner_messages = {}
        
        script_status = False
        script_changes = None
        script_messages = {}

        conf_status = False
        conf_changes = None
        conf_messages = {}
        
        conf_status = False
        conf_changes = None
        conf_messages = {}

        dt_status = False
        dt_changes = None
        dt_messages = {}

        # get the desired banner text
        if optionDict['bannerSrc'] == "0" :
            banner_text = open("/etc/motd","r").readlines()
        elif optionDict['bannerSrc']:
            banner_text = optionDict['bannerText'].splitlines()
            
        # reformat if asked
        if optionDict['formatBanner'] == "1":
            banner_text = self.preformat_text(banner_text)
        
        if optionDict['requireAssent'] == "0":  # Information only, no assent required
            bannertype = "INFO_ONLY"
        else:
            bannertype = "REQUIRE_CONSENT"
        banner_script = self.banner_script.replace("BANNERFILEVAR", self.banner_filename)  
        banner_script =      banner_script.replace("BANNERTYPEVAR", bannertype)  
        script_text = banner_script.splitlines(True)

        if os.path.exists(self.script_conf_file) :
            gdm_kdm_avail = True
            
            # verify desired banner text is present and correct
            banner_status, banner_changes, banner_messages = self.set_banner_text("Apply", self.banner_filename, banner_text)
            messages.update(banner_messages) 

            # verify script to display banner text is present and correct, including INFO_ONLY or REQUIRE_CONSENT options

            script_status , script_changes, script_messages = self.set_script_text("Apply", "GDM/KDM", self.script_file, script_text)
            messages.update(script_messages) 
        
            # verify extra line in the config file is present and correct
            conf_status, conf_changes, conf_messages = self.set_conf_settings("Apply", self.script_conf_file, self.invocation)
            messages.update(conf_messages)
        

        if os.path.exists(self.dt_conf_dir):
            dt_avail = True
            
            dt_status, dt_changes, dt_messages = self.set_script_text("Apply", "Dtlogin", self.dt_script_filename, script_text)
            if dt_status == False:
                retval = False

        if not gdm_kdm_avail and not dt_avail:
            raise tcs_utils.ScanNotApplicable("No supported display managers are installed, nothing to do.")
              
        if banner_changes != None :
            change_record['banner'] = banner_changes
        if script_changes != None :
            change_record['script'] = script_changes
        if conf_changes != None :
            change_record['conf'] = conf_changes
        if dt_changes != None :
            change_record['dt'] = dt_changes
        
        if change_record != {}:
            retval = True
        else :
            retval = False
            
        return retval, str(change_record), messages
        
    ########################################################################## 
    def undo(self, change_record=None):

        
        retval = True
        messages = {'messages':[]}

        banner_status = True
        banner_changes = None
        banner_messages = {}
        
        script_status = True
        script_changes = None
        script_messages = {}

        conf_status = True
        conf_changes = None
        conf_messages = {}

        dt_status = True
        dt_changes = None
        dt_messages = {}

         # convert back from string to dictionary
        change_record = tcs_utils.string_to_dictionary(change_record)

        if change_record.has_key('banner'):
            banner_text = change_record['banner']
            banner_status, banner_changes, banner_messages = self.set_banner_text("Undo", self.banner_filename, banner_text)
            messages.update(banner_messages)

        if change_record.has_key('dt'):
            script_text = change_record['dt']
            dt_status, dt_changes, dt_messages = self.set_script_text("Undo", "Dtlogin", self.dt_script_filename, script_text)
            messages.update(banner_messages)
                
        if change_record.has_key('script'):
            script_text = change_record['script']
            script_status, script_changes, script_messages = self.set_script_text("Undo", "GDK/KDM", self.script_file, script_text) 
            messages.update(script_messages)

        if change_record.has_key('conf'):
            invocation = change_record['conf']
            conf_status, conf_changes, conf_messages = self.set_conf_settings("Undo", self.script_conf_file, invocation) 
            messages.update(conf_messages)
                
        if banner_status == False or script_status == False or conf_status == False or dt_status == False:
            retval = False
        return retval, '', {'messages':[]}
