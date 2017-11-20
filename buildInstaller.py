#!/usr/bin/env python
#
# Copyright (c) 2007-2016 by Forcepoint LLC
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#  
#;
# Script to help package a set of discrete set of directories holding the
# built OS Lockdown packages and documention files into a single
# combined installer.

#######
#######

import sys
import os
import re
import pwd
import commands
import getopt
import tarfile
import re
import cStringIO
import time


# Since we might be running on older Solaris 10 (Python 2.3.4) ....
try:
   set
except NameError:
   from sets import Set as set


pkgRe = re.compile("oslockdown(-(?P<module>([a-z]+|[a-z]+-ibmjava)))?(-(?P<version>(\d+\.\d+\.\d+)))(-(?P<releaseName>\w+))")


### Prompt the user to select an entry from a list - entry is returned or 'None' if no selection
def selectFromList(prompt=None, foundName = "", choices=[], default=-1, preprompt=None):

  # Insert a 'Do not use ' Option as first entry, if we don't already have one
  choices.insert(0,"Do not include")
  print ""
  prompt_str = ""
  default_str = ""
  if prompt == None:
    prompt = "Please select from above "
  
  default_item = -1
  
  if type(default) == type(0) and default >= 0 and default < len(choices) :
    default_str = " [%d]" % default
  else :
    default = None
  prompt_str = "%s %s:" % (prompt, default_str)
  sel_item=-1

  while True:
    if preprompt:
      print "%s\n" % preprompt
    
    for opt in range(len(choices)):
      if default != None and default == opt:
        print "*",
      else:
        print " ",
      print "%3d %s " % (opt, choices[opt])
    print
    sel_input = raw_input(prompt_str).strip()

    if sel_input == "":
      if default != None :
        sel_item = default
    elif sel_input.isdigit():
      sel_item=int(sel_input)
    
    if sel_item >= 0 and sel_item < len(choices):
      break 
    print "\nPlease enter a choice from the above list.\n"
 
  if sel_item != 0: 
    return choices[sel_item]
  else:
    return None
     
## Prompt the user with a Yes/No prompt
def askYesOrNo(prompt=None, default = None):
  default_str = ""
  prompt_str = ""

  if prompt == None :
    prompt = "Please answer "
  
  if default and str(default).upper() in ['Y','YES'] :
    default_str += " [Y]" 
    default = "YES"
  elif default and str(default).upper() in ['N','NO']:
    default_str += " [N]"
    default = "NO"
  else:
    default = ""
  
  prompt_str = "%s(Y/N)%s: " % ( prompt, default_str)
  answer = ""
  while answer.upper() not in ["YES", "NO", "Y", "N" ] :
    answer = raw_input(prompt_str).upper()
    if answer == "Y" or answer == "Y":
      answer = "YES"
    elif answer == "N" or answer == "NO":
      answer = "NO"
    elif answer == "" and default :
      answer = default
    else:
      print "Please specify either yes or no."
    
  return answer.upper()
  

## Prompt the user for a plain string - yes, a short routine
def askForString(prompt=None, default = None):
  default_str = ""
  prompt_str = ""

  if prompt == None:
    prompt = "Your answer: "

  if default != None:
    default_str += " [%s]" % default

  prompt_str = "%s%s: " % ( prompt, default_str)
  answer = raw_input(prompt_str)
  if answer == "" and default != None:
    answer = default
  return answer


# add srcObject, or if srcObject is a directory all 
# top level non-hidden files therein, to the indicated
# dstDir in the tar archive
def addToArchive(tarArchive, srcObject, dstDir):
  savedPath = os.getcwd()
  os.chdir(srcDir)
  if (os.path.isdir(srcObject)):
    for f in os.listdirs("."):
      #skip all hidden files
      if f.startswith("."): continue
      shutil.copy(f, dstDir)
  else:
     pass
  os.chdir(savedPath)

