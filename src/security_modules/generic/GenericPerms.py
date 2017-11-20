#!/usr/bin/env python
#
# Copyright (c) 2012 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import os
import sys
import shutil
import sha

import  xml.sax.saxutils

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.os.software
import sb_utils.file.fileperms
import sb_utils.file.exclusion

try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 


# generate exclusion list early...
sb_utils.file.exclusion.exlist()

# A generic routine to simplify the check/set/undo of the allowed UID/GID/maxPerms of set of files.
# Can be imported by other modules similar to the Enable_Disable_Any_Service routines, just pass the 
# args from the scan/apply/undo on unchanged
##########################################################################
def scan(optionDict={}):

    messages = []
    retval = True

    requiredChanges = {}
    fileList = ''
    
    # These are common to both files
    if 'allowedUnames' in optionDict and optionDict['allowedUnames']:
        requiredChanges['owner'] = optionDict['allowedUnames']
    if 'allowedGnames' in optionDict and optionDict['allowedGnames']:
        requiredChanges['group'] = optionDict['allowedGnames']
    if 'dacs' in optionDict and optionDict['dacs']:
        requiredChanges['dacs'] = optionDict['dacs']
    if 'fileList' in optionDict and optionDict['fileList']:
        fileList = optionDict['fileList']

    options = {'checkOnly':True}        
    if 'globNames' in optionDict and optionDict['globNames']:
        options['globNames'] = optionDict['globNames']
    if 'recursive' in optionDict and optionDict['recursive']:
        options['recursive'] = optionDict['recursive']

    allChanges = sb_utils.file.fileperms.search_and_change_file_attributes(fileList, requiredChanges, options)
            
    if allChanges:
        retval = False
        msg = "Invalid permissions discovered on one or more files"
    else:
        msg = ""
    return retval, msg


##########################################################################
def apply(optionDict={}):

    retval = False
    requiredChanges = {}
    fileList = ''

    allChanges = {}

    # These are common to both files
    if 'allowedUnames' in optionDict and optionDict['allowedUnames']:
        requiredChanges['owner'] = optionDict['allowedUnames']
    if 'allowedGnames' in optionDict and optionDict['allowedGnames']:
        requiredChanges['group'] = optionDict['allowedGnames']
    if 'dacs' in optionDict and optionDict['dacs']:
        requiredChanges['dacs'] = optionDict['dacs']
    if 'fileList' in optionDict and optionDict['fileList']:
        fileList = optionDict['fileList']

    options = {'checkOnly':False}        
    if 'globNames' in optionDict and optionDict['globNames']:
        options['globNames'] = optionDict['globNames']
    if 'recursive' in optionDict and optionDict['recursive']:
        options['recursive'] = optionDict['recursive']

    allChanges = sb_utils.file.fileperms.search_and_change_file_attributes(fileList, requiredChanges, options)
    
    if allChanges:
        retval = True
    return retval, str(allChanges)


##########################################################################
def undo(change_record=None):

    retval = False
    # catch the case were we get a straight text string....
    if type(change_record) != type ({}):
	change_record = tcs_utils.string_to_dictionary(change_record)


    allChanges = {}
    
    options = {'checkOnly':False ,'exactDACs' : True}
    
    # we *do* need to split these out now, as each file may have an individual set of changes....
    for fileName, changesToUndo in change_record.items():
        changes = sb_utils.file.fileperms.search_and_change_file_attributes(fileName, changesToUndo, options)         
        allChanges.update(changes)

    if allChanges:
        msg = "Undo Performed"
        retval = True
    else:
        msg = "No changes were reverted"
        retval = False
    
    return retval, msg

