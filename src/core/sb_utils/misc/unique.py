#!/usr/bin/python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#  Return a unique (unordered) list

def unique(myarray=None):
    """
    Accept an array and return a unique list of items
    (no repeats). This is to help python 2.3 because it does
    not have a the set() function
    """
    if myarray == None:
        return False

    myhash = {}
    for key in myarray:
        myhash[key] = True

    newarray = []
    for key in myhash.keys():
        newarray.append(key)

    return newarray
