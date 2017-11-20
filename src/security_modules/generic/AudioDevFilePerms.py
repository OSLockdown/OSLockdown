#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import glob
import stat

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms


class AudioDevFilePerms:
    """
    Handles the guideline for access permissions on audio device files
    which require that /dev/audio* be owned by root and be AT LEAST 0640
    """

    def __init__(self):
        """Constructor"""
        self.module_name = "AudioDevFilePerms"
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__log_analyze = 1

    ##########################################################################
    def validate_input(self, option=None):
        """Validate input - this class requires none"""
        if option and option != 'None':
            return 1
        return 0


    ##########################################################################
    def scan(self, option=None):

        audio_devices = glob.glob('/dev/audio*')

        failure_flag = False
        for audio_file in audio_devices:
            try:
                statinfo = os.stat(audio_file)
            except (OSError, IOError), err:
                msg = "Unable to stat %s: %s" % (audio_file, err)
                self.logger.error(self.module_name, 'Scan Error: ' + msg)
                continue

            # Check file ownerhsip
            if statinfo.st_uid != 0 or statinfo.st_gid != 0:
                reason = '%s has UID:GID of %d:%d instead of 0:0' % \
                     (audio_file, statinfo.st_uid, statinfo.st_gid)
                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                failure_flag = True
                continue


            # Check to see if it is 0640
            if statinfo.st_mode & 0777 ^ 0640 != 0 and statinfo.st_mode & 0777 ^ 0600 != 0:
                reason = '%s has permissions of %o instead of at least 640' % \
                         (audio_file,stat.S_IMODE(statinfo.st_mode))
                self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
                failure_flag = True
                continue

        if failure_flag == True:
            return 'Fail', '/dev/audio* files have bad access controls'
        else:
            return 'Pass', ''


    ##########################################################################
    def apply(self, option=None):

        self.__log_analyze = 0
        result, reason = self.scan()
        self.__log_analyze = 1
        if result == 'Pass':
            return 0, ''

        action_record = {}
        audio_devices = glob.glob('/dev/audio*')

        for audio_file in audio_devices:

            try:
                statinfo = os.stat(audio_file)
            except (OSError, IOError), err:
                msg = "Unable to stat %s: %s" % (audio_file, err)
                self.logger.error(self.module_name, 'Apply Error: ' + msg)
                continue

#            change_record = '%d %d %d %s\n' % \
#            (statinfo.st_uid,statinfo.st_gid, \
#            stat.S_IMODE(statinfo.st_mode), audio_file)
      
            # Now set owenrship/group to root/root and permissions to 0640
            changes_to_make = {'owner':'root',
                               'group':'root'}
            if statinfo.st_mode & 0777 ^ 0640 != 0 and statinfo.st_mode & 0777 ^ 0600 != 0:
                changes_to_make.update({'dacs':0640})

            action_record.update(sb_utils.file.fileperms.change_file_attributes(audio_file, changes_to_make))

            msg = "%s : ownership and group set to root/root and ensured "\
                  "permissions were at least 0640."
            self.logger.info(self.module_name, 'Apply Performed: ' + msg)

        msg = 'Permissions on audio device files altered as needed.'
        self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        return 1, str(action_record)

            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the file permissions on audio device files.
        """


        result, reason = self.scan()
        if result == 'Fail':
            return 0

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return 0


        # check to see if this might be an oldstyle change record, which is a string of entries
        #    "uid gid mode filename\n"
        # If so, convert that into the new dictionary style 
        # remember that the oldstyle record kept the mode as a straight decimal number, so read it as such
        
        if not change_record[0:200].strip().startswith('{') :
            new_rec = {}
            for line in change_record.split('\n'):
                fspecs = line.split(' ')
                if len(fspecs) != 4:
                    continue
                new_rec[fspecs[3]] = {'owner':fspecs[0],
                                      'group':fspecs[1],
                                      'dacs':int(fspecs[2],10)}  # explicitly decimal
            change_record = new_rec
            
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        msg = 'audio device files permissions reset'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return 1

