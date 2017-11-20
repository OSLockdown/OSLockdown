#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Functions to work with standard UNIX configuration files
# to validate their structure. 
#
# For example, the /etc/passwd file is comprised of single
# line entries. Each line is comprised of 7 fields separated
# by colons.
#
# The functions in this module should simply be the name
# of the file to be checked (minus full path) and should
# do appropriate logging and simply return True or False
# to indicate if it is valid.
#


import os
import sys
import re
import shutil

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sbProps
import sb_utils.file.dac

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()


MODULE_NAME = "sb_utils.os.validateFile"

##############################################################################
def passwd(configFile='/etc/passwd'):
    """
    Verify passwd file according to passwd(5) structure
    """

    
    logger.log_info(MODULE_NAME, "Validating %s..." % configFile)
    if not os.path.isfile(configFile):
        logger.log_err(MODULE_NAME, "%s is not a file" % configFile)
        return False


    try:
        in_obj = open(configFile, 'r')
    except IOError, err:
        msg = 'Unable to open %s: %s' % (configFile, err)        
        logger.log_err(MODULE_NAME, msg)
        return False

    # Check to see if immutable attribute is enabled
    sb_utils.file.dac.isImmutable(configFile)

    regexp  = re.compile('( |[A-Z])+')
    regexp2 = re.compile('( )+')
    for lineNumber, line in enumerate(in_obj.readlines()):
        fields = line.split(':')
        if len(fields) != 7:
             msg = "Line number %d of %s does not have exactly 7 fields" % (lineNumber+1, configFile)
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # Ensure first field (username) does not contains spaces or uppercase letters
        if regexp.search(fields[0]):
             msg = "Line number %d of %s, the first field must not contain spaces or uppercase letters" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # UID field must be an integer
        if fields[2].isdigit() == False:
             msg = "Line number %d of %s, third field (UID) must be an integer" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # GID field must be an integer
        if fields[3].isdigit() == False:
             msg = "Line number %d of %s, fourth field (GID) must be an integer" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # GID field must be an integer
        if regexp2.search(fields[5]) or regexp2.search(fields[6]):
             msg = "Line number %d of %s, fields 5 and 6 must not contain spaces" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

    return True
        

##############################################################################
def group(configFile='/etc/group'):
    """
    Verify passwd file according to passwd(5) structure
    """

    logger.log_info(MODULE_NAME, "Validating %s..." % configFile)
    if not os.path.isfile(configFile):
        logger.log_err(MODULE_NAME, "%s is not a file" % configFile)
        return False


    try:
        in_obj = open(configFile, 'r')
    except IOError, err:
        msg = 'Unable to open %s: %s' % (configFile, err)        
        logger.log_err(MODULE_NAME, msg)
        return False

    # Check to see if immutable attribute is enabled
    sb_utils.file.dac.isImmutable(configFile)

    regexp  = re.compile('( |[A-Z])+')
    regexp2 = re.compile('( )+')
    for lineNumber, line in enumerate(in_obj.readlines()):
        fields = line.split(':')
        if len(fields) != 4:
             msg = "Line number %d of %s does not have exactly 4 fields" % (lineNumber+1, configFile)
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # Ensure first field (group) does not contains spaces or uppercase letters
        if regexp.search(fields[0]):
             msg = "Line number %d of %s, the first field must not contain spaces or uppercase letters" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # GID field must be an integer
        if fields[2].isdigit() == False:
             msg = "Line number %d of %s, the third field (GID) must be an integer" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

        # Group members must have no spaces
        if regexp2.search(fields[3]):
             msg = "Line number %d of %s, the last field must not contain spaces" % (lineNumber+1, configFile) 
             logger.log_notice(MODULE_NAME, msg)
             in_obj.close()
             return False

    return True
        



if __name__ == '__main__':
    print group()
