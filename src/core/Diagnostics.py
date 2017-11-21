#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# This module contains various functions to test the operating
# environment required by the core engine of OS Lockdown.
#
#
global SELinuxEnabled
global MLSenabled

# These modules are part of the core Python package
# (Except the sbProps of course)
import sys

try:
    import atexit
    import base64
    import datetime
    import getopt
    import inspect
    import os
    import commands
    import platform
    import pwd
    import grp
    import re
    import sha
    import shutil
    import signal
    import socket
    import stat
    import StringIO
    import time
    import traceback
    import statvfs

    import sbProps

except ImportError, err:
    print >> sys.stderr, "ERROR: Unable to import core modules: %s" % err
    sys.exit(1)

##############################################################################
# Let's try to import our module to determine operating system and package
# information
try:
    import sb_utils.os.info
    import sb_utils.os.software
    import sb_utils.hardware
except ImportError, err:
    print >> sys.stderr, "ERROR: Unable to import modules: %s" % err
    sys.exit(sbProps.EXIT_PYTHON_IMPORT_ERR)

##############################################################################
# Libxml2 - Required for all of our configuration parsing and report generation
try:
    import libxml2
except ImportError, err:
    print >> sys.stderr, "ERROR: Unable to import modules: %s" % err
    print >> sys.stderr, "ERROR: Linux systems   - install 'libxml2-python'"
    print >> sys.stderr, "ERROR: Solaris systems - install 'SUNWlxml-python'"
    sys.exit(sbProps.EXIT_PYTHON_IMPORT_ERR)

##############################################################################
# Test OS Lockdown global Property settings
try:
    sys.path.append(sbProps.SB_BASE)
except AttributeError, err:
    print >> sys.stderr, "WARNING: %s" % err
    print >> sys.stderr, "WARNING: Using /usr/share/oslockdown as default base directory"

if not os.path.exists(sbProps.SB_BASE):
    print >> sys.stderr, "ERROR: %s does not exist." % sbProps.SB_BASE
    sys.exit(sbProps.EXIT_CONFIG_ERR)


##############################################################################
def sbDirectories():
    """Test to see if key directories exist"""
    testResult = True

    # removed the report directories as they can be created on the fly:
    for testDir in [sbProps.SB_BASE, sbProps.SB_DATA, sbProps.SECURITY_PROFILES, sbProps.BASELINE_PROFILES ]:
    
        if not os.path.exists(testDir):
            print >> sys.stderr, "ERROR: %s does not exist." % testDir
            testResult = False

        try: 
            results = os.access(testDir, os.R_OK)
            if results != True:
                print >> sys.stderr, "ERROR: Unable to access %s." % testDir
                testResult = False
        except AttributeError:
            # Some older versions of Python don't have this
            continue

    return testResult

##############################################################################
def fsFreeSpace(filePath):
    """Return MB Free"""
    try:
        myst = os.statvfs(filePath)
    except OSError, err:
        print >> sys.stderr, "ERROR: %s" % err
        return None

    return ((myst[statvfs.F_BAVAIL]*myst[statvfs.F_BSIZE])/1024)/1024


def check_ssl_certificate(certificate, userIDs, groupIDs, checkSSL, infoText):
    import sb_utils.os.info

    testFile = os.path.join(sbProps.SB_DIR_CERTS, certificate)
    testCA = os.path.join(sbProps.SB_DIR_CERTS, 'cacert.pem')
    status = '[Wrong Owner]'
    info = None
    try:
        if not os.path.exists(testFile):
            raise UserWarning("no such file")
    
        statInfo = os.stat(testFile)
        errorList=[]
	if statInfo.st_uid not in userIDs:
            errorList.append("owned by UID %d, should be owned by one of %s" % ( statInfo.st_uid, ",".join(userIDs)))
	if statInfo.st_gid not in groupIDs:
            errorList.append("owned by GID %d, should be owned by one of %s" % ( statInfo.st_gid, ",".join(groupIDs)))
	if errorList:
            raise UserWarning("\n".join(errorList))
    
        if testFile.endswith(".pem") and checkSSL :
            cmd = ""
            if sb_utils.os.info.is_solaris() == True:
                cmd = "/usr/sfw/bin/"
            cmd += "openssl verify -CAfile %s %s" % (testCA, testFile)
            status, results = commands.getstatusoutput(cmd)
            result_lines = results.splitlines()
            if 'has expired' in results:
                raise UserWarning("Certificate has expired")
            elif not result_lines[0].strip().endswith('OK') :
                
                raise UserWarning("Certificate is invalid")
