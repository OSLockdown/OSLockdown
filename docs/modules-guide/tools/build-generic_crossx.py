#!/usr/bin/python

import sys
import libxml2
import os
import commands
import re
from itertools import izip, chain, repeat

import readGuideLine

def tryint(item):
    try:
       item = int(item)
    except:
       pass
    return item
    
def convInts(items):
    return [ tryint(c) for c in items]

def sortNaturally(items):
    scratch = [ (convInts(re.split(u"(\d+|[a-zA-Z]+|\W+)", a)[1::2]), a)  for a in items]
    scratch.sort()
    items[:] = [ a[1] for a in scratch]
    return items

def coverageTable(guideName, coveredCount, uncoveredCount):
    table_node = libxml2.newNode("para")
    
    s = []
    s.append("%*d   Total number of line items in guideline" % ( 5, coveredCount + uncoveredCount))
    s.append("%*d   Items at least partially addressed by OS Lockdown" % (5, coveredCount))
    s.append("%*d   Items not addressed by OS Lockdown" % (5, uncoveredCount))
    
    
    table_node.newChild(None, "literallayout",  '\n'.join(s))

    return table_node
    

def coverageTable2(guideName, coveredCount, uncoveredCount):

    table_node = libxml2.newNode("informaltable")
    table_node.setProp("xml:id", "%s-coverage" % (guideName))
    table_node.setProp("frame", "none")
    table_node.setProp("tocentry", "0")
    table_node.setProp("border", "0")
    table_node.setProp("cellspacing", "0")
    table_node.setProp("cellpadding", "0")
    table_node.setProp("pgwide", "1")
    table_node.setProp("colsep", "0")
    table_node.setProp("rowsep", "0")
    table_node.setProp("rules", "none")
    
#    tableName = "Guideline name/description for %s %s %s" % (guideSource, guideName, guideVersion)
#    table_node.newChild(None, "title", "%s" % tableName)
    tgroup = table_node.newChild(None, "tgroup", None)
    tgroup.setProp("cols", "2")

    c1 = tgroup.newChild(None, "colspec", None)
    c1.setProp("colname", "c1")
    c1.setProp("colwidth", "0.0*")
    c1.setProp("align", "left")

    c2 = tgroup.newChild(None, "colspec", None)
    c2.setProp("colname", "c2")
    c2.setProp("colwidth", "0.9*")
    c2.setProp("align", "left")

#    thead = tgroup.newChild(None, "thead", None)
#    trow = thead.newChild(None, "row", None)
#    trow.newChild(None, "entry", "Line Item")
#    trow.newChild(None, "entry", "Description Item")

    tbody = tgroup.newChild(None, "tbody", None)
    tbody.setProp("valign", "middle")


    trow = tbody.newChild(None, "row", None)
    trow.newChild(None, "entry",  "%d" % (coveredCount + uncoveredCount))
    trow.newChild(None, "entry",  "Total number of line items in guideline")

    trow = tbody.newChild(None, "row", None)
    trow.newChild(None, "entry",  "%d" % coveredCount)
    trow.newChild(None, "entry",  "Items at least partially addressed by OS Lockdown")

    trow = tbody.newChild(None, "row", None)
    trow.newChild(None, "entry",  "%d" % uncoveredCount)
    trow.newChild(None, "entry",  "Items not addressed by OS Lockdown")
    return table_node
        

def processGuideline_LineItemsPerModule(guidelineName, guideline):

    shortName = os.path.splitext(os.path.split(guidelineName)[-1])[0]
    guideSource  = guideline['source']
    guideName    = guideline['name']
    guideVersion = guideline['version']
    guideEnabled = guideline['enabled'] 
    guideItems   = guideline['lineitems']
    guideItemsSkipped   = guideline['notcovered']
    guidePrefix  = guideline['lineitemprefix']

    print "::: Processing %s %s %s with %d items" % (guideSource, guideName, guideVersion, len(guideItems))
    
    # Ok, remember that guideItems is a dict of Guideline -> list of modules
    # we need to reorder this to module-> list of guideline
    # we're going to assume that the line items are in the correct order...
    
    libraryToLineItem = {}
    lineItems = {}
    
    for gItem in guideItems:
        lineItems[gItem] = {}
        lineItems[gItem]['description'] = guideItems[gItem]['description']
        lineItems[gItem]['xml_id'] = "%s-desc" % gItem
        for mod in guideItems[gItem]['modules']:
            if mod not in libraryToLineItem:
                libraryToLineItem[mod] = []
            if gItem not in libraryToLineItem[mod]:
                libraryToLineItem[mod].append(gItem)
    numLineItems = len(lineItems)
    
    lineItemNames = sortNaturally(lineItems.keys())
    
    # ok, sort the modules by the module name, not the library name
    sortedMods = sortNaturally([libraryToModule[lib] for lib in libraryToLineItem.keys()])
