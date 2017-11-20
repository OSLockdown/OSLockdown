#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2009 Forcepoint LLC
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import libxml2
import sys
import os
import commands

import readGuideLine

xmldoc = libxml2.parseFile('../../../src/security_modules/cfg/security-modules.xml')
modules_dir = "../modules"

guideDir = '../../../src/security_modules/cfg/prod_sources/guidelines'
#
#

# ok, preliminary work - read all *.xml files from the guidelines directory.  If the guideline
# is marked as disable then ignore it, otherwise pull it into a stacked dictionary that we can search through

allGuides = {}
for cfgFile in os.listdir(guideDir):
    if not cfgFile.endswith('.xml'):
        continue
    guideDoc = readGuideLine.readXML('%s/%s' % (guideDir,cfgFile))
    if guideDoc['enabled'] != 'True':
        continue
    print "Processing %s" % cfgFile
    guideSource = guideDoc['source']
    guideName = guideDoc['name']
    guideVersion =guideDoc['version']
    
    # ok, process it...
    if guideSource not in allGuides:
        allGuides[guideSource] = {}
    combinedName = guideName+guideVersion
    if combinedName not in allGuides[guideSource]:
        allGuides[guideSource][combinedName] = {}
    else:
        print "**** WARNING - Duplicate entry for Guidance document found"
        print "Source  -> %s" % guideSource
        print "Name    -> %s" % guideName
        print "Version -> %s" % guideVersion
        continue
    allGuides[guideSource][combinedName] = guideDoc['lineitems']

cNode = xmldoc.newDocComment("Do not edit. Automatically generated")
for node in xmldoc.xpathEval("//security_module"):
        simplesect_tag = ''
        moduleID = '' 
        for lnode in node.xpathEval("//security_module[@name='%s']/library" % node.prop("name")):
	    if lnode.getContent() != "":
                simplesect_tag = "%s-compliancy" % lnode.getContent().strip("'")
                moduleID = "%s.xml" % lnode.getContent().strip("'")

        if simplesect_tag == '':
            print "Missing //security_module[@name='%s']/library" % node.prop("name")
            continue

        repl_node = libxml2.newNode("simplesect")
        repl_node.newProp("xml:id", simplesect_tag)

        # Add title child element
        tNode = repl_node.newChild(None, "title", "Compliancy")

        # Get compliancy items
        complist = {}
        for lnode in node.xpathEval("//security_module[@name='%s']/compliancy/line-item" % node.prop("name")):


#commenting out explicit addition of trademark sign to CCE for now....
#            if lnode.prop("name") == "CCE":
#                header = "%s CCE™ (%s)" % (lnode.prop("source"), lnode.prop("version"))
#            else:
#                header = "%s %s (%s)" % (lnode.prop("source"), lnode.prop("name"), lnode.prop("version"))

            header = "%s %s" % (lnode.prop("source"), lnode.prop("name"))
            
            if lnode.prop("version"):
                header = header + " (%s)" % lnode.prop("version")


            if not complist.has_key(header):
                complist[header] = []
         
            titem = lnode.prop('item')
            
            # get/synthesize the lookup names - being very clever with variable names :p
            x=lnode.prop('source')
            y=lnode.prop('name')
            z=lnode.prop('version')
            if z == None:
                z=""
            
            text = [titem]
             
            try:
                descript = allGuides[x][y+z][titem]['description']
            except Exception, err:
                continue
            if descript != None:
                text.append(descript)           
                  
            lineitem = " - ".join(text)
            complist[header].append(lineitem)
        
        

        # Sort the dictionary
        theList = complist.keys()
        theList.sort()
        if theList:
            for compl_key in theList:
                tNode = repl_node.newChild(None, "itemizedlist", None)
                xNode = tNode.newChild(None, "title", compl_key)
                for lineitem in complist[compl_key]:
                    xNode = tNode.newChild(None, "listitem", "")
                    pNode = xNode.newChild(None, "para", lineitem)
        else:
            tNode = repl_node.newChild(None,"para","N/A")
        try:
            found_flag = False
            filename = os.path.join(modules_dir, moduleID)
            if not os.path.isfile(filename):
                print ":: Missing %s" % filename
                continue

            modulesguide = libxml2.parseFile(filename)
            xc = modulesguide.xpathNewContext()
            xc.xpathRegisterNs("docbook","http://docbook.org/ns/docbook")
            for compnode in xc.xpathEval("//docbook:section/docbook:simplesect"):
                if compnode.prop("id") == simplesect_tag: 
                    compnode.unlinkNode()
		    compnode.freeNode()

            topNode = xc.xpathEval("//docbook:section")[0]
            print ":: %s - adding //docbook:simplesect[@id='%s']" % (filename, simplesect_tag)
            topNode.addChild(repl_node)
            modulesguide.saveFile(filename)
            modulesguide.freeDoc()

            cmd = "XMLLINT_INDENT=\"  \" /usr/bin/xmllint --format %s > xx; cat xx > %s" % (filename, filename)
            (status, output) = commands.getstatusoutput(cmd)

        except Exception, err:
            print "+++",err


xmldoc.freeDoc()
os.unlink('xx')
