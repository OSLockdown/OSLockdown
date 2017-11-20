#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# This module ensures that standard login banner files such as 
# /etc/motd and /etc/issue contain appropriate text.
#
# This module takes a SHA1 digest of the above file and
# compares it to a SHA1 digest of the system banner files
# (i.e., /etc/motd). If they don't match, this module will
# update the standard banner with with the contents of the
# master banner file.
#
# If the master banner file's access is too permissive
# or it does not exist, this module will resort to using a
# a default message. It will update the master file
# with the default message, too.
#
#


import sha
import sys
import os

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.file.fileperms


class CreateLoginBanner:

    def __init__(self):
        self.module_name = "CreateLoginBanner"


        self.__bannerfiles = ['/etc/issue', '/etc/motd' ]

        if sb_utils.os.info.is_solaris() != True:
            self.__bannerfiles.append('/etc/issue.net')

        self.logger = TCSLogger.TCSLogger.getInstance()

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
        except (OSError, IOError), err:
            msg = "Unable to read %s: %s" % (filename, err)
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


        if optionDict == None or not 'loginBanner' in optionDict:
            msg = "No banner text provided"
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg)) 

        option = optionDict['loginBanner']
        master_fingerprint = sha.new(option).hexdigest()

        failure_flag = False

        for bannerfile in self.__bannerfiles:
            if not os.path.isfile(bannerfile):
                msg = "%s does not exist" % bannerfile
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                failure_flag = True
                continue
              
            msg = "Checking contents of %s" % bannerfile
            self.logger.info(self.module_name, msg)

            fingerprint = self._sha1(filename=bannerfile)

            if fingerprint != master_fingerprint:  
                msg = "'%s' (SHA1: %s) does not match desired login banner "\
                      "message (SHA1: %s)" % (bannerfile, fingerprint, 
                                                           master_fingerprint)
                self.logger.notice(self.module_name, 'Scan Failed: ' + msg)
                failure_flag = True 
            else:
                msg = "'%s' is okay" % bannerfile
                self.logger.info(self.module_name, msg)
            

        if failure_flag == True:
            return 'Fail', 'Some login banners are not correct.'
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, optionDict=None):

        result, reason = self.scan(optionDict)
        if result == 'Pass':
            return 0, reason

        option = optionDict['loginBanner']
        master_fingerprint = sha.new(option).hexdigest()

        action_record = []
        apply_problem = False

        for bannerfile in self.__bannerfiles:
            if self._sha1(bannerfile) != master_fingerprint:
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
            
                record = "BANNERFILE=%s|%s\n" % (bannerfile, ''.join(lines))
                action_record.append(record)
                 

                # Copy master banner to a temporary file
                try: 
                    out_obj = open(bannerfile, 'w')
                    out_obj.write(option)
                    out_obj.close()
                    if lines == "EMPTY\n":
                        changes_to_make = {'owner':'root',
                                     'group':'root',
                                     'dacs':0444}
                        ignore_results = sb_utils.file.fileperms.change_file_attributes(bannerfile, changes_to_make)
                    msg = "Apply Performed: %s updated." % (bannerfile)
                    self.logger.notice(self.module_name, msg)
                except (OSError, IOError), err: 
                    apply_problem = True
                    msg = "Unable to update %s: %s" % (bannerfile, err)
                    self.logger.error(self.module_name, 'Apply Error: ' + msg)

        if apply_problem == True:
            return 0, ''

        return 1, ''.join(action_record)


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""


        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, msg)
            return 1

        for record in change_record.split('BANNERFILE='):
            if not record:
                continue
            try:
                bannerfile, message = record.split('|')
            except Exception, err: 
                self.logger.debug(self.module_name, 'Undo Error: ' + err)
                continue

            # If previous banner file did not exist, remove it.
            if message.rstrip() == 'EMPTY':
                try:
                    os.unlink(bannerfile)
                except (OSError, IOError), err:
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
                    


        msg = 'Login banner configurations restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