#    sortedMods = sorted(libraryToLineItem.keys())
    outdoc = libxml2.newDoc("1.0")
    rootelem = outdoc.newChild(None, "section", None)
    ns = rootelem.newNs('http://docbook.org/ns/docbook', None)
    rootelem.setNs(ns)
    rootelem.setProp("version", "5.0")
    
    try:
        guideTitle = guideline['title']
    except KeyError:
        guideTitle = "%s %s %s" % (guideSource, guideName, guideVersion) 
    if type(guideTitle) == type(''):
        rootelem.newChild(None, "title", guideTitle)
    else:
        rootelem.addChild(guideTitle.copyNode(1))

    try:
        subTitle = guideline['subtitle']
        if subTitle:
            if type(subTitle) == type(''):                            
                rootelem.newChild(None, "subtitle", subTitle)            
            else:                                                       
                rootelem.addChild(subTitle.copyNode(1)) 
    except KeyError:
        pass
    rootelem.setProp("xml:id", "app-crossx-%s"% shortName)
        
    try:
        guideDesc = guideline['abstract']
    except KeyError:
        guideDesc = "Guideline items related to %s" % (guideTitle) 
    if guideDesc:
        abstr = rootelem.newChild(None, "para", None)
        if type(guideDesc) == type(''):
            abstr.newChild(None, "abstract", guideDesc)
        else:
            abstr.addChild(guideDesc.copyNode(1))

    rootelem.addChild(coverageTable(shortName, len(guideItems), len(guideItemsSkipped)).copyNode(1))        

    # build a table matching guideline *name* to *description*
    table_node = rootelem.newChild(None,"table", None)
    table_node.setProp("xml:id", "app-crossx-%s-description" % (shortName))
    table_node.setProp("frame", "all")
    table_node.setProp("tocentry", "1")
    table_node.setProp("cellspacing", "2")
    table_node.setProp("cellpadding", "2")
    table_node.setProp("pgwide", "1")
    
    tableName = "Guideline name/description for %s %s %s" % (guideSource, guideName, guideVersion)
    table_node.newChild(None, "title", "%s" % tableName)
    tgroup = table_node.newChild(None, "tgroup", None)
    tgroup.setProp("cols", "2")

    c1 = tgroup.newChild(None, "colspec", None)
    c1.setProp("colname", "c1")
    c1.setProp("colwidth", "0.2*")
    c1.setProp("align", "center")

    c2 = tgroup.newChild(None, "colspec", None)
    c2.setProp("colname", "c2")
    c2.setProp("colwidth", "0.5*")
    c2.setProp("align", "left")

    thead = tgroup.newChild(None, "thead", None)
    trow = thead.newChild(None, "row", None)
    trow.newChild(None, "entry", "Line Item")
    trow.newChild(None, "entry", "Description Item")

    tbody = tgroup.newChild(None, "tbody", None)
    tbody.setProp("valign", "middle")
    for li in lineItemNames:
        trow = tbody.newChild(None, "row", None)
        trow.setProp("xml:id", lineItems[li]['xml_id'])
        trow.newChild(None, "entry",  li)
        trow.newChild(None, "entry",  lineItems[li]['description'])

    ##
    ## Build Table 
    ##
    table_node = rootelem.newChild(None, "table", None)
    table_name = "Module to line item breakdown for %s %s %s" % (guideSource, guideName, guideVersion)
    xml_id = "app-crossx-%s-items" % (shortName)
    table_node.setProp("xml:id", xml_id)
    table_node.setProp("frame", "all")
    table_node.setProp("tocentry", "1")
    table_node.setProp("cellspacing", "2")
    table_node.setProp("cellpadding", "2")
    table_node.setProp("pgwide", "1")
    table_node.newChild(None, "title", table_name)

    tgroup = table_node.newChild(None, "tgroup", None)
    tgroup.setProp("cols", "%d" % (numLineItems + 1))

    # First column is name of module
    c1 = tgroup.newChild(None, "colspec", None)
    c1.setProp("colname", "c1")
    c1.setProp("colwidth", "1.0*")
    c1.setProp("align", "right")

    for li in lineItemNames:
        c2 = tgroup.newChild(None, "colspec", None)
        c2.setProp("colname", "c-%s" % li)
        c2.setProp("colwidth", "0.2*")
        c2.setProp("align", "center")

    thead = tgroup.newChild(None, "thead", None)
    thead.setProp("valign", "middle")
    trow = thead.newChild(None, "row", None)

    trow.newChild(None, "entry", "OS Lockdown Module")
    for li in lineItemNames:
        rtu = trow.newChild(None, "entry", None)
        rtu.setProp("align", "center")
        test = rtu.addChild(outdoc.newDocPI('dbfo orientation="90" ', None))
        test = rtu.addChild(outdoc.newDocPI('dbfo rotated-width="0.5in" ', None))

        # Ok, gen the table headings, striping the optional lineitemprefix from each line (NERC/FERC guides for example)
        try:
            if guidePrefix and li.startswith(guidePrefix):
                newLi = li[len(guidePrefix):]
            else:
                newLi = li
        except Exception, err:
            newLi = li
        rtu.addContent(newLi)

    tbody = tgroup.newChild(None, "tbody", None)
    tbody.setProp("valign", "middle")

    for modName in sortedMods:
        trow = tbody.newChild(None, "row", None)
        modentry = trow.newChild(None, "entry",  None)
        modentry = modentry.newChild(None, "xref",  modName)
        modentry.setProp("linkend", moduleToLibrary[modName])
        modentry.setProp("xrefstyle", "select: title page")

        for li in lineItemNames:
            try:
                if li in libraryToLineItem[moduleToLibrary[modName]]:
                    xyz = trow.newChild(None, "entry", None)
                    xyz = xyz.newChild(None, "emphasis", "X")
                    xyz.setProp("xml:id", lineItems[li]['xml_id'])
                    xyz.setProp("role", "bold")
                else:
                    trow.newChild(None, "entry", None)
            except KeyError:
                trow.newChild(None, "entry", None)
        

    ###
    ### Create the file
    ###
    outFile = "app-crossx-%s.xml" % shortName 
    out_obj = open('../%s' % outFile, 'w')
    outdoc.saveTo(out_obj, 'UTF-8', 1)
    out_obj.close()
    outdoc.freeDoc()
    return guideTitle, outFile



