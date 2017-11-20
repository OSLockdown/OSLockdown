#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2009 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import libxml2
import sys
import os
import commands
import pprint

xmldoc = libxml2.parseFile('../../../src/security_modules/cfg/security-modules.xml')
modules_dir = "../modules"

#
#
print "\nChecking for modules in security-modules.xml without help page..."
missingMods = []
for node in xmldoc.xpathEval("//security_module/library"):
    moduleNode = node.parent
    libraryName = node.getContent().strip("'")
    if not os.path.exists("%s/%s.xml" % (modules_dir, libraryName)):
        print "\tNo module help found for %s" % libraryName
        missingMods.append(libraryName)

if missingMods:
    print "%d modules found w/o help pages" % len(missingMods)
