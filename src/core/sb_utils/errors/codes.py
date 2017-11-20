#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# codes.py
# List of error codes & exceptions
#


##############################################################################
# Exit Codes

OK                              = 0
INVALID_CLI_SYNTAX              = 1
INVALID_CLI_PARAM               = 2
INTERNAL_IMPORT_ERROR           = 3
INTERNAL_INITIALIZE_ERROR       = 4
INTERNAL_OTHER_ERROR            = 5


##############################################################################
# Error Messages
#  - Standard error messages to be used by modules
#  - Functions to return pre-formatted error messages


def os_na(osname=None, name=None):
    """
      Specific 'name' is not applicable to 'osname'
    """

    if osname == None or name == None:
        msg = "Not part of this operating system's standard distribution." 
    else:
        msg = "'%s' is not part of the standard %s distribution" % \
         (name, osname)

    return msg
