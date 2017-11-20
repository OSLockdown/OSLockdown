import libxml2,os
##############################################################################
# Copyright (c) 2013 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################


def readXML(fileName):
    doc=libxml2.parseFile(fileName)
    mods = []
    for mod in doc.xpathEval('//security_module'):
        modName = mod.prop('name')
        if modName not in mods:
            mods.append(modName)
        else:
            print "MODULE '%s' ALREADY PRESENT IN %s" % (modName, fileName)
    print "Found %d modules in %s" % (len(mods), fileName)
    return mods    






baseDir = '..'
allModules = []
allProfiles = {}

allModules = readXML('%s/cfg/security-modules.xml' % (baseDir))

profiles = [ f for f in os.listdir('%s/profiles' % baseDir) if f.endswith('.xml')]

for profile in profiles:
    profName = '%s/profiles/%s' % (baseDir, profile)
    allProfiles[profile] = readXML(profName) 

for profile in profiles:
    for mod in allProfiles[profile]:
        if not mod in allModules:
            print "%s: Module '%s' not found in master list" % (profile,mod)
            