def processGuideline_ModulePerLineItem(guidelineName, guideline):

    shortName = os.path.splitext(os.path.split(guidelineName)[-1])[0]
    guideSource  = guideline['source']
    guideName    = guideline['name']
    guideVersion = guideline['version']
    guideEnabled = guideline['enabled'] 
    guideItems   = guideline['lineitems']
    guideItemsSkipped   = guideline['notcovered']

    print "::: Processing %s %s %s with %d items" % (guideSource, guideName, guideVersion, len(guideItems))
        
    outdoc = libxml2.newDoc("1.0")
    rootelem = outdoc.newChild(None, "section", None)
    ns = rootelem.newNs('http://docbook.org/ns/docbook', None)
    rootelem.setNs(ns)
    rootelem.setProp("version", "5.0")
    
    try:
        guideTitle = guideline['title']
    except KeyError:
        guideTitle = "%s %s %s" % (guideSource, guideName, guideVersion) 
    if type(guideTitle) == type(''):
        rootelem.newChild(None, "title", guideTitle)
    else:
        rootelem.addChild(guideTitle.copyNode(1))

    try:
        subTitle = guideline['subTitle']
        if subTitle:
            if type(subTitle) == type(''):                            
                rootelem.newChild(None, "subtitle", subTitle)            
            else:                                                       
                rootelem.addChild(subTitle.copyNode(1)) 
    except KeyError:
        pass
    rootelem.setProp("xml:id", "app-crossx-%s"% shortName)
        

    try:
        guideDesc = guideline['abstract']
    except KeyError:
        guideDesc = "Guideline items related to %s" % (guideTitle) 
    if guideDesc:
        abstr = rootelem.newChild(None, "para", None)
        if type(guideDesc) == type(''):
            abstr.newChild(None, "abstract", guideDesc)
        else:
            abstr.addChild(guideDesc.copyNode(1))

    rootelem.addChild(coverageTable(shortName, len(guideItems), len(guideItemsSkipped)).copyNode(1))        
    


    # Break the table up in to chunks of 100 items, generating table subreferences as we go
    sortedKeys = sortNaturally(guideItems.keys())
    chunks = []
    try:
        numItemsPerChunk = int(guideline['MaxItemsPerTable'])
    except Exception, err:
        numItemsPerChunk = len(sortedKeys)

    for chunk in izip(*[chain(sortedKeys, repeat(None,numItemsPerChunk-1))]*numItemsPerChunk):
        items=[item for item in chunk if item]
        xml_id = "app-crossx-%s-%s-%s" % (shortName, items[0].replace('-','_'),items[-1].replace('-','_'))
        tableRange = " %s to %s" % ( chunk[0], chunk[-1])

        chunks.append( {'items': items, 'xml_id': xml_id, 'tableRange':tableRange})

    if len(chunks) == 1:
        chunks[0]['tableRange'] = ""
    else:
        msg = "Due to the number of line items in this guideline, it has been divided into subtables of up to %d line-items each.  The following table will help you navigate to the correct subtable." % numItemsPerChunk
        rootelem.newChild(None,"para",msg)
        table_node = rootelem.newChild(None,"table", None)
        table_node.setProp("xml:id", "app-crossx-%s-tables" % (shortName))
        table_node.setProp("frame", "all")
        table_node.setProp("tocentry", "1")
        table_node.setProp("cellspacing", "2")
        table_node.setProp("cellpadding", "2")
        table_node.setProp("pgwide", "1")

        tableName = "Line item breakdown for %s %s %s" % (guideSource, guideName, guideVersion)
        table_node.newChild(None, "title", "%s" % tableName)
        tgroup = table_node.newChild(None, "tgroup", None)
        tgroup.setProp("cols", "3")

        c1 = tgroup.newChild(None, "colspec", None)
        c1.setProp("colname", "c1")
        c1.setProp("colwidth", "0.2*")
        c1.setProp("align", "center")

        c2 = tgroup.newChild(None, "colspec", None)
        c2.setProp("colname", "c2")
        c2.setProp("colwidth", "0.5*")
        c2.setProp("align", "left")

        c3 = tgroup.newChild(None, "colspec", None)
        c3.setProp("colname", "c3")
        c3.setProp("colwidth", "0.5*")
        c3.setProp("align", "left")

        thead = tgroup.newChild(None, "thead", None)
        trow = thead.newChild(None, "row", None)
        trow.newChild(None, "entry", "Subtable Name")
        trow.newChild(None, "entry", "Starting Item")
        trow.newChild(None, "entry", "Ending Item")

        tbody = tgroup.newChild(None, "tbody", None)
        tbody.setProp("valign", "middle")
        for subtable in chunks:
            chunk = subtable['items']
            startItem = chunk[0]
            endItem = chunk[-1]
            tableName = subtable['xml_id']
            
            trow = tbody.newChild(None, "row", None)
            xref = trow.newChild(None, "entry", None)
            xref = xref.newChild(None, "xref", None)
            xref.setProp("linkend", tableName)
            xref.setProp("xrefstyle", "select: title page")
            trow.newChild(None, "entry",  startItem)
            trow.newChild(None, "entry",  endItem)
            
            
    baseTableName = "%s %s %s" % (guideSource, guideName, guideVersion)
    for subtable in chunks:
        chunk = subtable['items']
        ##
        ## Build Table 
        ##
        table_node = rootelem.newChild(None, "table", None)
        xml_id = subtable['xml_id']
        table_node.setProp("xml:id", xml_id)
        table_node.setProp("frame", "all")
        table_node.setProp("tocentry", "1")
        table_node.setProp("cellspacing", "2")
        table_node.setProp("cellpadding", "2")
        table_node.setProp("pgwide", "1")
    
        table_node.newChild(None, "title", "%s%s" % (baseTableName, subtable['tableRange']))

        tgroup = table_node.newChild(None, "tgroup", None)
        tgroup.setProp("cols", "3")

        c1 = tgroup.newChild(None, "colspec", None)
        c1.setProp("colname", "c1")
        c1.setProp("colwidth", "0.2*")
        c1.setProp("align", "center")

        c2 = tgroup.newChild(None, "colspec", None)
        c2.setProp("colname", "c2")
        c2.setProp("colwidth", "0.5*")
        c2.setProp("align", "left")

        c3 = tgroup.newChild(None, "colspec", None)
        c3.setProp("colname", "c3")
        c3.setProp("colwidth", "0.5*")
        c3.setProp("align", "left")

        thead = tgroup.newChild(None, "thead", None)
        trow = thead.newChild(None, "row", None)
        trow.newChild(None, "entry", "Item")
        trow.newChild(None, "entry", "Title")
        trow.newChild(None, "entry", "OS Lockdown Modules")

        tbody = tgroup.newChild(None, "tbody", None)
        tbody.setProp("valign", "middle")

        for item_name in chunk:
            trow = tbody.newChild(None, "row", None)
            trow.newChild(None, "entry",  item_name)
            try:
                xrow = trow.newChild(None, "entry",  guideItems[item_name]['description'])
            except:
                xrow = trow.newChild(None, "entry",  item_name)

            last_column = trow.newChild(None, "entry", None)
            last_column = last_column.newChild(None, "simplelist", None)
            last_column.setProp("type", "horiz")
            last_column.setProp("columns", "1")
            mods = sortNaturally([libraryToModule[mod] for mod in guideItems[item_name]['modules']])
            for xref in mods:
                xref_item = last_column.newChild(None, "member", None)
                xref_link = xref_item.newChild(None, "xref", xref)
                xref_link.setProp("linkend", moduleToLibrary[xref])
                xref_link.setProp("xrefstyle", "select: title page")

    ###
    ### Create the file
    ###
    outFile = "app-crossx-%s.xml" % shortName 
    out_obj = open('../%s' % outFile, 'w')
    outdoc.saveTo(out_obj, 'UTF-8', 1)
    out_obj.close()
    outdoc.freeDoc()
    return guideTitle, outFile