# A given package looks like 'oslockdown[-MODULE]-VERSION-RELEASE[-DISTRO][-MajorVersion]-ARCH.(pkg|rpm)
#   MODULE is optional.
#   Version = X.Y.Z, where X,Y, and Z are integers
#   RELEASE is a text 'word' (no whitespace)
#   DISTRO and MAJORVersion are optional
def getReleaseNameFromPackage(package):
  moduleName = ""
  match = pkgRe.search(package)
  if not match:
    print "Exiting.  Unable to determine release name from '%s'" % package
    sys.exit(1)
  return match.group('releaseName')
    
# For a given directory, parse the contents looking for:
# Console packages (any pkg or rpm file with 'console'
# Non-console packages (any pkg or rpm file without 'console'
# Docs (anything ending in .pdf)
# autoupdate files (anything with *.pyo or *.so)

# If we found packages, determine the 'release' name
# A given package looks like 'oslockdown[-MODULE][-ibmjava]-VERSION-RELEASE[-DISTRO][-MajorVersion]-ARCH.(pkg|rpm)
#   MODULE is optional.
#   Version = X.Y.Z, where X,Y, and Z are integers
#   RELEASE is a text 'word' (no whitespace)
#   DISTRO and MAJORVersion are optional
#
# return the 'built_for' name and dictionary of information with your findings, or raise an error and exit
def vetBuildDirectory(buildDir):
  # change to that directory so we're not constantly building a path
  dirContents={ 'srcpath': os.path.abspath(buildDir), 'console_pkg':[],'console_rpm':[], 'nonconsole':[], 'docs':[], 'autoupdate':[],'releaseName':'' }
  built_for = None
  savedPath = os.getcwd()
  os.chdir(buildDir)
  
  # loop over contents
  for f in os.listdir("."):
    if not os.path.isfile(f) or f.startswith('.'): continue
    if f.endswith('.pkg') or f.endswith('.rpm'):
      # get releasename from file
      relName = getReleaseNameFromPackage(f)
      if not dirContents['releaseName']:
        dirContents['releaseName'] = relName
      elif relName != dirContents['releaseName']:
        print "Exiting.  Found mismatch in build product names in '%s'" % buildDir
        sys.exit(1)
      if 'console' in f:
        if f.endswith('.rpm'):
          dirContents['console_rpm'].append(f)
        else:
          dirContents['console_pkg'].append(f)
      else:
        dirContents['nonconsole'].append(f)
    elif f.endswith('.pdf'):
      dirContents['docs'].append(f)
    elif f.endswith('.pyo') or f.endswith('.so'):
      dirContents['autoupdate'].append(f)  
    elif f == "BUILT_FOR":
      built_for = open(f).read().strip()
  os.chdir(savedPath)
  if not built_for:
    print "Ignoring %s, unable to determine target platform" % buildDir
  return built_for, dirContents
  
# Given a list of directories, verify that everything appears legit
#
#
def vetBuildProducts(dirList):
  prodData = {}
  for d in dirList:
    prodName, prodInfo = vetBuildDirectory(d)
    if not prodName : continue
    prodData[prodName] = prodInfo
    
  # Verify that we only have *one* build naem across all products....
  foundRel = set( [prodData[prod]['releaseName'] for prod in prodData] )
  if len(foundRel) == 0:
    print "Exiting.  No release name found in any product directory."
    sys.exit(1)
  if len(foundRel) > 1 :
    print "Exiting.  Found multiple release names in product directories."
    print "Found -> %s" % ", ".join(list(foundRel))
    sys.exit(1)
  
  # Got here, so return the 'first' element from the set and the data itself.
  return foundRel.pop(), prodData
      
# Go through the indicated list of files and see where they are duplicated
# Do this by effectively inverting the dictionary have fild:[hosts...] rather
# than host:[files....]

def findDups(prodData, dupsToFind):
  dups = {}
  
  for dup in dupsToFind:
    filesFound = {}
    for box,boxData in prodData.iteritems():    
      for f in boxData[dup]:
        if f not in filesFound:
          filesFound[f] = []
        filesFound[f].append(box)
    dups[dup] = filesFound
  return dups

# Find out which of the files may be duplicated.  Some of the build products
# are such that the output from one box can be used on all or almost all of
# the other boxes, such as the docs and the console packages.  Where there
# are duplicates, let the user choose.

