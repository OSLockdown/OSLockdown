##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# EnforcePermsAsPerRPM - consult RPM database to verify file/directory ownership/permissions
#   Note that we need to finalize the checks ourself because we need to potentially exempt files/directories
#   from being changed (for example, on things that other SB modules have restricted).
#
# NOTE: None.
#
#
##############################################################################
import rpm
import sys
import pwd
import re
import os
import pwd
import grp

try:
    foobar = set([])
except NameError:
    from sets import Set as set

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import tcs_utils
import sb_utils.file.dac
import sb_utils.file.fileperms
import sbProps

class ConsultRPMDatabase:
 
    def __init__(self):
 
        self.module_name = self.__class__.__name__
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.rpmsToIgnore = set()
        self.filesToIgnore = []
        self.testHarnessRPMs = None
        
        self.ignoreRootRoot000 = True
        self.validLineRE = re.compile("^\s*([?SM5DLUGTP.]{8,9})  ([cd ]) (.*)")

        # most modules keep messages/changes buried in the methods, we're keeping ours *here* so 
        # we don't have to worry about passing stuff back in returns
        self.messages = []
        self.changes = {}
        self.ignorePackagesCount = 0
        self.ignoreFilesCount = 0
        self.rpmData = {}
        self.rpmPackages = []
        self.rpmFiles = []
        
        # the 'no problem' return codes are logically different from scan/apply, so we'll just keep track
        # of if we found a problem and let the scan/apply methods look at *this* as part of their return
        # remember that apply() returns True *** IF *** any changes were made.
        
        self.problemFound = False
        
    def validate_input(self, optionDict):
        trueFalse = {'1':True, 'True':True, '0': False, 'False':False}
        
        try:
            self.rpmsToIgnore      = set( tcs_utils.splitNaturally(optionDict['packageExemptions'],wordAdditions='-.'))
            self.filesToIgnore     = optionDict['fileExemptions'].splitlines()
            self.ignoreRootRoot000 = trueFalse[optionDict['honorChangesBySB']]
        except ValueError:
            msg = "Invalid option value -> '%s'" % optionDict
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

    def getDataFromRPM(self):
        # we need to get pretty much 'the world' as far as RPM is concerned.  There is a bug in the bindings that
        # results in a large memory leak if we need to query things too often from one process.  So we'll get what we *might*
        # need once and then search through that.
        # Basically - list of packages, and for each package a list of files with the (user,group,dacs) tuple

        if self.testHarnessRPMs:
            msg = "**TESTING** - restricting search to %d packages -> %s" % (len(self.testHarnessRPMs), ', '.join(self.testHarnessRPMs))
            self.logger.notice(self.module_name, msg)
            
        ts = rpm.TransactionSet()
        rpmDict={}
        mi = ts.dbMatch()
        for hdr in mi:
          if not self.testHarnessRPMs or hdr['name'] in self.testHarnessRPMs:
              shortName = hdr['name']
              fullName = "%s-%s-%s" % (hdr['name'], hdr['version'], hdr['release'])
              if hdr['arch']:
                  fullName = "%s.%s" % (fullName, hdr['arch'])
              rpmDict[fullName] = shortName
              fi=hdr.fiFromHeader()
              fileList = {}
              for f in fi:
                  fileList[fi.FN()] = (fi.FUser(), fi.FGroup(), 0177777 & fi.FMode())
              self.rpmData[fullName] = {'files':fileList, 'shortName':shortName}
              
        self.rpmPackages = rpmDict.keys()
        self.rpmPackages.sort()
        msg = "Found %d installed packages" % len(self.rpmPackages)
        self.logger.notice(self.module_name, msg)
        if self.testHarnessRPMs:
            msg = "**TESTING** - looked for %d packages, found %d -> %s" % (len(self.testHarnessRPMs), len(self.rpmPackages), ', '.join(self.rpmPackages))
            self.logger.notice(self.module_name, msg)

        numFiles = 0
        for x,y in self.rpmData.items():
           numFiles = numFiles + len(y['files'])
        msg =  "Found %d files install in packages" % numFiles
        self.logger.notice(self.module_name, msg)

    def getFileDataFromDisk(self, fileName):
        # get on-disk details (uid/gid/DACs)
        info = None
        if os.path.exists(fileName):
            statbuf = os.stat(fileName)
            try:
                username = pwd.getpwuid(statbuf.st_uid)[0]
            except KeyError:
                username = 'root'
            try:
                groupname = grp.getgrgid(statbuf.st_gid)[0]
            except KeyError:
                groupname = 'root'
            info = (username, groupname , statbuf.st_mode)
        return info

    def getFileDataFromRPM(self, fileName):
        # Verify that the file in question either belongs to a single RPM, or if it is owned by 
        # multiple RPMs the details are *identical*
        rpms = {}
        for pkgName in self.rpmPackages:
            pkgData = self.rpmData[pkgName]
            for fileinfo, filedata in pkgData['files'].items():
                if fileinfo == fileName:
                    rpms[pkgName] = filedata
                    # file appears once per package, so if we see it punt out
                    break                
       
        return rpms

        
    def getFileDataFromRPM_old(self, fileName):
        # Verify that the file in question either belongs to a single RPM, or if it is owned by 
        # multiple RPMs the details are *identical*
        
        ts=rpm.TransactionSet()
        rpms={}
        mi = ts.dbMatch('basenames', fileName)
        for entry in mi:
          fi = entry.fiFromHeader()
          
          for f in fi:
              if fileName != fi.FN():
                  continue
              # have to mask this to make sure it is interpreted right
              vals = (fi.FUser(),fi.FGroup(),0177777 & fi.FMode())
              rpms[entry['name']] = vals
        return rpms
 

    def checkRPMs(self, action='scan'):
        
        # populate our RPM database 
        self.getDataFromRPM()
        pkgCount=0
        pkgTotal=len(self.rpmPackages)
        msg = "Total number of packages to check = %d" % pkgTotal
        self.logger.notice(self.module_name, msg)
        
        for packageName in self.rpmPackages:
            packageData = self.rpmData[packageName]
            shortName = packageData['shortName']
            pkgCount = pkgCount+1
            # this could be a long-term operation, so see if we were requested to abort
            if sbProps.ABORT_REQUESTED==True:
               msg = "Abort requested in mid operation - skipping remaining packages."
               self.logger.warning(self.module_name, msg)
               break
            # see if either the short or long name is explicitly ignored
            if shortName in self.rpmsToIgnore:
               msg = "Package %s is explicitly ignored - skipping" % (shortName)
               self.logger.warning(self.module_name, msg)
               self.ignorePackagesCount = self.ignorePackagesCount + 1
               continue
            elif packageName in self.rpmsToIgnore:
               msg = "Package %s is explicitly ignored - skipping" % (packageName)
               self.logger.warning(self.module_name, msg)
               self.ignorePackagesCount = self.ignorePackagesCount + 1
               continue
            # ok, check the package, but use the *full* name, so we can also track architecture for dual arch machines
            msg = "Checking package %d of %d -> %s ..." % (pkgCount, pkgTotal, packageName)
            self.logger.info(self.module_name, msg)
            self.checkRPM(action, packageName);
            
            

    def checkRPM(self, action='scan', packageName='foo'):
        cmd = "/bin/rpm -V %s" % packageName 
        
        # Note - *must* capture stderr also to detect cases where prelinking is getting in the way...
        status,output,error = tcs_utils.tcs_run_cmd(cmd, cmdTimeout=(60*20), capture_err=True)
        if status == 0:
            return
        unexpectedCount = 0
        filesToCheck = {}  
        lastline = ""
        # check each line for what problem we've found
        for line in output.splitlines():
            fileName = None        
            issues = set()

            # check if we have a 'valid' line, a 'missing' line, or something else.
            match = self.validLineRE.search(line)
            if match:
                rpmFlags = match.group(1)
                confOrDir = match.group(2)
                fileName = match.group(3)
                
                # if we've seen this file already, get what we know about it....
                try:
                    issues = filesToCheck[fileName]
                except KeyError:
                    issues = set()
                                       
               # rpmFlags[0] == "S":  ->  size
               # rpmFlags[1] == "M":  ->  permissions
               # rpmFlags[2] == '5'   ->  contents (checksum) if *NOT* a config file
               # rpmFlags[3] == 'D' : ->  device numbers
               # rpmFlags[4] == 'L' : ->  symlink
               # rpmFlags[5] == 'U' : ->  file owner
               # rpmFlags[6] == 'G' : ->  group owner
               # rpmFlags[7] == 'T' : ->  modification time (could indicate an abortive change?)
                
                if rpmFlags[1] == "M": # permissions
                    issues.add('permissions') 
                if rpmFlags[2] == '5' and confOrDir != 'c': # contents (checksum) if *NOT* a config file
                    issues.add('checksum')
                if rpmFlags[2] == '?' and rpmFlags[0] == "S" and lastline.startswith('prelink'): # note as prelink 
                    issues.add('prelink')
                if rpmFlags[5] == 'U' : # file owner
                    issues.add('uid')
                if rpmFlags[6] == 'G' : # group owner
                    issues.add('gid')
                if rpmFlags[7] == 'T' and confOrDir != 'c': # timestamp if *NOT* a config file
                    issues.add('timestamp')
            elif line.startswith('missing'):
                fileName = line.split(None,1)[1].strip()
                if fileName.startswith('c '):
                    fileName = fileName[2:]
                issues.add('missing')
            elif line.startswith('prelink'):
                pass
            else :
                msg = "Unexpected line found in 'rpm -V' output, manual action may be required -> %s" % (line)
                self.logger.warn(self.module_name, msg)
                unexpectedCount = unexpectedCount + 1
            
            if issues and fileName:
                filesToCheck[fileName] = issues
            lastline = line
            
        if unexpectedCount > 0 :
            msg = "Found %d unexpected line from 'rpm -V'  - see log file for more information" % unexpectedCount
            self.logger.warning(self.module_name, msg)
            self.messages.append("Warn " + msg)
        
        if filesToCheck:
            self.fixFiles(packageName, filesToCheck, action)
    
        
    def fixFiles(self, packageName, filesToCheck, action):
        """
        Given a dictionary of filenames, go find out what may be the problem.  The value gives us an idea
        of what we need check that we can fix (mode, uid, gid), as well as issues we can't (prelink, MD5, missing)
        We want to focus on things one file at a time.  Some complications are that a file can belong to more than one
        package, with potentially different settings.  
        Note that we're including a list of files *and* packages to not make changes to.  If at any point the file would be on 
        either list we just make note of the problme and ignore it.
        If we get past this, check to see if we have one agreed set of mode/uid/gid values (if file owned by multiple RPMs).  If
        we have dueling settings - punt with a warning
        If one set, and they differ from what is on disk, now we could do something :)
        
        """
        
        msg = "Package %s indicates %d potential issues" % (packageName, len(filesToCheck))
        self.logger.warning(self.module_name, msg)
        
        changeOptions = {'ignoreExcludes':True, 'checkOnly': False, 'recursive':False}
        rpmsToReLoad = []
        changesToMake = []
        for fileName,issues in filesToCheck.items():
            DoNotChange = False
            text = []
            
            # Get info from RPM and disk - note that a file *may* belong to multiple packages...
            rpmInfo = self.getFileDataFromRPM(fileName)
            fileInfo = self.getFileDataFromDisk(fileName)
            # see if the RPM holding this file is on our list of packages to exclude, or we're excluding it
            # specifically
            fileIsExcluded = False
            
            if fileName in self.filesToIgnore:
                fileIsExcluded = True
                msg = "'%s' is marked to explicitly ignore" % fileName
                self.logger.warning(self.module_name, msg)
                self.ignoreFilesCount = self.ignoreFilesCount + 1

            if fileIsExcluded:
                continue

            msg = "%s has the following issues : %s " % (fileName, ', '.join(issues))
            self.logger.debug(self.module_name, msg)
            if fileInfo and not 'checksum' in issues:
                # Ok, file exists and we don't have a *contents* issue - we could make changes
                rpmSettings = set()
                for r,d in rpmInfo.items():
                    rpmSettings.add(d)