def processGuideline(guidelineName):
    docName = None
    docFile = None
    guideline = readGuideLine.readXML(guidelineName)
    guideEnabled = guideline['enabled'] 
   
    if guideEnabled == 'True':
        guideStyle = guideline['style'] 
        # ModulesPerLineItem = show line item, description, and relevent modules  in a straight vertical table
        # LineItemsPerModule = show x/y of modules vice line items.  Line item *also* ties to table at end with text on item.
        
        if guideStyle == 'ModulesPerLineItem':   
            docName, docFile = processGuideline_ModulePerLineItem(guidelineName, guideline)
        elif guideStyle == 'LineItemPerModule':
            docName, docFile = processGuideline_LineItemsPerModule(guidelineName, guideline)
        else:
            print "Unknown Style for %s" % guidelineName
    else:
        print "%s is disabled" % guidelineName
    
    return docName, docFile        

def buildCrossxAppendix(appendixDoc, crossxDocs):

    newDoc = libxml2.parseFile(appendixDoc)
    xc = newDoc.xpathNewContext()
    xc.xpathRegisterNs("docbook", "http://docbook.org/ns/docbook")
    xc.xpathRegisterNs("xi", "http://www.w3.org/2001/XInclude")
    # Delete *all* <xi:includes> from the section
    print "Rebuilding appendix section"
    for node in xc.xpathEval('//docbook:book/docbook:appendix[@xml:id="app-crossx"]/xi:include'):
        node.unlinkNode()
        node.freeNode()

    section = xc.xpathEval('//docbook:book/docbook:appendix[@xml:id="app-crossx"]')[0] 
    for mod in sortNaturally(crossxDocs.keys()):
        node = section.newChild(None,'xi:include',None)
        node.newProp("xmlns:xi", "http://www.w3.org/2001/XInclude")
        node.newProp("href", "%s" % crossxDocs[mod])

    newDoc.saveFile(appendixDoc)
    cmd = "XMLLINT_INDENT=\"  \" /usr/bin/xmllint --format %s > xx; cat xx > %s" % (appendixDoc, appendixDoc)
    (status, output) = commands.getstatusoutput(cmd)

    


