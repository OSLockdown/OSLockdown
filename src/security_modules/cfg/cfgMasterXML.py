import os
import sys
import libxml2
import getopt
import re
import pprint

##############################################################################
# Copyright (c) 2013-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

def usage_message(retcode):
    print "Usage: %s -O[O] [-x xmlFile] [-d dirRoot] -s|j" % sys.argv[0]
    print "\t-x xmlFile  -> what XML file to use for modules - default is 'security-modules.xml'"
    print "\t-d dirRoot  -> what directectory to use for modules heirarchy - default is 'modules'"
    print "\t-s          -> populate dirRoot from contents of xmlFile"
    print "\t-j          -> reconstiture xmlFile from contents of dirRoot"
    sys.exit(retcode)


sys.path.append('../../core')

import sbProps

# This python file is designed to take the 'security-modules.xml' file and split
# it into a file heirarchy -or- pointed at such a heirarchy recombine them into
# a single file.  Note that neither operation will be allowed to happen if the
# output file/directory is the PRODUCTION/SVN output target.  For example, when
# splitting security-modules.xml the output target *may not be* modules/, and
# when combining a directory into a single file the output file *may not be* 
# security-modules.xml, to prevent inadvertent overwritting.
# Note that for -s:
#     contents of dirRoot (if any) will be overwritten
# Note that for -j:
#     contents of xmlFile (if any) will be overwritten
      


def parseArgs():
    cmdArgString = "hx:d:sj"
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], cmdArgString )
    except getopt.GetoptError, err:
        print >> sys.stderr, "Error: %s" % err
        usage_message(1)
        sys.exit(sbProps.EXIT_FAILURE)

    force = False
    xmlFile = 'security-modules.xml'
    dirRoot = 'modules'
    action = None
    
    for o, a in opts:
        if o == '-h':
            usage_message(0)
        elif o == '-x':
            xmlFile = a
        elif o == '-d':
            dirRoot = a
        elif o == '-s':
            action = 'split'
        elif o == '-j':
            action = 'join'
        else:
            print "OOPS"
    
    if not action:
        print "No action provided"
        usage_message(1)

    if action == 'split':
        if dirRoot.endswith('modules'):
            print "Output: Will not override what may be the official directory."
            sys.exit(1)
        elif os.path.exists(dirRoot):
            print "Output directory %s already exists!" % dirRoot
            print "Please delete it first, or try again with a different name"
            sys.exit(1)
        else:
            os.makedirs(dirRoot)

    elif action == 'join':
        if xmlFile.endswith('security-modules.xml'):
            print "Output: Will not override what may be the official directory."
            sys.exit(1)
        elif os.path.exists(xmlFile):
            print "Output XMLfile %s already exists!" % xmlFile
            print "Please delete it first, or try again with a different name"
            sys.exit(1)
    return xmlFile, dirRoot, action
               
def splitCfg(xmlFile, dirRoot):
    # we'll keep and delete *groups* as they are processed
    doc = libxml2.parseFile(xmlFile)
    
    # we'll generate a master list of compliancy items here and then parse it out based on source/name/version/item later...
    compliancy = []
    allModules = []
    # walk down the list of groups.  get the group name, and massage it to 
    # create a group directory (spaces to '_', all lower)
    groups = doc.xpathEval('//module_group')
    print "Found %d module groups" % len (groups)
    
    for group in groups:
        groupName = group.prop('name')
        groupDir = "%s/module_groups/%s" % (dirRoot, groupName.replace(' ','_').lower())
        
        os.makedirs('%s' % groupDir)
        open("%s/%s" % (groupDir, "GroupName.txt"), 'w').write(groupName)
        modules = doc.xpathEval("//module_group[@name='%s']/security_module" % groupName)
        print "\tFound %d modules in group %s" % (len(modules), groupName)
        for module in modules:
            libraryName = module.xpathEval("./library")[0].getContent().strip()

            # sanity check for duplicate modules - yowl and skip all but the first
            if libraryName in allModules :
                print "DUPLICATE MODULE FOUND - '%s' " % libraryName
                continue
            else:
                allModules.append(libraryName)
            
            # extract compliancy items and populate dictionary for later splitting
            # and 'unset' the compliancy item data for now before saving
            compNode = module.xpathEval('./compliancy')[0]
            for line_item in compNode.xpathEval("./line-item"):
                compItem = {}
                for prop in ['source', 'name', 'item', 'version']:
                    propVal = line_item.prop(prop)
                    compItem[prop] = propVal    
                compItem['libraryName'] = libraryName
                compliancy.append(compItem)
            # extract compliancy items and populate dictionary for later splitting
            # and 'unset' the compliancy item data for now before saving

            compNode.replaceNode(libxml2.newNode("compliancy"))
           

            newDoc = libxml2.newDoc("1.0")
            newDoc.setRootElement(module.copyNode(1))
            fullLibraryName = "%s/%s.xml" % (groupDir, module.xpathEval("library")[0].getContent().strip())
