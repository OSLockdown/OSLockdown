#!/usr/bin/env python 
##############################################################################
# Copyright (c) 2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
#
# This script is designed to properly search a given directory (recursively)
# to find all 'properly' built OS Lockdown releases.  For each one
# found, it will populate the OS Lockdown 'autoupdate' directory with
# the required files and rebuild the autoupdate.tgz file as required.  All SB
# files in any given directory are assumed to be built for the same target
# platform.  
#
# A 'properly' built SB release will consist of the following RPMs/PKGs, as well
# as two non-packaged files:
#
#
#  oslockdown-<release>.{pkg,rpm}
#  oslockdown-modules-<release>.{pkg,rpm}
#  oslockdown-dispatcher-<release>.{pkg,rpm}
#  oslockdown-selinux-<release>{pkg,rpm}  *** OPTIONAL ***
#  AutoupdateComms.pyo
#  _AutoupdateComms.so

#  For all RPMs, the actual 'built for' information is part of the RPM
#  description.  For the Solaris packages, the name of the dispatcher PKG
#  will indicate the required architecture.

import os
import sys
import re
import commands
import getopt
import shutil
import pwd
import grp

dirsWithSBFiles = {}

# All our package/rpms have a format like this - elements in {} are optional
#  oslockdown{-<MODULE>}-<VERSION>-<RELEASE>{.<OS>}.<ARCH>.<RPM|PKG>
sbFilesRegex = """
        (?P<base>^oslockdown)        # all start with this
        (-(?P<module>[^-]*))?        # module is *OPTIONAL*
        -(?P<version>\w+.\w+.\w+)    # what version
        -(?P<release>[^.]+)          # what release
        .(?P<distro>\w*)             # what distribution
        .(?P<arch>\w*)               # what architecture
        .(?P<type>rpm|pkg)$          # must end with pkg or rpm"""
sbFilesRE = re.compile(sbFilesRegex,re.VERBOSE)

# The Linux RPMs have the 'platform' they are applicable for built into the
# description string.  Here's a regex to pull that out..

sbBuiltForRegex = """Applicable for (\w+-\w+-\w+) systems"""
sbBuiltForRE = re.compile(sbBuiltForRegex)

def checkForSBFiles(thisDir):
    sbCore = None
    sbModules = None
    sbDispatcher = None
    sbSelinux = None
    sbAutoUpdateSO = None
    sbAutoUpdatePYO = None
    sbArchitecture = None
    sbType = None
    
    for f in os.listdir(thisDir):
        if not (f.startswith('oslockdown') or "Comm" in f):
            continue
        if f.startswith('oslockdown'):
            g = sbFilesRE.match(f)
            if g:
                modName = g.group('module')
                if modName == None:
                    sbCore = f
                elif modName == 'modules':
                    sbModules = f
                elif modName == 'dispatcher':
                    sbDispatcher = f
                    sbArchitecture = g.group('arch')
                    sbType = g.group('type')
                elif modName == 'selinux':
                    sbSelinux = f
                # we don't care about the Console for autoupdate        
        elif f == 'AutoupdateComms.pyo':
            sbAutoUpdatePYO = f
        elif f == '_AutoupdateComms.so':
            sbAutoUpdateSO = f
        
    
    # if we don't have the minimum files, then punt silently
    if not (sbCore and sbModules and sbDispatcher and sbAutoUpdateSO and sbAutoUpdatePYO):
        return
        
    # Now to add these to our working group
    
    # If we're an RPM, query the dispatcher module to get the correct 'built-for' data.
    # we could use the python bindings, but there has been a memory leak in older versions there, 
    # and we'll likely be calling it repeatedly
    
    if sbType == 'rpm':
        cmd ='rpm -q --queryformat "%%{DESCRIPTION}" -p %s/%s' % (thisDir,sbDispatcher) 
        status,output = commands.getstatusoutput(cmd)
        try:
            builtFor = sbBuiltForRE.search(output).group(1)
        except Exception, e:
            print e
            return
        #    
    else:
        # Ok, if we're a pkg (Solaris), we know we're for Solaris 10.  Just need to find out what
        # architecure, so look at the 
        builtFor = "solaris-10-%s" % sbArchitecture
        
#    print "\tsbCore %s" % sbCore
#    print "\tsbModules %s" % sbModules
#    print "\tsbDispatcher %s" % sbDispatcher
#    print "\tsbSelinux %s" % sbSelinux
#    print "\tssbAutoUpdateSO %s" % sbAutoUpdateSO
#    print "\tsbAutoUpdatePYO %s" % sbAutoUpdatePYO
    # Now build our record with this builtfor info
    autoupdaterFiles = []
    installFiles = []
    for f in [sbCore, sbModules, sbDispatcher, sbSelinux]:
        if f:
            installFiles.append(os.path.join(thisDir,f))
    
    for f in [sbAutoUpdateSO, sbAutoUpdatePYO]:
        autoupdaterFiles.append(os.path.join(thisDir,f))
    if sbCore.split('.')[-1] == 'rpm':
        pkg_rpm = 'rpm' 
    else:
        pkg_rpm = 'pkg'
    dirsWithSBFiles[builtFor] = {'pkg_rpm': pkg_rpm, 'installFiles': installFiles, 'autoupdaterFiles' : autoupdaterFiles}
    