if __name__ == "__main__":

    pathname = os.path.dirname(sys.argv[0])
    
    MODULES_CONFIG = os.path.join(pathname, 
         '../../../src/security_modules/cfg/security-modules.xml')
    GUIDEDIR =  os.path.join(pathname, 
         '../../../src/security_modules/cfg/prod_sources/guidelines')
    APPENDIXDOC = '../oslockdown-modules.xml'

    try:
        modulesdoc = libxml2.parseFile(MODULES_CONFIG)
        print "Processed %d Security Modules from %s" % (len(modulesdoc.xpathEval('//security_module')), MODULES_CONFIG)
        # Ok, generate a map of library name to module name (i.e. 'AuditEnable' -> 'Enable the Audit Subsystem'
        moduleToLibrary = {}
        libraryToModule = {}
        for lib in modulesdoc.xpathEval('//library'):
            libName = lib.content
            modName = lib.get_parent().prop('name')
            libraryToModule[libName] = modName
            moduleToLibrary[modName] = libName
    except Exception, err:
        print str(err)
        sys.exit(1)

    os.chdir(pathname)
    
    crossxDocs = {}
    if len(sys.argv) > 1:
        docName, docFile = processGuideline(sys.argv[1])
        if docName and docFile:
            crossxDocs[docName] = docFile
    else:        
        for guideFile in os.listdir(GUIDEDIR):
            if guideFile.endswith('.xml'):
                docName, docFile = processGuideline("%s/%s" % (GUIDEDIR, guideFile))
                if docName and docFile:
                    crossxDocs[docName] = docFile 
    buildCrossxAppendix (APPENDIXDOC, crossxDocs)
    
