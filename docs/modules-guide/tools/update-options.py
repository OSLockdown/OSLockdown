#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2009 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import libxml2
import sys
import os
import commands
import pprint

xmldoc = libxml2.parseFile('../../../src/security_modules/cfg/security-modules.xml')
optionsdoc = libxml2.parseFile('../../../src/security_modules/cfg/optionTypes.xml')
modules_dir = "../modules"

#
#

modulesWithOptions={}

# Ok, these are the *default* help texts as per the optionTypes doc.  They can be overridden by what is in 
# the module itself.
helpMap = {}
for optionHelp in optionsdoc.xpathEval('//helpText'):
    optName = optionHelp.parent.prop('name')
    optionHelp.setName('para')
    helpMap[optName] = optionHelp.copyNode(1)
optionsdoc.freeDoc()

# start at the configurationOptions nodes (one per module with options)

for node in xmldoc.xpathEval("//security_module/configurationOptions"):
    
    moduleNode = node.parent
    libraryName = moduleNode.xpathEval('./library')[0].getContent().strip("'")
    simplesect_tag = "%s-options" % libraryName
    moduleID = "%s.xml" % libraryName
    repl_node = libxml2.newNode("simplesect")
    repl_node.newProp("xml:id", simplesect_tag)
    tNode = repl_node.newChild(None, "title", "Module Options")
    tNode = repl_node.newChild(None, "itemizedlist", None)

    for option in node.xpathEval("./option"):
        optDetails = {}
        for helpDetail in ['description', 'default', 'helpName', 'helpText']:
            optDetails[helpDetail] = None
            
        try:
            optDetails['helpText'] = helpMap[option.prop('type')]
        except:
            pass

        # get the details for the option entry
        for detail in ['name', 'type']:
            optDetails[detail] = option.prop(detail)
        for helpDetail in ['description', 'default', 'helpName', 'helpText']:
            helpDetailNode = option.xpathEval("./%s" % helpDetail)

            if helpDetailNode:
                if helpDetail == 'helpText':
                    optDetails[helpDetail] = helpDetailNode[0].copyNode(1)
                    optDetails[helpDetail].setName('para')
                else:
                    optDetails[helpDetail] = helpDetailNode[0].content.strip()
        

        XNodeListItem = tNode.newChild(None, "listitem", None)
        xNode = XNodeListItem.newChild(None, "para", optDetails['description'])
        if 'helpText' in optDetails and optDetails['helpText']:
            if type(optDetails['helpText']) != type(""):
                eNode = xNode.newChild(None, 'emphasis', None)
                pNode = eNode.addChild(optDetails['helpText'].copyNode(1))
            else:
                eNode = xNode.newChild(None, 'emphasis', None)
                pNode = eNode.newChild(None, "para", optDetails['helpText'])

# Ok, go replace/add the new simplesect...
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
        print err
    
os.unlink('xx')
