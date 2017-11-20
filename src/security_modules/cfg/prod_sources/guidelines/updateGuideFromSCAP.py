import re,sys,os
import libxml2
import getopt
import textwrap    
import pprint

try:
    foobar = set([])
except NameError:
    from sets import Set as set

#  Given a SCAP based STIG document and an RTCS OS Lockdown 'guideline' file, ensure that all 
#  line items in the STIG document have a matching entry in the guideline file. 
#  If a line item is missing - add it with the 'title' of the line item
#  If a line item is present, update the title if required but *keep* all other data in the Guideline

#
        
def parseXML( xmlName):
    entries = {}
    f = open(xmlName).read()
    doc = libxml2.parseFile(xmlName)
    ctxt = doc.xpathNewContext()
    xmlns = {}
    for match in re.findall('xmlns:(\w*)="([^"]*)"',f):
        xmlns[match[0]] = match[1]
    for match in xmlns.items():
        ctxt.xpathRegisterNs(match[0], match[1])
    if 'cdf' not in xmlns:
        ctxt.xpathRegisterNs('cdf' , 'http://checklists.nist.gov/xccdf/1.1')

    scapSource = ctxt.xpathEval("//cdf:Benchmark/cdf:reference/dc:publisher")[0].get_content()
    scapName = ctxt.xpathEval("//cdf:Benchmark/cdf:title")[0].get_content()
    scapRel = ctxt.xpathEval("//cdf:Benchmark/cdf:plain-text")[0].get_content().split()[1]
    scapVer = ctxt.xpathEval("//cdf:Benchmark/cdf:version")[0].get_content()
    for group in  ctxt.xpathEval("//cdf:Benchmark/cdf:Group"):
            
        ctxt.setContextNode(group)
        rule = ctxt.xpathEval("./cdf:Rule")[0]
        cat = rule.prop('severity')
        ctxt.setContextNode(rule)
        lineItem = ctxt.xpathEval('./cdf:version')[0].get_content()
        summary = ctxt.xpathEval('./cdf:title')[0].get_content()
        blat = "<blat>"+ctxt.xpathEval('./cdf:description')[0].get_content()+"</blat>"
        pdi=libxml2.parseDoc(blat).xpathEval("//blat/VulnDiscussion")[0].get_content()


        entries[lineItem] = summary.splitlines()[0].strip()
    return entries, (scapSource, scapName, "V%sR%s" % (scapVer,scapRel))
     
def usage():
    print "%s: -s SCAPDOC [-g GUIDEDOC] -o NEWGUIDEDOC [-n NAME] [-t TITLE] [-r RELEASE] [-S SOURCE ] [-e | -d] " % sys.argv[0]
    print "    : -e == enabled,  -d == disabled"
    sys.exit(0)
    
if __name__ == "__main__":
    scapDoc = None
    guideDoc = None
    newGuideDoc = None
    opts,args = getopt.gnu_getopt(sys.argv[1:], "edt:n:v:s:g:o:S:vh")
    source=None
    name=None
    title=None
    version=None
    enabled="True"
    for o,a in opts:
        if o == '-h':
            usage()
        elif o == '-s':
            scapDoc = a
        elif o == '-t':
            title = a
        elif o == '-S':
            source = a
        elif o == '-g':
            guideDoc = a
        elif o == '-o':
            newGuideDoc = a
        elif o == '-n':
            name = a
        elif o == '-v':
            version = a
        elif o == '-d':
            enabled = "False"
        elif o == '-e':
            enabled = "True"
            
    
    # get dictionary of lineitem:description
    scapItems,scapInfo=parseXML(scapDoc)  
    scapEntries = set(scapItems.keys())
    print "Found %d line items in SCAP document" % len(scapEntries)

    # if have a guide to update, pull it in.  Otherwise create an empty one
    if not guideDoc:
        print scapInfo
        guideDoc = libxml2.newDoc("1.0")
        compliancyNode = guideDoc.newChild(None, "compliancy", None)
        compliancyNode.newProp("source","None")
        compliancyNode.newProp("name","None")
        compliancyNode.newProp("version","None")
        compliancyNode.newProp("enabled",enabled)
        titleNode = compliancyNode.newChild(None, "title", "None")
        styleNode = compliancyNode.newChild(None, "style", "ModulesPerLineItem")
        abstract = compliancyNode.newChild(None, "abstract", None)
        lineItems = compliancyNode.newChild(None, "line-items", None)
        guideEntries = set([])
        print "Starting with empty SB Guide"
    else:
    # we're going to modify this *document*, so keep it as such
        guideDoc = libxml2.parseFile(guideDoc)
        guideEntries = set([item.prop('name') for item in guideDoc.xpathEval('//line-item')])
        print "Found %d line items in Guide document" % len(guideEntries)
        compliancyNode = guideDoc.xpathEval("//compliancy")[0]
        titleNode = guideDoc.xpathEval("//compliancy/title")[0]
    if source:
        compliancyNode.setProp('source',source)
    if name:
        compliancyNode.setProp('name',name)
    if version:
        compliancyNode.setProp('version',version)
    if enabled:
        compliancyNode.setProp('enabled',enabled)
    if title:
        titleNode.setContent(title)
        
        
    # Check for what things need to be updated....
    
    print "Checking for items in both documents - these may have title changes"
    inBoth = guideEntries.intersection(scapEntries)
    
    print "Checking for items in guide but not in SCAP - these need to be removed"
    inGuideNotSCAP = guideEntries - scapEntries
    print "  .. found %d such entries" % len(inGuideNotSCAP)

    print "Checking for items in Guide but not in SCAPGuide - these need to be added"
    inSCAPNotGuide =  scapEntries - guideEntries 
    print "  .. found %d such entries" % len(inSCAPNotGuide)

    print "\nUpdating Guide document...\n"
    
    if inGuideNotSCAP:
        print "\n\nRemoving entries from Guide document not in SCAP document..."
        for entry in inGuideNotSCAP:
            for item in guideDoc.xpathEval('//line-item[@name="%s"]'% entry):
                print "  Removing %s" % (entry)
                item.unlinkNode()
                item.freeNode()

    if inSCAPNotGuide:
        print "\n\nAdding %d entries from SCAP not in Guide document..." % len(inSCAPNotGuide)
        lineItemsNode = guideDoc.xpathEval('//line-items')[0]
        for entry in inSCAPNotGuide:
            desc = scapItems[entry]
            print "  Adding %s : %s" % (entry,desc)
            newItem = libxml2.newNode('line-item')
            newItem.setProp('name', entry)
            newItem.setProp('description', desc)
            lineItemsNode.addChild(newItem)

    if inBoth:
        print "\n\nVerifying titles are the same between documents..."
        for entry in inBoth:
            itemGuide = guideDoc.xpathEval('//line-item[@name="%s"]'% entry)[0]
            descGuide = itemGuide.prop('description').strip()
            descScap = scapItems[entry].strip()
            
            if descGuide != descScap:
                print "  Updating %s" % (entry)
                print "\t\t- %s\n\t\t+ %s\n" % (descGuide,descScap)
                itemGuide.setProp('description', descScap)

    if newGuideDoc:
        print "Saving to %s" % newGuideDoc
        newFile = open(newGuideDoc,"w")
        guideDoc.saveTo(newFile, 'UTF-8',1)
        newFile.close()
                   
#    for key in sorted(scapItems.keys()):
#        print "%s|%s" % (key, scapItems[key])
