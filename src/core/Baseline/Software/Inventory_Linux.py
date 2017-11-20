#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Linux - Software packages and patches
###############################################################################

import sha
import os
import libxml2
import sys
import rpm
import re
import cgi
import time

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.os.info

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()


MODULE_NAME = "Baseline"
MODULE_REV  = "$Rev: 23917 $".strip('$')

    
def collect(infoNode, sha1Packages):

    packageCount = 0

    transet = rpm.TransactionSet()
    match_index = transet.dbMatch()
    for hdr in match_index:
        try:
            textdata = unicode(hdr['summary'].strip(), 'ascii', errors='ignore')
            spat = re.compile("%c" % 0xae)
            textdata = cgi.escape(spat.sub("(R)", textdata))
            xrpm = infoNode.newChild(None, "package", None )
        except (UnicodeEncodeError, UnicodeDecodeError), err: 
            msg = """Unable to encode "%s" - %s""" % (hdr['summary'], err)
            logger.log_err('BaselineReporting', msg )
            xrpm = infoNode.newChild(None, "package", "-")
    
        packageCount = packageCount + 1

        xrpm.setProp("name", unicode(hdr['name'], 'ascii', errors='ignore'))
    
        try:
            xrpm.setProp("epoch", unicode(hdr['epoch'], 'ascii', errors='ignore'))
        except:
            xrpm.setProp("epoch", "")
    
        try:
            xrpm.setProp("version", unicode(hdr['version'], 'ascii', errors='ignore'))
        except: 
            xrpm.setProp("version", "")
     
        try:
            xrpm.setProp("release", unicode(hdr['release'], 'ascii', errors='ignore'))
        except:
            xrpm.setProp("release", "")
    
        
        xrpm.setProp("installtime", str(hdr['installtime']))
    
        try:
            local_date_string = time.strftime("%a %b %d %T %Z %Y", time.localtime(hdr['installtime']))
            xrpm.setProp("install_localtime", local_date_string)
        except:
            xrpm.setProp("install_localtime", "")
    
        xrpm.setProp("summary", textdata)
    
        sha1Packages.update(str(hdr['name']))
        sha1Packages.update(str(textdata))
        sha1Packages.update(str(hdr['epoch']))
        sha1Packages.update(str(hdr['version']))
        sha1Packages.update(str(hdr['release']))
        sha1Packages.update(str(hdr['installtime']))
    
    del transet
    del match_index
   
    logger.log_info(MODULE_NAME, "Found %d installed packages" % packageCount)
    infoNode.setProp("fingerprint", sha1Packages.hexdigest())
    
