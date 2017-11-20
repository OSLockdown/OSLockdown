#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import os
import stat

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.file.fileperms

global QUICK_SCAN
try:
    if QUICK_SCAN == False:
        pass    
except NameError:
    QUICK_SCAN = False

class DisableFileShare:
    """
    Disable anonymous File transfer services
    """

    def __init__(self):
        """Constructor"""
        self.module_name = 'DisableFileShare'
        self.__target_file = ''
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__targetpath = ['/bin/apollon',     
                             '/sbin/apollon', 
                             '/usr/bin/apollon', 
                             '/usr/sbin/apollon', 
                             '/usr/local/bin/apollon', 
                             '/usr/local/sbin/apollon', 
                             '/bin/bittorrent', 
                             '/sbin/bittorrent', 
                             '/usr/bin/bittorrent', 
                             '/usr/sbin/bittorrent', 
                             '/usr/local/bin/bittorrent', 
                             '/usr/local/sbin/bittorrent', 
                             '/bin/bittorrent-console', 
                             '/sbin/bittorrent-console', 
                             '/usr/bin/bittorrent-console', 
                             '/usr/sbin/bittorrent-console', 
                             '/usr/local/bin/bittorrent-console', 
                             '/usr/local/sbin/bittorrent-console',
                             '/bin/bittorrent-curses', 
                             '/sbin/bittorrent-curses', 
                             '/usr/bin/bittorrent-curses', 
                             '/usr/sbin/bittorrent-curses', 
                             '/usr/local/bin/bittorrent-curses', 
                             '/usr/local/sbin/bittorrent-curses', 
                             '/bin/giftd', 
                             '/sbin/giftd', 
                             '/usr/bin/giftd', 
                             '/usr/sbin/giftd', 
                             '/usr/local/bin/giftd', 
                             '/usr/local/sbin/giftd', 
                             '/bin/gift-setup', 
                             '/sbin/gift-setup', 
                             '/usr/bin/gift-setup', 
                             '/usr/sbin/gift-setup', 
                             '/usr/local/bin/gift-setup', 
                             '/usr/local/sbin/gift-setup', 
                             '/bin/gift-gnutella', 
                             '/sbin/gift-gnutella', 
                             '/usr/bin/gift-gnutella', 
                             '/usr/sbin/gift-gnutella', 
                             '/usr/local/bin/gift-gnutella', 
                             '/usr/local/sbin/gift-gnutella', 
                             '/bin/gift-gnutella', 
                             '/sbin/gift-gnutella', 
                             '/usr/bin/gift-gnutella', 
                             '/usr/sbin/gift-gnutella', 
                             '/usr/local/bin/gift-gnutella', 
                             '/usr/local/sbin/gift-gnutella', 
                             '/bin/gtk-gnutella', 
                             '/sbin/gtk-gnutella', 
                             '/usr/bin/gtk-gnutella', 
                             '/usr/sbin/gtk-gnutella', 
                             '/usr/local/bin/gtk-gnutella', 
                             '/usr/local/sbin/gtk-gnutella', 
                             '/bin/LimeWire.jar', 
                             '/sbin/LimeWire.jar', 
                             '/usr/bin/LimeWire.jar', 
                             '/usr/sbin/LimeWire.jar', 
                             '/usr/local/bin/LimeWire.jar', 
                             '/usr/local/sbin/LimeWire.jar', 
                             '/bin/mldonkey', 
                             '/sbin/mldonkey', 
                             '/usr/bin/mldonkey', 
                             '/usr/sbin/mldonkey', 
                             '/usr/local/bin/mldonkey', 
                             '/usr/local/sbin/mldonkey', 
                             '/bin/mlslsk', 
                             '/sbin/mlslsk', 
                             '/usr/bin/mlslsk', 
                             '/usr/sbin/mlslsk', 
                             '/usr/local/bin/mlslsk', 
                             '/usr/local/sbin/mlslsk', 
                             '/bin/mlgnut', 
                             '/sbin/mlgnut', 
                             '/usr/bin/mlgnut', 
                             '/usr/sbin/mlgnut', 
                             '/usr/local/bin/mlgnut', 
                             '/usr/local/sbin/mlgnut', 
                             '/bin/mldc', 
                             '/sbin/mldc', 
                             '/usr/bin/mldc', 
                             '/usr/sbin/mldc', 
                             '/usr/local/bin/mldc', 
                             '/usr/local/sbin/mldc', 
                             '/bin/mlbt', 
                             '/sbin/mlbt', 
                             '/usr/bin/mlbt', 
                             '/usr/sbin/mlbt', 
                             '/usr/local/bin/mlbt', 
                             '/usr/local/sbin/mlbt', 
                             '/bin/nap', 
                             '/sbin/nap', 
                             '/usr/bin/nap', 
                             '/usr/sbin/nap', 
                             '/usr/local/bin/nap', 
                             '/usr/local/sbin/nap', 
                             '/bin/napping', 
                             '/sbin/napping', 
                             '/usr/bin/napping', 
                             '/usr/sbin/napping', 
                             '/usr/local/bin/napping', 
                             '/usr/local/sbin/napping', 
                             '/bin/qtella', '/sbin/qtella', 
                             '/usr/bin/qtella', 
                             '/usr/sbin/qtella', 
                             '/usr/local/bin/qtella', 
                             '/usr/local/sbin/qtella' ]
                             
    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

    ##########################################################################
    def scan(self, option=None):
        """Check for files and file permissions"""
        if option != None:
            option = None

        module_failed = False
        for loc in self.__targetpath:
            if  os.path.isfile(loc):
                msg = "Scan: Checking permissions/ownership of %s" % loc
                self.logger.debug(self.module_name, msg)

                #Now check the file permissions$
                try:
                    statinfo = os.stat(loc)
                except (OSError, IOError), err:
                    msg = "Scan Error: Unable to stat file %s: " % (loc, err)
                    self.logger.error(self.module_name, msg)
                    continue

                # We want the permissions to 000
                if statinfo.st_mode & 0777 ^ 0000 != 0:
                    reason = "Scan Failed: %s has permissions of %o instead "\
                             "of 000" % (loc, stat.S_IMODE(statinfo.st_mode))
                    self.logger.notice(self.module_name, reason)
                    module_failed = True
                    if QUICK_SCAN == True:
                        msg = "Quick Scan Enabled - Module finishes after first issue detected"
                        self.logger.info(self.module_name, msg)
                        return 'Fail', reason
                    else: 
                        continue

                elif statinfo.st_uid != 0:
                    reason = "Scan Failed: %s has owner %d instead of 0 (root)" \
                             % (loc, statinfo.st_uid)
                    self.logger.notice(self.module_name, reason)
                    module_failed = True
                    if QUICK_SCAN == True:
                        msg = "Quick Scan Enabled - Module finishes after first issue detected"
                        self.logger.info(self.module_name, msg)
                        return 'Fail', reason
                    else: 
                        continue

        if module_failed == True:
            return False, '', {}
        else:
            return True, '', {}


    ##########################################################################
    def apply(self, option=None):
        """
        Disable the executable if present
        """

        change_record = {}
        try:
            result, reason, msgs = self.scan()
            if result == True:
                return False, reason,msgs
        except tcs_utils.ScanNotApplicable:
            msg = 'module is not applicable for this system'
            self.logger.error(self.module_name, 'Apply Error: ' + msg)
            return False, '', {'messages':[msg]}

        loc = None
        found = False
        for loc in self.__targetpath:
            if os.path.isfile(loc):
                found = True
                #Now check the file permissions$
                try:
                    statinfo = os.stat(loc)
                except (OSError, IOError), err:
                    msg = "Scan Error: Unable to stat file %s: " % (loc, err)
                    self.logger.error(self.module_name, msg)
                    continue

                changes_to_make = {}
                # We want the permissions to 000
                if statinfo.st_mode & 0777 ^ 0000 != 0:
                    changes_to_make.update({'dacs':0})
                elif statinfo.st_uid != 0:
                    changes_to_make.update({'owner':'root'})
                elif statinfo.st_gid != 0:
                    changes_to_make.update({'group':'root'})
                change_record.update(sb_utils.file.fileperms.change_file_attributes(loc, changes_to_make))
                

        if found == False:
            msg = "File sharing programs are not installed on this system"
            self.logger.notice(self.module_name, 'Not Applicable: ' + msg)
            return False, '', {'messages':[msg]}

        return True, str(change_record), {'messages':[]}

    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""

        # Original code never kept track of what modules where changed, so we have never
        # had a record of files to revert. So if we ever get a blank list,
        # blindly try to fix whatever files are there.. 
        # 
        
        if change_record == "":
            change_record = {}
            for loc in self.__targetpath:
                if os.path.isfile(loc):
                    change_record[loc] = {'owner':'root',
                                          'group':'root',
                                          'dacs':0755}
                    
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record)

        return True, '',{}

