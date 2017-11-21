#!/usr/bin/python

import sys
import os
import glob
import libxml2
import re


##Register the toto namespace
##ns = root.newNs('http://toto.org', 'toto')
##root.setNs(ns)  #put this node in the namespace

DOC = """<?xml version="1.0" encoding="UTF-8"?>
<appendix xmlns="http://docbook.org/ns/docbook" xml:id="modules-index" role="NotInToc" version="5.0"/>"""

indexdoc = libxml2.parseDoc(DOC)
rootelem = indexdoc.getRootElement()

msg = "\n  OS Lockdown Modules Guide - Index\n  DO NOT EDIT - Automatically Generated\n"
xml_comment = indexdoc.newDocComment(msg)
rootelem.addPrevSibling(xml_comment)

rootelem.newChild(None, "title", "Index")

module_files = glob.glob('../modules/*.xml')
#module_files.extend(glob.glob('../app-*.xml'))

#
# Build wordlist
#
print ":: Building word list from ../wordlist.txt ..."
wordlist = open("../wordlist.txt", 'r')
testwords = []
for word in wordlist.readlines():
    word = word.strip()
    if not word: continue
    testwords.append(word)
wordlist.close()
testwords = set(testwords)
print ":: %d words in list" % len(testwords)

zonemap = {}
for filename in module_files:
    print " + Analyzing %s ..." % (filename)
    zonename = filename.split('/')[-1].split('.')[0]
    indoc = open(filename, 'r')
    lines = indoc.readlines() 
    lines = ''.join(lines)
    indoc.close()

    wordcount = 0
    for word in testwords:
        # Check for matching word using word boundaries unless the
        # word is really a "pathname" (begins with forward slash).
        try:
            if word.startswith('/'):
                regexp = re.compile("(?i)%s\\b" % (word))
            else:
                regexp = re.compile("(?i)\\b%s\\b" % (word))
        except Exception:
            print 
            print ">>>> Bad expression: %s" % word
            print 
            continue
        
        if regexp.search(lines):
            #indexterm = rootelem.newChild(None, "indexterm", None)
            #indexterm.setProp("zone", zonename)
            #primaryterm = indexterm.newChild(None, "primary", word)
            wordcount = wordcount + 1
            if zonemap.has_key(word):
                zonemap[word] = "%s %s" % (zonemap[word], zonename)
            else:
                zonemap[word] = zonename

print ":: Converting zone map to indexterm elements..."
for word in zonemap.keys():
    indexterm = rootelem.newChild(None, "indexterm", None)
    indexterm.setProp("zone", zonemap[word])

    if word.startswith('svc:/'): 
        primaryterm = indexterm.newChild(None, "primary", "Solaris services")
        primaryterm = indexterm.newChild(None, "secondary", word)
        continue

    primaryterm = indexterm.newChild(None, "primary", word)


print ":: Updating ../modules-index.xml"
#rootelem.newChild(None, "index", None)
out_obj = open('../modules-index.xml', 'w')
indexdoc.saveTo(out_obj, 'UTF-8', 1)
out_obj.close()

indexdoc.freeDoc()