#            print >> sys.stderr, status, results 

        status = '[    OK     ]'
        why = ""
        infoText = ""
    except UserWarning , err:
        status = '[   Error   ]'
	why =    '              : %s' %str(err)
    
        
    print >> sys.stdout, "%s - %s" % (status, testFile)
    if why:
        print >>sys.stdout, "              - %s" %str(err)
    if infoText:
        print >>sys.stdout, "              - %s" % infoText

##############################################################################
def consoleConfig():
    print >> sys.stdout, "\nConsole Config:"
    print >> sys.stdout, "==================="
    try:
        userInfo = pwd.getpwnam('sbwebapp')
    except KeyError:
        print >> sys.stdout, "User 'sbwebapp': missing"
        return None

    print >> sys.stdout, "User 'sbwebapp': Present"
    print >> sys.stdout, "        UID/GID: %s/%s" % (userInfo[2], userInfo[3])

    if not os.path.isfile(userInfo[6]):
        status = "[Missing]"
    else: 
        status = "[OK]"
    print >> sys.stdout, "          Shell: %s %s" % (userInfo[6], status)

    if not os.path.isdir(userInfo[5]):
        status = "[Missing]"
    else: 
        status = "[OK]"
    print >> sys.stdout, " Home Directory: %s %s" % (userInfo[5], status)

    if not os.path.exists("%s/.profile" % userInfo[5]):
        status = "[Missing]"
    else: 
        status = "[OK]"
    print >> sys.stdout, "  Shell Profile: %s/.profile %s" % (userInfo[5], status)
    
    ##
    ## Check JAVA_HOME from sbwebapp's profile
    ##
    if os.path.exists("%s/.profile" % userInfo[5]):
        try:
            inProfile = open("%s/.profile" % userInfo[5], 'r')
            lines = inProfile.readlines()
            inProfile.close()
            javaHome = ''
            for line in lines:
                line = line.strip()
                if line.startswith('JAVA_HOME='):
                    try:
                        javaHome = line.split('=')[1]
                    except IndexError:
                        continue
            if javaHome != '':
                if os.path.isdir(javaHome):
                    status = '[OK]'
                else:
                    status = '[Missing]'
                print >> sys.stdout, "      JAVA_HOME: %s %s" % (javaHome, status)


        except IOError, err:
            print >> sys.stderr, "ERROR: Unable to read %s/.profile" % userInfo[5]

    return None

def checkCerts(consoleFlag):
    # userIDs is an array with acceptable UIDs for ownership
        
    print >> sys.stdout ," "
    reqCerts = []
    extraCerts = []
    if os.path.isdir(sbProps.SB_DIR_CERTS):
        # Determine who should own the files - note they differ if Console is installed or not
        userIDs = []
        groupIDs = []
        for userName in ['root', 'sbwebapp']:
            try:
                thisUID = pwd.getpwnam(userName)[2]
            except KeyError:
                thisUID = 0
            if thisUID not in userIDs:
                userIDs.append(thisUID)
            
            try:
                thisGID= grp.getgrnam(userName)[2]
            except KeyError:
                thisGID = 0
            if thisGID not in groupIDs:
                groupIDs.append(thisGID)

        #                file/dir path                  SL CHECK       text
        # NOTE : if allowed user doesn't exist - ROOT is automatically allowed
        reqCerts =      [['.'                            , False , 'required by Console and Dispatcher'],
                         ['cacert.pem'                   , True  , 'required by Console and Dispatcher'],
                         ['Disp.pem'                     , True  , 'required by Dispatcher' ],
                         ['.sb_dispatcher_keystore.dat'  , False , 'required by Dispatcher' ]]

        if consoleFlag:
           extraCerts = [['GUIcert.pem'                  , True  , 'required by Console' ], 
                         ['GUIkey.pem'                   , False , 'required by Console'], 
                         ['GUI_keystore'                 , False , 'required by Console'], 
                         ['GUI_truststore'               , False , 'required by Console' ], 
                         ['.sb_tomcat_keystore.dat'      , False , 'required by Console'],     
                         ['.sb_tomcat_truststore.dat'    , False , 'required by Console']]


            
        print >> sys.stdout, "\nCertificates should be owned and group owned by root or sbwebapp"
        for testFile, checkSSL, infoText in reqCerts + extraCerts:
            check_ssl_certificate(testFile, userIDs, groupIDs, checkSSL, infoText)
    else:
        print >> sys.stdout, "%s does not exist, certs are required to interact with a Console)" % (sbProps.SB_DIR_CERTS)
    return None

