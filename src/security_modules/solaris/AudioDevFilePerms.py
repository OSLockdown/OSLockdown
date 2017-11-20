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
import pwd
import grp

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
        self.__allowed_unames = ['root']
        self.__allowed_gnames = ['root', 'sys', 'bin']
        self.__allowed_uids = []
        self.__allowed_gids = []

    ##########################################################################
    def validate_input(self, option=None):
        """Validate input - this class requires none"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def _set_allowed(self):
        for uname in self.__allowed_unames:
            try:
                self.__allowed_uids.append(pwd.getpwnam(uname).pw_uid)
            except Exception, e:
                self.logger.warn(self.module_name, "Unable to determine UID for username '%s'" % uname)

        for gname in self.__allowed_gnames:
            try:
                self.__allowed_gids.append(grp.getgrnam(gname).gr_gid)
            except Exception, e:
                self.logger.warn(self.module_name, "Unable to determine GID for groupname '%s'" % gname)

    ##########################################################################
    def check_file(self, audio_file):
        changes_to_make = {}
        reason = ''
        try:
            statinfo = os.stat(audio_file)
        except (OSError, IOError), err:
            msg = "Unable to stat %s: %s" % (audio_file, err)
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            return changes_to_make
            
        # Check file ownerhsip
        if statinfo.st_uid not in self.__allowed_uids :
            changes_to_make['owner'] = 'root'
        if statinfo.st_gid not in self.__allowed_gids :
            changes_to_make['group'] = 'root'
        if changes_to_make != {}: 
            reason = "%s is owned by '%s' and group '%s'; expecting owner to "\
                     "be in '%s' and group to be in '%s'" % (audio_file, 
                        pwd.getpwuid(statinfo.st_uid)[0], grp.getgrgid(statinfo.st_gid)[0],
                        ','.join(self.__allowed_unames), ','.join(self.__allowed_gnames))
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)

        # Check to see if it is 0640
        if statinfo.st_mode & 0777 ^ 0640 != 0 and statinfo.st_mode & 0777 ^ 0600 != 0:
            reason = '%s has permissions of %o instead of no more than 640' % \
                     (audio_file,stat.S_IMODE(statinfo.st_mode))
            self.logger.notice(self.module_name, 'Scan Failed: ' + reason)
            changes_to_make['dacs'] = 0640
        return changes_to_make , reason        

    ##########################################################################
    def scan(self, option=None):

        self._set_allowed()
        audio_devices = glob.glob('/dev/audio*')
        messages = []
        
        failure_flag = False
        for audio_file in audio_devices:
            changes_to_make, reason = self.check_file(audio_file) 
            if changes_to_make != {}:
                failure_flag = True
                messages.append(reason)

        if failure_flag == True:
            return False, '', {'messages':messages}
        else:
            return True, '', {'messages':[]}


    ##########################################################################
    def apply(self, option=None):

        self._set_allowed()
        result, reason, messages = self.scan()

        if result == True:
            return False, reason, messages

        action_record = {}
        audio_devices = glob.glob('/dev/audio*')
        messages = []
        
        for audio_file in audio_devices:

            changes_to_make, reason = self.check_file(audio_file)
                  
            if changes_to_make != {}:
                action_record.update(sb_utils.file.fileperms.change_file_attributes(audio_file, changes_to_make))
                changetext = ','.join(sorted(changes_to_make.keys()))
                messages.append('Changed %s for %s' % (changetext, audio_file))

        if action_record != {}:
            msg = 'Permissions on audio device files altered as needed.'
            self.logger.notice(self.module_name, 'Apply Performed: ' + msg)
            return True, str(action_record), {'messages':messages}
        else:
            return False, '', {'messages':[]}
            
    ##########################################################################
    def undo(self, change_record=None):
        """
        Reset the file permissions on audio device files.
        """


        result, reason, messages = self.scan()
        if result == False:
            return result, reason, messages

        if not change_record:
            msg = "Skipping Undo: No change record in state file."
            self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
            return False, '', {'messages':[msg]}


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
            
        tcs_utils.change_bulk_file_attributes(change_record)

        msg = 'audio device files permissions reset'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, '', {'messages':[]}

