#!/usr/bin/env python
#########################################################################
# Copyright (c) 2012-2015 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##########################################################################

import sys
import platform
import commands
import re
import os
import pprint
import shutil
import logging
import urlparse
import time

from SB_errors import *

# fileList = dictionary {filename:filedata} of elements contained in Consoleupdate zipfile
# pretend = don't actually *do* anything

class SB_UpdaterSuper:
    def __init__(self, fileList, pretend, forceFlag):
        self.fileList = fileList
        self.pretend = pretend
        self.forceFlag = forceFlag
        self.pkgMatrix = {}
        self.allPackages = {}
        self.transitionPP = False
        self.lastConsoleAddr = "localhost"
        self.lastConsolePort = "8443"
        # All the packages in requiredPackges will be updated.  This allows us to add a new package if need be.  This list should be in order.
        self.requiredPackageTypes = ['core', 'modules', 'dispatcher' ]

        # Packages in optionalPackages will only be updated if installed originally, *after* the required packages, and in order.
        self.optionalPkgTypes    = ['console-ibmjava', 'console', 'selinux' ]

        # Packages in legacyPackages are to be removed and not replaced
        self.legacyPkgTypes = ['license']

        # This array *must* be ordered in the same order the packages should be applied if done by hand 
        self.allPackageTypes = self.requiredPackageTypes + self.optionalPkgTypes + self.legacyPkgTypes

        for pkgType in self.allPackageTypes:
            self.pkgMatrix [pkgType] = {
                                     'avail' : None,
                                     'loaded' : None,
                                     'fileName' : None,
                                     'data' : None}

        self.oldProductName = None

        self._determineLoadedPkgs()
        self.dumpMatrix()
        if self.oldProductName == "Security Blanket":     
            self.oldProductDirName = 'security-blanket'
            self.oldProductDispatcher = 'sb-dispatcher'
        elif self.oldProductName == "OS Lockdown":
            self.oldProductDirName = 'oslockdown'
            self.oldProductDispatcher = 'osl-dispatcher'
        else:
            msg = "\tUnable to determine currently installed product version (Security Blanket or OS Lockdown)"
            raise AutoUpdateExit("Unable to update - %s"% msg)

        self.newProductDirName = 'oslockdown'
        self.newProductName = 'OS Lockdown'
        self.newProductDispatcher = 'osl-dispatcher'
        
        self.productNameUpdated = not (self.oldProductDirName == self.newProductDirName)
        
        self.varBaseDir = '/var/lib/%s/files' % self.oldProductDirName       
        self.updateDir = 'update_working' 
    
    def dumpMatrix(self):
        logging.getLogger('AutoUpdate').info( "%15s %7s %7s %s" % ("Pkg", "avail","loaded", "fileName"))
        for entry,attributes in self.pkgMatrix.items()  :
