#!/usr/bin/python
###############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Solaris - Software packages and patches 
###############################################################################

import sha
import os
import libxml2
import sys
import re
import cgi
import time
from datetime import datetime

sys.path.append("/usr/share/oslockdown")
sys.path.append("/usr/share/oslockdown/lib/python")
import TCSLogger
import sb_utils.os.info

PACKAGES_DIR = "/var/sadm/pkg"
INSTALLED_FILES = "/var/sadm/install/contents"

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()


def collect(packageNode, patchesNode, sha1Packages, sha1Patches):

    for pkgName in os.listdir(PACKAGES_DIR):
         pkgInfoFile = os.path.join(PACKAGES_DIR, pkgName, "pkginfo")
         try:
             inObject = open(pkgInfoFile, 'r')
         except (IOError, OSError), err:
             print >> sys.stderr, "ERROR: %s" % err
             continue

         pkgMetaData = {}
         patchList = []
         for line in inObject.readlines():
             line = line.strip()
             try:
                 keyName  = unicode(line.split('=')[0], 'ascii', errors='ignore')
                 keyValue = ''.join(line.split('=')[1:])
                 if keyName == 'VERSION':
                     if line.count(',') > 0:
                         keyValue = line.split('=')[1]
                         pkgvers = keyValue.split(',')[0]
                         pkgrel  = line.split(',')[1]
                     else:
                         pkgvers = keyValue
                         pkgrel = '-'

             except Exception, err:
                 print >> sys.stderr, "ERROR: %s" % err
                 continue

             keyValue = keyValue.replace('&', 'and')
             keyValue = keyValue.replace('>', '%gt;')
             keyValue = keyValue.replace('<', '%lt;')

             pkgMetaData[keyName] = unicode(keyValue, 'ascii', errors='ignore')

         inObject.close()
         if not pkgMetaData.has_key('PKG'):
             continue

         if not pkgMetaData.has_key('VERSION'):
             continue

         pkgRecord = packageNode.newChild(None, "package", None )
         pkgRecord.setProp("name", pkgMetaData['PKG'])
         pkgRecord.setProp("version", pkgvers)
         pkgRecord.setProp("release", pkgrel)

         if pkgMetaData.has_key('NAME'):
             pkgRecord.setProp("summary", pkgMetaData['NAME'])
             sha1Packages.update(pkgMetaData['NAME'])
         else:
             pkgRecord.setProp("summary", "-")
             sha1Packages.update("-")

         # Installation Times
         if not pkgMetaData.has_key('INSTDATE'):
             installTime = ""
             installLocalTime = ""
         else:
             try:
                installTime = time.strptime(pkgMetaData['INSTDATE'], "%b %d %Y %H:%M")
                epochTime = int(time.mktime(installTime))
                installTime = str(epochTime)
                installLocalTime = time.strftime("%a %b %d %T %Z %Y", time.localtime(epochTime))
             except (ValueError, KeyError), e:
                logger.log_err('BaselineReporting', e )
                logger.log_err('BaselineReporting', "Unable to parse timestring for package %s" % pkgName )
                installTime = "Unable to parse timestring"
                installLocalTime = pkgMetaData['INSTDATE']
         pkgRecord.setProp("installtime", installTime)
         pkgRecord.setProp("install_localtime", installLocalTime)

         # Added data to master fingerprint
         sha1Packages.update(pkgMetaData['PKG'])
         sha1Packages.update(pkgvers)
         sha1Packages.update(pkgrel)
         sha1Packages.update(pkgrel)
         sha1Packages.update(installTime)
         sha1Packages.update(installLocalTime)


         # Add entries for related patches
         if not pkgMetaData.has_key('PATCHLIST'):
             continue

         patchList = pkgMetaData['PATCHLIST'].split(' ')
         for patchName in patchList:
             if not patchName:
                 continue 
             patchRecord = patchesNode.newChild(None, "patch", None)
             patchRecord.setProp("name", patchName)
             patchRecord.setProp("pkg", pkgMetaData['PKG'])

             patchInfoKey = "PATCH_INFO_%s" % patchName
             installTime = ""
             installLocalTime = ""
             
             if pkgMetaData.has_key(patchInfoKey):
                 # strptime sucks: %Z does properly work with timezone conversion
                 # will have to just estimate epochTime and record actuall string, too
                 if pkgMetaData[patchInfoKey].startswith("Installed: "):
                     tempString = pkgMetaData[patchInfoKey].split(' From:')[0]
                     tempString = tempString.replace("Installed: ", "")
                     installLocalTime = tempString
                     # use a 'default' split to handle any whitespace -
                     # found an error if we try to split a unicode string on spaces
                     # it doesn't remove all spaces... :(
                     fields = tempString.split()
                     
                     try:
                         tempString = "%s %s %s %s %s" % (fields[0], fields[1], fields[2], fields[3], fields[5])
                     
                         installTime = time.strptime(tempString, "%a %b %d %H:%M:%S %Y")
                         epochTime = int(time.mktime(installTime))
                         installTime = str(epochTime)
                     except (ValueError, KeyError), e:
                         logger.log_err('BaselineReporting', e )
                         logger.log_err('BaselineReporting', "Unable to parse timestring for package and patch %s %s" % (pkgName,patchName) )
                         installTime = "Unable to parse timestring"
    
                             
             patchRecord.setProp("installtime", installTime)
             patchRecord.setProp("install_localtime", installLocalTime)

             sha1Patches.update(installTime)
             sha1Patches.update(installLocalTime)
             sha1Patches.update(pkgMetaData['PKG'])
             sha1Patches.update(patchName)

             
    packageNode.setProp("fingerprint", sha1Packages.hexdigest())
    patchesNode.setProp("fingerprint", sha1Patches.hexdigest())
    