def dealWithMultiplePackages(prodData):
  dups = findDups(prodData, ['docs', 'console_pkg', 'console_rpm'])

  selectedData = {}
  for i,idata in dups.iteritems():
    selItems={}
    for f, fdata in idata.iteritems():
      if len(fdata) > 1:
        fdata.sort()
        selectedDir = selectFromList(preprompt="Found %s from multiple products:" %f, foundName=f, choices=fdata, default=-1, prompt="Select which product's version to use")
      else:
        selectedDir = fdata[0]
      if selectedDir:
        if selectedDir not in selItems:
          selItems[selectedDir] = []
        selItems[selectedDir].append(f)  
    
    if selItems:
      selectedData[i] = selItems  
  return selectedData


def usage():
  print "%s: -a archiveName [-v] [-n releaseName ] [ -h ] prodDir1 [prodDir2 ...]" % sys.argv[0]
  print "   -a archiveName   specify output name of tarball (.tgz appended if needed)"
  print "   -n releaseName   specify directory name within archive tarball rather than "
  print "                    determine from build products"
  print "   -v verbose       list each discrete file being added"
  print "   -h help          display this help message"
  print ""
  sys.exit(0)


def addFilesToTarball(tarArchive, category, tarList, verbose=False):
  
  print  "Adding %s files..." % category
  
  for entry in tarList:
    dstName = entry['dstName']
    if 'srcName' in entry:
      srcName = entry['srcName']
      if verbose:
        print "Adding '%s' to archive as %s" % (srcName, dstName)
      tarArchive.add(srcName, arcname=dstName)
    else:
      srcData = entry['srcData']
      if verbose:
        print "Adding '%s' to archive using %d bytes of data" % (dstName, len(srcData))
      tarinfo = tarfile.TarInfo(dstName)
      tarinfo.mtime = time.time()
      tarinfo.size = len(srcData)
      tarArchive.addfile(tarinfo, cStringIO.StringIO(srcData))


  
