##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

#
# Whitelists
#

import sys
import re
import os
import stat
import pwd

sys.path.append('/usr/share/oslockdown')
try:
    import TCSLogger
    import tcs_utils
    import sb_utils.os.info
    import sb_utils.os.solaris
    import sb_utils.misc.unique
    import sb_utils.filesystem.mount
    import sb_utils.file.dac
    import sb_utils.file.fileread
    import sbProps
    
except ImportError, merr:
    print "Unable to load modules: %s" % merr
    sys.exit(1)


MODULE_NAME            = "sb_utils.file.whitelists"

# a few exceptions for our use later
class PathExcluded (Exception):
    pass
   
##############################################################################

class Whitelists:
    suid_master_list = None
    sgid_master_list = None

    def __init__(self, refresh = False):
        self.module_name = "sb_utils.file.whitelists.py"
               
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


        # _whitelist_generate() will raise an exception if there are *no* files listed
        
        if (Whitelists.suid_master_list or Whitelists.sgid_master_list) and refresh == True:
            self.logger.log_notice(MODULE_NAME,"Disgarding existing whitelist(s)")
            if (Whitelists.suid_master_list):
            	Whitelists.suid_master_list = None
            if (Whitelists.sgid_master_list):
            	Whitelists.sgid_master_list = None

        if Whitelists.suid_master_list == None:
            self.logger.log_notice(MODULE_NAME,"Generating fresh SUID whitelist")
            Whitelists.suid_master_list = sb_utils.file.fileread.read_files_with_custom_changes("SUID whitelist", sbProps.SUID_WHITELIST, True)
            msg = "Master SUID whilelist: has %d entries" % len(Whitelists.suid_master_list)
            self.logger.log_info(MODULE_NAME, msg)
        else:
#            self.logger.log_notice(MODULE_NAME,"Using existing SUID whitelist")
            pass

        if Whitelists.sgid_master_list == None:
            self.logger.log_notice(MODULE_NAME,"Generating fresh SGID whitelist")
            Whitelists.sgid_master_list = sb_utils.file.fileread.read_files_with_custom_changes("SGID whitelist", sbProps.SGID_WHITELIST, True)
            msg = "Master SGID whilelist: has %d entries" % len(Whitelists.sgid_master_list)
            self.logger.log_info(MODULE_NAME, msg)
        else:
#            self.logger.log_notice(MODULE_NAME,"Using existing SGID whitelist")
            pass

                
        
    ##########################################################################
    def validate_input(self, option):
        """Validate input"""
        if option and option != 'None':
            return 1
        return 0

                    
    ##########################################################################
    def suid_whitelist(self):
        return Whitelists.master_suid_list

    ##########################################################################
    def sgid_whitelist(self):
        return Whitelists.master_sgid_list

    # Return (False,"") if the filename passed (or its canonical name) is on either the SUID or SGID 
    # Returns (True, msg) with msg explaining why the passed filename should be excluded otherwise

    ##########################################################################
    def file_is_whitelisted(self, fileName, whitelist, listtype):
        
        fileName = os.path.normpath(fileName.strip())
        entries = [ fileName ]
        retval = True
        retmsg = "" 

        # comment next 4 lines to not try to resolve symbolic links or non-canonical path names
        real_entry = os.path.realpath(fileName)
        if real_entry != fileName:
            self.logger.log_debug(MODULE_NAME,"%s is a symbolic link or is not canonical, adding it and the real endpoint %s" % (fileName, real_entry))
            entries.append(real_entry)

        why = ""   


        retval = False
        for itemNum in range(len(entries)):
            entry = entries[itemNum]
            if entry in whitelist :
                if itemNum == 0 :   # first entry, which is the normalized path, so return it
                    retmsg = "Found %s on the %s whitelist" % (entry, listtype)
                else:               # ok, might be a resolved path, so indicate so
                    retmsg = "%s has canonical name %s, found on the %s whitelist" % (fileName, entry, listtype)
                retval = True
                break   
                  
                    
        return retval, retmsg    

    # helper routines to check the lists....
    def is_SUID_whitelisted(self, fileName):
        return self.file_is_whitelisted(fileName, self.suid_master_list, "SUID")
    
    def is_SGID_whitelisted(self, fileName):
        return self.file_is_whitelisted(fileName, self.sgid_master_list, "SGID")
 
    def dump_whitelists(self):
        import pprint
        return self.suid_master_list, self.sgid_master_list;
                       
                       
                
# The following two methods are to check the current SUID or SGID whitelist.  The
# return values for both are one of :
# (true, reason)   if on the whitelist, and why
# (false, none)    if not on the whitelist
#
# The reason test will indicate if the file or it's canonically path is on the whitelist

def is_SUID_whitelisted(fileName):
    whitelists = Whitelists()
    return whitelists.is_SUID_whitelisted(fileName)

def is_SGID_whitelisted(fileName):
    whitelists = Whitelists()
    return whitelists.is_SGID_whitelisted(fileName) 

    
def whlists(refresh=False):
    whitelists = Whitelists(refresh=refresh)

if __name__ == '__main__':
    import pprint
    whitelists = Whitelists()
    suidlist, sgidlist = whitelists.dump_whitelists()

    print "SUID whitelist has %d entries" % len(suidlist)
    if "-v" in sys.argv[1:]:
        pprint.pprint (suidlist)     

    print "\nSGID whitelist has %d entries" % len(sgidlist)
    if "-v" in sys.argv[1:]:
        pprint.pprint (sgidlist)     
