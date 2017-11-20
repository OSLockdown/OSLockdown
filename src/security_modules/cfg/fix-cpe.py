#! /usr/bin/python
##############################################################################
# Copyright (c) 2010-2011 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################


import libxml2


xmldoc = libxml2.parseFile('./security-modules.xml')

for moduleNode in xmldoc.xpathEval("//security_module/platforms"):
    for cpeItem in moduleNode.xpathEval("./cpe-item"):

        if cpeItem.prop("name") == "cpe:/o:centos:centos:5":
            linuxos = cpeItem.copyNode(1)
            linuxos.setProp("name", "cpe:/o:centos:centos:6")
            moduleNode.addChild(linuxos)


xmldoc.saveFormatFile('new-test.xml', 1)
xmldoc.freeDoc()


