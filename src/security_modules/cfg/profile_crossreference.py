import libxml2,os,sys
# Copyright (c) 2012-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

try:
    foobar = set([])
except NameError:
    from sets import Set as set

def selectFromList (elementList):
    while True:
        for idx,item in enumerate(elementList):
            print "%2d) %s" % (idx+1,item)
        idx = int(raw_input("Enter selection (0 to exit): ")) -1
        if idx < 0 :
            item = None
            break
        try:
            item = elementList[idx]
            break
        except Exception:
            print "Invalid selection, please try again..."
    return item

class ProfileCrossReference:
    def __init__(self):
        # if in dev mode - figure out where we are by looking at the executable name
        if "-d" in sys.argv:
            secModsDevBase = os.path.dirname(sys.argv[0])
            self.secModsDir = secModsDevBase
            self.profilesDir = os.path.dirname(secModsDevBase)+"/profiles"
        else:
            self.secModsDir = '/usr/share/oslockdown/cfg'
            self.profilesDir = "/var/lib/oslockdown/profiles"
        
        self.sefModsFile = "%s/security-modules.xml" % self.secModsDir
        self.modules = libxml2.parseFile(self.sefModsFile)
        self.selectedCompliancy = ""
        self.selectedProfile = ""
        self.moduleToCompliancy = {}
        self.compliancyToModule = {}
        self.crossRefType = "item-to-module"

    def printItemToModule(self):
        print "The following item(s) have associated module(s) for '%s'" % (self.selectedCompliancy)
        print "="*40
        for item, values in sorted(self.compliancyToModule.items()):
            print "\t%s: %s" % (item, ','.join(values))
        
    def printModuleToItem(self):
        print "The following module(s) have associated compliancy(ies) for '%s'" % (self.selectedCompliancy)
        print "="*40
        for item, values in sorted(self.moduleToCompliancy.items()):
            print "\t%s: %s" % (item, ','.join(values))
        
    def printModuleWithoutItem(self):
        modulesWithOutCompliancy = sorted([module for module in self.moduleToCompliancy if not self.moduleToCompliancy[module]])
        
        if modulesWithOutCompliancy:
            print "Found %d module(s) without an associated compliancy for '%s'" % (len(modulesWithOutCompliancy), self.selectedCompliancy)
            print "="*40
            for item in modulesWithOutCompliancy:
                print "\t%s" % item
        else:
            print "All modules had at least one compliancy item."
            print "="*40
        

    def selectCrossReferenceType(self):
        
        typeSet = ['item-to-module','module-to-item','module-without-item']
        print "Please select the cross reference mapping to use:"
        self.crossRefType = selectFromList(typeSet)
        
    def selectCompliancy(self):
        # parse the module list to get the 'names' of the current compliancies

        compSet = set([])
        print "Please select the Compliancy Guideline to use:"
        for compliancyNode in self.modules.xpathEval("//security_module/compliancy/line-item"):
            compSet.add(compliancyNode.prop("name"))

        compNames = sorted(compSet)   
        self.selectedCompliancy = selectFromList(compNames)
        
    def selectProfile(self):
        profiles = ["All Modules"]
        profiles.extend(sorted([fileName for fileName in os.listdir(self.profilesDir) if fileName.endswith('.xml') ]))
        print profiles
        selected = selectFromList(profiles)
        print "Please select the Profile to use, or 'All Modules':"
        if selected:
             self.selectedProfile = selected

    def generateCrossReference(self):
        self.selectCompliancy()
        self.selectProfile()
        self.selectCrossReferenceType()
        
        if not self.selectedProfile:
            print "No profile selected to cross reference"
            sys.exit(1)
        if not self.selectedCompliancy:      
            print "No compliancy selected to cross reference"
            sys.exit(1)
        if not self.crossRefType:      
            print "No report type selected."
            sys.exit(1)

        # Generate list of Modules to look for
        modList = []
        print self.selectedProfile
        if (self.selectedProfile != "All Modules"):
            profile = libxml2.parseFile(self.profilesDir+"/"+self.selectedProfile)
            for profModule in profile.xpathEval('//security_module'):
                modList.append(profModule.prop('name'))
        else:
            for entry in self.modules.xpathEval("//security_module"):
                modList.append(entry.prop('name'))
	
        for modName in modList:
            self.moduleToCompliancy[modName] = []
            for compliancy in self.modules.xpathEval("//security_module[@name='%s']/compliancy/line-item[@name='%s']" % (modName, self.selectedCompliancy)):
                compliancyItem = compliancy.prop('item')
                if compliancyItem not in self.moduleToCompliancy[modName]:
                    self.moduleToCompliancy[modName].append(compliancyItem)

                if compliancyItem not in self.compliancyToModule:
                   self.compliancyToModule[compliancyItem] = []
                if modName not in self.compliancyToModule[compliancyItem]:
                    self.compliancyToModule[compliancyItem].append(modName)
	    
        if self.crossRefType == 'item-to-module':
            self.printItemToModule()
        elif self.crossRefType == 'module-to-item':
            self.printModuleToItem()
        elif self.crossRefType == 'module-without-item':
            self.printModuleWithoutItem()
            
        


if __name__ == "__main__":
    profileCrossReference = ProfileCrossReference()
    profileCrossReference.generateCrossReference()

