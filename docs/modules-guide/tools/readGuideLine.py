import libxml2
import os

def readText(guideFile):
    guideDict = {}
    infile = open(guideFile, 'r')
    lines = infile.readlines()
    for line in lines:
        (lineitem, desc) = line.split('|')
        guideDict[lineitem] = desc.strip()
    infile.close()
    return guideDict
    
def readXML(guideFile):    
    guideDict = {}
    lineItems = {}
    notCovered = {}
    xmlDoc = libxml2.parseFile(guideFile)
    compLine = xmlDoc.xpathEval('//compliancy')[0]
    for entry in ['source', 'name', 'version', 'enabled']:
        z = compLine.prop(entry)
        if z != None and z != "None":
            guideDict[entry] = z
        else:
            guideDict[entry] = ""


    # Grab the following including embedded html/xml styling
    defVals = {'abstract':'No Description Provided', 'subtitle':None}
    for piece in defVals.keys():
        try:
            guideDict[piece] = compLine.xpathEval(piece)[0].copyNode(1)
        except Exception, err:
            if piece == 'title':
                guideDict['title'] = '%s %s %s' % (guideDict['source'], guideDict['name'], guideDict['version'])
            else:
                guideDict[piece] = defVals[piece]
    #Grab the following as raw text
    defVals = {'style':'ModulesPerLineItem', 'MaxItemsPerTable': None, 'lineitemprefix': None}
    for piece in defVals.keys():
        try:
            guideDict[piece] = compLine.xpathEval(piece)[0].getContent()
        except Exception, err:
            guideDict[piece] = defVals[piece]

    for entry in xmlDoc.xpathEval('//line-item'):
        docItem = entry.prop('name')
        docDesc = entry.prop('description')
        docModules = [mod.prop('libraryName') for mod in entry.xpathEval('module') ] 
        docModules.sort()
        docData = {}
        docData['description'] = docDesc
        docData['modules'] = docModules
        if docModules:
            lineItems[docItem] = docData
        else:
            notCovered[docItem] = docData
    guideDict['lineitems'] = lineItems
    guideDict['notcovered'] = notCovered
    return guideDict
    
def read(guideFile):
    return readText(guideFile)
#    return readXML(guideFile)

if __name__ == "__main__":
    import sys
    import pprint
    if sys.argv[1].endswith('.xml'):
        z= readXML(sys.argv[1])
        pprint.pprint(z)
    