#            if attributes['osPkgName']:
                logging.getLogger('AutoUpdate').info( "%15s %7s %7s %s"  % (entry, attributes['avail'], attributes['loaded'], attributes['fileName']))    
    
    def _sortPackages(self, pkgList):
        retList = []
        for pkg in self.allPackageTypes:
            if pkg in pkgList:
                retList.append(pkg)
        return retList
    
    def _getListToRemove(self):
        listToRemove = [pkg for pkg in self.pkgMatrix if self.pkgMatrix[pkg]['loaded']]
        return self._sortPackages(listToRemove)[::-1]

    def _getListToAdd(self):
        listToAdd = [pkg for pkg in self.requiredPackageTypes if self.pkgMatrix.has_key(pkg) and self.pkgMatrix[pkg]['avail']]
        listToAdd += [pkg for pkg in self.optionalPkgTypes if self.pkgMatrix.has_key(pkg) and self.pkgMatrix[pkg]['loaded']]
        return listToAdd

    def _preserveOldFiles(self):  
         logging.getLogger('AutoUpdate').info( "preserving certain files in %s..." % self.varBaseDir)  
         for i in [ 'suid_whitelist', 'sgid_whitelist', 'exclude-dirs', 'inclusion-fstypes' ]:  
             fullName = "%s/%s" % (self.varBaseDir, i)  
             newName = fullName + ".previous"  
             if os.path.exists(fullName) and not self.pretend:  
                 os.rename(fullName, newName)  
 
    def _updateWithConsoleList(self):
        for entry in self.fileList.keys():
            if entry.endswith(".rpm") or entry.endswith(".pkg"):
                pkg, version = self._getVersionFromName(entry)
                self.pkgMatrix[pkg]['avail'] = version
                self.pkgMatrix[pkg]['data'] = self.fileList[entry]
                self.pkgMatrix[pkg]['fileName'] = entry
    
    def _saveFile(self, fileName, fileData):
        fullName ="%s/%s" % (self.updateDir, fileName) 
        fileDir = os.path.dirname (fullName)
        
        if not self.pretend:
            if not os.path.exists(fileDir) :
                os.makedirs(fileDir)
            open(fullName,"w").write(fileData)
        logging.getLogger('AutoUpdate').info( "\tWrote %d bytes to %s" % (len(fileData), fileName))

    
    # Note - combining the 'X.Y.Z' version and the 'releaseName' fields to be a combined 'version'
    # The Dispatcher won't get to us if the X.Y.Z match unless we're told to check the discrete package versions,
    # but this will also deal with all the differences when called from the command line.
    def _getVersionFromName(self, fileName):
        pkgRe = re.compile("(?P<product>security-blanket|oslockdown)(-(?P<module>([a-z]+|[a-z]+-ibmjava)))?(-(?P<version>(\d+\.\d+\.\d+)))(-(?P<releaseName>\w+))")
        
        pkgType=None
        pkgVersion=None
        match = pkgRe.search(fileName)
        try:
            pkgType = match.group('module')
            if pkgType == None:
              pkgType = 'core'
            pkgVersion = "%s-%s" % (match.group('version'), match.group('releaseName'))        
        except Exception,e:
            raise AutoUpdateError("Unable to identify pgkType from filename : (%s) %s" % (fileName,str(e)))
        return pkgType, pkgVersion

    def _exitIfNoUpdateRequired(self):
        updateIndicated = False
        
        # first things first - if we have Console package then do not do anything  - we may be the Client on an 
        # Enterprise machine, and if we run we'd clobber the Console....
        
        if self.pkgMatrix['console']['loaded'] != None:
             msg = "Console package found - update halted with no changes"
             logging.getLogger('AutoUpdate').info(msg) 
             raise AutoUpdateExit(msg)

        if self.pkgMatrix['console-ibmjava']['loaded'] != None:
             msg = "Console package found (ibmjava) - update halted with no changes"
             logging.getLogger('AutoUpdate').info(msg) 
             raise AutoUpdateExit(msg)
            
        # check for all required packages
        for entry in self.requiredPackageTypes:
            logging.getLogger('AutoUpdate').info( "Checking to see if required '%s' package installed" % entry)
            if self.pkgMatrix[entry]['loaded'] == None:
              updateIndicated = True
              logging.getLogger('AutoUpdate').error( "--> missing '%s' package - update required" % entry)
                  
        for entry,attributes in self.pkgMatrix.items():
            if attributes['loaded'] and attributes['avail'] and attributes['loaded']!=attributes['avail']:
                updateIndicated = True
        
        if not updateIndicated:
            msg = "All required packages match those provided by the Console" 
            logging.getLogger('AutoUpdate').info( msg )
            if self.forceFlag == True:
                logging.getLogger('AutoUpdate').info("Force flag active - update will occur anyway") 
            else:
                raise AutoUpdateExit("Update not required - %s"% msg)
       
    # All required packages must be in the matrix.
    def _validatePkgMatrix(self):    
        for entry in self.requiredPackageTypes:
            if entry not in self.pkgMatrix.keys():
                raise AutoUpdateError("Required package for '%s' not present in Console Update" % entry)
                
    # MUST BE PROVIDED BY SUBCLASSES, even if a 'do-nothing' routine
    
    def _prep(self):
        raise NotImplementedError("Method not overriden in subclass") 
        
    def _get_osPkgName_For_PkgType(self, pkg, productName):
        raise NotImplementedError("Method not overriden in subclass") 
    
    def _removePackage(self, osPkgName,force=False):
        raise NotImplementedError("Method not overriden in subclass") 

    def _verifyPackageRequirements(self):
        raise NotImplementedError("Method not overriden in subclass") 
        
    def _installPackage(self, pkgType, fileName):
        raise NotImplementedError("Method not overriden in subclass") 

    def _stopDispatcher(self):
        raise NotImplementedError("Method not overriden in subclass") 
                
    def _determineLoadedPkgs(self):
        raise NotImplementedError("Method not overriden in subclass") 
    
    def _successfulInstallCleanup(self):
        raise NotImplementedError("Method not overriden in subclass") 
            
    def _preserveCustomChanges(self):
       # at this point the new packages are loaded, so import the preserver
       # from the /usr/share/security-blanket or /usr/share/oslockdown directory and carry on
       sys.path.append("/usr/share/%s" % self.newProductDirName)
       try:
           import PreserveCustomChanges
           PreserveCustomChanges.preserveAllChanges()
       except ImportError, e:
           logging.getLogger('AutoUpdate').error( "Unable to import PreserveCustomChange, manual action will be requird to preserve changes")
           logging.getLogger('AutoUpdate').error( "Files will be in /var/lib/%s/files with .previous or .rpmsave suffix" % self.oldProductDirName)
       
           
    def _upgradeSBtoOSL(self):
        # *IF* we see SB related names/paths then rename them to the 
        # equivalent OSL names.  If we do so, don't forget to change
        # the home directory for the sbwebapp account as well
        # For Clients, this should just be the following paths
        #   /var/lib/security-blanket
        #   /var/lib/security-blanket/files/security-blanket-state.xml
        #   /var/lib/security-blanket/logs/security-blanket.log
        #   /usr/share/security-blanket
        #   /etc/logrotate.d/security-blanket
        #   /etc/securityblanket_gui_banner
        #   /etc/modprobe.d/SecurityBlanket_remediation.conf
        
        # quietly skip things if the new directory name already exists....
        if os.path.isdir ("/usr/share/%s" % self.newProductDirName):
            logging.getLogger('AutoUpdate').info( "%s directory detected, no path/name upgrade required" % self.newProductDirName)
            return

        renames = [ 
            ("/var/lib/security-blanket",                            "/var/lib/oslockdown"),
            ("/var/lib/oslockdown/files/security-blanket-state.xml", "/var/lib/oslockdown/files/oslockdown-state.xml"),
            ("/var/lib/oslockdown/logs/security-blanket.log",        "/var/lib/oslockdown/logs/oslockdown.log"),
            ("/var/log/security-blanket-dispatcher.log",             "/var/log/oslockdown-dispatcher.log"),
            ("/usr/share/security-blanket",                          "/usr/share/oslockdown"),
            ("/usr/share/oslockdown/cfg/sb_dispatcher.properties",   "/usr/share/oslockdown/cfg/osl-dispatcher.properties"),
            ("/etc/logrotate.d/security-blanket",                    "/etc/logrotate.d/oslockdown"),
            ("/etc/securityblanket_gui_banner",                      "/etc/oslockdown_gui_banner"),
            ("/etc/modprobe.d/SecurityBlanket_remediation.conf",     "/etc/modprobe.d/oslockdown_remediation.conf")
        ]

        for (old,new) in renames:
            if os.path.exists(old):
                logging.getLogger('AutoUpdate').info( "Renaming %s to %s" % (old,new))
                if os.path.isdir(old):
                    shutil.copytree(old,new)
                else:
                    shutil.copy2(old,new)
            else:
                logging.getLogger('AutoUpdate').info( "%s does not exist, rename not required" % (old))
  
     
        
        # and change sbwebapp's home directory - just like the installer, don't use the '-m' flag since
        # the rename above should have already moved the actual location.
        logging.getLogger('AutoUpdate').info( "Changing home directory for sbwebapp user to /usr/share/oslockdown/console")
        cmd = "usermod -d /usr/share/oslockdown/console sbwebapp"
        status,output = commands.getstatusoutput(cmd)
        if status != 0:
            logging.getLogger('AutoUpdate').error("Unable to change sbwebapp home directory to /usr/share/oslockdown/console -> %s" % output)

    # Public function, not subclassed,but calls subclass routines...

        
    def locateLastConsole(self):
        logFile = '/var/log/security-blanket-dispatcher.log'
        lastConsoleAddr=""
        exitVal=1

        regex = re.compile(r'(https?://\S+)')
        try:
            for line in open(logFile):
                match = regex.search(line)
                if match:
                    self.lastConsoleAddr, self.lastConsolePort = urlparse.urlparse(match.group(1))[1].split(':')
        except IOError, e:
            # If we can't open/read/process the file then assume no registration
            logging.getLogger('AutoUpdate').error("Determing last Console error -> %s" %e)
        except Exception,e:
            logging.getLogger('AutoUpdate').error("Determing last Console error -> %s" %e)
    
        logging.getLogger('AutoUpdate').info("Last Console contact from %s:%s" % (self.lastConsoleAddr, self.lastConsolePort))
            
    def applyUpdate(self):
       
        # what do *we* have installed already
