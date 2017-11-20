#!/usr/bin/env python

#
# Copyright (c) 2008-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Scan the system for vulnerable packages according 
# to DISA UNIX STIG
# 

import sys
import os
import rpm

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger
import sb_utils.misc.unique


CHECKLIST = "/var/lib/oslockdown/files/iava-checklist"
MODNAME   = "iava"

logger = TCSLogger.TCSLogger.getInstance() 


def check():

    logger.log_info(MODNAME, " Software Version Check ".center(60, '-'))

    if not os.path.isfile(CHECKLIST):
        msg = "%s is missing" % CHECKLIST
        logger.log_err(MODNAME, msg)
        return None

    try:
        infile = open(CHECKLIST, 'r')
    except IOError, err:
        msg = "Unable to open %s: %s" % (CHECKLIST, err)
        logger.log_err(MODNAME, msg)
        return None

    lines = infile.readlines()
    infile.close()

    try:
        transet = rpm.TransactionSet()
    except Exception, err:
        msg = "Unable to read RPM database: %s" % (err)
        logger.log_err(MODNAME, msg)
        return None

    vul_pkgs = {}
    pkglist = {}

    fail_flag = False 
    for lnr, line in enumerate(lines):
        line = line.strip()
        fields = line.split('|')
        if len(fields) != 4:
            msg = "Ignoring line number %d of %s because it is " \
                  "malformed" % (CHECKLIST, int(lnr))
            logger.log_info(MODNAME, msg)
            continue

        try:
            idx = fields[3].index(':')
            e2 = fields[3].split(':')[0]
        except ValueError:
            e2 = "None"

        try:
            v2 = fields[3].split('-')[0]
        except IndexError:
            v2 = ""

        try:
            r2 = fields[3].split('-')[1]
        except IndexError:
            r2 = ""

        if fields[1] == '-':
            fields[1] = fields[0]

        if not pkglist.has_key(fields[1]):
            pkglist[fields[1]] = {}
            pkglist[fields[1]]['iava']  = fields[0]
            pkglist[fields[1]]['expected']  = fields[3]
            pkglist[fields[1]]['installed']  = 'not installed'
            pkglist[fields[1]]['operator']  = '-'

            if fields[2].strip() == 'lt':
                pkglist[fields[1]]['operator']  = '<'

            if fields[2].strip() == 'lte':
                pkglist[fields[1]]['operator']  = '<='

            if fields[2].strip() == 'eq':
                pkglist[fields[1]]['operator']  = '=='

        #
        # Check to see if it is installed
        #
        try:
            mi = transet.dbMatch('name', str(fields[1]))
        except Exception, err:
            logger.log_err(MODNAME, str(err))
            continue

        found_flag = False
        for hdr in mi:
            if e2 == "None": 
                e1 = "None"
            else:
                e1 = str(hdr['epoch'])

            v1 = str(hdr['version'])
            r1 = str(hdr['release'])
            arch = str(hdr['arch'])

            pkglist[fields[1]]['installed'] = "%s-%s" % (v1, r1)

            found_flag = True

            results = rpm.labelCompare( (e1, v1, r1), (e2, v2, r2))
            badver_flag = False
            status_msg = ""

            if fields[2].strip() == 'lt' and results < 0:
                status_msg = "greater than or equal to"                    
                badver_flag = True

            if fields[2].strip() == 'lte' and results < 1:
                status_msg = "greater than"
                badver_flag = True

            if fields[2].strip() == 'eq' and results == 0:
                status_msg = "not equal to"
                badver_flag = True


            if badver_flag == True:
                if not vul_pkgs.has_key("%s (%s)" % (fields[1], arch)):
                    vul_pkgs["%s (%s)" % (fields[1], arch)] = "x"

                pkglist[fields[1]]['status']  = '*FAIL*'

                msg = "'%s-%s-%s' (%s) package is installed but expected it "\
                      "to be %s '%s-%s' (DISA UNIX STIG %s)" % \
                      (fields[1], v1, r1, arch, status_msg, v2, r2, fields[0] )
                logger.log_notice(MODNAME, msg)
                fail_flag = True
            else:
                msg = "Okay, '%s-%s-%s' (%s) package is installed (%s)" % \
                     (fields[1], v1, r1, arch, fields[0])
                logger.log_info(MODNAME, msg)
                pkglist[fields[1]]['status']  = ' pass '

        if found_flag == False:
            msg = "Okay, '%s' package not installed (%s)" % (fields[1], fields[0])
            logger.log_info(MODNAME, msg)
            pkglist[fields[1]]['status']  = ' pass '
            
    del transet
    return pkglist


def dump(pkglist=None):

    if pkglist == None:
        return

    results = []
    badpkgs = []
    for iava in pkglist.keys():
        if pkglist[iava]['installed'] == "not installed":
            if iava == pkglist[iava]['iava']:
                line = "%-15s %-8s not applicable to this OS" % (pkglist[iava]['iava'], " pass ")
            else:
                line = "%-15s %-8s %s is not installed" % (pkglist[iava]['iava'], " pass ", iava)
        else:
            line = "%-15s %-8s %s-%s %s %s" % (pkglist[iava]['iava'], 
                                              pkglist[iava]['status'],
                                              iava, pkglist[iava]['installed'], 
                                              pkglist[iava]['operator'], 
                                              pkglist[iava]['expected'])

        results.append(line)
        if pkglist[iava]['status'] == '*FAIL*':
            badpkgs.append(iava)

    
    print >> sys.stdout, "=".center(60, '=')
    print >> sys.stdout, "%-15s %-8s %s" % ("IAVA", "Status", "Installed / Expected")
    print >> sys.stdout, "=".center(60, '=')
    for iava in sorted(results):
        print >> sys.stdout, iava

    print >> sys.stdout, "\n%d of %d IAVA checks failed." % (len(badpkgs), len(results))

    badpkgs = sb_utils.misc.unique.unique(badpkgs)
    print >> sys.stdout, "\n%d packages should be updated: %s\n" % (len(badpkgs), badpkgs)

if __name__ == '__main__':
    results = check()
    dump(pkglist=results)