#            print "\t",fullLibraryName

            newDoc.saveTo(open(fullLibraryName, 'w'), sbProps.XML_ENCODING, 1)
            module.unlinkNode()
        group.unlinkNode()
    
#    pprint.pprint(compliancy,open('/tmp/comp.txt','w'))
    print "Processed %d modules" % len(allModules)
    
    # Ok, delete the 'security_modules' tag with one that is empty, to avoid the blank line in the file from removing nodes...
    doc.xpathEval('//security_modules')[0].replaceNode(libxml2.newNode("security_modules"))
    doc.saveTo(open("%s/WRAPPER.xml" % dirRoot, 'w'), sbProps.XML_ENCODING, 1)

    # Now we need to generate the various compliancy documents.
    # yet again, an xml document
    # details of the guideline at the top, followed by list of line-items, each holding a list of SB *LibraryName* (ie - basename of Python module)
    
    nameList = {}
    for entry in compliancy:
        s = entry['source']
        n = entry['name']
        v = entry['version']
        i = entry['item']
        l = entry['libraryName']

        filename = ""
        newtag = []
        for tag in [s, n, v]:
            if tag:
                newtag.append(re.sub('[^0-9a-zA-Z:]+', '_',tag).strip('_'))
        fileName = '_'.join(newtag).strip('_')
        
        # make a top level entry if needed
        if fileName not in nameList:
            nameList[fileName] = {}
            nameList[fileName]['source']  = s
            nameList[fileName]['name']    = n
            nameList[fileName]['version'] = v
            nameList[fileName]['items'] = {}
                
        # Ok, have we seen this line item yet?
        if i not in nameList[fileName]['items']:
            nameList[fileName]['items'][i] = []
        
        # sanity check for duplicatem module entry:
        if l not in nameList[fileName]['items'][i]:
            nameList[fileName]['items'][i].append(l)

    guideDir = "%s/guidelines" % (dirRoot)
    os.makedirs(guideDir)
    for fileName in nameList.keys():
        items = nameList[fileName]['items'].keys()
        items.sort(key=sortLineItemKey)
        docNode = libxml2.newDoc("1.0")
        compNode = libxml2.newNode("compliancy")
        docNode.addChild(compNode)
#        compFile = open("%s/%s.txt" % (guideDir, fileName),'w')
        for tag in ['source', 'name', 'version']:
            if nameList[fileName][tag]:
                compNode.setProp(tag, nameList[fileName][tag])
        compNode.setProp("enabled", "True")
        itemsNode = libxml2.newNode("line-items")
        for item in items:
            itemNode = libxml2.newNode("line-item")
            itemNode.setProp('name', item)
            modList = sorted(nameList[fileName]['items'][item])
            for mod in modList:
                modNode = libxml2.newNode('module')
                modNode.setProp('libraryName', mod)
                itemNode.addChild(modNode)
            itemsNode.addChild(itemNode)
        compNode.addChild(itemsNode)
        docNode.saveTo(open("%s/%s.xml" % (guideDir, fileName),'w'), sbProps.XML_ENCODING, 1)
        
def sortLineItemKey(item):
    #Some example of line items
    # GEN123456
    # GEN123456-LNX0000
    # AC-1
    # 4.B.2.b(5)(a)
    # 2.6.2.1
    # we'll sort by breaking on non-alphanum characters, then left padding each entry with 10 spaces and rejoining the string
    # By using this routine we don't have to worry about remapping stuff
    item = re.sub('[^0-9a-zA-Z]+', '.',item)
    newkey = '.'.join(["%10s" % field for field in re.sub('[^0-9a-zA-Z]+', '.',item).split('.')])
    return newkey
                