#        logging.getLogger('AutoUpdate').info( "Determining current packages on this box...")
#        self._determineLoadedPkgs()
        logging.getLogger('AutoUpdate').info( "All packages = %d, %s packages = %d" % (len(self.allPackages), self.oldProductName, len( self.pkgMatrix)))
        
        # if we have the selinux package loaded, *and* the installed product is Security Blanket, we'll need a 
        # temporary transition package....
        self.transitionPP = (self.pkgMatrix['selinux']['loaded'] and self.oldProductName == "Security Blanket" )

        # add this info to what the Console said that it had
        logging.getLogger('AutoUpdate').info( "Update determination matrix with Console info...")
        self._updateWithConsoleList()
        
        # Verify that the Console supplied a package for all *required* packages
        logging.getLogger('AutoUpdate').info( "Verify all required packages were supplied by Console...")
        self._validatePkgMatrix()

        logging.getLogger('AutoUpdate').info( "Dumping current matrix of loaded/available %s products..." % self.oldProductName)
        self.dumpMatrix()
        
        # do we need to update - raises AUTOUPDATE_EXIT if not
        #
        logging.getLogger('AutoUpdate').info( "Determine if an update is required at all...")
        self._exitIfNoUpdateRequired()     

        # Preserve some possibly altered files first  
        logging.getLogger('AutoUpdate').info( "Preserve potentially altered customer files...")  
        self._preserveOldFiles()  
 
        # create our working directory (delete if already there) and
        # extract the zipFile contents there 
        logging.getLogger('AutoUpdate').info( "Extracting package files into (pristine) working directory")
        if os.path.exists(self.updateDir) and not self.pretend:
            shutil.rmtree(self.updateDir)

        for fileName, fileData in self.fileList.items():
            # initially save only the packages to be installed/updated, we'll handle the non-packaged files later
            if fileName.startswith('PKGS/') or fileName.startswith('RPMS/') or fileName.startswith('Packages/'):
                self._saveFile(fileName, fileData)
        
        self.pkgFilesInOrder = [self.pkgMatrix[pkg]['fileName'] for pkg in self._getListToAdd() ]

        logging.getLogger('AutoUpdate').info( "Verifying all package prerequisites are met...")
        self._verifyPackageRequirements()
        
        # do any initial stuff before actually removing/installing stuff 
        logging.getLogger('AutoUpdate').info( "Doing OS specific setup before removal/installation...")
        self._prep()

        # stop the Dispatcher
        logging.getLogger('AutoUpdate').info( "Stopping the Dispatcher...")
        self._stopDispatcher()

        # remove existing packages
        logging.getLogger('AutoUpdate').info( "Removing *all* existing %s packages..." % self.oldProductName)
        for pkg in  self._getListToRemove():
            self._removePackage(self._get_osPkgName_For_PkgType(pkg, self.oldProductName))

        # Ok, we know we *might* have some directories that need to be updated outside of the packages, 
        # delete them if present
        for dirName in ['Attributions', 'docs', 'toolupdates' ] :
            fulldirName = "/usr/share/%s/%s" % (dirName, self.oldProductDirName)
            logging.getLogger('AutoUpdate').info( "Looking for '%s' ..." % fulldirName)
            if os.path.isdir(fulldirName):
                logging.getLogger('AutoUpdate').info( "Removing existing '%s' ..." % fulldirName)
                shutil.rmtree(fulldirName)
                
        # Handle any required file/directory renames due to upgrading from 
        # 'Security Blanket' to 'OS Lockdown'

        
        self._upgradeSBtoOSL()
        
        # install the new ones (save the package first to disk...)
        logging.getLogger('AutoUpdate').info( "Installing new %s packages..." % self.newProductName)
        for pkg in self._getListToAdd():   
            self._installPackage(pkg, self.pkgMatrix[pkg]['fileName'])
        
        # now write any non-packages files to the correct locations...
        for fileName, fileData in self.fileList.items():
            # initially save only the packages to be installed/updated, we'll handle the non-packaged files later
            if not fileName.startswith('PKGS/') and not fileName.startswith('RPMS/') and not fileName.startswith('Packages/'):
                self._saveFile("/usr/share/%s/%s" % (self.newProductDirName, fileName) , fileData)
        
        # Ok, call the *newly installed* PreserveCustomChanges.py code to meld any changes together...
        #
        logging.getLogger('AutoUpdate').info( "Preserve any custom changes to file in /var/lib/%s/files..." % self.newProductDirName)
        self._preserveCustomChanges()

        
        self.locateLastConsole()

        # Force a 'fetch' of the latest certs - ensures the passphrases are *correctly* updated
        try:
            logging.getLogger('AutoUpdate').info( "Refetch latest SSL certs and passphrases...")
            cmd = "/usr/share/%s/tools/RegisterClient -c -n -s \'%s\' -p \'%s\'" % (self.newProductDirName, self.lastConsoleAddr, self.lastConsolePort)
            logging.getLogger("AutoUpdate").info("Refetch cmd -> %s" % cmd)
            status,output = commands.getstatusoutput(cmd)
            if status != 0:
                logging.getLogger('AutoUpdate').error("Fetching certs error -> %s" % output)
            else:
                dispPassphrase = output.strip()
            
        except Exception,e :
            logging.getLogger('AutoUpdate').error("Fetching certs error -> %s" % e)
            raise

        # Ok, reset the start scripts for the Dispatcher, this will *also* attempt to restart the Dispatcher
        try:
            logging.getLogger('AutoUpdate').info( "Reconfig/restart the Dispatcher...")
            cmd = "/usr/share/%s/tools/SB_Setup -d -n" % self.newProductDirName
            status,output = commands.getstatusoutput(cmd)
            if status != 0:
                logging.getLogger('AutoUpdate').error("Reconfig/restart the dispatcher error -> %s" % output)
            
        except Exception,e :
            logging.getLogger('AutoUpdate').error("Reconfig/restart the dispatcher error -> %s" % e)
            raise

    # Called after a successful install to do terminal post processing/cleanup
    # IMPORTANT - NO LOGGING DONE FROM HERE ON - in an SELINUX envirnoment the policy
    # MAY OR MAY NOT BE UITABLE TO DO MUCH OF ANYTHING
    def successfulInstallCleanup(self, logfile):
        
        # if this is an update from SB to OSL, preserve the autoupate log and 
        # cleanup the legacy directories
                # If this is an upgrade of SB to OSL, we copied the legacy /usr/share/security-blanket and /var/lib/security-blanket
        # directories to new names.  So now go clean up those legacy directories...
        if self.productNameUpdated and self.oldProductDirName != self.newProductDirName:
            shutil.copy2(logfile, "/var/lib/%s/logs" % self.newProductDirName)

        #lastly, call any os specific cleanup
        self._successfulInstallCleanup()  
                 
