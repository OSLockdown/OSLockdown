#!/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

import sys,os,shlex

class appReports:
    def __init__(self):
        self.moddict = {}
        self.maxwidth = 5
        self.count = {'Apply':0, 'Undo':0}

    def read_report(self, rpt):
        print "Reading report %s..." % rpt
        num_mods = 0
        
        for line in open(rpt, 'r'):
            line = line.strip()
            if line.startswith('<ApplyReport'):
                print line
                rpttype = "Apply"
            elif line.startswith('<UndoReport'):
                print line
                rpttype = 'Undo'
            elif not line.startswith('<module '):
                continue
                
            num_mods = num_mods + 1
            fields = shlex.split(line)
            self.count[rpttype] = self.count[rpttype]+1
            modname='UNKNOWN'
            modres='UNKNOWN'
            for field in fields:
                if field.startswith('name='):
                    modname=field.split('=')[1]
                elif field.startswith('results='):
                    modres=field.split('=')[1]
            if self.moddict.has_key(modname):
                moddata=self.moddict[modname]
            else:
                moddata={}
            moddata.update({rpttype:modres})
            self.moddict[modname]=moddata
            self.maxwidth = max(self.maxwidth, len(modname))
        print "Processed %d modules" % num_mods
        
def compare_reports(rpt1, rpt2):
        
    reports=appReports()
    
    print "Comparing %s and %s" % (rpt1, rpt2)
    reports.read_report(rpt1)
    reports.read_report(rpt2)
    print "Looking for mismatched apply/undo actions ..."
    for key in reports.moddict.keys():
        entry = reports.moddict[key]
        if entry['Apply']=='Applied' and entry['Undo'] != 'Undone':
            print "%s -> Apply='%s' and Undo='%s' " % (key.ljust(reports.maxwidth), entry['Apply'], entry['Undo'])
        if entry['Apply']!='Applied' and entry['Undo'] == 'Undone':
            print "%s -> Apply='%s' and Undo='%s' " % (key.ljust(reports.maxwidth), entry['Apply'], entry['Undo'])

if __name__ == '__main__':
    if len(sys.argv) < 3 :
        print "Usage: %s <rpt1> <rpt2>" % (sys.argv[0])
    else:
        for fn in sys.argv[1:]:
            if not os.path.isfile(fn):
                print ("%s is not a valid file" % fn)
                sys.exit(1)
                
        compare_reports(sys.argv[1], sys.argv[2])
