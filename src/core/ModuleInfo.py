#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
MODULE_NAME = "ModuleInfo"
MODULE_REV  = "$Rev: 23917 $".strip('$').strip()

import sys
import os
import libxml2

sys.path.append("/usr/share/oslockdown")
import sbProps
import sb_utils.os.info

try:
    import TCSLogger
except ImportError:
    try:
        from sb_utils.misc import TCSLogger
    except ImportError:
        raise

##############################################################################
def sbModule(configFile=sbProps.SB_CONFIG_FILE):
    moduleMeta = {} 

    xmldoc = libxml2.parseFile(configFile)
    for module_name in xmldoc.xpathEval("//security_module"):
        libname = None
        try:
            libname = module_name.xpathEval("library")[0].getContent().strip("'")
            moduleMeta[libname] = {}
            moduleMeta[libname]['views'] = []
            moduleMeta[libname]['compliancy'] = []
            moduleMeta[libname]['platforms'] = []
            moduleMeta[libname]['sortKey'] = None
            moduleMeta[libname]['severity_level'] = "5"
            # note that 'options' must be an array to preserve the order as seen in the dictionary
            moduleMeta[libname]['options'] = []
            # optionsDefaults is a dictionary, because we don't care about order 
            moduleMeta[libname]['optionsDefaults'] = {}
            
        except IndexError:
            continue

        if libname:
            try:
                moduleMeta[libname]['description'] = str(module_name.xpathEval("./description")[0].getContent())
            except:
                pass

            try:
                moduleMeta[libname]['severity_level'] = str(module_name.xpathEval("./severity_level")[0].getContent())
            except:
                pass

            try:
                moduleMeta[libname]['name'] = str(module_name.prop("name"))
                moduleMeta[libname]['sortKey'] = str(module_name.prop("sortKey"))
            except:
                pass

            for option in module_name.xpathEval("./configurationOptions/option"):
                moduleMeta[libname]['options'].append(option.prop('name'))
                # give the 'default' value if any
                defValue = None
                defaults = option.xpathEval('./default')
                if defaults:
                    defValue = defaults[0].getContent()                    
                moduleMeta[libname]['optionsDefaults'][option.prop('name')] = defValue

            for view in module_name.xpathEval("./views/member"):
                moduleMeta[libname]['views'].append(view.getContent())

            for cpeItem in module_name.xpathEval("./platforms/cpe-item"):
                moduleMeta[libname]['platforms'].append(cpeItem.prop("name"))

            for cNode in module_name.xpathEval("./compliancy/line-item"):
                lineItem = "%s|%s|%s|%s" % (cNode.prop("source"), cNode.prop("name"),
                                         cNode.prop("version"), cNode.prop("item"))  
                moduleMeta[libname]['compliancy'].append(lineItem)
                
    xmldoc.freeDoc()
    return moduleMeta


##############################################################################
def getModuleToLibraryMap(configFile=sbProps.SB_CONFIG_FILE):
    moduleMeta = {}

    xmldoc = libxml2.parseFile(configFile)
    for module_name in xmldoc.xpathEval("//security_module"):
        try:
            moduleName = str(module_name.prop("name"))
            libname = module_name.xpathEval("library")[0].getContent().strip("'")
        except IndexError:
            continue

        moduleMeta[moduleName] = libname

    xmldoc.freeDoc()
    return moduleMeta

##############################################################################
def dumpModuleList():
    moduleInfo = sbModule()
    print >> sys.stdout, "-" * 60
    print >> sys.stdout, "Available Modules"
    print >> sys.stdout, "-" * 60
    modlist = []
    for modtest in moduleInfo.keys(): 
        modlist.append(moduleInfo[modtest]['name'])

    del moduleInfo
    modlist.sort()
    for modName in modlist:
        print >> sys.stdout, modName

    print >> sys.stdout, " "

    return

##############################################################################
def dumpModuleInfo(moduleName=None):
    moduleInfo = sbModule()

    if moduleName == None:
        return 
 

    if not moduleInfo.has_key(moduleName):
        for modtest in moduleInfo.keys(): 
            if moduleInfo[modtest]['name'] == moduleName:
                moduleName = modtest
                break

    # Now, try ... 
    if moduleInfo.has_key(moduleName):
        #print >> sys.stdout
        #print >> sys.stdout, "-" * 60
        #print >> sys.stdout, "Module Full Name: %s" % moduleInfo[moduleName]['name']
        #print >> sys.stdout, "    Library Name: %s.pyo" % moduleName
        #print >> sys.stdout, "-" * 60
        #print >> sys.stdout, moduleInfo[moduleName]['description']

        # Compliancy Information
        #for lineItem in moduleInfo[moduleName]['compliancy']:
        #    stuff = lineItem.split('|')
        #    try:
        #       print "  *  %s %s: %s" % (stuff[0], stuff[1], stuff[3])
        #    except IndexError:
        #       pass

        # Dump out profile snippet
        try:
            #print >> sys.stdout, "-" * 60
            xmldoc = libxml2.parseFile(sbProps.SB_CONFIG_FILE)
            print """<?xml version="1.0" encoding="UTF-8"?>"""
            print """<profile name="Test-%s" sysProfile="false">""" % moduleName
            print """  <info>"""
            print """    <description>"""
            print """       <summary>Test of '%s' Module</summary>""" % moduleInfo[moduleName]['name']
            print """       <verbose>None</verbose>"""
            print """       <comments>None</comments>"""
            print """    </description>"""
            print """  </info>"""
            print """    <security_module name="%s">""" % moduleInfo[moduleName]['name']
            optvalue = []
            for modname in xmldoc.xpathEval("//security_module"):
                if modname.prop("name") ==  moduleInfo[moduleName]['name']:
                    for option in modname.xpathEval("./configurationOptions/option"):
                        optValue=""
                        for optionDev in option.xpathEval("./default"):
                            optValue += optionDev.getContent()
                        print """      <option name="%s">%s</option>""" % (option.prop('name'), optValue)

            xmldoc.freeDoc()
            print """    </security_module>"""
            print """</profile>"""
        except:
            pass

    print >> sys.stdout
    return

