#!/usr/bin/env python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#


import sys
import os
import shutil

sys.path.append("/usr/share/oslockdown")



#TODO: Error handling and exception handling has to be improved here
#      Unify error handling

from sb_utils.misc import tcs_utils
import sb_utils.SELinux

##############################################################################
def generate_diff_record(fromfilename, tofilename, calling_ident=None):
    """
    Generate a string containing a unified diff between the specified files.
    """
    diff_string = ""
    cmd = "/usr/bin/diff -Nur " + fromfilename + ' ' + tofilename
    out = tcs_utils.tcs_run_cmd(cmd, True)
    if out[0] == 2:
        msg = "ERROR: Unable to generate diff record."
        raise tcs_utils.ActionError(msg)

    elif out[0] == 1:
        diff_string = out[1]

    return diff_string

##############################################################################
def revert_to_diff(diff, target_file):
    """
    Helper function to revert file to previous state.
    """
    
    try:
        # TODO: find more elegant way of doing this
        tmp_file = open("trash", 'w')
        tmp_file.write(diff)
        tmp_file.close()
        
    except Exception, err:
        msg = "Cannot create tempory undo file (" + str(err) + ")."
        raise tcs_utils.ActionError(msg)
    
    cmd = "/usr/bin/patch -p0 -s -t < trash"
    ret = tcs_utils.tcs_run_cmd(cmd, True)
    os.unlink('trash')
    
    if ret[0] != 0:
        msg = "Unable to revert file: (%s)." % ret[1].rstrip('\n')
        raise tcs_utils.ActionError(msg)

    return (True, '')


##############################################################################
def move_file_over(tmp_file, target_file):
    """
    Copy temp file over to target file, ensuring target's permissions are not
    changed
    """
    
    try:
        shutil.copymode(target_file, tmp_file)
        shutil.copy2(tmp_file, target_file)
        shutil.copymode(tmp_file, target_file)
        sb_utils.SELinux.restoreSecurityContext(target_file)
        os.unlink(tmp_file)
    
    except Exception, err:
        msg = "Unexpected error replacing original file (" + str(err) + ")."
        raise tcs_utils.ActionError(msg)    
    
    return (True, '')
