#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Functions to work with standard UNIX configuration files
# which operate on key/pair values separated by a standard delimiter
# or just white space.  KEY MUST BE ALPHANUMERIC+dash+underscore+space
#
# For example, Solaris might set CMASK=022 in /etc/default/init
#


import os
import sys
import re
import shutil

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.SELinux

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()

def makeRegex(delimiters):
    """
    Ok, we want to generate our regular expression matching based on possible delimiters.
    First see if delimiters is a string, if so, there are no 'options'
    If delimiters is a list, then we have possiblities, so build a list of these to pass through
    Note that if delimiters *can* contain regex specific metastrings, such as '\w', or '[ \t]'
    """
    
    delimStr = ""
    if type(delimiters) == type(''):
        delimStr = delimiters
    else:
        delimStr = '|'.join(delimiters)
    
    # Ok, heres the *pattern* for the regex, in exploded terms for ease of understanding
    # Regex is spelled out here for clarity with each 'group' on a separate line.  We're not using
    # the re.VERBOSE setting to avoid having to escape things. Note that group three
    # (the delimeter string) uses a %s so the actual possible strings are inserted.
    #   ^(\s*)                 # any number of leading whitespace
    #    ([\S].*?)             # one non-whitespace followed by any number of characters
    #    ([ \t]*)              # optional space/tab characters
    #    (%s)                  # optential delimiter(s)
    #    ([ \t]*)              # optional space/tab characters
    #    (.*)$                 # the rest of the line
    
            
    regex_pattern = r'''^(\s*)([\S].*?)([ \t]*)(%s)([ \t]*)(.*)$''' % delimStr
    
    try:
        regex = re.compile(regex_pattern)
    except Exception, err:
        msg = "Unable to generate regex to parse config file lines using delimeter '%s' -> %s" % (delimStr, str(err))
        logger.error('sb_utils.os.config.makeRegex', msg)
        raise tcs_utils.ActionError('sb_utils.os.config.makeRegex',msg)
    
    return regex
    
##############################################################################
def get_list(configfile=None, delim='='):
    """
    Get list of parameters and return dictionary
    """
 
    paramdict = {}

    if configfile == None: return None
    if delim == None:delim = '='
    if not os.path.isfile(configfile): return None

    try:
        in_obj = open(configfile, 'r')
    except IOError, err:
        msg = 'Unable to open %s: %s' % (configfile, err)        
        logger.error('sb_utils.os.config', msg)
        return None

    search_pattern = makeRegex(delim)
        
    for line in in_obj.readlines():
        
        match = search_pattern.search(line)
        if not match: continue
       
        try:
            # we know we'll have 4 match groups if we got here (any of which *possibly* empty)
            # we only care about the param and value elements at the moment
            
            (prefixFound, paramFound, delimPrefix, delimFound, delimSuffix, valueFound) = match.groups()
        except ValueError:
            raise
            continue

        if paramFound:
            paramFound = paramFound.strip()
            if not delimFound: delimFound = ''
            paramdict[paramFound] = valueFound.strip()
    
    in_obj.close()
    return paramdict

def dumpit(text,val):
    print "%s " % text,
    if val:
        print "(%d) <%s>"  % (len(val),val)
    else:
        print "(--) NONE"
    
    
##############################################################################
def setparam(param=None, value=None, delim='=', configfile=None):
    """
    Set parameter in configuration file.
    Return False on failure or previous value of parameter
              (return empty string if parameter was not previously set)
    """
    if configfile == None: return None
    configfile_new = configfile + '.new'
    if delim == None: delim = '='
    if value == None: return None
    if not os.path.isfile(configfile): return None
    originalValue = ''
    valueFound = ''

    if type(delim) == type(' '):
        defaultDelim = delim
    else:
        defaultDelim = delim[0]
    search_pattern = makeRegex(delim)
    msg = ''
    try:
        in_obj = open(configfile, 'r')
        out_obj = open(configfile_new, 'w')
    except IOError, err:
        msg = 'Unable to open %s: %s' % (configfile, err)        
        logger.error('sb_utils.os.config', msg)
        return False

    foundit = False
    for line in in_obj.readlines():
        match = search_pattern.search(line)
        if match: 
            # 
            (prefixFound, paramFound, delimPrefix, delimFound, delimSuffix, valueFound) = match.groups()
# Uncomment the following to see what *actually* matched
#            dumpit('prefixFound',prefixFound)
#            dumpit('paramFound',paramFound)
#            dumpit('delimPrefix',delimPrefix)
#            dumpit('delimFound',delimFound)
#            dumpit('delimSuffix',delimSuffix)
#            dumpit('valueFound',valueFound)
            
            if param == paramFound:
                valueFound = valueFound.rstrip('\n')
                line = str(prefixFound + paramFound + delimPrefix +delimFound + delimSuffix + value + '\n')
                foundit = True
                originalValue = valueFound
                msg = "Resetting '%s' to '%s' in %s" % (str(paramFound), str(value), configfile)
#                dumpit('line',line) 
            out_obj.write(line)
        else:
            out_obj.write(line)

    # If it was not found, append the setting to the end of the file
    # use the first character of the delimiter, just in case we were
    # allowing a choice of potential delimiter characters
    if not foundit:
        msg = "Set '%s' to '%s' in %s" % (str(param), str(value), configfile) 
        
        out_obj.write(param + defaultDelim + value + '\n')

    in_obj.close()
    out_obj.close()

    try:
        shutil.copymode(configfile, configfile_new)
        shutil.copy2(configfile_new, configfile)
        sb_utils.SELinux.restoreSecurityContext(configfile)
        os.unlink(configfile_new)
    except OSError, err:
        logger.error('sb_utils.os.config', err)
        return False

    logger.log_debug('sb_utils.os.config', msg)
#    dumpit('originalValue',originalValue)
    return originalValue

##############################################################################
def unsetparam(param=None, delim='=', configfile=None):
    """
    Set parameter in configuration file.
    Return False on failure or previous value of parameter
              (return empty string if parameter was not previously set)
    """

    if configfile == None: return None
    configfile_new = configfile + '.new'
    if delim == None: delim = '='
    if not os.path.isfile(configfile): return None

    try:
        in_obj = open(configfile, 'r')
        out_obj = open(configfile_new,'w')
    except IOError, err:
        msg = '%s - %s' % (configfile, err)
        logger.error('sb_utils.os.config', msg)
        return False

    search_pattern = makeRegex(delim)

    for line in in_obj.readlines():
        match = search_pattern.search(line)
        # if we have a match for the basic line style, see if the param matches.  If so, swallow it and move on
        if match :
            (prefixFound, paramFound, delimPrefix, delimFound, delimSuffix, valueFound) = match.groups()
            
            if paramFound == param:                
                continue
        out_obj.write(line)

    in_obj.close()
    out_obj.close()

    try:
        shutil.copymode(configfile, configfile_new)
        shutil.copy2(configfile_new, configfile)
        sb_utils.SELinux.restoreSecurityContext(configfile)
        os.unlink(configfile_new)
    except OSError, err:
        logger.error('sb_utils.os.config', err)
        return False

    return True

