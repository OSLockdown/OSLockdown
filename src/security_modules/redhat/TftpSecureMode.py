#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Ensure that TFTP Service is using the -s option 
#  - If under xinetd control, check configuration file's server_args param.
#
#
##############################################################################

import sys
import os
import shutil

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger

import sb_utils.os.software
import sb_utils.os.info

class TftpSecureMode:

    def __init__(self):
        self.module_name = 'TftpSecureMode'
        if sb_utils.os.info.is_LikeSUSE() == True:
            self.rpm_name = 'tftp'
        else:
            self.rpm_name = 'tftp-server'
            
        self.logger = TCSLogger.TCSLogger.getInstance()

    ##########################################################################
    def scan(self, option=None):
        """Check for rpm and for -s mode"""
        if option != None:
            option = None

        messages = {'messages': []}

        flagIndex = None
        dirIndex = None
        dirName = None

        results =  sb_utils.os.software.is_installed(pkgname=self.rpm_name)
        if results != True:
            msg = "'%s' package is not installed" % self.rpm_name
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "'%s' package is installed" % self.rpm_name
            self.logger.info(self.module_name, msg)
            messages['messages'].append(msg)

        try:
            myfile = open('/etc/xinetd.d/tftp', 'r')
        except IOError, err: 
            msg = "Unable to open /etc/xinetd.d/tftp: %s" % str(err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        msg = "Looking for '-s' in /etc/xinetd.d/tftp"
        self.logger.info(self.module_name, msg)
        messages['messages'].append(msg)

        foundit = False 
        for line in myfile.xreadlines():
            line = line.strip('\n')
            line = line.strip(' ')
            line = line.strip('\t')
            if '=' in line:
                line = line.strip('\t')
                param, thevalue = line.split('=')
                param    = param.strip(' ')
                param    = param.strip('\t')
                thevalue = thevalue.strip(' ')
                if param == 'server_args':
                    thefields = thevalue.split()
                    try:
                        flagIndex = thefields.index('-s')
                        dirIndex = flagIndex+1
                        dirName = thefields[dirIndex]
                        foundit = True
                        msg = "Found '-s %s' in /etc/xinetd.d/tftp " % dirName
                        self.logger.info(self.module_name, msg)
                        if os.path.exists(dirName) == False:
                            wmsg = "Warning:'%s' does not exist!" % dirName
                            messages['messages'].append(wmsg)    
                            self.logger.info(self.module_name, wmsg)
                    except ValueError:  # couldn't find -s flag
                        pass
                    except IndexError:  # couldn't find argument to -s
                            wmsg = "Warning: No argument for '-s' option !"
                            messages['messages'].append(wmsg)
                            self.logger.info(self.module_name, wmsg)
                    
                    break

        myfile.close()
        if foundit != True:
            msg = "Could not find '-s' for server_args in /etc/xinetd.d/tftp"
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            return False, msg, messages
 
        return True, msg, messages
 
    
    ##########################################################################
    def apply(self, option=None):

        # indicate initially there was no setting
        messages = {'messages':[]}
        try:
            (result, reason, messages) = self.scan()
            if result == True:
                return False, reason, messages
        except tcs_utils.ScanNotApplicable, err:
            return False, str(err), messages

        # since we got here, we know we need to add this, so we know we'll have a change record of some sort
        change_record = {'oldline':None}
        
        messages = {'messages': []}
        try:
            shutil.copy2('/etc/xinetd.d/tftp', '/tmp/.tftp.new')
            sb_utils.SELinux.restoreSecurityContext('/etc/xinetd.d/tftp')
            out_obj = open('/etc/xinetd.d/tftp', 'w')
            in_obj  = open('/tmp/.tftp.new', 'r')
        except (IOError, OSError), err:
            msg = "Unable to create temp file: %s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' %
                                              (self.module_name, msg))

        messages['messages'].append("Editing /etc/xinetd.d/tftp")
        foundit = False 
        for lineNr, line in enumerate(in_obj.xreadlines()):
            if line.startswith('#'):
                out_obj.write(line)
                continue
            line = line.strip('\n')
            tline = line.strip('\t')
            tline = tline.strip(' ')
            if not tline.startswith('server_args'):
                if line.endswith('}') and foundit == False:
                    out_obj.write('\tserver_args     = -s /tftpboot\n')
                out_obj.write(line + '\n')
                msg = "Inserting 'server_args = -s /tftpboot' at line %d" % (lineNr+1)
                messages['messages'].append(msg)
            else:
                param, thevalue = tline.split('=')
                param    = param.strip(' ')
                param    = param.strip('\t')
                thevalue = thevalue.strip(' ')
                
                # since we *found* the setting, remember what it was
                change_record['oldline'] = thevalue
                if '-s' not in thevalue:
                    foundit = True
                    out_obj.write(line + ' -s /tftpboot\n')
                    msg = "Adding '-s /tftpboot' to line %d" % (lineNr+1)
                    messages['messages'].append(msg)
                else:
                    brokenout = thevalue.split()
                    idx = brokenout.index('-s')
                    try:
                        brokenout[idx+1] = '/tftpboot'
                    except IndexError:
                        brokenout[idx] = '-s /tftpboot'
                    out_obj.write('\t' + param + '     = ')
                    for things in brokenout:
                        out_obj.write(things + ' ')
                    out_obj.write('\n')
                    msg = "Adding '-s /tftpboot' to line %d" % (lineNr+1)
                    messages['messages'].append(msg)
                    foundit = True
   
        if not os.path.exists('/tftpboot'):
            messages['messages'].append("Warning: '/tftpboot' does not exist")
        
        out_obj.close()
        in_obj.close()
        try:
            os.unlink('/tmp/.tftp.new')
        except (OSError, IOError), err:
            msg = "Unable to remove /tmp/.tftp.new: %s" % err
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
        
        return True, str(change_record), messages


    ##########################################################################
    def undo(self, change_record=None):

        messages = {'messages': []}
    
        # if we have a newstyle change record (a dictionary) we can take the value of the 'oldline' key and then
        # use it as the change record itself, since we no longer allow for an 'empty' change record to be in the state file
        if change_record[0:100].strip().startswith('{'): 
            change_record = tcs_utils.string_to_dictionary(change_record)
            change_record = change_record['oldline']
        
        try:
            shutil.copy2('/etc/xinetd.d/tftp', '/tmp/.tftp.new')
            sb_utils.SELinux.restoreSecurityContext('/etc/xinetd.d/tftp')
            out_obj = open('/etc/xinetd.d/tftp', 'w')
            in_obj  = open('/tmp/.tftp.new', 'r')
        except (OSError, IOError), err:
            msg = "Unable to create temp file: %s" % err
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        for lineNr, line in enumerate(in_obj.xreadlines()):
            tline = line.strip()
            if tline.startswith('server_args'):
                if change_record:
                    out_obj.write("\tserver_args = %s\n" % change_record)
                    messages['messages'].append("Replaced line %d of /etc/xinetd.d/tftp" % (lineNr+1))
                else:
                    messages['messages'].append("Deleted line %d of /etc/xinetd.d/tftp" % (lineNr+1))
            else:
                out_obj.write(line)

        out_obj.close()
        in_obj.close()
        try:
            os.unlink('/tmp/.tftp.new')
        except OSError:
            msg = "Unable to remove /tmp/.tftp.new"
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
        
        return True, 'Reverted changes in /etc/xinetd.d/tftp', messages