def joinCfg(xmlFile, dirRoot):
    # Ok, start with the WRAPPER document
    doc = libxml2.parseFile('%s/WRAPPER.xml' % dirRoot)
    groupDir = "%s/module_groups" % dirRoot
    # and get our insertion point for new 'groups'
    oslockdown = doc.xpathEval('//security_modules')[0]
    
    modMap = {}
    allLibs = []
    groupDirs = [ thisDir for thisDir in os.listdir(groupDir) if not thisDir.startswith('.svn') ]
    for group in groupDirs:
        if group.startswith('.svn'):
            continue
        dirName = "%s/%s" % (groupDir, group)
        groupName = open("%s/GroupName.txt" % dirName).read()
        
        # create a new node to old this group
        
        groupNode = libxml2.newNode("module_group")
        groupNode.setProp('name',groupName)
    
        # ok, now walk through the directory reading each file (except GroupName.txt) and include...
        for f in [ entry for entry in os.listdir(dirName) if not entry.startswith('.svn') ] :
            if f.startswith('.svn'): 
                continue
            if f == 'GroupName.txt' : continue
            tempDoc = libxml2.parseFile("%s/%s" % (dirName, f))
            modNode = tempDoc.xpathEval("//security_module")[0]
            
            modName = modNode.prop('name')
            libName = modNode.xpathEval("//library")[0].getContent().strip()
            # SANITY CHECK - the libName *should* match the filename minus directory/suffix components
            if f != "%s.xml" % libName:
                print "****** WARNING - Found module where libraryName does not match filename! - %s/%s" % (dirName,f)
                sys.exit(1)
            
            modMap[modName] = libName
            allLibs.append(libName)
            groupNode.addChild(modNode.copyNode(1))
        oslockdown.addChild(groupNode.copyNode(1))

    # First we need to process the compliancy items.  These are listed in flat files in './guidelines' directory.
    # The *name* of the file doesn't matter, as the file has the correct source/name/version details, then a listing of compliancy items.
    # Note that the items in the files are already listed in order, both by compliancy item as well as module name.
    modules = {}
    
    guideDir = "%s/guidelines" % dirRoot
    for fileName in [entry for entry in os.listdir(guideDir) if entry.endswith('.xml') ]:
        # parse the XML file
        compDoc = libxml2.parseFile("%s/%s" % (guideDir, fileName))
        
        # get the source, name, and version details first from the 'compliancy' node
        compNode = compDoc.xpathEval('//compliancy')[0]
        s = compNode.prop('source')
        n = compNode.prop('name')
        v = compNode.prop('version')
        enabled = compNode.prop('enabled')
        if enabled == "False":
            continue
        #iterate over line-items
        for lineItemNode in compNode.xpathEval('./line-items/line-item'):
            lineItem = lineItemNode.prop('name')
            for moduleNode in lineItemNode.xpathEval('./module'):
                libraryName = moduleNode.prop('libraryName')
                if libraryName not in allLibs:
                    print "%s -> Did not find the actual libraryName referenced in compliancy for %s : %s" % (fileName, lineItem,libraryName)
                if libraryName not in modules:
                    modules[libraryName] = []
                modules[libraryName].append([s,n,v,lineItem])

    # ok, now loop over the *modules* we have adding any applicable compliancies - callout those without any
    
    for module in oslockdown.xpathEval('//security_module'):
        modName = module.prop('name')
        compNode = module.xpathEval('//security_module[@name="%s"]/compliancy' % modName)[0]
        if modMap[modName] in modules:
            count = 0
            for s,n,v,i in modules[modMap[modName]]:
                newNode = libxml2.newNode("line-item")
                newNode.setProp('source', s)
                newNode.setProp('name', n)
                if v:
                    newNode.setProp('version', v)
                newNode.setProp('item', i)
                compNode.addChild(newNode)
                count = count +1
#            print "Added %d compliancy items for '%s'" % (count, modName)
        else:
            print "Module '%s' has no compliancy data" % modName 


    try:
        import libxslt
        styledoc = libxml2.parseFile("./sort-security-modules.xsl")
        style = libxslt.parseStylesheetDoc(styledoc)
        result = style.applyStylesheet(doc,None)
        style.saveResultToFilename(xmlFile, result, 0)
        msg = "Wrote sorted master modules list to %s" % xmlFile
        print msg
    except ImportError, err:
        msg = "You must install the 'libxslt-python' (Solaris 'SUNWlxsl-python') "\
              "package in order to generate text reports from the command line." 
        print >> sys.stderr, msg
        msg = "Writing *unformatted* file to %s" % xmlFile             
        doc.saveTo(open(xmlFile,'w'), sbProps.XML_ENCODING, 1)


            
if __name__ == "__main__":
    xmlFile, dirRoot, action = parseArgs()
    if action == 'split':
        splitCfg(xmlFile, dirRoot)
    elif action == 'join':
        joinCfg(xmlFile, dirRoot)
    else:
        print "OOPS"
    
