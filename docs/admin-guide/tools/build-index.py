#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import glob
import libxml2
import re

##Register the toto namespace
##ns = root.newNs('http://toto.org', 'toto')
##root.setNs(ns)  #put this node in the namespace

DOC = """<?xml version="1.0" encoding="UTF-8"?>
<simplesect xml:id="admin-index">
  <para> </para>
</simplesect>"""

indexdoc = libxml2.parseDoc(DOC)
rootelem = indexdoc.getRootElement()

msg = "\n  OS Lockdown Admin Guide - Index\n  DO NOT EDIT - Automatically Generated\n  $Id$\n"
xml_comment = indexdoc.newDocComment(msg)
rootelem.addPrevSibling(xml_comment)

#
# Specificy the (xml) files you'd like indexed.
#
module_files = glob.glob('../SB_*.xml')

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
zonename = ""
content_data = ""
for filename in module_files:
    print " + Analyzing %s ..." % (filename)
    try:
        xmldoc = libxml2.parseFile(filename)
    except:
        print 
        print ">> Unable to parse %s" % (filename)
        print
        continue

    #kids = xmldoc.xpathEval("//*")
    kids = xmldoc.xpathEval("//section[@id]")
    content_data = ""
    for child in kids:
        if child.hasProp("id"):
            if child.prop("id") != zonename:
                content_data = "%s %s" % (content_data, child.content)
                #if zonename != "":
                    # For debugging, write content to file
                    #testout = open("junk/%s" % zonename, 'w')
                    #testout.write(content_data)
                    #testout.close()

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
                    
                    if regexp.search(content_data):
                        #print "Found: %s in zone %s" % (word, zonename)
                        wordcount = wordcount + 1
                        if zonemap.has_key(word):
                            zonemap[word] = "%s %s" % (zonemap[word], zonename)
                        else:
                            zonemap[word] = zonename


                # I like verbose output so I can see what is going on
                if wordcount > 0:
                    number_words = len(set(content_data.split()))
                    print "   Id = %s (%s)"  % (child.prop("id"), child.get_name())
                    print "      ├─ Content contains %d bytes " %  (len(content_data))
                    print "      ├─ Content word count %d (unique)" % number_words
                    print "      └─ %d matched words" % (wordcount)
                else:
                    print "   Id = %s (%s) / %d bytes"  % (child.prop("id"), child.get_name(), len(content_data))

                # Blank content so it is ready for the next section
                content_data = ""
                zonename = child.prop("id")

    xmldoc.freeDoc() 
    wordcount = 0


print ":: Converting zone map to indexterm elements..."
for word in zonemap.keys():
    indexterm = rootelem.newChild(None, "indexterm", None)
    indexterm.setProp("zone", zonemap[word])
    primaryterm = indexterm.newChild(None, "primary", word)


print ":: Updating ../admin-guide-index.xml"
#rootelem.newChild(None, "index", None)
out_obj = open('../admin-guide-index.xml', 'w')
indexdoc.saveTo(out_obj, 'UTF-8', 1)
out_obj.close()

indexdoc.freeDoc()
