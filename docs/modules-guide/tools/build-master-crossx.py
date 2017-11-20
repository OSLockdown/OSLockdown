#!/usr/bin/python

import sys
import libxml2
import os


pathname = os.path.dirname(sys.argv[0])
MODULES_CONFIG = os.path.join(pathname, 
     '../../../src/security_modules/cfg/security-modules.xml')
CROSSX_DOC = os.path.join(pathname, '../../dist/Marketing-master-crossx.csv')
try:
    modulesdoc = libxml2.parseFile(MODULES_CONFIG)
except Exception, err:
    print str(err)
    sys.exit(1)

os.chdir(pathname)

##############################################################################
include_mods = []
master_crossx = {}
module_names = {}
print ":: Gathering Module information..."
for module_node in modulesdoc.xpathEval("//security_module"):

    module_name = module_node.prop("name")
    for lnode in module_node.xpathEval("library"):
        if lnode.getContent() != "":
            moduleID = "%s" % lnode.getContent().strip("'")
            module_names[moduleID] = module_name
            break

    #print ":: %s (%s)" % (module_name, moduleID)
    for cnode in module_node.xpathEval("compliancy/line-item"):
        source_ref = "%s" % (cnode.prop("source"))

        if not master_crossx.has_key(source_ref):
            master_crossx[source_ref] = []

        if not moduleID in master_crossx[source_ref]:
            master_crossx[source_ref].append(moduleID)

        include_mods.append(moduleID)

modulesdoc.freeDoc()    

include_mods = set(include_mods)

out_obj = open(CROSSX_DOC, 'w')
out_obj.write(""""OS Lockdown Module",""")
for source_key in sorted(master_crossx.keys()):
    out_obj.write(""""%s",""" % source_key)
out_obj.write(""""Custom"\n""")

for modname in include_mods:
    line = """"%s",""" % module_names[modname]
    compl_items = []
    for source_key in sorted(master_crossx.keys()):
         if modname in master_crossx[source_key]:
             line = """%s"X",""" % (line)
         else:
             line = """%s"",""" % (line)

    out_obj.write(line)
    out_obj.write(""""X"\n""")

print ":: Wrote %s" % CROSSX_DOC
out_obj.close()
