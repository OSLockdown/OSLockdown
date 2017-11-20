#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable CUPS browsing mode
#
#

import sys
import re
import os
import sb_utils.os.software

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
from ModuleInfo import getPackageList

class DisableCupsPrinterBrowsing:

    def __init__(self):
        self.module_name = "DisableCupsPrinterBrowsing"
        self.__target_file = "/etc/cups/cupsd.conf"
        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

    ##########################################################################
    def _is_cups_installed(self):
        """ return true/false if CUPS installed
        """
        
        packageList = getPackageList(libraryName=self.module_name)

        messages = {}
        messages['messages'] = []
        # Check for each package in the list. If ONE package is missing,
        # report a not applicable
        for pkg_item in packageList:
            results = sb_utils.os.software.is_installed(pkgname=pkg_item) 
            if results == False:
                msg = "'%s' package is not installed" % pkg_item
                self.logger.warning(self.module_name, 'Not Applicable: ' + msg)
                raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
            else:
                msg = "'%s' package is installed" % pkg_item
                self.logger.info(self.module_name, msg)
                messages['messages'].append(msg)
            
        return messages    
    
    ##########################################################################
    # lines = list of lines in file
    # changes_to_make = list of changes to make, each entry is a two 
    #       element list [ 'tag', 'value' ] - value can be str or int as required
    #                                         or 'None' to indicate tag should be removed
    # isUndo - boolean to indicate this is an Undo operation - for logging

    def process_tag_in_file(self, lines, changes_to_make, isUndo ):
        results = []
        status = 'missing'
        change_rec = []
        
        # we control the caller, so this line should *never* fail
        tag, value = changes_to_make
            
        for linenum in range(len(lines)):
            fields = re.split('(\W+)', lines[linenum])
            
            # we need to skip over any hypothetical whitespace at the start of the line
        
            tagfield = 0
            valuefield = 0
            while tagfield < len(fields) and fields[tagfield].isspace():
                tagfield = tagfield + 1

            if fields[tagfield].startswith('#') :
                continue
            valuefield = tagfield + 2
            
            if len(fields) < valuefield or fields[tagfield] != tag :
                continue
            
            if value == None:   # implicit remove the line
                del(lines[linenum])
                msg = "Removing '%s' line from '%s'" % (tag, self.__target_file)
                results.append(['fix', msg] )
                status = 'removed'
                break
            elif isUndo and value != fields[valuefield]:
                msg = "Reverting '%s' in '%s' back to '%s'" % ( tag, self.__target_file, value)
                results.append(['fix', msg] )
                fields[valuefield] = value
                lines[linenum] = ''.join(fields)
                status = 'changed'
                break
            elif type(value) == type("") and value != fields[valuefield] :
                msg = "Found '%s' in '%s' with unacceptable value of '%s' (should be '%s')" % ( tag, self.__target_file, fields[valuefield], value)
                results.append(['problem', msg])
                msg = "Changed '%s' in '%s' to '%s'" % ( tag, self.__target_file, value)
                results.append(['fix', msg])
                change_rec.append( [tag, fields[valuefield]])
                fields[valuefield] = str(value)
                lines[linenum] = ''.join(fields)
                status = 'changed'
                break
            elif type(value) == type(0) and int(fields[valuefield]) > int(value):
                msg = "Found '%s' in '%s' with unacceptable value of '%s' (should be <= '%s')" % ( tag, self.__target_file, fields[valuefield], value)
                results.append( ['problem', msg ])
                msg = "Changed '%s' in '%s' to '%s'" % ( tag, self.__target_file, value)
                results.append([ 'fix', msg ])
                change_rec.append( [tag, int(fields[valuefield])])
                fields[valuefield] = str(value)
                lines[linenum] = ''.join(fields)
                status = 'changed'
                break
            else :
                msg = "Found '%s' in '%s' with acceptable value of '%s'" % ( tag, self.__target_file, fields[valuefield])
                results.append( ['ok', msg] )
                status = 'found'
                break
        if status == 'missing':
            msg = "Unable to find '%s' in '%s'" % ( tag, self.__target_file)
            results.append( ['problem', msg ])
            msg = "Added '%s %s' to '%s'" % ( tag, value, self.__target_file)
            results.append( ['fix', msg ])
            status = 'added'
            lines.append("%s %s\n" % ( tag, value))
            change_rec.append( [tag, None])  
        return results, change_rec, lines

    ##########################################################################
    def process_file(self, lines, changes_to_make, isUndo = False ):
        
        results = []
        change_record = []
        
        for this_change in changes_to_make:
            
            r, c, lines = self.process_tag_in_file(lines, this_change, isUndo)
            results.extend(r)
            change_record.extend(c)
             
        return results, change_record, lines 

    ##########################################################################
    def scan(self, option=None):

        messages = {}
        messages['messages'] = []

        # first see if all of our dependencies (services, packages) are here...
        # and don't bother if we're missing stuff
        messages.update(self._is_cups_installed())
             
        changes_to_make = [ ['Browsing', 'Off' ] , 
                            ['BrowseAllow', 'none' ] ]

        if not os.path.isfile(self.__target_file):
            msg = "%s file does not exist." % self.__target_file
            
            #indicate that we hit a snag...
            messages['messages'].append(msg)
            change_record = "missing file"
        else:    
            try:
                lines = open(self.__target_file).readlines()
            except Exception, err:
                msg = "Unable to process file %s: %s" % (self.__target_file, str(err))
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        
            results, change_record, lines = self.process_file(lines, changes_to_make, False)
            for msg in results:
                if msg[0] in ['ok', 'problem' ] :
                    self.logger.notice(self.module_name, msg[1] ) 
                    messages['messages'].append(msg[1])
        
        if change_record != []:
            retval = False
        else:
            retval = True
            
        return retval, '', messages
  
    ##########################################################################
    def apply(self, option=None):

        messages = {}
        messages['messages'] = []
        newfile = False
        
        changes_to_make = [ ['Browsing', 'Off' ] , 
                            ['BrowseAllow', 'none' ] ]
        # first see if all of our dependencies (services, packages) are here...
        # and don't bother if we're missing stuff
        messages.update(self._is_cups_installed())

        if not os.path.isfile(self.__target_file):
            lines = []
            msg = "%s file does not exist and will be created" % self.__target_file
            self.logger.notice(self.module_name, msg)
            newfile = True
        else:
            try:
                lines = open(self.__target_file).readlines()
            except Exception, err:
                msg = "Unable to process file %s: %s" % (self.__target_file, str(err))
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

        results, change_record, lines = self.process_file(lines, changes_to_make, False)
        
        for msg in results:
            if msg[0] in ['ok', 'problem', 'fix' ]:
                self.logger.notice(self.module_name, msg[1] ) 
                messages['messages'].append(msg[1])
        
        
        if change_record == [] :
            retval = False
            change_record = ""
        else:
            retval = True
            open(self.__target_file,"w").writelines(lines)

        if newfile == True:
            retval = True
            change_record = ['newfile']
        return retval, str(change_record), messages
                                                            
            
    ##########################################################################
    def undo(self, change_record=None):

        retval = True
        if not change_record or change_record == '': 
            msg = "Unable to perform undo operation without change record."
            self.logger.error(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        messages = {}
        messages['messages'] = []

        changes_to_make = tcs_utils.string_to_dictionary(change_record)
        
        if changes_to_make == ['newfile']:
            fix_count = len(changes_to_make)
            os.unlink(self.__target_file)
            msg = "Removed %s file" % self.__target_file
        else:
            try:
                lines = open(self.__target_file).readlines()
            except Exception, err:
                msg = "Unable to process file %s: %s" % (self.__target_file, str(err))
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

            results , change_record, lines = self.process_file(lines, changes_to_make, True)

            fix_count = 0
            for msg in results:
                if msg[0] in ['fix']:
                    fix_count = fix_count + 1
                    self.logger.notice(self.module_name, msg[1] ) 
                    messages['messages'].append(msg[1])
        
            if fix_count != len(changes_to_make):
                retval = False
                msg = "Unable to revert all changes to %s, no changes will be made" % self.__target_file
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                retval = True
                open(self.__target_file,"w").writelines(lines)
        
        return retval, '', messages
