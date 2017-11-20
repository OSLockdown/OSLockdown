#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# State Handler - Responsible for recording the status of actions
#   as reported by the CoreEngine. Also, responsible for recording
#   and retrieving change records used by each module's apply() and
#   undo() methods.
#
##############################################################################

import sys
import libxml2
import sbProps
import os
import platform
import shutil
import xml.sax.saxutils

os.sys.path.append(sbProps.SB_BASE)
import sb_utils.SELinux
import ModuleInfo
try:
    import TCSLogger
except ImportError:
    try:
        from sb_utils.misc import TCSLogger
    except ImportError:
        raise

import sb_utils.os.info
from sb_utils.misc import tcs_utils


MODULE_NAME = "StateHandler"
MODULE_REV  = "$Rev: 23917 $".strip('$').strip()


class EmptyChangeRecord(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


class StateHandler:
    """
    Manage the states of security modules to include recording the
    results of their actions and retrieving change records for the undo
    action.
    """

    def __init__(self):
        """Constructor"""
        os.umask(077) 

        self.MODULE_NAME = MODULE_NAME
        self.REV = MODULE_REV
        self.STATE_FILE = sbProps.SB_STATE_FILE
        self.STATE_FILE_BACKUP = sbProps.SB_STATE_FILE_BACKUP
        self.stateFileXmlDoc = None

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6)
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance()

        #
        # Look for files in default location otherwise,
        # look in a relative path because we might be operating
        # in development mode.
        #
        if os.path.isfile(sbProps.SB_CONFIG_FILE):
            SB_CONFIG_FILE = sbProps.SB_CONFIG_FILE 
        else:
            SB_CONFIG_FILE = "../security_modules/cfg/security-modules.xml"

        if os.path.isfile(sbProps.XSD_STATE_FILE):
            self.XSD_STATE_FILE = sbProps.XSD_STATE_FILE
        else:
            self.XSD_STATE_FILE = "../../cfg/schema/oslockdown-state.xsd"            

        if os.path.isfile(self.STATE_FILE):
            try: 
                shutil.copy2(self.STATE_FILE, self.STATE_FILE_BACKUP)
                sb_utils.SELinux.restoreSecurityContext(self.STATE_FILE_BACKUP)
                msg = "Backed up state file to %s" % (self.STATE_FILE_BACKUP)
                self.logger.notice(MODULE_NAME, msg)
            except Exception, err:
                msg = "Unable to copy state file to %s : %s" % (self.STATE_FILE_BACKUP, str(err))
                self.logger.error(MODULE_NAME, msg)

        msg = "StateHandler (%s) activated." % MODULE_REV
        self.logger.notice(MODULE_NAME, msg)

        msg = "Using state file %s" % self.STATE_FILE
        self.logger.debug(MODULE_NAME, msg)

        self._ModuleConfigs  = ModuleInfo.sbModule(configFile=SB_CONFIG_FILE)
        self.logger.debug(MODULE_NAME, "Loaded metadata for %d modules" % len(self._ModuleConfigs))

        self._LibraryMapping = ModuleInfo. getModuleToLibraryMap(configFile=SB_CONFIG_FILE)
        self.logger.debug(MODULE_NAME, "Mapped %d modules to their libraries" % len(self._LibraryMapping))

        self.VALID_STATE_FILE = self._validateStateFile()


    def __del__(self):
        """ 
        Make sure the state file gets written to disk if 
        the class instance is destroyed
        """
        self._saveStateFile()

        if self.stateFileXmlDoc:
            try:
                self.stateFileXmlDoc.freeDoc()
            except:
                pass


    #################################
    ###    Set action status      ###
    #################################
    def setActionStatus(self, libraryName=None, action=None, results=None, execTimeMs=None):
        """
        Update a module record's action element with current date/time 
        and provided results string
        """
        acceptableResults = ['Pass',  'Fail', 'Applied', 'Undone', 'Error', 
                             'Manual Action', 'NA',  'OS NA',   'Zone NA', 
                             'NAVAIL', 'Not Required', 'Module Unsupported']

        if libraryName == None:
            msg = "No libraryName provided"
            self.logger.error(MODULE_NAME, msg)
            return False

        if action == None:
            msg = "No action provided"
            self.logger.error(MODULE_NAME, msg)
            return False

        if results == None:
            msg = "No results provided"
            self.logger.error(MODULE_NAME, msg)
            return False

        if action not in ['scan', 'apply', 'undo']:
            msg = "'%s' is not a recognized action" % action
            self.logger.error(MODULE_NAME, msg)
            return False

        # Results string MUST match recognized values in the 
        # security-blanekt-state.xsd schema file.
        if results not in acceptableResults:
            msg = "'%s' is not a recognized results string" % results
            self.logger.error(MODULE_NAME, msg)
            return False
            
        moduleNode = self.stateFileXmlDoc.xpathEval("/ModuleStates/module[@libraryName='%s']" % libraryName)
        # If we can't find a node for this module, create one.
        if len(moduleNode) < 1:
            moduleNode = self._createNewModuleNode(libraryName=libraryName)
            # ok, just created it, so we *know* we have an action node, just get it
            
