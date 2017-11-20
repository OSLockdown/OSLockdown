#! /usr/bin/python
##############################################################################
# Copyright (c) 2007-2012 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

import libxml2
import pprint
import sys
import os

def parseCPE(cpeNode):
    cpeInfo = {}
    services = {}
    packages = {}
#    print cpeNode
    for service in cpeNode.xpathEval("./services/service"):
      seq = service.prop("seq")
      name = service.prop("name")
      services[seq] = name
    for package in cpeNode.xpathEval("./packages/package"):
      name = package.prop("name")
      packages[name] = True
    return {"services":services, "packages":packages}

def parseModule(moduleNode):
    modInfo = {}
    haveData = False
    for i in ["4", "5", "6"]:
      modInfo[i] = {}
      for j in ["centos", "redhat", "oracle"]:
        modInfo[i][j] = {}

    for cpeItem in moduleNode.xpathEval("./platforms/cpe-item"):
        cpeFields = cpeItem.prop("name").split(":")
        if cpeFields[1] == "/o" and cpeFields[2] in ['centos','oracle','redhat'] and cpeFields[3] in ['centos' , 'enterprise_linux']:
            haveData = True
            vers = cpeFields[4]
            vendor = cpeFields[2]
            modInfo[vers][vendor] = parseCPE(cpeItem)
            
    if not haveData:
        retdata = {}    
    else :
        retdata = {modName: modInfo}
    return retdata

def get_os (module, vers, os):
    data = None
    try:
        data = module[vers][os]
    except KeyError:
        pass
    return data
    
def verifyModule(modName, moduleData, ignoreOracle6=False):
    different = False
    dumps = []
    for vers in  sorted(moduleData.keys()):
        centos = get_os(moduleData, vers, 'centos')
        redhat = get_os(moduleData, vers, 'redhat')
        oracle = get_os(moduleData, vers, 'oracle')
        
        if centos != redhat or (not ignoreOracle6 and oracle != centos):
            dumps += ["Version = %s                                         METADATA DIFFERENCE IDENTIFIED\n" % (vers) ]
        else:
            dumps += ["Version = %s\n" % (vers) ]
        
        dumps.extend((pprint.pformat({"centos":centos})+"\n").splitlines(True))
        dumps.extend((pprint.pformat({"redhat":redhat})+"\n").splitlines(True))
        if not vers == "6" or not ignoreOracle6:
            dumps.extend((pprint.pformat({"oracle":oracle})+"\n").splitlines(True))
    if dumps :
        print "\n\n%s" % modName
        sys.stdout.writelines(dumps)
    
try:
    if sys.argv[1]:
        if os.path.exists(sys.argv[1]):
            xmlFile = sys.argv[1]
        else:
            print "File %s does not exists" % sys.argv[1]
            sys.exit(1)
except Exception, e:
    print e
    xmlFile = './security-modules.xml'
    
print xmlFile        
    
xmldoc = libxml2.parseFile(xmlFile)
modules = {}


for moduleNode in xmldoc.xpathEval("//security_module"):
    modName = moduleNode.prop("name")
    modules[modName] = {}
    modules.update(parseModule(moduleNode))
            
for module, data in modules.items():
  verifyModule(module, data, ignoreOracle6=False)


