#!/usr/bin/env python
#
# Copyright (c) 2009-2015 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#

import libxml2
import sys


unixstig = {}
infile = open('../../docs/modules-guide/guideline-xrefs/unixstig_list.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    unixstig[lineitem] = desc.strip()
infile.close()
print ":: Loading FERC CIP descriptions..."
ferc = {}
infile = open('../../docs/modules-guide/guideline-xrefs/ferc_cip.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    ferc[lineitem] = desc.strip()
infile.close()
print ":: Loading Solaris 10 Benchmark descriptions..."
cis_solaris = {}
infile = open('../../docs/modules-guide/guideline-xrefs/cis_solaris_list.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    cis_solaris[lineitem] = desc.strip()
infile.close()

print ":: Loading RHEL 4 Benchmark descriptions..."
cis_rhel4 = {}
infile = open('../../docs/modules-guide/guideline-xrefs/cis_rhel4.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    cis_rhel4[lineitem] = desc.strip()
infile.close()

print ":: Loading RHEL 5 Benchmark descriptions..."
cis_rhel5 = {}
infile = open('../../docs/modules-guide/guideline-xrefs/cis_rhel5.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    cis_rhel5[lineitem] = desc.strip()
infile.close()

print ":: Loading NISPOM Ch8 descriptions..."
nispom = {}
infile = open('../../docs/modules-guide/guideline-xrefs/nispom8.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    nispom[lineitem] = desc.strip()
infile.close()

print ":: Loading PCI DSS descriptions..."
pcidss = {}
infile = open('../../docs/modules-guide/guideline-xrefs/pcidss.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    pcidss[lineitem] = desc.strip()

print ":: Loading CAG descriptions..."
cag = {}
infile = open('../../docs/modules-guide/guideline-xrefs/cag.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    cag[lineitem] = desc.strip()

print ":: Loading FISMA descriptions..."
fisma = {}
infile = open('../../docs/modules-guide/guideline-xrefs/fisma.txt', 'r')
lines = infile.readlines()
for line in lines:
    (lineitem, desc) = line.split('|')
    fisma[lineitem] = desc.strip()


xmldoc = libxml2.parseFile('../cfg/security-modules.xml')

cag_list = {}
complist = {}
master_list = []
for node in xmldoc.xpathEval("//security_module"):

        for lnode in node.xpathEval("//security_module[@name='%s']/compliancy/line-item" % node.prop("name")):
            header = "%s %s (%s)" % (lnode.prop("source"), lnode.prop("name"), lnode.prop("version"))

            if not complist.has_key(node.prop("name")):
                complist[node.prop("name")] = {}

            if header not in master_list:
               master_list.append(header)

            if not complist[node.prop("name")].has_key(header):
                complist[node.prop("name")][header] = []

            lineitem = lnode.prop("item")

           
            if lnode.prop("source") == "CAG" and lnode.prop("name") == "20 Critical Security Controls":
                if not cag_list.has_key(lnode.prop("item")):
                   cag_list[lnode.prop("item")] = True
            

            complist[node.prop("name")][header].append(lineitem)

        #print complist

line = ['Module Name']
line.extend(master_list)

print '|'.join(line)

for module in complist.keys():
    sys.stdout.write("%s|" % module)
    for comp in master_list:
       if complist[module].has_key(comp):
           sys.stdout.write(', '.join(complist[module][comp]))
       else:
           sys.stdout.write('-')

       sys.stdout.write('|')

    print
       #for lineItem in complist[module]:
           #print "\t\t", lineItem
           #print complist[module][lineItem] 
           #for subitems in complist[module][lineItem]:
               #print "\t\t\t", subitems

