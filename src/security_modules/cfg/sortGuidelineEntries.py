import os
import sys
import libxml2
import getopt
import re
import pprint
# Copyright (c) 2013 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.


try:
        import libxslt
except ImportError, err:
    msg = "You must install the 'libxslt-python' (Solaris 'SUNWlxsl-python') "\
          "package in order to generate text reports from the command line." 
    print >> sys.stderr, msg
    exit(1)
    
def sortGuidelineEntry(entry):
    
        doc = libxml2.parseFile(entry)
        styledoc = libxml2.parseFile("./sort_guidelines.xsl")
        style = libxslt.parseStylesheetDoc(styledoc)
        result = style.applyStylesheet(doc,None)
        style.saveResultToFilename(entry, result, 0)
        msg = "Wrote sorted master modules list to %s" % entry
        print msg

def sortGuidelineEntries():
            
    for entry in os.listdir("./prod_sources/guidelines"):
        if not entry.endswith('.xml'):
            continue
        entry = "./prod_sources/guidelines/%s" % entry
        sortGuidelineEntry(entry)
    
if __name__ == "__main__":

    sortGuidelineEntries()
