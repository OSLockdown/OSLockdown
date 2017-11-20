#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import pwd
import os
import re

sys.path.append('/usr/share/oslockdown')
import sbProps
import TCSLogger
try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

import tcs_utils
import sb_utils.os.info


MODULE_NAME   = "sb_utils.gdm"
GCONF_COMMAND = "/usr/bin/gconftool-2"

CONFIG_SOURCE = ""

for cfg in [ '/etc/gconf/gconf.xml.mandatory', '/etc/opt/gnome/gconf/gconf.xml.mandatory']: 
    if os.path.exists(cfg):
        CONFIG_SOURCE = "xml:readwrite:%s" % cfg
        break

##############################################################################
def get(paramKey=None):

    if paramKey == None or sb_utils.os.info.is_solaris() == True:
        return None

    if CONFIG_SOURCE == "":
        msg = "Unable to locate gconf.xml.mandatory file to get value from"
        logger.log_err(MODULE_NAME, msg)
        return None
        
    cmdString = "%s --direct --config-source %s --get %s" % \
         (GCONF_COMMAND, CONFIG_SOURCE, str(paramKey))

    output = tcs_utils.tcs_run_cmd(cmdString, True)
    keyValue = None
    if output[0] != 0:
        msg = "Unable get GDM '%s' key from %s (%s)" % (paramKey, CONFIG_SOURCE, output[2])
        logger.log_err(MODULE_NAME, msg)
    else:
        if output[2].strip().startswith('No value set for ') :
            msg = "GDM '%s' key is not set" % paramKey
        else:
            msg = "GDM '%s' key is set" % paramKey
            keyValue = output[1].strip()
        logger.log_info(MODULE_NAME, msg)

    return keyValue

##############################################################################
def set(paramKey=None, paramValue=None, dataType=None):

    if CONFIG_SOURCE == "":
        msg = "Unable to locate gconf.xml.mandatory file to set value in"
        logger.log_err(MODULE_NAME, msg)
        return None

    if paramKey == None or paramValue == None:
        return False

    if dataType == None or sb_utils.os.info.is_solaris() == True:
        return False

    dataType = str(dataType)
    if dataType not in ['int', 'bool', 'float', 'string']:
        msg = "Unsupported data type: %s" % dataType
        logger.log_err(MODULE_NAME, msg)
        return False

    if dataType == 'string':
        cmdString = "%s --direct --config-source %s --type %s --set %s \"%s\"" % \
                  (GCONF_COMMAND, CONFIG_SOURCE, dataType, str(paramKey), paramValue)
    else:
        cmdString = "%s --direct --config-source %s --type %s --set %s %s" % \
                  (GCONF_COMMAND, CONFIG_SOURCE, dataType, str(paramKey), paramValue)

    output = tcs_utils.tcs_run_cmd(cmdString, True)
    if output[0] != 0:
        msg = "Unable set GDM \"%s\" key to \"%s\" [%s](%s)" % (paramKey, paramValue, 
                                                                output[0], output[2])
        logger.log_err(MODULE_NAME, msg)
        return False

    msg = "GDM \"%s\" key set to \"%s\" in %s" % (paramKey, paramValue, CONFIG_SOURCE)
    logger.log_info(MODULE_NAME, msg)
    return True

##############################################################################
def unset(paramKey=None):

    if CONFIG_SOURCE == "":
        msg = "Unable to locate gconf.xml.mandatory file to clear value from"
        logger.log_err(MODULE_NAME, msg)
        return None

    if paramKey == None or sb_utils.os.info.is_solaris() == True:
        return None

    cmdString = "%s --direct --config-source %s --unset %s" % \
         (GCONF_COMMAND, CONFIG_SOURCE, str(paramKey))

    output = tcs_utils.tcs_run_cmd(cmdString, True)
    if output[0] != 0:
        msg = "Unable unset GDM \"%s\" key in %s: (%s) " % (paramKey, CONFIG_SOURCE, output[2])
        logger.log_err(MODULE_NAME, msg)
        return False

    msg = "GDM \"%s\" key unset  in %s" % (paramKey, CONFIG_SOURCE)
    logger.log_info(MODULE_NAME, msg)
    return True