def check_schema(xmllint, schema, filenames):
    valid = {}
    invalid = {}
    for filename in filenames:
        cmd = "%s --noout --schema %s %s" % (xmllint, schema, filename)
        status,results = commands.getstatusoutput(cmd)
        if status == 0:
            valid[filename] = {'valid' : True , 'results':"Valid"}
        else:
            invalid[filename] = {'valid' : False , 'results':results}
    return valid, invalid
  

def check_files(xmllint, schema, entry):
    valid = {}
    invalid = {}
    if os.path.exists(entry):
        if os.path.isdir(entry):
            filenames = [ "%s/%s" % (entry,element) for element in os.listdir(entry) if element.endswith(".xml")]
            valid, invalid = check_schema(xmllint,schema, filenames)
        elif os.path.isfile(entry):
            valid, invalid = check_schema(xmllint,schema, [entry])
       
    return valid, invalid  
    
def validate_profiles_and_statefile():


    print >> sys.stdout, "Validating security profiles, baseline profiles, and state file"
    print >> sys.stdout, "==============================================================="
    xmllint = None
    for candidate in ['/usr/bin/xmllint', '/bin/xmllint' ] :
      if os.path.exists(candidate) and os.access(candidate, os.X_OK):
        xmllint = candidate
        break
    if not xmllint:
        print >> sys.stdout,"Unable to locate 'xmllint' command to perform external validation of files"
	return


    todo=[]
    todo.append( { 'type'     : 'Baseline Profiles',
                   'schema'   : '/usr/share/oslockdown/cfg/schema/BaselineProfile.xsd', 
                   'location' : '/var/lib/oslockdown/baseline-profiles'})
    todo.append( { 'type'     : 'Security Profiles',
                   'schema'   : '/usr/share/oslockdown/cfg/schema/SecurityProfile.xsd',
                   'location' : '/var/lib/oslockdown/profiles'})
    todo.append( { 'type'     : 'State File',
                   'schema'   : '/usr/share/oslockdown/cfg/schema/oslockdown-state.xsd',
                   'location' : '/var/lib/oslockdown/oslockdown-state.xml'})
         
    results={}                
    for entry in todo:
        valid, invalid =  check_files(xmllint,entry['schema'],entry['location'])
        if valid or invalid :
            print "Checking %s..." % (entry['type'])
            if valid and len(valid) > 0:
                print >> sys.stdout,"\tNumber valid   : %d" % len(valid)
            if invalid and len(invalid) > 0:
                print >> sys.stdout,"\tNumber invalid : %d" % len(invalid)
                for badfile, reasons in invalid.items():
                    print >> sys.stdout,"\t\t%s" % (reasons['results'].splitlines()[0])
            
        else:
            print >> sys.stdout,"No %s exist." % entry['type']



