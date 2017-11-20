#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#  
#
# Replacement for shell script to do OS Lockdown setup
#######
#######
#######  IMPORTANT - cdfiles/JavaHomeUtils.py must be in sync with  core/tools/JavaHomeUtils.py

import sys
import os
import re
import pwd
import commands
import platform
import getopt

### Prompt the user to select an entry from a list - entry is returned or 'None' if no selection
def selectFromList(prompt=None, choices=[], default=-1):

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
    
    print sel_item    
    return sel_item
    
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
    
## Check to see if a particular package was installed, by name (ignoring version)

def isPkgInstalled(swname=""):
    
    retval = False
    if swname != "":
        if platform.system() == 'Linux':
            cmd = '/bin/rpm -q "%s" ' % swname
        else:
            cmd = '/usr/bin/pkginfo -q "%s" ' % swname
        cmd += ' 1>/dev/null 2>&1'
        
        status, output = commands.getstatusoutput(cmd)
        if status == 0 :
            retval = True
    return retval

def determineFlavorVersion(javaexec):

    javaFlavor  = ""
    javaVersion = ""
    javadir = ""
    javaexec = os.path.realpath(javaexec)
    if os.path.isdir(javaexec):
        javadir = javaexec
        javaexec = "%s/bin/java" % javaexec
    if not javadir:
        javadir = '/'.join(javaexec.split('/')[0:-2])
    
    if javaexec and os.path.isfile(javaexec) and os.access(javaexec, os.X_OK):
        cmd = "%s -version" % javaexec
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
    else:
        realpath = None
       
    return javaFlavor, javaVersion, javadir    


class DetermineJavaHome:
    def __init__(self, acctName='sbwebapp', profileName=''):
        self.canonicalPaths = []
        self.candidatePaths = []
        self.acctJavaHome = None
        self.default = -1
        self.longestPretext = 0
        self.longestJavaStyle = 0
        self.candidatePaths.append (('', '', 'Enter JAVA_HOME manually'))

        if not profileName:
            try:
                profileName = os.path.join(pwd.getpwnam(acctName).pw_dir,'.profile')
            except KeyError:
                pass
        self.profileName = profileName
        
    def addDir(self, pretext="", path="", flagIfNoDefault=False, allowDuplication=False):
        if path == None:
            return
        javaFlavor, javaVersion, javadir = determineFlavorVersion(path)
        realPath = os.path.realpath(javadir)
        if realPath:
            javaStyle="[%s/%s]" % (javaFlavor, javaVersion)
            # print "Checking %s %s -> %s == %s" % (pretext, path, realPath, javaStyle)
            if javaFlavor and javaVersion and javaVersion in ['1.6', '1.7']:
                if pretext == "symlink" or pretext == "profile":
                   self.canonicalPaths.append(realPath)

                elif allowDuplication == False:
                    if realPath in self.canonicalPaths :
                        return
                    else:
                        self.canonicalPaths.append(realPath)
                if self.default < 0 and flagIfNoDefault == True:
                    self.default = len(self.candidatePaths)
                if len(pretext) > self.longestPretext:
                    self.longestPretext = len(pretext)
                if len(javaStyle) > self.longestJavaStyle:
                    self.longestJavaStyle = len(javaStyle)
                if pretext=="symlink" or pretext == "profile":
                    self.candidatePaths.append((pretext, javaStyle, path))
                else :
                    self.candidatePaths.append((pretext, javaStyle, javadir))
       
                       
    def getJavaHomeInProfile(self, interactive = False):
        
        java_dir=""
        
        javahome_re = re.compile ('^\s*JAVA_HOME=')
        if os.path.isfile(self.profileName):
            try:
                lines = open(self.profileName).readlines()
                for line in  lines:
                    if not javahome_re.match(line):
                        continue
                    java_dir = line.split('=')[1].split()[0]   # get the first 'word' after the equal sign
                    break
            except:
                print >> sys.stderr, "Problem parsing %s looking for JAVA_HOME assignment." % self.profileName
        
        return java_dir

    def setJavaHomeInProfile(self, JavaHome="/my/JavaHome"):
        write_it = False
        found_it = False
        
        # since this is *our* file, we're assuming one line per assignment
        # Get existing lines
        try:
            lines = open(self.profileName).readlines()
        except Exception,err:
            lines = ["#!/bin/sh\n"]

        for linenum in  range(len(lines)):
            line = lines[linenum].strip()
            if not line.startswith('JAVA_HOME='):
                continue
            found_it = True
            oldhome=line.split('=',1)
            if oldhome != JavaHome:
                lines[linenum] = lines[linenum].split('=')[0] + "=%s\n" % JavaHome
                write_it = True

        if found_it == False:
           lines.append("JAVA_HOME=%s\n"%JavaHome)
           lines.append("export JAVA_HOME\n");
           write_it = True

        if write_it == True:
            try:
                open(self.profileName,'w').writelines(lines)                
                os.chmod(self.profileName,0700)
