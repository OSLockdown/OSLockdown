#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import sha
import re

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.file.fileperms

class CreateLoginFTPBanner:

    def __init__(self):
        self.module_name = "CreateLoginFTPBanner"
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        self.__bannerfiles = ['/etc/ftpd/banner.msg', 
                              '/etc/ftpd/welcome.msg' ]
        self.__ftpaccess = '/etc/ftpd/ftpaccess'

        

    ##########################################################################
    def _sha1(self, filename=None):
        """Compute SHA1 digest on given file and return fingerprint string"""
    
        # If no filename was provided or the filename does not physically
        # exist, return default message.
        if filename == None or not os.path.isfile(filename):
            return None

        # Now, compute the SHA1 digest
        digest_key = sha.new()
        try:
            fdes = open(filename, 'rb')
        except IOError, err:
            msg = "Unable to read %s: %s" % (filename, str(err))
            self.logger.error(self.module_name, msg)
            return None

        try:
            while True:
                block = fdes.read(1024)
                if not block:
                    break
                digest_key.update(block)
        finally:
            fdes.close()

        return digest_key.hexdigest()


    ##########################################################################
    def scan(self, optionDict=None):

        if sb_utils.os.software.is_installed(pkgname='SUNWftpr') != True:
            msg = "SUNWftpr package is not installed"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))

        if not os.path.isfile(self.__ftpaccess):
            msg = "%s not present - ftp setup is not configured properly"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
        if optionDict == None or not 'ftpLoginBanner' in optionDict:
            msg = 'Missing option: No warning banner provided'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['ftpLoginBanner']
        replacePat = re.compile('\n')
        option = replacePat.sub(' ', option)
        option = option.strip("\"")

        bannerOptionHash = sha.new()
        bannerOptionHash.update(option)
        bannerOptionHash = bannerOptionHash.hexdigest() 

        failure_flag = False
        for bannerfile in self.__bannerfiles:
            if not os.path.isfile(bannerfile):
                msg = "%s does not exist" % bannerfile
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                failure_flag = True
                continue
              
            msg = "Checking contents of %s" % bannerfile
            self.logger.info(self.module_name, msg)

            fingerprint = self._sha1(bannerfile)
            if fingerprint != bannerOptionHash:
                msg = "'%s' (SHA1: %s) does not match desired login banner "\
                      "message (SHA1: %s)" % (bannerfile, fingerprint, 
                                                           bannerOptionHash)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                failure_flag = True 
            else:
                msg = "'%s' is okay" % bannerfile
                self.logger.info(self.module_name, msg)
         
        line1_regex = re.compile('^banner\s*/etc/ftpd/banner.msg')
        line2_regex = re.compile('^message\s*/etc/ftpd/welcome.msg\s*login')
        line1_found = False
        line2_found = False
        missing_lines = []
        for line in open(self.__ftpaccess):
            if line1_regex.search(line):               
                line1_found = True
            elif line2_regex.search(line):
                line2_found = True
        
        if not line1_found:
            missing_lines.append('banner')
        if not line2_found:
            missing_lines.append('message')
            
        if missing_lines != [] :
            msg = 'Missing the following entries from %s : %s' % (self.__ftpaccess, ', '.join(missing_lines))
            self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
            failure_flag = True
            
        if failure_flag == True:
            return False, '', {'messages':['FTP login banners are not correct.']}
        else:
            return True, '', {'messages':[]}


    ##########################################################################
    def apply(self, optionDict=None):

        result, reason, messages = self.scan(optionDict)
        if result == 'Pass':
            return False, reason, messages

        option = optionDict['ftpLoginBanner']
        
        replacePat = re.compile('\n')
        option = replacePat.sub(' ', option)
        option = option.strip("\"")

        bannerOptionHash = sha.new()
        bannerOptionHash.update(option)
        bannerOptionHash = bannerOptionHash.hexdigest() 

        banner_changes = {}
        ftpaccess_changes = []
        
        for bannerfile in self.__bannerfiles:
  
            if self._sha1(bannerfile) != bannerOptionHash:
                if os.path.isfile(bannerfile):
                    try:
                        infile = open(bannerfile, 'r')
                        lines = infile.readlines()
                        infile.close()
                    except IOError, err:
                        msg = "Unable to read %s: %s" % (bannerfile, err)
                        self.logger.error(self.module_name, 'Apply Error: ' + msg)
                        raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                else:
                    lines = "EMPTY\n"
            
                # Update/Write "option" value to banner file 
                try:
                    outFile = open(bannerfile, 'w')
                    outFile.write(option)
                    outFile.close()
                    
                    record = "BANNERFILE=%s|%s\n" % (bannerfile, ''.join(lines))
                    banner_changes[bannerfile] = ''.join(lines)
                except (OSError, IOError), err:
                    msg = "Unable to write to %s : %s" % (bannerfile, str(err))
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)
                    raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                changes_to_make = {'owner':'root',
                                    'group':'root',
                                    'dacs':0444}
                ignore_results = sb_utils.file.fileperms.change_file_attributes(bannerfile, changes_to_make)

        line1_regex = re.compile('^banner\s*/etc/ftpd/banner.msg')
        line2_regex = re.compile('^message\s*/etc/ftpd/welcome.msg\s*login')
        line1_found = False
        line2_found = False
        missing_lines = []
        for line in open(self.__ftpaccess):
            if line1_regex.search(line):               
                line1_found = True
            elif line2_regex.search(line):
                line2_found = True

        if not line1_found or not line2_found:
            ftpaccess = open(self.__ftpaccess,"a")
            if not line1_found:
                missing_lines.append('banner')
                linetoadd = "banner\t/etc/ftpd/banner.msg\n"
                ftpaccess.write(linetoadd)
                ftpaccess_changes.append(linetoadd)
            if not line2_found:
                missing_lines.append('message')
                linetoadd = "message\t/etc/ftpd/welcome.msg\tlogin\n"
                ftpaccess.write(linetoadd)
                ftpaccess_changes.append(linetoadd)
            ftpaccess.close()
            
            msg = 'Adding the following entries to %s : %s' % (self.__ftpaccess, ', '.join(missing_lines))
            self.logger.notice(self.module_name, msg)
            failure_flag = True
        
        # if we make no change then make sure we return a blank change_rec, otherwise create it
        if banner_changes == {} and ftpaccess_changes == [] :
            return False, '', {'messages':[]}
        else:
            change_record = {'bannerfiles':banner_changes, 'ftpaccess':ftpaccess_changes}
            return True, str(change_record), {'messages':[]}


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
        
        # if this is an oldstyle change record try to convert it inplace to a 'new' one
        if change_record[0:11] == 'BANNERFILE=' :
            tmprec = {'bannerfiles':{}, 'ftpaccess':{}}
            for rec in change_record.split('BANNERFILE='):
                try:
                    bannerfile, message = rec.split('|')
                except:
                    continue
                tmprec['bannerfiles'].update({bannerfile:message})
            change_record = tmprec
        else:
            change_record = tcs_utils.string_to_dictionary(change_record)
                
        if change_record.has_key('bannerfiles'):
            for bannerfile, message in change_record['bannerfiles'].items():
                # If previous banner file did not exist, remove it.
                if message.rstrip() == 'EMPTY':
                    if not os.path.isfile(bannerfile):
                        msg = "Undo should delete %s, but it doesn't exist" % bannerfile
                        self.logger.error(self.module_name, 'Undo Error: ' + msg)
                        continue
                    try:
                        os.unlink(bannerfile)
                    except OSError, err:
                        msg = "Unable to remove %s: %s" % (bannerfile, err)
                        self.logger.error(self.module_name, 'Undo Error: ' + msg)
                        raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

                    msg = "Undo Performed: Removed %s" % bannerfile
                    self.logger.notice(self.module_name, msg)

                else:
                    try:
                        outfile = open(bannerfile, 'w')
                        outfile.write(message)
                        outfile.close()
                    except IOError, err:
                        msg = "Unable to restore  %s: %s" % (bannerfile, err)
                        self.logger.error(self.module_name, 'Undo Error: ' + msg)
                        raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))


                    msg = "Undo Performed: %s has been restored" % bannerfile
                    self.logger.notice(self.module_name, msg)
        
        if change_record.has_key('ftpaccess'):            
            added_lines = change_record['ftpaccess']
            filelines = open(self.__ftpaccess,"r").readlines()
            for checkline in added_lines:
                filelines.remove(checkline)
            open(self.__ftpaccess,"w").writelines(filelines)

                        

        msg = 'Login banner configurations restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {'messages':[]}

