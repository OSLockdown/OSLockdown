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
    import sb_utils.file.dac
    
except ImportError, merr:
    print "Unable to load modules: %s" % merr
    sys.exit(1)

try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

MODULE_NAME = 'sb_utils.file.fileread'

# In order we should read the stock, then modify with the profile, and finally 
# modify with the box specific.
# IE - work from generic to specific

customMods = [ ('profile specific customization', '.profile'),
	       ('box specific customization' , '.custom'),
             ]
                            
##########################################################################
def read_file_entry(listtype, fileName, isrequired, fileType):
    
    if not os.path.exists(fileName) or not os.path.isfile(fileName):
        if isrequired:
            msg = "%s file %s does not exist or is not a file but is required." % (listtype, fileName)
            logger.error(MODULE_NAME, msg);
        else:
            msg = "%s file %s does not exist or isn't a file - skipping it because it is optional" % (listtype, fileName)
            logger.info(MODULE_NAME, msg);
        return [];

    try:
        statinfo = os.stat(fileName)
    except OSError, err:
        msg = "Unable to stat %s %s file: %s" % (fileType, listtype, err)
        logger.debug(MODULE_NAME, msg)
        return 
    except IOError, err:
        msg = "Unable to stat %s %s file: %s" % (fileType, listtype, err)
        logger.debug(MODULE_NAME, msg)
        return 
    
    
    #
    # Make sure owner and perms are okay
    #
    msg = "Checking ownership and permissions of %s %s %s" % (fileType, listtype, fileName)
    logger.debug(MODULE_NAME, msg)

    mode  = int(oct(stat.S_IMODE(statinfo.st_mode)))
    owner = pwd.getpwuid(statinfo.st_uid)[0]

    if owner != 'root':
        msg = "%s %s %s not owned by root" % (fileType, listtype, fileName)
        logger.warn(MODULE_NAME, msg)
    if not sb_utils.file.dac.isPermOkay(fileName, '0440', True):
        msg = "%s %s %s permissions are more permissive than 440" % (fileType, listtype, fileName)
        logger.warn(MODULE_NAME, msg)

    # Load authorized list of files
    fileList = []
    try:
        for line in open(fileName, 'r'):
            line = line.strip() 
            if not line or line.startswith("#"):
                continue 
            if line not in fileList:
                if os.path.isdir(line) and not line.endswith('/'):
                  line += '/'
                fileList.append(line)
        msg = "Loaded %s %s %s" % (fileType, listtype, fileName)
        logger.debug(MODULE_NAME, msg)
    except IOError, err:
        msg = "Unable to read %s %s %s: %s" % (fileType, listtype, fileName, err)
        logger.error(MODULE_NAME, msg)
    return fileList


def merge_custom_changes(stockList, customList, fileType):
    if customList:          
        customRemoves = []
        for entry in customList:
            if entry.startswith('-') and allowRemoval:
                customRemoves.append(entry[1:])
            else:
                if entry not in stockList:
                    stockList.append(entry)

        for entry in customRemoves:                              
            if entry in stockList:
                stockList.remove(entry[1:])
                msg = "explicitly removing '%s' from %s as per %s" % (entry[1:], fileType)
                logger.notice(MODULE_NAME, msg) 

    return stockList
    
##########################################################################
def read_files_with_custom_changes( listtype, stockFile = None, allowRemoval = False):

    
    if stockFile:
        stockList = read_file_entry(listtype=listtype, fileName=stockFile, isrequired=True, fileType="Stock")
    else:
        msg = "No filename provided for stock '%s' file - skipping module to prevent potentially bricking your OS" % listtype
        raise tcs_utils.ScanError(msg) 
        
    
    for modType, modSuffix in customMods:
        customFile = stockFile + modSuffix
        
        if customFile:
            customList = read_file_entry(listtype=listtype, fileName=customFile, isrequired=False, fileType = modType)

    
        stockList = merge_custom_changes(stockList, customList, fileType=modType)
        
    if not stockList:
        msg = "Final '%s' list is empty/unprocessable - aborting remainder of Profile to prevent potentially bricking your OS" % listtype
        raise tcs_utils.AbortProfile(msg) 
    return stockList
    
if __name__ == "__main__":
    loggerInst = TCSLogger.TCSLogger.getInstance()
    loggerInst.force_log_level(7)
    loggerInst._fileobj = sys.stdout
 
    fileList = read_files_with_custom_changes('whitelist', '/var/lib/oslockdown/files/suid_whitelist', True)
    print fileList