def getServiceList(libraryName=None):
    """
    Get a list of associated service names associated with the library 
    defined in the modules configuration file.
    """
    if libraryName == None or type(libraryName) != type(''):
        return []    

    configFile=sbProps.SB_CONFIG_FILE
    if not os.path.isfile(configFile):
       return []

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    sysCpeName =  sb_utils.os.info.getCpeName()

    service_list =  []
    working_dict =  {}
    property_dict = {}
    xmldoc = libxml2.parseFile(configFile)
    for module_node in xmldoc.xpathEval("//security_module"):
        cpe_nodes = None
        try:
            libname = module_node.xpathEval("library")[0].getContent().strip("'")
            if libname == libraryName:
                cpe_nodes = module_node.xpathEval("platforms/cpe-item")
        except:
            continue

        if not cpe_nodes:
            continue

        exact_match = False
        for test_cpe in cpe_nodes:
            if sysCpeName == test_cpe.prop("name"):
                exact_match = True
                for service_node in test_cpe.xpathEval("services/service"):
                    svcname = service_node.prop("name")
                    sortKey =  "%s-%s" % (service_node.prop("seq"), svcname)
                    working_dict[sortKey] = svcname

                    if not property_dict.has_key(svcname):
                        property_dict[svcname] = {}

                    if service_node.hasProp("stop-now"):
                        property_dict[svcname]['stop-now'] = service_node.prop("stop-now")

                    if service_node.hasProp("global-zone-only"):
                        property_dict[svcname]['global-zone-only'] = service_node.prop("global-zone-only")
                break
        
        # No exact match so look for partial match...
        if exact_match == False:
            for test_cpe in cpe_nodes:
                if sysCpeName.startswith(test_cpe.prop("name")):
                    for service_node in test_cpe.xpathEval("services/service"):
                        svcname = service_node.prop("name")
                        sortKey =  "%s-%s" % (service_node.prop("seq"), svcname)
                        working_dict[sortKey] = svcname
    
                        if not property_dict.has_key(svcname):
                            property_dict[svcname] = {}
    
                        if service_node.hasProp("stop-now"):
                            property_dict[svcname]['stop-now'] = service_node.prop("stop-now")

                        if service_node.hasProp("global-zone-only"):
                            property_dict[svcname]['global-zone-only'] = service_node.prop("global-zone-only")


        xmldoc.freeDoc()

        keyList = working_dict.keys()
        keyList.sort()
        for svc in keyList:
            service_list.append(working_dict[svc])

        msg = "Identified %s services for module library '%s'" % (str(service_list), libraryName)
        logger.debug(MODULE_NAME, msg)

        # Return an ordered list for proper shutdown/startup sequence and a dictionary
        # of properties that controls module behavior. (i.e., stop-now or not)

        return service_list, property_dict


def getPackageList(libraryName=None):
    """
    Get a list of associated packages associated with the library 
    defined in the modules configuration file.
    """
    if libraryName == None or type(libraryName) != type(''):
        return []    

    configFile=sbProps.SB_CONFIG_FILE
    if not os.path.isfile(configFile):
       return []

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    sysCpeName =  sb_utils.os.info.getCpeName()

    package_list = []
    working_dict = {}
    xmldoc = libxml2.parseFile(configFile)
    for module_node in xmldoc.xpathEval("//security_module"):
        cpe_nodes = None
        try:
            libname = module_node.xpathEval("library")[0].getContent().strip("'")
            if libname == libraryName:
                cpe_nodes = module_node.xpathEval("platforms/cpe-item")
        except:
            continue

        if not cpe_nodes:
            continue

        exact_match = False
        for test_cpe in cpe_nodes:
            if sysCpeName == test_cpe.prop("name"):
                exact_match = True
                for package_node in test_cpe.xpathEval("packages/package"):
                    package_list.append(package_node.prop("name"))
                break
                    

        if exact_match == False:
            for test_cpe in cpe_nodes:
                if sysCpeName.startswith(test_cpe.prop("name")):
                    for package_node in test_cpe.xpathEval("packages/package"):
                        package_list.append(package_node.prop("name"))

        xmldoc.freeDoc()

        msg = "Identified %s packages for module library '%s'" % (str(package_list), libraryName)
        logger.debug(MODULE_NAME, msg)

        return package_list



if __name__ == '__main__':
    #print getServiceList(libraryName='DisableISDN')
    #print getPackageList(libraryName='DisableISDN')

    modname = "Adjust Maximum Pending Connections"
    dumpModuleInfo(modname)
