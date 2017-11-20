#!/usr/bin/python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Execute the ${JAVA_HOME}/bin/java command (if it exists) with the '-version'
# argument and try to determine what version and flavor of Java it is
# return two text fields (space separated) 
#   <flavor> <version>
#        flavor can be openjdk, oracle, ibm
#        version can be 1.6 or 1.7

import sys
import os
import commands
import re
import getopt

javaVersion = "Unknown"
javaFlavor  = "Unknown"

showVersion = False
showFlavor = False
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "vf")
    for o,a in opts:
        if o == "-v":
            showVersion = True
        elif o == "-f":
            showFlavor = True
    try:
        javahome = args[0]
    except:
        javahome = os.getenv('JAVA_HOME')
             
except getopt.GetoptError, err:
  sys.exit(str(err))

if javahome:
    fullPath = os.path.join(javahome,"bin","java")
    if os.path.exists(fullPath) and os.access(fullPath, os.X_OK):
        cmd = "%s -version" % fullPath
        status, output = commands.getstatusoutput(cmd)
        lines = output.splitlines()
        if status == 0:
            regex = re.compile("""^java version\s["'](\d+\.\d+).*""")
            match = regex.search(output)
            if match:
                javaVersion = match.group(1)
            
            if lines[2].startswith("OpenJDK"):
                javaFlavor = "OpenJDK"
            elif lines[2].startswith('Java HotSpot'):
                javaFlavor = "Oracle"
            elif lines[2].startswith('IBM'):
                javaFlavor = "IBM"

            if  showVersion==False and showFlavor==False:
                print >> sys.stdout, "Java Provider     = %s\nJava Version(x.y) = %s" % (javaFlavor, javaVersion)
            else:
                if showFlavor==True:
                    print >> sys.stdout, javaFlavor
                if showVersion==True:
                    print >> sys.stdout, javaVersion
            
        else:
            sys.exit("Unable to execute '%s'" % cmd)
    else:
        sys.exit("Unable to find executable command '%s'" % fullPath)
else:
    sys.exit("JAVA_HOME environment variable is not set")
    