#                print "Updated JAVA_HOME specification in .profile for '%s' account" % acctName
            except Exception, err:
                print >> sys.stderr,  "Problem updating JAVA_HOME assignment in %s." % self.profileName
                print >> sys.stderr, str(err)
                sys.exit(1)

    def getFromProfile(self):
        
        java_dir = self.getJavaHomeInProfile()
        if java_dir :
            self.acctJavaHome = java_dir
            self.addDir(pretext="profile", path=java_dir, flagIfNoDefault=True, allowDuplication=True)
        
                
    ## See if the pkg has a 'bin/java' command that it installs

    def getJavaFromPkg(self, pkg):
        if platform.system() == 'Linux':
            cmd = "rpm -q %s --list | egrep '/bin/java$'" % pkg
        else:
            cmd = 'echo ""'
        javaexec = None
        status, output = commands.getstatusoutput(cmd)
        if status != 0 :
            print >>sys.stderr, output
        else:
            if os.path.exists(output) and os.access(output, os.X_OK):
                javaexec = output[:-9] 
        return javaexec
        
                    
    def getJavaFromInstalledPackages(self):
#        print "\n\nLooking for Java executables in known packages..."

        packages= []
        javas_found = []
        if platform.system() == 'Linux':
            for minorVersion in ['6', '7']:
                if os.path.exists('/etc/SuSE-release'):
                    packages.append(['OpenJDK Java Runtime Engine'    , 'java-1_%s_0-openjdk' % minorVersion])
                    packages.append(['OpenJDK Java Development Kit'   , 'java-1_%s_0-openjdk-devel' % minorVersion])
                else:
                    packages.append(['OpenJDK Java Runtime Engine'    , 'java-1.%s.0-openjdk' % minorVersion])
                    packages.append(['OpenJDK Java Development Kit'   , 'java-1.%s.0-openjdk-devel' % minorVersion])
            # Oracle packages appear to only allow a *single* jre or jdk version, so just check....
            packages.append(['Oracle/SUN Java Development Kit', 'jdk' ])
            packages.append(['Oracle/SUN Java Runtime Engine' , 'jre' ])
        else:
            pass

        for pkg in packages:
            if isPkgInstalled(pkg[1]):
#                print '%s is installed.... ' % pkg[1]
                pkgdir = self.getJavaFromPkg(pkg[1])
                self.addDir(pretext='(%s)' % pkg[1], path=pkgdir)
            else:
