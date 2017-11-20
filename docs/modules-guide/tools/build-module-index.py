#!/usr/bin/python

import sys
import os
import libxml2
import pprint

# Ok, first things first - go all of the current modules and build a 
# master list of available modules

#!/usr/bin/python

import sys
import libxml2
import os
import commands

pathname = os.path.dirname(sys.argv[0])
MODULES_INDEX = os.path.join(pathname, 
     '../oslockdown-modules.xml')
MODULES_DIR = os.path.join(pathname, '../modules')


os.chdir(pathname)

chapters = {}
allModules = {}
for module in os.listdir(MODULES_DIR):
    if not module.endswith('.xml'):
        continue
    modDoc = libxml2.parseFile("%s/%s" % (MODULES_DIR, module))
    xc = modDoc.xpathNewContext()
    xc.xpathRegisterNs("docbook", "http://docbook.org/ns/docbook")
    # find the 'title' section
    node = xc.xpathEval('//docbook:section')[0]
    modLibrary = module.split('.')[0]
    chapter = xc.xpathEval("./docbook:section/docbook:title")[0].prop('id')
    modName = xc.xpathEval("./docbook:section/docbook:title")[0].getContent()
    
    if modName in allModules:
        print "Module '%s' already processed !" % modName
        sys.exit(1)
        
    if chapter not in chapters:
        chapters[chapter] = []
    
    allModules[modName] = modLibrary 
    chapters[chapter].append(modName)

# now that we have all of the modules info, pull in the current index *as text* and remove any line starting with <xi:include, but *only* if we're 


#
# now process *this* as XML

newDoc = libxml2.parseFile(MODULES_INDEX)
xc = newDoc.xpathNewContext()
xc.xpathRegisterNs("docbook", "http://docbook.org/ns/docbook")
xc.xpathRegisterNs("xi", "http://www.w3.org/2001/XInclude")

# Delete *all* <xi:includes> from the chapters - leave the appendixes untouched
for node in xc.xpathEval('//docbook:book/docbook:chapter/xi:include'):
    node.unlinkNode()
    node.freeNode()

# walk through each chapter, and sort the elements by the human readable module name, and insert suitable lines
print "Building index of modules guide by 'chapter'..."
for chapter in xc.xpathEval('//docbook:book/docbook:chapter'):
    chapName = chapter.prop('id')
    print "Working on '%s'" % chapName
#    newDoc.xpathEval("//docbook:book/docbook:chapter[@id='%s']/title" % chapName)
    sortedModules = sorted(chapters[chapName])
    for mod in sortedModules:
        node = chapter.newChild(None,'xi:include',None)
        node.newProp("xmlns:xi", "http://www.w3.org/2001/XInclude")
        node.newProp("href", "modules/%s.xml" % allModules[mod])
newDoc.saveFile(MODULES_INDEX)
cmd = "XMLLINT_INDENT=\"  \" /usr/bin/xmllint --format %s > xx; cat xx > %s" % (MODULES_INDEX, MODULES_INDEX)
(status, output) = commands.getstatusoutput(cmd)


    