#            actionNode = moduleNode.newChild(None, "action", None)
            actionNode = moduleNode.xpathEval("./action[@operation='%s']" % action)[0]
            actionNode.setProp("operation", action)
        else:
            # For some reason, the a full xpathEval statement with @operation match
            # was not working for me!!
            actionNode = moduleNode[0].xpathEval("./action")
            mustAdd = True
            for testNode in actionNode:
                if testNode.prop("operation") == action:
                    actionNode = testNode
                    mustAdd = False
                    break

            if mustAdd == True:
                actionNode = moduleNode[0].newChild(None, "action", None)
                actionNode.setProp("operation", action)


        # Update the "dynamic" attributes...
        actionNode.setProp("date", tcs_utils.get_timestamp())
        if execTimeMs != None:
            # To eleminate any garbage here. First convert provided
            # value to integer and then back to string
            actionNode.setProp("execTimeMs", str(int(execTimeMs)))

        return True


    #################################
    ###  Retrieve Change Records  ###
    #################################
    def getLibraryLastChangeRecord(self, libraryName=None):
        """Get last change record for specified library"""

        if libraryName == None:
            return None

        if self.VALID_STATE_FILE == False:
            msg = "State file %s is invalid" % self.STATE_FILE
            self.logger.critical(MODULE_NAME, msg)
            return False

        changeRecord = self.stateFileXmlDoc.xpathEval("/ModuleStates/module[@libraryName='%s']/ChangeRecords/change_record[@seq='1']" % libraryName)
        if len(changeRecord) < 1:
            msg = "No change record for module library '%s' in state file." % libraryName
            self.logger.info(MODULE_NAME, msg)
            changeRecord = None
        else:
            if changeRecord[0].hasProp("date") and changeRecord[0].hasProp("sbVersion"):
                extraInfo = " / v%s record (seq1) stored on %s" % (changeRecord[0].prop("sbVersion"), changeRecord[0].prop("date"))
            else:
                extraInfo = ''

            changeRecord = changeRecord[0].getContent()
            msg = "Retrieved %d byte change record for module library '%s'%s" % (len(changeRecord), libraryName, extraInfo)
            self.logger.debug(MODULE_NAME, msg)
           
        return xml.sax.saxutils.unescape(changeRecord)


    ###################################
    ##  Set library's change record ###
    ###################################
    def setLibraryChangeRecord(self, libraryName=None, changeRecord=None):
        """Set change record for specified module"""

        if libraryName == None:
            msg = "No module name specified"
            self.logger.error(MODULE_NAME, msg)
            return False

        if not self._ModuleConfigs.has_key(libraryName):
            msg = "Unable to map '%s' library with full module name." % libraryName
            self.logger.warning(MODULE_NAME, msg)
            moduleName = ''
        else: 
            moduleName =  self._ModuleConfigs[libraryName]['name']

        # Empty chage records are unacceptable
        if changeRecord == None:
            msg = "Provided change record for module library '%s' is data type 'None'" % libraryName
            raise EmptyChangeRecord(msg)

        if changeRecord == '':
            msg = "Provided change record for module library '%s' is ''" % libraryName
            raise EmptyChangeRecord(msg)

        changeRecord = xml.sax.saxutils.escape(changeRecord)

        try:
            moduleNode = self.stateFileXmlDoc.xpathEval("/ModuleStates/module[@libraryName='%s']" % libraryName)
        except libxml2.xpathError, err:
            self.logger.critical(MODULE_NAME, str(err) )
            return False

        if len(moduleNode) < 1:
            msg = "Unable to locate entry for '%s' in state file" % libraryName
            self.logger.info(MODULE_NAME, msg)
            moduleNode = self._createNewModuleNode(libraryName=libraryName)
        else:
            moduleNode = moduleNode[0]

        changeRecordsNode =  moduleNode.xpathEval("./ChangeRecords")

        ## No change records exist all
        if len(changeRecordsNode) < 1:
            changeRecordsNode = moduleNode(None, "ChangeRecords", None)

            changeNode1 = changeRecordsNode.newChild(None, "change_record", str(changeRecord))
            changeNode1.setProp("seq", "1")
            changeNode1.setProp("date", tcs_utils.get_timestamp())
            changeNode1.setProp("sbVersion", sbProps.VERSION)

            changeNode2 = changeRecordsNode.newChild(None, "change_record", str(changeRecord))
            changeNode2.setProp("seq", "2")
            changeNode2.setProp("sbVersion", sbProps.VERSION)


        else:
            changeRecordsNode = changeRecordsNode[0]

            changeNode1 =  changeRecordsNode.xpathEval("./change_record[@seq='1']")
            changeNode2 =  changeRecordsNode.xpathEval("./change_record[@seq='2']")

            if len(changeNode2) < 1:
                changeNode2 = changeRecordsNode.newChild(None, "change_record", None)
                changeNode2.setProp("seq", "2")
            else:
                changeNode2 = changeNode2[0]
                

            # Change record (seq=1) does NOT Exist
            if len(changeNode1) < 1:
                changeNode1 = changeRecordsNode.newChild(None, "change_record", str(changeRecord))
                changeNode1.setProp("seq", "1")
                changeNode1.setProp("date", tcs_utils.get_timestamp())

            # First change record exists so copy it into the second (seq=2)
            else:
                msg = "Copying change record seq1 to seq2 (module library %s)" % libraryName
                self.logger.debug(MODULE_NAME, msg)

                changeNode1 = changeNode1[0]
                tempData = xml.sax.saxutils.escape(changeNode1.getContent())
                changeNode2.setContent(tempData)
                if changeNode1.hasProp("date"):
                    changeNode2.setProp("date", changeNode1.prop("date"))
                else:
                    changeNode2.setProp("date", tcs_utils.get_timestamp())

                changeNode2.setProp("sbVersion", sbProps.VERSION)

                changeNode1.setContent(str(changeRecord))
                changeNode1.setProp("date", tcs_utils.get_timestamp())
                changeNode1.setProp("sbVersion", sbProps.VERSION)
                

        msg = "Wrote %d byte change record for module library '%s'" % (len(str(changeRecord)), libraryName)
        self.logger.notice(MODULE_NAME, msg)
        self._saveStateFile()

        return True

    ###################################
    ###      Create module node     ###
    ###################################
    def _createNewModuleNode(self, libraryName=None):
        """Create blank module node and return xmlNode of the new element"""

        if libraryName == None:
            return None

        if not self._ModuleConfigs.has_key(libraryName):
            moduleName = ''
        else:
            moduleName =  self._ModuleConfigs[libraryName]['name']

        root = self.stateFileXmlDoc.getRootElement()
        moduleNode = root.newChild(None, "module", None)
        moduleNode.setProp("libraryName", libraryName)
        moduleNode.setProp("name", moduleName)

        for action in ['scan', 'apply', 'undo']:
            actionNode = moduleNode.newChild(None, "action", None)
            actionNode.setProp("operation", action)

        changeNode = moduleNode.newChild(None, "ChangeRecords", None)
        for changeIndex in range(1, 3):
            tempNode = changeNode.newChild(None, "change_record", None)
            tempNode.setProp("seq", str(changeIndex))

        return moduleNode

    ######################################
    ### Update lastAction* info fields ###
    ######################################
    def updateLastAction(self, action=None):
        """
        Update info element's lastAction and lastActionTime attributes
        """
        if action == None or self.VALID_STATE_FILE == False:
            return

        if action not in ['scan', 'apply', 'undo']:
            msg = "'%s' is not a recognized action" % action
            self.logger.error(MODULE_NAME, msg)
            return

        infoNode = self.stateFileXmlDoc.xpathEval("/ModuleStates/info")
        if len(infoNode) < 1:
            msg = "Unable to locate 'info' element"
            self.logger.error(MODULE_NAME, msg)
            return

        infoNode[0].setProp("lastAction", action)
        infoNode[0].setProp("lastActionTime",  tcs_utils.get_timestamp() )
        return

        

    ###################################
    ### Clear Current Change Record ###
    ###################################
    def clearLastChangeRecord(self, libraryName=None):
        """
        Copy last change record (seq1) to backup (seq2) and then
        set last change record (seq1) to ''
        """
        if libraryName == None:
            msg = "No module name specified"
            self.logger.error(MODULE_NAME, msg)
            return False

        moduleNode = self.stateFileXmlDoc.xpathEval("/ModuleStates/module[@libraryName='%s']" % libraryName)
        if len(moduleNode) < 1:
            msg = "Unable to locate entry for '%s' in state file" % libraryName
            self.logger.info(MODULE_NAME, msg)
            return False

        changeRecordsNode =  moduleNode[0].xpathEval("./ChangeRecords")

        if len(changeRecordsNode) < 1:
            changeRecordsNode = moduleNode(None, "ChangeRecords", None)
            changeNode1 = changeRecordsNode.newChild(None, "change_record", '')
            changeNode1.setProp("seq", "1")
            changeNode2 = changeRecordsNode.newChild(None, "change_record", '')
            changeNode2.setProp("seq", "2")
            return False

        else:
            changeRecordsNode = changeRecordsNode[0]

            changeNode1 =  changeRecordsNode.xpathEval("./change_record[@seq='1']")
            changeNode2 =  changeRecordsNode.xpathEval("./change_record[@seq='2']")

            if len(changeNode2) < 1:
                changeNode2 = changeRecordsNode.newChild(None, "change_record", None)
                changeNode2.setProp("seq", "2")
            else:
                changeNode2 = changeNode2[0]
                

            # Change record (seq=1) does NOT Exist
            if len(changeNode1) < 1:
                changeNode1 = changeRecordsNode.newChild(None, "change_record", '')
                changeNode1.setProp("seq", "1")
                changeNode1.setProp("date", tcs_utils.get_timestamp())

            # First change record exists so copy it into the second (seq=2)
            else:
                msg = "Copying change record seq1 to seq2 (module library %s)" % libraryName
                self.logger.debug(MODULE_NAME, msg)

                changeNode1 = changeNode1[0]
                changeNode2.setContent(xml.sax.saxutils.escape(changeNode1.getContent()))
                msg = "Copied module library '%s' last change record to backup (seq2)" % libraryName
                self.logger.debug(MODULE_NAME, msg)

                if changeNode1.hasProp("date"):
                    changeNode2.setProp("date", changeNode1.prop("date"))
                else:
                    changeNode2.setProp("date", tcs_utils.get_timestamp())

                changeNode2.setProp("sbVersion", sbProps.VERSION)
                changeNode1.setContent('')
                changeNode1.setProp("date", tcs_utils.get_timestamp())
                changeNode1.setProp("sbVersion", sbProps.VERSION)
                

        msg = "Cleared last change record for module library '%s'" % (libraryName)
        self.logger.notice(MODULE_NAME, msg)
        self._saveStateFile()

        return True


    ###################################
    ### Validate Current State File ###
    ###################################
    def _validateStateFile(self):
        """Validate state file against its schema"""
        
        if not os.path.isfile(self.STATE_FILE):
            self._createNewStateFile()
            return True

        msg = "Using schema %s to verify state file" % (self.XSD_STATE_FILE)
        self.logger.debug(MODULE_NAME, msg)
        try:
            ctxt = libxml2.schemaNewParserCtxt(self.XSD_STATE_FILE)
            schema = ctxt.schemaParse()
            validationCtxt = schema.schemaNewValidCtxt()
            self.stateFileXmlDoc = libxml2.parseFile(self.STATE_FILE)
            instance_Err = validationCtxt.schemaValidateDoc(self.stateFileXmlDoc)

        except Exception, err:
            self.logger.error(MODULE_NAME, str(err))
            return False


        if instance_Err != 0:
            msg = "%s is invalid according to its schema %s" % (self.STATE_FILE, self.XSD_STATE_FILE) 
            self.logger.error(MODULE_NAME, msg)
            return self.convertOldStateFile()

        msg = "%s has been validated against its schema %s" % (self.STATE_FILE, self.XSD_STATE_FILE) 
        self.logger.debug(MODULE_NAME, msg)
        return True


    #################################
    ##### Save State file to disk ###
    #################################
    def _saveStateFile(self):
        if self.stateFileXmlDoc == None:
            return False

        try:
            out_obj = open(self.STATE_FILE, 'w')
            self.stateFileXmlDoc.saveTo(out_obj,  sbProps.XML_ENCODING, 1)
            out_obj.close()

        except (IOError, OSError), err:
            msg = "Unable to write to %s : %s" % (self.STATE_FILE, str(err))
            self.logger.error(MODULE_NAME, msg)
            raise

        try:
            os.chown(self.STATE_FILE, 0, 0)
            os.chmod(self.STATE_FILE, 0600)
	    sb_utils.SELinux.restoreSecurityContext(self.STATE_FILE);
        except OSError, err:
            msg = "Unable to properly set access controls on %s: %s" % (self.STATE_FILE, str(err))
            self.logger.error(MODULE_NAME, msg)

        return True 

    ################################
    ##### Create New State File ####
    ################################
    def _createNewStateFile(self):
        """Create a new state file"""
        
        msg = "Creating a new state file: %s" % (self.STATE_FILE)
        self.logger.notice(MODULE_NAME, msg)

        newReport = libxml2.newDoc("1.0")
        root = newReport.newChild(None,  "ModuleStates", None)
        root.setProp("sbVersion", sbProps.VERSION)

        ##
        ## Add top level XML comments
        ##
        sysCpeName =  sb_utils.os.info.getCpeName()
        msg = "\n     %s \n\n         Purpose: %s Modules State File "\
              "\n     Initialized: %s\n" % \
             (sbProps.COPYRIGHT, sbProps.PRODUCT_NAME, tcs_utils.get_timestamp())
        msg = "%s        Nodename: %s\n" % (msg, platform.node())
        msg = "%s             CPE: %s\n" % (msg, sysCpeName)
        msg = "%s\n            Note: DO NOT manually edit because it could "\
              "affect your ability to undo actions !!\n" % msg
        comment = newReport.newDocComment(msg)
        root.addPrevSibling(comment)
        del comment

        ##
        ## Add 'info' element to record system specific information
        ##
        infoNode = root.newChild(None, "info", None)
        infoNode.setProp("nodename", platform.node())
        infoNode.setProp("platform", sysCpeName)
        infoNode.setProp("lastAction", '-')
        infoNode.setProp("lastActionTime", '-')
        del infoNode

        self.stateFileXmlDoc = newReport
        self._saveStateFile()

        ##
        ## Create a node for every module in the current inventory
        ##
        for moduleName in self._LibraryMapping.keys():
            self._createNewModuleNode(libraryName=self._LibraryMapping[moduleName])

        msg = "Added %d blank module records to state file" % len(self._LibraryMapping.keys())
        self.logger.debug(MODULE_NAME, msg)

        self._saveStateFile()

        return True

    ########################################
    ###  Check perissions of state file  ###
    ########################################
    def checkStateFilePermissions(self):
        """
        Check to see if state file is own by root, group root, 
        and file mode is 0600.

        Returns: Boolean
        """

        msg = "Checking access controls on %s" % self.STATE_FILE
        self.logger.debug(MODULE_NAME, msg)

        # If the file doesn't exist, the permissions are okay. :-)
        if not os.path.isfile(self.STATE_FILE):
            return True

        try:
            statinfo = os.stat(self.STATE_FILE)
        except OSError, err:
            # Since we are unable to determine permissions, assume the
            # permissions are unacceptable
            msg = "Unable to stat %s: %s" % (self.STATE_FILE, err)
            self.logger.error(MODULE_NAME, msg)
            return False

        goodDAC = True
        if statinfo.st_uid != 0:
            msg = "%s is not owned by 'root'" %  self.STATE_FILE
            self.logger.info(MODULE_NAME, msg)
            goodDAC = False

        if statinfo.st_gid != 0:
            msg = "%s state file's group is not 'root'" %  self.STATE_FILE
            self.logger.info(MODULE_NAME, msg)
            goodDAC = False

        if statinfo.st_mode & 0777 ^ 0600 != 0:
            msg = "%s state file's base mode is not 0600" % self.STATE_FILE
            self.logger.info(MODULE_NAME, msg)
            goodDAC = False
             
        return goodDAC


    ################################
    ###  Convert old State File  ###
    ################################
    def convertOldStateFile(self):
        """Convert previous state files to current version"""

        altStateFilePath = '/var/lib/oslockdown/reports/standalone/oslockdown-state.xml'
        if os.path.isfile(self.STATE_FILE):
            try:
                shutil.copy2(self.STATE_FILE, self.STATE_FILE + ".backup")
                sb_utils.SELinux.restoreSecurityContext(self.STATE_FILE_BACKUP)
            except Exception, err:
                msg = "Unable to make a backup copy of %s : %s" % (self.STATE_FILE, str(err))
                self.logger.error(MODULE_NAME, msg)
                return False

        msg = "Created backup copy of state file: %s.backup" % self.STATE_FILE
        self.logger.debug(MODULE_NAME, msg)

        # Create new state file
        self._createNewStateFile()

        try:
            oldStateFile = libxml2.parseFile(self.STATE_FILE + ".backup")
        except Exception, err:
            return False
        
        moduleNodes = oldStateFile.xpathEval("//security_module")
        if len(moduleNodes) < 1:
            msg = "Unable to locate any <security_module> elements in older state file"
            self.logger.error(MODULE_NAME, msg)
            return False

        ##
        ## Examine every security_module entry in old state file and retrieve
        ## the old chagne record.
        ##
        for moduleNode in moduleNodes:
            if not moduleNode.hasProp("name"): continue
            moduleName = moduleNode.prop("name")

            if not self._LibraryMapping.has_key(moduleName): continue
            libraryName = self._LibraryMapping[moduleName]

            # First and foremost, let's copy over the change record
            changeNode = moduleNode.xpathEval("./change_record")
            if len(changeNode) > 0:
                changeString = str(changeNode[0].getContent())
                if changeString != '':
                    self.setLibraryChangeRecord(libraryName=libraryName, changeRecord=changeString)

        oldStateFile.freeDoc()
        self._saveStateFile()

        return True



if __name__ == '__main__':
    Test = StateHandler()
    Test.updateLastAction(action="apply")

    #print Test.getLibraryLastChangeRecord(libraryName='DefaultUmask')
    #print Test.setLibraryChangeRecord(libraryName='DefaultUmask', changeRecord="Rob Change Records")
    #print Test.setActionStatus(libraryName='DefaultUmask', action='scan', results='Pass', execTimeMs=None)
    #print Test.setActionStatus(libraryName='DefaultUmask', action='apply', results='Applied', execTimeMs="12")
    #print Test.setActionStatus(libraryName='DefaultUmask', action='undo', results='Undone', execTimeMs="12")
    #print Test.clearLastChangeRecord(libraryName='DefaultUmask')

