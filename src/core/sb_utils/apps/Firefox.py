#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Functions to manage Mozilla Firefox Configuration Files
##############################################################################

import sys
import pwd
import os
import re

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import sb_utils.file.exclusion
import sb_utils.acctmgt.users

logger = TCSLogger.TCSLogger.getInstance()

MODULE_NAME = "MozillaFirefox"
MODULE_REV = "$Rev: 23917 $".strip('$').strip()


##############################################################################
def getUserPrefFiles():
    """
    Get a list of home directories from the passwd database
    and return list of Firefox prefs.js files
    """ 
    # We must alias 'os' because of child sb_utils.os module
    from sb_utils.misc.unique import unique

    dirloc = '.mozilla/firefox'
    pref_file_name = 'prefs.js'
    pref_files = []
    homedirs = []
#    for user in pwd.getpwall():
    for userName in sb_utils.acctmgt.users.local_AllUsers():
        user = pwd.getpwnam(userName)
        is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(user.pw_dir)
        if is_excluded == True:
            logger.debug(MODULE_NAME, why_excluded)
        else:
            homedirs.append(user.pw_dir)

    homedirs = unique(homedirs)
    for mdir in homedirs:
        for root, dirs, files in os.walk(os.path.join(mdir, dirloc)):
            for name in files:
                if name == pref_file_name:
                    pref_files.append(os.path.join(root, name))

    return pref_files

##############################################################################
def getSettings(prefs_file=None):
    """
    Extract user_prefs settings from a user's prefs.js file and return
    a dictionary
    """
    settings = {}
    if not prefs_file: 
        return settings
    if not os.path.isfile(prefs_file):
        return settings
    try:
        inprefs = open(prefs_file, 'r')
    except (IOError, IOError), err:
        msg = "Unable to open %s (%s)" % (prefs_file, str(err))
        logger.error(MODULE_NAME, msg)
        return settings

    lines = inprefs.readlines()
    inprefs.close()

    # Use Regex to extract the key-value pairs
    # Sample: user_pref("security.warn_entering_secure", false);
    pat = re.compile('user_pref\("(\S+)",\s+(.*)\);')

    for line in lines:
        if not line.startswith('user_pref('):
            continue
        line = line.rstrip('\n')
        line = line.strip(' ')
        mat = pat.match(line)
        key = mat.group(1)
        cur_value = mat.group(2)
        #cur_value = cur_value.strip('"')
        settings[key] = cur_value

    return settings

##############################################################################
def setParameters(prefs_file=None, params=None):
    """
    Set parameters in given Firefox preferences file. If the value in the
    key-pair-value is 'unset' then remove the key from the file.

    Return:
       True for success 
      False for failure
    """

    if not prefs_file: 
        return False
    if not os.path.isfile(prefs_file):
        return False

    if type(params) != type({}):
        return False

    try:
        inprefs = open(prefs_file, 'r')
    except (IOError, IOError), err:
        msg = "Unable to open %s (%s)" % (prefs_file, str(err))
        logger.error(MODULE_NAME, msg)

    lines = inprefs.readlines()
    inprefs.close()
    pat = re.compile('user_pref\("(\S+)",\s+(.*)\);')

    newfile = []
    for line in lines:
        if not line.startswith('user_pref('):
            newfile.append(line)
            continue
        line = line.rstrip('\n')
        line = line.strip(' ')
        mat = pat.match(line)
        key = mat.group(1)
        cur_value = mat.group(2)
        #cur_value = cur_value.strip('"')
        
        if not params.has_key(key):
            line = """user_pref("%s", %s);\n""" % (key, cur_value)
            newfile.append(line)
            continue

        if params[key] == cur_value:
            newfile.append("%s\n" % line)  
            del params[key]
            continue

        # Do not re-write keys which have been marked as 'unset'
        if params[key] == 'unset':
            del params[key]
            continue

        line = """user_pref("%s", %s);\n""" % (key, params[key])
        newfile.append(line)
        del params[key]

    # Append remaining key-pair-values left over
    for key in params.keys():
        line = """user_pref("%s", %s);\n""" % (key, params[key])
        newfile.append(line) 
        del params[key]

    try:
        inprefs = open(prefs_file, 'w')
        inprefs.write(''.join(newfile))
    except (IOError, IOError), err:
        msg = "Unable to write to  %s (%s)" % (prefs_file, str(err))
        logger.error(MODULE_NAME, msg)
        return False

    return True
