#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Functions to work with editting the various syslog.conf variants
# out there. 
#

import os
import sys
import re
import shutil
import traceback

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import sb_utils.acctmgt.acctfiles
try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()


#  
# These routines (accessed by the process_arbitrary_file(filename, elements, action) method,
# are designed to look for lines in a file and either add them if not found, or delete them if found.
# Currently it can't look for a line which only needs a tweak to a parameter and indicate that the parameter
# has ben altered, although perhaps it could do this with some work.

# filename = name of the file to be examined (will be re-written if altered if action is 'apply' or 'undo', with perms set to 0600
# action = 'scan', 'apply', or 'undo'
# elements = array of 'things to do'

# Each 'things to do' is a dictionary with:
#  'search' = array of things to look for
#        if 'action' is 'scan' or 'apply' then each target to look for is considered to be a regular expression
#        if 'action' is 'undo' an exact match is required, *unless* there is a dictionary entry for 'regex', which indicates
#           the undo will look for a regex instead
#  'replace_with' = line to replace with if 'search' isn't found.  Not required if action == undo
#  

class Found_it(Exception):
    pass


##########################################################################
# quickly try and take a regular expression search string and 'textify' it for printing

def _convert_pattern_to_text(pattern):
    conversions = [ [ r"\w+", " "],
                    [ r"\w" , " "],
                    [ r"^" , ""],
                    [ r"\s+", " "],
                    [ r"\s", " "],
                    [ "\\",  ""]]
                    
    for conv in conversions:
        pattern = pattern.replace(conv[0], conv[1])
        
    return pattern
         
##########################################################################
def _process_arbitrary_file_element(filename, lines, element, action):
    messages = []
    changes = []
    msg = ''
    if action == 'undo':
    
        search_re = None
        if element.has_key('regex'):       
            search_re = re.compile(element['search'])
        
        for linenum in range(len(lines)):
            found_it = False
            
            # indented for clarity
            if      (search_re and search_re.search(lines[linenum])) or \
                    (not search_re and lines[linenum] == element['search']) :
                msg = ['fix', "Removing line '%s' from %s" % (element['search'].strip(), filename)]
                messages.append(msg)
                lines.pop(linenum)
                changes.append({})
                break
    elif action in ['apply', 'scan']:
        to_add = element['replace_with']
        element['re'] = []

        for searchphrase in element['search']:
            element['re'].append(re.compile(searchphrase))
        found_it = False
        try:
            for search_re in element['re']:                
                for linenum in range(len(lines)):
                    thisline = lines[linenum]
                    located = search_re.search(thisline)
                    if located:
                        found_text = thisline[located.start():located.end()].strip()
                        raise Found_it
                msg = ['problem', "Scan : did not find line equivalent to '%s' in '%s'" % (_convert_pattern_to_text(search_re.pattern), filename)]
                messages.append(msg)
        except Found_it:
            found_it = True    
            
        if found_it == True:
            msg = ['ok', "Scan : found '%s' in %s" % (found_text, filename) ]
            messages.append(msg)
        else:
            msg = ['fix',"Apply: adding '%s' to file %s" % (to_add, filename)]
            messages.append(msg)
            lines.append("%s\n" % to_add)
            changes.append({'search':"%s\n" % to_add})  
 
    return lines, messages, changes
 
##########################################################################
def process_arbitary_file(filename, elements, action):
    messages = []
    changes_made = False
    changes = []
    
    # walk through the elements, compiling the regular expressions for searching *IF* we are in scan/apply mode
    # in undo we're looking for exactly what we put there.  If the user modifies the file that is their lookout
           
    lines = []
    if os.path.exists(filename):
        try:
            lines = open(filename, 'r').readlines()
        except:
            msg = ['error', "ERROR: Unable to read %s" % filename]
    else:
        msg = ['ok', "No such file %s" % filename]
        messages.append(msg)
        return messages, changes
    try:
        for element in elements:
            lines, m, c = _process_arbitrary_file_element(filename, lines, element, action)
            messages.extend(m)
            changes.extend(c)
        if action in ['apply', 'undo' ] and changes != [] :
            try:    
                open(filename, 'w').writelines(lines)
                changes_to_make = {'dacs': 0600}
                ignore_results = sb_utils.acctmgt.acctfiles.change_file_attributes( filename, changes_to_make)
            except Exception, E:
                msg = ['error', "ERROR: Unable to write changes to '%s'" % filename]
                messages.append(msg)
    except Exception, E:
        print traceback.print_exc(file=sys.stderr)
        msg = ['error', "%s: Unable to process %s" % (action, filename)]
        messages.append(msg)

    return messages, changes
         
 
