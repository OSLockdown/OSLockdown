#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

import os
import sys
import shutil
import logging

# read the file in, ignoring blanks/comments/duplicates

def read_file_lines(fileName):
    fileList = []
    try:
        for line in open(fileName):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fileList.append(line)
    except Exception, err:
#        print >>sys.stderr,"   Unable to read %s : %s" % (fileName, str(err))
        fileList = []
    return fileList
    
def preserve_custom_changes(fileName, pretend=False):
    logging.getLogger('AutoUpdate').info("Checking for user customization of %s..." % (fileName))
    newStockFile = fileName
    oldStockFile = "%s.previous" % fileName
    customFile = "%s.custom" % fileName
        
    # Ok, read all files (if exist) in to arrays - don't worry on order 
    
    newStockList = read_file_lines(newStockFile)
    oldStockList = read_file_lines(oldStockFile)
    customList = read_file_lines(customFile)
    
    addList = []
    
    for item in oldStockList:
        if item not in newStockList and item not in addList and item not in customList:
            addList.append(item)

    if addList:
        logging.getLogger('AutoUpdate').info( "  Preserving the following lines to from %s in %s" % (os.path.basename(oldStockFile), os.path.basename(customFile)))
        
        for item in addList:
            logging.getLogger('AutoUpdate').info("    %s" % item)
        
        if not pretend:
            outFile = open(customFile,"a")
            for item in addList:
                outFile.write("%s\n" % item)        
            outFile.close()
            
    if oldStockList:
        try:
            os.unlink(oldStockFile)
        except Exception,err:
            pass
            logging.getLogger('AutoUpdate').error( str(err))

def preserveAllChanges(cfgDir="/var/lib/oslockdown/files", pretend=False):
                    
    candidates = [ 'sgid_whitelist', 'suid_whitelist', 'exclude-dirs', 'inclusion-fstypes' ]
    for candidate in candidates:
        preserve_custom_changes("%s/%s" % (cfgDir, candidate), pretend)

if __name__ == "__main__":
    preserveAllChanges()
    