class Linux_Updater (SB_UpdaterSuper):
            
    def __init__(self, filelist, pretend, forceFlag):
        SB_UpdaterSuper.__init__(self, filelist, pretend, forceFlag)        
        
    def _prep(self):
        pass
        
    def _get_osPkgName_For_PkgType(self, pkgType, productName):
        osPkgName = ""
        if productName == "Security Blanket":
            if pkgType == "core":
                osPkgName = "security-blanket" 
            else:
                osPkgName += "security-blanket-" + pkgType
        else:
            if pkgType == "core":
                osPkgName = "oslockdown" 
            else:
                osPkgName += "oslockdown-" + pkgType
        return osPkgName
            
    # All Linux packages start with 'security-blanket' or 'oslockdown, so go find 'em all
    # Remember that the core package is actually named 'security-blanket', all others have the 'name' 
    # appended to 'security-blanket' (IE console is 'security-blanket-console').  Each entry is a dictionary
    # with the osPkgName and the version being the values
    def _determineLoadedPkgs(self):
       
        allPackages = {}
        pkgList = {}
        
        # easier to match against the RPM list using a regex...
        regex = re.compile('(?P<product>oslockdown|security-blanket)(-(?P<pkg>.*))?')

        # create pkgList with the plain entries for each of our 'known' packages     
        # show us the command 
        cmd = """rpm -aq --queryformat '%{NAME} %{VERSION} %{RELEASE}\n' """
        logging.getLogger('AutoUpdate').info("Getting list of current package and versions with : %s" % cmd.__repr__())
        status, output = commands.getstatusoutput(cmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        status = 0
        status, output = commands.getstatusoutput(cmd)
        if status != 0 :
            raise AutoUpdateError("Query of RPM database failed ")
        
        for line in output.splitlines():
            fields = line.split()
            self.allPackages[fields[0]] = fields[2]
            match = regex.search(fields[0])
            if not match: 
                continue

            if not self.oldProductName:
                if match.group('product') == "security-blanket":
                    self.oldProductName = "Security Blanket"
                else:
                    self.oldProductName = "OS Lockdown"
            name = match.group('pkg')
            if not name: 
                name = "core"
            version = fields[2].split('.')[0]
            self.pkgMatrix[name]['loaded'] = "%s-%s" % (fields[1], version)
             
    def _removePackage(self, osPkgName, force=False):
        if not force and "selinux" in osPkgName:
            logging.getLogger('AutoUpdate').info( "\tSELinux package not removed - will be updated instead on install")
        else:
            pkgCmd = "/bin/rpm -e %s " % (osPkgName)
            logging.getLogger('AutoUpdate').info( "\tRemoving %s with '%s' ... " % (osPkgName, pkgCmd))
            status = 0
            if not self.pretend:
                status, output = commands.getstatusoutput(pkgCmd)
            logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
            if status  !=  0 :
                raise AutoUpdateError(output)
    
    def _installPackage(self, pkgType, pkgFile):    
        pkgCmd = "/bin/rpm -vU %s/%s" % (self.updateDir, pkgFile)
        if "selinux" in pkgFile:
            pkgCmd += " --force"
        logging.getLogger('AutoUpdate').info( "Adding '%s' with '%s' ... " % (pkgType, pkgCmd))
        status = 0
        if not self.pretend:
            status, output = commands.getstatusoutput(pkgCmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        if status != 0 :
            raise AutoUpdateError(output)

    def _stopDispatcher(self):
        stopDispatcherCmd = "/sbin/service %s stop" % self.oldProductDispatcher
        logging.getLogger('AutoUpdate').info( "Stopping dispatcher with '%s'..." % (stopDispatcherCmd))
        status = 0
        if not self.pretend:
            status, output = commands.getstatusoutput(stopDispatcherCmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        if status  != 0 :
            print "**** AutoUpdateError ****"
            raise AutoUpdateError(output)
        logging.getLogger('AutoUpdate').info( "Pausing 5 seconds to let it shutdown...")
        time.sleep(5)
                
    def _verifyPackageRequirements(self):
        # Ok, this is pretty simple.  We'll use the 'rpm -Uvh --test" command to see what is missing...
        dependCmd = "/bin/rpm -Uv --test %s 2>&1 " % ' '.join(["%s/%s" % (self.updateDir, pkgFile) for pkgFile in self.pkgFilesInOrder  ] )
        logging.getLogger('AutoUpdate').info( "Verifying packages dependencies with '%s'..." % (dependCmd))
        
        status = 0
        status, output = commands.getstatusoutput(dependCmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        
        #note - the return code is the number of packages 'failing'.  Could be because it is installed already, or it is missing something, so
        # we need to look at the actual output to see what.
        if status  != 0 :
            missingPkgs = {}
            for line in output.splitlines():
                if line.startswith("error: "):
                   raise AutoUpdateError("RPM Test failed with : %s" % output)
                elif "is needed by" in line:
                   pkg = line.split()[0]
                   missingPkgs[pkg] = True
                
            if missingPkgs:
                raise AutoUpdateError("The following package(s) need to be installed : %s" % ', '.join(missingPkgs.keys()))
        
    def _successfulInstallCleanup(self):
        if self.productNameUpdated:
            # we want to force a redownload of any profiles from the Console after the update is done
            # this has the side effect of helping clean up some duplicated installer files...
            if os.path.isdir('/var/lib/%s/profiles/.enterprise' % self.newProductDirName):
                shutil.rmtree('/var/lib/%s/profiles/.enterprise' % self.newProductDirName)

            # Since we're an update, make sure the legacy SB /usr/hare/ and /var/lib dirs go away
            # have to do this between the RPM actions to make sure we have the RPM to install above
            # but before we kill policy to delete the directories.....
            if os.path.isdir ("/var/lib/security-blanket"):
                shutil.rmtree("/var/lib/security-blanket")
            if os.path.isdir ("/var/lib/security-blanket"):
                shutil.rmtree("/usr/share/security-blanket")
            
	    # Try to remove the transitional policy.  If that succeeded then we also need to unload the legacy
	    # SELinux policy RPM also
	    
	    status, output = commands.getstatusoutput("semodule -r TransitionSBtoOSL")
	    if status == 0 :
                # To avoid some AVC's and a potential system *crash*, go ahead and fork here
                # parent should exit immediately, child does an execl to do the RPM removal
                if os.fork():
                   os.execl("/bin/rpm", "/bin/rpm", "-e", self._get_osPkgName_For_PkgType('selinux', self.oldProductName))
                # regardless, exit immediately if we get here
                sys.exit(0)

        


class Solaris_Updater (SB_UpdaterSuper):
        
    def __init__(self, filelist, pretend, forceFlag):
        SB_UpdaterSuper.__init__(self, filelist, pretend, forceFlag)        
        self.adminName = "admin"
     
    def _get_osPkgName_For_PkgType(self, pkgType, productName):
        osPkgName = ""
        
        if productName == "Security Blanket":
            if pkgType == "core":   
                osPkgName += "TCSsecblanket"
            else:
                osPkgName = "TCSsb" + pkgType
        else:
            if pkgType == "core":   
                osPkgName += "TCSoslockdown" 
            else:
                osPkgName = "TCSoslockdown-" + pkgType
        
        return osPkgName

    # All Solaris packages start with 'TCSs', so go find 'em all
    # Remember that the core package is actually named 'TCSsecblanket', all others have the 'name' 
    # appended to 'TCSs' (IE console is 'TCSsbconsole').  Each entry is a dictionary
    # with the pkgName and the version being the values
            
    def _determineLoadedPkgs(self):
        cmd = """pkginfo -x"""
        status, output = commands.getstatusoutput(cmd)
        if status != 0:
            raise AutoUpdateError("Unable to determine list of packages")
        # 'pkginfo -x' returns two lines for each package, essentially "<name> <info>\n<whitespace><arch><version>
        # we don't care about version right now, just the major package names.  We're using regex to parse the
        # output for simplicity...
        lineRE = re.compile("^\S+.*?(?:\n|\n\r)\s.*$", re.MULTILINE)
        allMatches = lineRE.findall(output)
        for match in allMatches:
            fields = match.split()
            self.allPackages[fields[0]] = fields[-1]
            if fields[0].startswith('TCSsecblanket'):
                name = "core"
                self.oldProductName = "Security Blanket"
            elif fields[0].startswith('TCSsb'):
                self.oldProductName = "Security Blanket"
                name = fields[0][5:]
            elif fields[0]. startswith("TCSoslockdown"):
                self.oldProductName = "OS Lockdown"
                name = fields[0][14:]
                if not name:
                    name = "core"
            else:
                continue
            self.pkgMatrix[name]['loaded'] = fields[-1]
    
    # write out 'admin' file out for unattended operations                     
    def _prep(self):
        adminText = ["mail=\n",
                     "instance=unique\n",
                     "partial=nocheck\n",
                     "runlevel=ask\n",
                     "idepend=quit\n",
                     "rdepend=quit\n",
                     "space=ask\n",
                     "setuid=quit\n",
                     "conflict=nocheck\n",
                     "action=nocheck\n",
                     "authentication=quit\n",
                     "basedir=default\n" ]
        self._saveFile(self.adminName, ''.join(adminText))
        
    def _removePackage(self, osPkgName, force=False):
        pkgCmd = "/usr/sbin/pkgrm -n -a %s/%s %s " % (self.updateDir, self.adminName, osPkgName)

        logging.getLogger('AutoUpdate').info( "Removing %s with '%s' ... " % (osPkgName, pkgCmd))
        status = 0
        if not self.pretend:
            status, output = commands.getstatusoutput(pkgCmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        if status  != 0 :
            raise AutoUpdateError(output)
    
    def _installPackage(self, pkgType, pkgFile):    
        pkgCmd = "/usr/sbin/pkgadd -n -a %s/%s -d  %s/%s all" % (self.updateDir, self.adminName, self.updateDir, pkgFile)
        logging.getLogger('AutoUpdate').info( "Adding '%s' with '%s' ... " % (pkgType, pkgCmd))
        status = 0
        if not self.pretend:
            status, output = commands.getstatusoutput(pkgCmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        if status  != 0 :
            raise AutoUpdateError(output)

    def _stopDispatcher(self):
        stopDispatcherCmd = "/usr/sbin/svcadm disable %s" % self.oldProductDispatcher
        logging.getLogger('AutoUpdate').info( "Stopping dispatcher with '%s'." % (stopDispatcherCmd))
        status = 0
        if not self.pretend:
            status, output = commands.getstatusoutput(stopDispatcherCmd)
        logging.getLogger('AutoUpdate').info( "    returned %d" % (status))
        if status  != 0 :
            raise AutoUpdateError(output)
        logging.getLogger('AutoUpdate').info( "Pausing 5 seconds to let it shutdown...")
        time.sleep(5)

        
    # Ok, the solaris side is going to get a bit sticky.  Each package is a pair of cpio archives, but Solaris doesn't provide any 
    # routines to look *inside* them.  So we're going to do this little hack that takes advantage of the fact that the sections are
    # in alphabetical order within the archive, and each section has its own CPIO header block.  So we want the data between the
    # 'install/depend' and the 'install/postinstall' sections.  Once we get that convert all 'nul' chars to newlines, then split
    # the resulting string in to discrete lines, keeping only those that start with 'P ', which indicates a package dependency.
    # We'll process that list to get the packages we need to look for.
    
    # This little routine is used to *just* get the dependencies in one file
    def _getSolarisPkgDependencies(self, pkgData):
        pkgList = {}
        sectionRE = re.compile("(070701[0-9a-f]{104}install/depend)(.*?)(070701[0-9a-f]{104}install/postinstall)",re.MULTILINE|re.DOTALL)    
        secData = sectionRE.search(pkgData).group(2).replace('\x00','\n').splitlines()
        for line in secData:
            if not line.startswith('P '):
                continue
            pkgName = line.split()[1]
            if pkgName not in self.allPackages:
                pkgList[pkgName] = True
        return pkgList

    def _verifyPackageRequirements(self):
        missingPkgs = {}
        potentialMissingPkgs = {}
        logging.getLogger('AutoUpdate').info("List to add -> %s" % ", ".join(self._getListToAdd()))
        pkgNamesBeingAdded = [self._get_osPkgName_For_PkgType(pkg,self.newProductName) for pkg in self._getListToAdd()]
        for pkg in self._getListToAdd() : 
            
            logging.getLogger('AutoUpdate').info( " Checking dep for %s (%s)" % (pkg,self._get_osPkgName_For_PkgType(pkg,self.newProductName)))
            poss = self._getSolarisPkgDependencies(self.pkgMatrix[pkg]['data'])
            potentialMissingPkgs.update(poss)     

        logging.getLogger('AutoUpdate').info( " Deps checked")
        # Ok, this list may have OS Lockdown packages on it, so filter out any package that we might install...
        for pkg in potentialMissingPkgs:
            if pkg not in pkgNamesBeingAdded:
                missingPkgs[pkg] = True
        
        if missingPkgs:
            raise AutoUpdateError("The following package(s) need to be installed : %s" % ', '.join(missingPkgs.keys()))

    def _successfulInstallCleanup(self):
        if self.productNameUpdated:
            # we want to force a redownload of any profiles from the Console after the update is done
            # this has the side effect of helping clean up some duplicated installer files...
            if os.path.isdir('/var/lib/%s/profiles/.enterprise' % self.newProductDirName):
                shutil.rmtree('/var/lib/%s/profiles/.enterprise' % self.newProductDirName)

            # Since we're an update, make sure the legacy SB /usr/hare/ and /var/lib dirs go away
            if os.path.isdir("/var/lib/security-blanket"):
                shutil.rmtree("/var/lib/security-blanket")
            if os.path.isdir("/usr/share/security-blanket"):
                shutil.rmtree("/usr/share/security-blanket")
            
        
if __name__ == "__main__":
    print "This program is not directly executable."
    sys.exit(1)