def buildInstallTarball():

  # get the location of this executable
  sbSourceDir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
  opts, args = getopt.gnu_getopt(sys.argv[1:], "a:n:h")

  relName=None
  archiveName=None
  verbose = False
  
  for o,a in opts:
    if o == "-a":
      archiveName=a
      if not archiveName.endswith('.tgz') and not archiveName.endswith('.tar.gz'):
        archiveName += '.tgz'
    elif o == "-h":
      usage()
    elif o == "-n":
      relName=a
    elif o == "-v":
      verbose = True

  # punt if no archive name -or- no products
  if not archiveName or not args:
    usage()
      
  # Ok, we've grabbed the command line, all remaining arguments should be directories with
  # build products, quickly vet them and ensure that all the pkg and rpm files have the
  # same 'release name'.  We're returning this separately so we can iterate through the
  # prodData dictionary easier later

  if os.path.exists(archiveName):
    if not os.path.isfile(archiveName):
      print "Exiting.  Archive name '%s' exists and is not a file." % archiveName
      sys.exit(1)
    else:
      print "Archive file '%s' exists." % archiveName
      if askYesOrNo("Overwrite file?", "NO") == "NO":
        print "Exiting with no changes."
        sys.exit(0)
   

  foundRelName, prodData = vetBuildProducts(args)
  selectedData = dealWithMultiplePackages(prodData)
  
  # Override the release name if indicated on the command line
  if not relName :
    relName = foundRelName
  

  # start building our list of 'get this from here and put it there' instructions
  # each entry will be duple of (sourceFileName, destFileName), the actual tarfile
  # builder will ensure the entry in the tarfile is correct.
  tarList = []


  # Add the common autoupdate files that control the autoupdate process on the Client 
  autoupdateRoot = os.path.join(sbSourceDir, "src", "console", "autoupdate")
  for f in os.listdir(autoupdateRoot):
    srcpath = os.path.join(autoupdateRoot,f)
    destpath = os.path.join("autoupdate",f)
    if srcpath.startswith('.') or not os.path.isfile(srcpath) : continue
    tarList.append({'dstName': destpath, 'srcName':srcpath})
  
  # and add the box specific files that are compiled C++/gSOAP code
  for shost, sdata in prodData.iteritems():
    for f in sdata['autoupdate']:
      srcpath = os.path.join(sdata['srcpath'], f)
      destpath = os.path.join('autoupdate','autoupdaters', shost, f)
      tarList.append({'dstName':destpath, 'srcName':srcpath})

  autoupdate_buffer = cStringIO.StringIO()
  autoupdateTarball = tarfile.open(fileobj=autoupdate_buffer,mode="w:gz",name="")
  addFilesToTarball(autoupdateTarball, "Internal tarball for autoupdate files", tarList)
  autoupdateTarball.close()
  autoupdateData = autoupdate_buffer.getvalue()
   
  
  autoupdateList = [{'dstName' : os.path.join(relName, "autoupdate.tgz"),
                      'srcData' : autoupdateData}]


  # and now create the list of files for the full installer
  tarList = []
  
  # start with the raw installer files...  
  sublist = []
  for f in os.listdir(os.path.join(sbSourceDir, "InstallerFiles")):
    srcpath = os.path.join(sbSourceDir,"InstallerFiles",f)
    destpath = os.path.join(relName,f)
    if srcpath.startswith('.') or not os.path.isfile(srcpath) : continue
    sublist.append({'dstName':destpath, 'srcName':srcpath})
  tarList.append(("Main installer", sublist))
  
  # Grab the 'SB_Remove' script from the core...
  srcpath = os.path.join(sbSourceDir,"src/core/tools/SB_Remove")
  destpath = os.path.join(relName,"SB_Remove")
  tarList.append(("SB/OSL Removal", [{'dstName':destpath, 'srcName':srcpath}]))
  
  sublist = []
  # Now work through the 'selected' doc files 
  if 'docs' in selectedData:
    for shost, sdata in selectedData['docs'].iteritems():
      for f in sdata:
        srcpath = os.path.join(prodData[shost]['srcpath'], f)
        destpath = os.path.join(relName, 'docs', f)
        sublist.append({'dstName':destpath, 'srcName':srcpath})
    tarList.append(("Documentation", sublist))

  sublist = []
  # Now the Console RPM files
  if 'console_rpm' in selectedData:
    for shost, sdata in selectedData['console_rpm'].iteritems():
      for f in sdata:
        srcpath = os.path.join(prodData[shost]['srcpath'], f)
        destpath = os.path.join(relName, 'Packages', f)
        sublist.append({'dstName':destpath, 'srcName':srcpath})
    tarList.append(("Console RPM", sublist))

  sublist = []
  # Now the Console PKG files
  if 'console_pkg' in selectedData:
    for shost, sdata in selectedData['console_pkg'].iteritems():
      for f in sdata:
        srcpath = os.path.join(prodData[shost]['srcpath'], f)
        destpath = os.path.join(relName, 'Packages', f)
        sublist.append({'dstName':destpath, 'srcName':srcpath})
    tarList.append(("Console PKG", sublist))

  # Now the distcrete hosts packages, taking only the 'nonconsole' and
  # 'autoupdate' contents, placing them in slightly different directories
  
  sublist = []
  for shost, sdata in prodData.iteritems():
    for f in sdata['nonconsole']:
      srcpath = os.path.join(sdata['srcpath'], f)
      destpath = os.path.join(relName, 'Packages', shost, f)
      sublist.append({'dstName':destpath, 'srcName':srcpath})
  tarList.append(("Box specific package", sublist))


  tarList.append(("Internal tarball with autoupdaters", autoupdateList))

  tarArchive = tarfile.open(archiveName, mode="w:gz")

  print "Preparing to write installer tarball..."
    
  for category, subList in tarList:
    addFilesToTarball(tarArchive, category, subList, verbose=verbose)

   
  print "Finalizing archive..."
  tarArchive.close()
  print "All done, final archive in %s" % archiveName

##########
##########

buildInstallTarball()
