#!/usr/bin/python

# Given one or more *Library* names (i.e, AccountLocks) locate and pull
# up the relevent files from 
#  - cfg/prod_sources/module_groups/ XML file
#  - oslockdown/docs/modules-guide/modules code
#  - Python library code (all variants)

import os
import sys

def populateName(dirName, libName, suffix):
    
    candidate = "%s/%s%s" % (dirName, libName, suffix)
    if not os.path.exists(candidate) :
        candidate = None
    if candidate:
        return [candidate]
    else:
        return []
    
def locatePython(libName):
    pyFiles = []
    for dirName in ['fedora', 'generic', 'redhat', 'redhat6', 'solaris', 'suse']:
        pyFiles.extend(populateName(dirName, libName, '.py'))
    return pyFiles
    
def locateModuleAPI(libName, createIfNotFound = False):
    apiFiles = []
    baseDir = 'cfg/prod_sources/module_groups'
    for dirName in os.listdir(baseDir):
        fullDir = "%s/%s" % ( baseDir, dirName)
        if os.path.isdir(fullDir):
            apiFiles.extend(populateName(fullDir, libName, '.xml'))
    return apiFiles
    
def locateDocs(libName, createIfNotFound = False):
    docFiles = []
    for dirName in ['../../docs/modules-guide/modules']:
        docFiles.extend(populateName(dirName, libName, '.xml'))
    return docFiles

def locateFiles(libName):
    x = locatePython(libName)
    y = locateModuleAPI(libName)
    z = locateDocs(libName)
    return x+y+z

if __name__ == "__main__":
    # get the *current* direction from the directory name of how we
    # were executed.  If no dirname, assume we're in the security-modules
    # directory.  If we *have* a dirname, then we need to cd there first so
    # that all relative directories are based from there
    
    startDir = None
    getFiles = []
    execName = sys.argv[0]
    execDir = os.path.dirname(execName)
    if execDir not in ["", "."] :
        startDir = os.curdir
        os.chdir (execDir)
        
    for i in sys.argv[1:]:
        getFiles.extend(locateFiles(i))

    print ' '.join(getFiles)
    if startDir:
        os.chdir (startDir)
        
