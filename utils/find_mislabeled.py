#!/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
import sys,os
import commands

def main():
    filepaths = []
    if len(sys.argv) == 1:
        filepaths.append('/')
    else:
        for path in sys.argv[1:] :
            if os.path.exists(path) and path not in filepaths:
                filepaths.append(path)
            else:
                print "%s does not exist, skipping it" % path
    
    command = "/sbin/restorecon -F -R -n -v %s " % " ".join(filepaths)
    print command
    
    status,output = commands.getstatusoutput(command)
    if status != 0 :
        print "Error code = %d from '%s'" % (status,command)
    else:
        # each line should be '<text1> <text2> <name> <text3> <context>' where name could
        # contain spaces. so be careful with parsing
        for line in output.splitlines():
            
            
            #the last space separated field is the paired contexts.  If they are the same, no further processing required
            line = line.strip()
            lastspace = line.rfind(" ")
            
            contexts = line[lastspace+1:]
            # split the contexts looking for the '->' chars
            delim = contexts.find('->')
            if delim > 0:
                c1 = contexts[0:delim]
                c2 = contexts[delim+2:]
                
                # if the contexts differ then extract the name
                if c1 != c2: 
                    space1 = line.find(' ')
                    space2 = line.find(' ',space1+1)
                    text3 = line.rfind(' ',0,lastspace-1)
                    fname = line[space2+1:text3]

                    #use a 'tab' key for the delimiter - eases parsing later
                    print "%s\t%s\t%s "% (fname,c1,c2)
            
if __name__ == "__main__":
    main()