#                    print "    %s (%s,%s,%04o)" % (r, d[0], d[1], d[2])
#                print "    -> (%s,%s,%04o)" % (fileInfo[0], fileInfo[1], fileInfo[2])
                if len(rpmSettings) > 1 : 
                    msg = "'%s' owned by multiple packages with different settings - one or more of the following RPMs need to be reloaded : %s " % (fileName, ', '.join(rpmInfo.keys()))
                    self.messages.append('Manual Action %s' % msg)
                    self.problemFound = True
                    self.logger.warning(self.module_name, msg)
                    continue
                else:
                    requiredChanges = {}
                    rpmSettings = rpmSettings.pop()
#                    print "%s -> %s  %s %s:%.3o" % (fileName, self.ignoreRootRoot000, fileInfo[0], fileInfo[1], fileInfo[2] & 07777)
                    if self.ignoreRootRoot000 and fileInfo[0] == 'root' and fileInfo[1] == 'root' and (fileInfo[2] & 07777)  == 0:
                        msg = "'%s' may have been set to root:root with permissions 000 by OS Lockdown - leaving alone" % fileName
                        self.logger.warning(self.module_name, msg)
                        self.ignoreFilesCount = self.ignoreFilesCount + 1
                        continue
                    if rpmSettings[0] != fileInfo[0]:
                        requiredChanges['owner'] = rpmSettings[0]
                        text.append("owner should be %s instead of %s" % (rpmSettings[0], fileInfo[0])) 
                    if rpmSettings[1] != fileInfo[1]:
                        requiredChanges['group'] = rpmSettings[1]
                        text.append("group should be %s instead of %s" % (rpmSettings[1], fileInfo[1]))
                    if rpmSettings[2] != fileInfo[2]: 
                        testmode = "%o" % (rpmSettings[2] & 0777) # ignore setuid/setgid/sticky
                        if not sb_utils.file.dac.isPermOkay(fileName, testmode, ignoreExcludes=True):
                            requiredChanges['dacs'] = rpmSettings[2]
                            text.append("mode(DACs) should be %04o instead of %04o" % (rpmSettings[2], fileInfo[2]))
            elif not fileInfo:
                # file doesn't exists on disk - must reload RPM to fix
                msg = "'%s' doesn't exist - one or more of the following RPMs need to be reloaded : %s " % (fileName, ', '.join(rpmInfo.keys()))
                if fileIsExcluded:
                    msg = msg + ":: file is explicitly ignored"
                else:
                    self.messages.append('Manual Action %s' % msg)
                    self.problemFound = True
                self.logger.warning(self.module_name, msg)
            else:
                # file doesn't exists on disk - must reload RPM to fix
                msg = "'%s' checksum different than expected - one or more of the following RPMs need to be reloaded : %s " % (fileName, ', '.join(rpmInfo.keys()))
                if fileIsExcluded:
                    msg = msg + ":: file is explicitly ignored"
                    self.logger.warning(self.module_name, msg)
                else:
                    self.messages.append('Manual Action %s' % msg)
                    self.problemFound = True
            
            if text:
                msg = "'%s' : %s" % (fileName, ', '.join(text))
                self.problemFound = True
                self.logger.warning(self.module_name, msg)
                if action == 'apply':
                    self.changes.update(sb_utils.file.fileperms.change_file_attributes(fileName, requiredChanges, changeOptions))
        
    def scan(self, optionDict=None):
        self.validate_input(optionDict)
        self.checkRPMs(action='scan')
        if self.problemFound == True:
            results = False
            reason = "One or more packages has files with incorrect settings"
        else:
            results = True
            reason = ""
        if self.ignorePackagesCount > 0:
            msg = "Found %d packages that were explicitly ignored" % self.ignorePackagesCount
            self.messages.append(msg)
        if self.ignoreFilesCount > 0:
            msg = "Found %d issues where either the file was explicitly ignored, or changes had been made by OS Lockdown" % self.ignoreFilesCount
            self.messages.append(msg)
                
        return results, reason, {'messages':self.messages} 
 
    def apply(self, optionDict=None):
        self.validate_input(optionDict)
        self.checkRPMs(action='apply')
        if self.problemFound == True:
            results = True
            reason = "One or more packages has files with incorrect settings"
        else:
            results = False
            reason = ""
        if self.ignorePackagesCount > 0:
            msg = "Found %d packages that were explicitly ignored" % self.ignorePackagesCount
            self.messages.append(msg)
        if self.ignoreFilesCount > 0:
            msg = "Found %d issues where either the file was explicitly ignored, or changes had been made by OS Lockdown" % self.ignoreFilesCount
            self.messages.append(msg)
                
        return results, str(self.changes), {'messages':self.messages} 
        pass   
 
    def undo(self, change_record=None):
        changeOptions = {'ignoreExcludes':True, 'checkOnly': False, 'recursive':False, 'exactDACs': True}
        sb_utils.file.fileperms.change_bulk_file_attributes(change_record, changeOptions)
        return 1
        
if __name__ == '__main__':
    test = ConsultRPMDatabase()
    test.logger.forceToStdout()
    sbRPMS = 'oslockdown zlib oslockdown-console oslockdown-license oslockdown-dispatcher oslockdown-modules'
    test.testHarnessRPMs = sbRPMS.split() 
    optdict = {'packageExemptions':'oslockdown-console oslockdown-modules', 'fileExemptions':'', 'honorChangesBySB': '1'}
    zz = test.scan(optdict)
    print zz
    