def locateSBFiles(startDir):
    # Ok, start looking...for each directory, call a separate routine to 
    # do the actual evaluation
    for root, subdir, files in os.walk(startDir):
        files = []
        # Go check for files
        checkForSBFiles(root)

def deepCopyFile (srcFile, destFile):
    parentDir = os.path.dirname(destFile)
    # try and make the directory.  Yowl if there is already a regular
    # file by that name or there is a problem other than the directory
    # already existing
    
    try:
        os.makedirs(parentDir)
#        print "Created %s" % parentDir
    except OSError, err:
        if not os.path.isdir(parentDir):
            print "Unable to create directory %s -> a file by that name exists" % parentDir
            sys.exit(1)
    
    shutil.copy(srcFile, destFile)
    
    
    
def copySBFiles(destDir):
    # walk through each 'entry' in the dirsWithSBFiles dirctionary
    # each key is the name that the files for that key were build for
    # by distro 'major number' and architecture.  We'll need to create
    # and entry by that name in the destdir and copy the files there.
    # We'll also need to split this field (on '-') and create an
    # entry in autoupaters/<DISTRO>/<MAJORls>/<ARCH>/ and copy the 
    # autoupdate files there.
    
    for cpeDirName,files in dirsWithSBFiles.iteritems():
        print "Updating '%s's for target platform %s" % (files['pkg_rpm'], cpeDirName)

        # split the cpdDirName into the distro/major/arch name and use those as path components
        cpePath = os.path.join('',*cpeDirName.split('-') )
        targetDir = os.path.join(destDir, "releases", cpePath)
        
        # split the 'builtFor' into 
        for entry in files['installFiles']:
            targetFile = os.path.join(targetDir,os.path.basename(entry))
            deepCopyFile(entry, targetFile)
        
        targetDir = os.path.join(destDir,"autoupdate","autoupdaters",cpePath)
        for entry in files['autoupdaterFiles']:
            targetFile = os.path.join(targetDir,os.path.basename(entry))
            deepCopyFile(entry, targetFile)

def createNewTarball(sbwebappUID, sbwebappGID, destDir):
    import tarfile
    
    print "Initially in ", os.getcwd()
    currentDir = os.getcwd()
    os.chdir(destDir)
    print "Moved to working directory ", os.getcwd()
    try:
        realFile = "autoupdate.tgz"
        tmpFile = "%s_tmp" % realFile
        out = tarfile.open(tmpFile, mode='w:gz')
        print "Creating new %s file as a temporary file..." % tmpFile
        try:
            out.add("autoupdate")
            out.close()
        except Exception, err:
            print "Unable to create %s -> %s" % (os.path.join(destDir,tmpFile), err)
            return
    
        print "Moving %s to %s..." %(tmpFile, realFile)
        try:
            if os.path.exists(realFile):
                os.unlink (realFile)
            os.rename (tmpFile, realFile)
            os.chown (realFile,sbwebappUID, sbwebappGID)
            os.chmod (realFile,0660)
        except Exception, err:
            print "Unable to copy %s to %s -> %s" % (tmpFile, realFile, err)
            return
    finally:
        os.chdir(currentDir)    
    print "Finally in ", os.getcwd()
 
def fixOwnerPerms(destDir, sbwebappUID, sbwebappGID, perms):
    #remember that directories must have execute perms to be read
    dperms = perms | (((perms&0400)>>2) | ((perms & 040)>>2) | ((perms & 004)>>2))
    for root, dirs,files in os.walk(destDir):
        for d in dirs:
            fullname = os.path.join(root,d)
            os.chown(fullname, sbwebappUID, sbwebappGID)
            os.chmod(fullname, dperms) 
    for f in files:
        fullname = os.path.join(root, f)
        os.chown(fullname, sbwebappUID, sbwebappGID)
        os.chmod(fullname, perms) 
        
            
def usage():
    print "%s : -s [srcdir] -d [destdir]" % sys.argv[0]
    sys.exit(1)
        
if __name__ == "__main__":

    cmdArgString  = 's:d:u:'
    srcDir = None
    destDir = '/var/lib/oslockdown/files/ClientUpdates'
    destUsr = 'sbwebapp'
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], cmdArgString)
        for o,a in opts:
            if o == '-s':
                srcDir = a
            elif o == '-d':
                destDir = a
            elif o == '-u':
                destUsr = a            
        if not srcDir:
            print "No source directory given to process"
            sys.exit(1)
        if  not os.path.isdir(srcDir):
            print "Srcdir '%s' does not exist" % srcDir
            sys.exit(1)
        if not destDir:
            print "No destination directory provided"
            sys.exit(1)
    except getopt.GetoptError,err:
        print err
        usage()

    try:
        sbwebappUID, sbwebappGID = pwd.getpwnam(destUsr)[2:4]
    except Exception, err:
        print "Unable to get user '%s' UID/GID -> %s" % (destUsr, err)
        sys.exit(1)

    # First, go locate any 'properly' built release files 
    locateSBFiles(srcDir)
    
    # Now go copy the RPMs or PKGs to the correct location
    copySBFiles(destDir)
    
    # Fix *everything* in the destDir correctly
    fixOwnerPerms(destDir, sbwebappUID, sbwebappGID, 0660)
    
    # Now go copy the autoupdater files to the correct locations so we can
    # make the new 'autoupdate.tgz' bundle
    createNewTarball(sbwebappUID, sbwebappGID, destDir)
    
   