#                print '%s is not installed.... ' % pkg[1]
                pass
        
                    
    # Go look in a set of directories, for any file that matches <dir>/*/bin/java, where '*' must have at least
    #  a name like the following regular expression :
    #   (jre|jdk|java).*1(\.|-|_)6' 
    #
    def getFromCommonLocations(self):
        locations=[]
        
        locations.append('/usr/java/latest')
        locations.append('/usr/lib/jvm/jre-1.6.0')
        locations.append('/usr/lib/jvm/java-1.6.0')
        locations.append('/usr/lib/jvm/jre-1.7.0')
        locations.append('/usr/lib/jvm/java-1.7.0')
        locations.append('/usr/java')
        locations.append('/usr/bin/java')
        locations.append('/etc/alternatives/java')
        locations.append('/etc/alternatives/java')
        locations.append('/opt')
        locations.append('/opt/ibm')
        for location in locations:
            
            if os.path.isfile(location) and os.access(location,os.X_OK):
                self.addDir(pretext="executable", path=location)
            elif os.path.isdir(location) and os.access(location+"/bin/java", os.X_OK):
                self.addDir(pretext="symlink", path=location)
            elif os.path.isdir(location):
                children = os.listdir(location)
                children.sort()
                for thisdir in children:
                    for subdir in [ 'bin/java', 'jre/bin/java', 'jdk/bin/java']:
                        javadir = os.path.join(location, thisdir,subdir)
                        self.addDir(pretext = "executable", path=javadir)

    def checkEnvironment(self):
        try:
            self.addDir(pretext='(environment)', path=os.environ['JAVA_HOME'], flagIfNoDefault=True, allowDuplication=True)
        except KeyError:
            pass
            
    # We're first going to check for an existing JAVA_HOME setting in ~sbwebapp/.profile, then for a 
    # JAVA_HOME environment variable, then for installed packages, then we'll cherry pick through
    # some 'well-known' locations looking for a jre/jdk/java directory that contains
    # a 'bin/java' *executable*.  When we present the user with a list, we'll also present a 'non of the above'
    # option, and let them manually insert a path.

    def locateJava(self, interactive=True, dryrun=False):
        self.profileJavaHome=""
        JavaHome = ""
        selIndex = -1
        
        self.getFromProfile()        
        self.checkEnvironment()
        self.getJavaFromInstalledPackages()
        self.getFromCommonLocations()
        
        # organize our list of options
        choices = []
        for opt in self.candidatePaths:
            if opt[0]=="symlink":
                choices.append("%*s %*s %s -> %s" % (self.longestPretext, opt[0], self.longestJavaStyle, opt[1], opt[2],os.path.realpath(opt[2]) )) 
            else:
                choices.append("%*s %*s %s" % (self.longestPretext, opt[0], self.longestJavaStyle, opt[1], opt[2]) )
        if interactive:
            print ""
            print ""
            print "The following is a list of possible JAVA_HOME directories.  If JAVA_HOME was"
            print "set previously in '.profile' for the 'sbwebapp' user, that will be the default"
            print "value.  Please remember there may be multiple possible settings for JAVA_HOME "
            print "that may actually point to the same place, due to the use of symbolic links."
            print ""        
            while True:
                selIndex = selectFromList("Please select which directory to use for JAVA_HOME", choices, self.default)       
    
                if selIndex == 0:
                    print ""
                    JavaHome = askForString("Enter JAVA_HOME location","")
                    if os.path.isfile(JavaHome) and os.access(JavaHome,os.X_OK):
                        print "You entered the path to an executable instead for Java : %s" % JavaHome
                        print "Removing the last two components of the path and continuting."
                        JavaHome = '/'.join(JavaHome.split('/')[0:-2]) 
                        
                    javaFlavor, javaVersion, realPath = determineFlavorVersion(JavaHome)
                    if not realPath:
                        print "Please try again, unable to locate java binary"
                        continue
                    if javaVersion not in ['1.6', '1.7']:
                        print "The java executable at %s does not appear to be for 1.6 or 1.7." % JavaHome
                        print "It seems to be a %s/%s version" % (javaFlavor, javaVersion) 
                        yesOrNo = askYesOrNo('Use it anyway(?)' , 'N')
                        if yesOrNo == 'NO':
                            continue
                    
                    break
                else:
                    JavaHome = self.candidatePaths[selIndex][2]
                    break
                            
        elif len(self.candidatePaths)>1:
            JavaHome = self.candidatePaths[1][2]
        else:
            print ""
            print "Unable to locate a Java 1.6 or Java 1.7 runtime."
                
        if interactive == True:
            print "Selecting '%s' for JAVA_HOME" % JavaHome
        if self.profileName and JavaHome != self.acctJavaHome and dryrun == False:
            self.setJavaHomeInProfile(JavaHome=JavaHome) 
    
def usage(msg=""):
    if msg:
        print >> sys.stderr, msg
    print >> sys.stderr, "Usage: %s [-h | -i | -n | -f | -v] [-u <username> | -p <profile name>]"
    print >> sys.stderr, "      -h                 Help message"
    print >> sys.stderr, "      -d                 make no changes (dry-run)"
    print >> sys.stderr, "      -i                 Set JAVA_HOME interactively"
    print >> sys.stderr, "      -n                 Set JAVA_HOME noninteractively"
    print >> sys.stderr, "      -v                 Show the version of JAVA_HOME"
    print >> sys.stderr, "      -f                 Show the vendor(flavor) of JAVA_HOME"
    print >> sys.stderr, "      -u  <username>     Use <username>'s .profile"
    print >> sys.stderr, "      -p  <profile name> Use <profile name> for the file to read/write"
    print >> sys.stderr
    print >> sys.stderr, "      If -u or -p is not specified then the .profile of the sbwebapp"
    print >> sys.stderr
    sys.exit(1)
    
if __name__ == "__main__":
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hinvfu:p:")
    acctName = ""
    profileName = ""
    action = ""
    dryrun = False
    for o,a in opts:
        if o in [ "-i", "-n" , "-f", "-v" ] :
            if action:
                usage("Only one action allowed")
            action = o
        elif o == "-d":
            dryrun=True
        elif o == "-h":
            usage()
        elif o == "-u":
            if acctName or profileName:
                usage("Cannot specificy both username and profile name")
            acctName = a
        elif o == "-p":
            if acctName or profileName:
                usage("Only one account allowed")
                usage("Cannot specificy both username and profile name")
            profileName = a
    djh = DetermineJavaHome(acctName, profileName)
    if action == "-i" :
        djh.locateJava(interactive=True, dryrun=dryrun)
    elif action == "-n" :    
        djh.locateJava(interactive=False, dryrun=dryrun)
    elif action == "-f":
        JavaHome = djh.getJavaHomeInProfile(interactive=True)
        javaFlavor, javaVersion, realPath = determineFlavorVersion(JavaHome)
        print javaFlavor
    elif action == "-v":
        JavaHome = djh.getJavaHomeInProfile(interactive=True)
        javaFlavor, javaVersion, realPath = determineFlavorVersion(JavaHome)
        print javaVersion
    else:
        print djh.getJavaHomeInProfile(interactive=True)