##############################################################################
def dumpConfiguration():
    # Not sure why I need a re-import here but it barfs in Red Hat 4.7 if I don't
    import sb_utils.os.info

    print >> sys.stdout, "Diagnostic Dump:"
    print >> sys.stdout, "==================="
    print >> sys.stdout, "  Product: %s (%s)" % (sbProps.PRODUCT_NAME, sbProps.VERSION)
    print >> sys.stdout, "Copyright: %s" % (sbProps.COPYRIGHT)

    print >> sys.stdout, " Packages:"
    consoleFlag = False
    dispatcherFlag = True

    if sb_utils.os.info.is_solaris() == True:
         pkglist = ['TCSoslockdown', 'TCSoslockdown-modules', 
                    'TCSoslockdown-dispatcher',  'TCSoslockdown-console'  ] 
    else:
         pkglist = ['oslockdown', 'oslockdown-modules',
                    'oslockdown-dispatcher', 'oslockdown-console', 'oslockdown-console-ibmjava','oslockdown-selinux']
         
    for pkgName in pkglist:
        if sb_utils.os.software.is_installed(pkgName) == True:
            pkgVers = sb_utils.os.software.version(pkgName)
            if pkgName in ['oslockdown-console', 'oslockdown-console-ibmjava', 'TCSoslockdown-console']:
                consoleFlag = True
            if pkgName in ['oslockdown-dispatcher' ,'TCSoslockdown-dispatcher']:
                dispatcherFlag = True

            if sb_utils.os.info.is_solaris() == True:
                print >> sys.stdout, "%30s %s" % (pkgName, pkgVers[0])
            else:
                print >> sys.stdout, "%30s %s-%s" % (pkgName, pkgVers[0], pkgVers[1])

        else:
            print >> sys.stdout, "%30s is not installed" % (pkgName)


    print >> sys.stdout, "\nThis Platform:"
    print >> sys.stdout, "==================="

    print >> sys.stdout, "Operating System: %s" % (sb_utils.os.info.getDistroFullname())
    print >> sys.stdout, "          Kernel: %s" % ( platform.uname()[2])
    print >> sys.stdout, "             CPE: %s" % ( sb_utils.os.info.getCpeName() )

    # SELinux check for non-Solaris and non-SUSE systems
    if sb_utils.os.info.getDistroName() != 'Solaris' and sb_utils.os.info.is_LikeSUSE() != True:
        import sb_utils.SELinux
        SELinuxEnabled = sb_utils.SELinux.isSELinuxEnabled()
        
        SELinuxMode = sb_utils.SELinux.SELinuxMode()

        print >> sys.stdout, " SELinux Enabled: %s" % ( SELinuxEnabled )
        print >> sys.stdout, "    SELinux Mode: %s" % ( SELinuxMode )

    print >> sys.stdout, "    Architecture: %s/%s %s" % (platform.machine(),
                                                      platform.architecture()[0],
                                                      platform.architecture()[1])
    print >> sys.stdout, "          Memory: %dMB" % (sb_utils.hardware.getTotalMemory())
    print >> sys.stdout, "  Python Version: %s" % (platform.python_version())

    if sb_utils.os.software.is_installed('libxml2-python') == True:
        pkgVers = sb_utils.os.software.version('libxml2-python')
        print >> sys.stdout, "  Libxml2 Python: %s (libxml2-python)" % (pkgVers[0])

    if sb_utils.os.software.is_installed('openssl') == True:
        pkgVers = sb_utils.os.software.version('openssl')
        print >> sys.stdout, " OpenSSL Version: %s" % (pkgVers[0])

    print >> sys.stdout, "\nDirectories:"
    print >> sys.stdout, "==================="

    listOfDirs = [sbProps.SB_BASE, sbProps.SB_DIR_LOGS, sbProps.SB_DIR_REPORTS, 
                    sbProps.SB_DATA, sbProps.ASSESSMENT_REPORTS, sbProps.BASELINE_REPORTS, 
                    sbProps.SECURITY_PROFILES, sbProps.BASELINE_PROFILES, sbProps.BACKUP_DIR]

    if consoleFlag == True or dispatcherFlag == True:
        listOfDirs.append(sbProps.SB_DIR_CERTS)

    for testDir in listOfDirs:

        # '[    OK   ]' 
        # '[  Failed ]' 
        # '[ Missing ]' 
        # '[No Access]'
        # '[ 0 bytes ]'

        if not os.path.exists(testDir):
            status = '[ Missing ]'
        else:
            try:
                results = os.access(testDir, os.R_OK)
                if results != True:
                    status = '[No Access]'
                else:
                    status = '[    OK   ]'
                    freeSpace = fsFreeSpace(testDir)
                    if freeSpace == None:
                        freeSpace = ''
                    else:
                        if int(freeSpace) < 100:
                            status = '[LOW Space]'
                        if int(freeSpace) > 999:
                            freeSpace = "(%dG free)" % (int(freeSpace)/1024)
                        else:
                            freeSpace = "(%dM free)" % freeSpace

            except AttributeError:
                status = '[    OK   ]'
                
        print "%s - %s %s" % (status, testDir, freeSpace)

    print >> sys.stdout, "\nFiles:"
    print >> sys.stdout, "==================="
    for testFile in [sbProps.SB_CONFIG_FILE,  sbProps.SB_STATE_FILE, 
                     sbProps.XSD_CONFIG_FILE, sbProps.XSD_PROFILE, 
                     sbProps.XSD_STATE_FILE,  sbProps.SB_LOG]:
        status = '-'
        fileSize = '-'
        if not os.path.exists(testFile):
            status = '[ Missing ]'
        else:
            try:
                statinfo = os.stat(testFile)
                fileSize = str(statinfo.st_size)
            except OSError, err:
                continue

            try:
                results = os.access(testFile, os.R_OK)
                if results != True:
                    status = '[No Access]'
                else:
                    status = '[    OK   ]'
            except AttributeError:
                status = 'OK'
                
        if fileSize == '-':
            print "%s - %s" % (status, testFile)
        else:
            if fileSize == '0':
                status = '[ 0 bytes ]'

            if testFile.endswith('/oslockdown.log') \
                  and int(fileSize) >= sbProps.SB_LOG_WARN_SIZE:
                status = '[  LARGE  ]'
                fileSize = "WARNING: %s" % fileSize

            print "%s - %s (%s bytes)" % (status, testFile, fileSize)
 
    # Check Console Configuration
    if consoleFlag == True:
        consoleConfig()

    checkCerts(consoleFlag)
    print >> sys.stdout, "\n"

    validate_profiles_and_statefile()

if __name__ == '__main__':
    checkCerts(True)
#    print dumpConfiguration()
