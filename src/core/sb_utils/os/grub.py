#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#


import sys
import pwd
import os
import re
import commands
import platform

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.os.info
import sb_utils.file.dac
import tcs_utils

logger = TCSLogger.TCSLogger.getInstance()
 
# This class is responsible for parsing/editing a grub style file.  The fun
# part of these file is that indenting is not significant, and lines may have
# multiple line continuation characters.
#
# To handle this, we're conceptualizing a grub file as containing multiple 
# sections, with each section containing one or more mlines (multilines),
# with each mline holding one or more lines (if more than one then the 
# first line *must* have line continuation characters.
#
# So something like this (pardon the C-isms):
# struct grubconf
#   array(strings) sectionNames
#   dictionary(section) sections
# 
# struct section
#   string name
#   array(mline) mlines
#
# struct mline
#   integer type   (0 = comment, 1 = blank, 2 = tag)
#   string tagName
#   string rawline (rawline = possibly multi-lined text including line continuation chars)
#   string value (rawline has <tag> [=] value), so everything after the tag (skipping optional '=')
#   integer valueStart (index of first char of value)
#   string lines[] (discrete lines from file including any line continuations and line feeds)
#   string cookedLine = (concat lines[] removing line continuation chars and all but terminal line feed)
# 
# By iterating down the elements of sectionNames, looking up each section, then 
# iterating over the mlines and printing the rawline, you should be able to 
# reproduce the original file, with the exception of surrounding whitespace
# at the beginning and ends of lines.
#
# Alterations can be done by looking for the correct sectionName/tagName and 
# editting the rawline data.  

# Shim logger class for development...


class GrubMLine:
    def __init__(self):
        self.type = 0
        self.tag = ""
        self.value = ""
        self.valueStart = -1
        self.rawLine = ""
        self.lines = []
        self.cookedLine = ""
        
    def add_text(self, rawText):
        self.rawLine += rawText
        self.lines.append(rawText)
 
    def collapseLines(self):
        # regex is :
        #    group consistign of whitespace/hash at beginning of line
        #    group of characters not whitespace or '='
        #    group with whitespace or =
        #    group with everything else up to end of line
        tag_re = re.compile('^([#\s]*)([^=\s]+)([\s|=])*(.*)$', re.MULTILINE|re.DOTALL)
        
        line = ""
        for thisLine in self.lines:
            if thisLine.endswith('\\\n'):
                thisLine = thisLine[:-2]
            line += " "+thisLine.strip()
        self.cookedLine = line.strip()
        if self.cookedLine == "":
            self.type = ""
        elif self.cookedLine[0] == "#":
            self.type = "#"
        else:
            self.type = "T"

            #the first 'tag' is separated from values by whitespace and/or '='
            #so we'll use a regex to split it.
            re_results = tag_re.search(self.cookedLine)
            if re_results:
                self.tag = re_results.group(2)
                self.value = re_results.group(4)           
                self.valueStart = re_results.start(4)
                   
class GrubHandler:
    def __init__(self):
        self.__moduleName = "GrubHandler"
        self.__sectionNames = []
        self.__sections = {}
        self.__widest_line = 0
        self.__numTitles = 0
        self.logger = TCSLogger.TCSLogger.getInstance()
        self.__fileName = None
     
    def writeGrub(self, filename=None):
        """
        Write the contents of the mLines back to the indicated file.  If file is 'None', then
        use the self.__fileName field, if valid (IE - not 'None')
        """
        outFileName = None
        if filename:
            outFileName = filename
        elif self.__fileName:
            outFileName = self.__fileName
        
        try:
            # are we immutable?
            immutable = False
            if os.path.exists(outFileName) and sb_utils.file.dac.isImmutable(outFileName):
                msg = "File '%s' has immutable flag set - removing flag for write" % outFileName
                self.logger.warning(self.__moduleName, msg)
                sb_utils.file.dac.setXttr(outFileName, immutable=False)
                immutable = True
            open(outFileName,"w").writelines(self._mlines())
            if immutable == True:
                sb_utils.file.dac.setXttr(outFileName, immutable=True)
                msg = "Restoring immutable flag to '%s'" % outFileName
                self.logger.warning(self.__moduleName, msg)
                
        except Exception, err:
            msg = "Unable to write %s - %s" % (str(outFileName),err )
            self.logger.error(self.__moduleName, msg)
            raise tcs_utils.ActionError(msg)
        
    def _isGrubAvailable(self ):
        """
        Return True if GRUB is available/active on this platform.
        Return False otherwise
        For Linux, check for GRUB package (explictly False for zSeries)
        For Solaris, True for x86, False for Solaris
        """   
        if sb_utils.os.info.is_solaris() :
            if sb_utils.os.info.is_x86():
                return True
            else:
                return False
        elif 's390' in platform.machine():
            return False
        else:
            return sb_utils.os.software.is_installed('grub')

    def _addSection(self, sectionName, sectionMLines):
        """
        Add a section by name, giving the actual lines as sectionMLines
        """
        messages = []
        if sectionName != None and sectionMLines != []:
            for mLine in sectionMLines:
                mLine.collapseLines()
            if sectionName in self.__sections.keys():
                msg = "Boot definition '%s' already present in '%s' file, ignoring" % (sectionName, self.__fileName)
                self.logger.error(self.__moduleName, msg )
                messages.append(msg)
            else:
                if sectionName != "":
                    self.__numTitles += 1    
                    self.__sectionNames.append(sectionName)
 
                self.__sections[sectionName] = sectionMLines
        return messages
        
    def _locateGrubSolaris(self):
        """
        Run bootadm and locate where the default grub menu should be.  We'll parse the output to locate the file, then
        parse it ourselves later.
        """
        bootadmOut = commands.getoutput('/usr/sbin/bootadm list-menu').splitlines()
        for line in bootadmOut:
            if not line.startswith("The location for the active"):
                continue
            if '(not mounted)' in line:
                self.logger.warning("Unable to parse grub.lst menu, location not mounted")
            else:
                location = line.split(':',1)[1].split()[0].strip()
            break
        return location
        
    def _locateGrub(self):
        """
        Attempt to locate the correct grub.conf or menu.lst file in a given directory.
        There are some potential gotcha's to consider when handling Solaris, see the 'bootadm' command for more info,
        specifically on list-menu if the grub menu location is not mounted.
        """
        datafile = None
        if sb_utils.os.info.is_solaris():
            datafile = self._locateGrubSolaris()
        else:    
            grubdir = '/boot/grub'
            for thisfile in ['grub.conf', 'menu.lst']:
                dfile = "%s/%s"% (grubdir, thisfile)
                if os.path.exists(dfile) :
                    datafile = dfile
                    break
        return datafile

    def readGrub(self, filename=None):
        """
        Verify GRUB is available for this platform
        read the entire contents of the file and generate the raw
        mline data.
        """
        messages = []
        if not self._isGrubAvailable():
            raise tcs_utils.OSNotApplicable("GRand Unified Bootloader (GRUB) not used on this platform.")

        if not filename or not os.path.exists(filename):
            filename = self._locateGrub()
        
        if not filename:
            msg = "No filename given to parse"
            self.logger.error(self.__moduleName, msg)
            raise tcs_utils.ScanError(msg)
        try: 
            self.__fileName = filename
            allMLines = []
            mLine = GrubMLine()
            for line in open(filename):
                mLine.add_text(line)
                if not line.strip().endswith('\\') :
                    allMLines.append(mLine)
                    mLine = GrubMLine()
        except Exception, err:
            msg = "Unable to read grub configuration file : %s " % str(err)
            self.logger.error(self.__moduleName, msg)
            raise tcs_utils.ScanError(msg)

        if mLine.rawLine:
            allMLines.append(mLine)
         
        #Ok, now process the mLines into sections.  A section begins at each 
        #line that starts with 'title', and continues until the next section
        #start.  The first section is unlabeled.
        
        messages.extend(self._processLines(allMLines))
        return messages

    def restoreSectionLines(self, lines):
        messages = []
        self.logger.error(self.__moduleName, 'restoring')
        allMLines = []
        mLine = GrubMLine()
        for line in lines:
            mLine.add_text(line)
            if not line.strip().endswith('\\') :
                allMLines.append(mLine)
                mLine = GrubMLine()
        if mLine.rawLine:
            allMLines.append(mLine)
        messages.extend(self._processLines(allMLines))
        return messages
        
    def _processLines(self, allMLines):
        """
        Given an array of MLines, process them into sections and populate the appropriate fields
        """
        
        messages = []
        
        title_re = re.compile('^\s*title\s+(.+)$')
        yast_re = re.compile('^\s*###.*YaST2 identifier')
        sectionMLines = []
        sectionName=""
        lastline = None
        yast_line = None
        for mLine in allMLines:
            mobj = title_re.search(mLine.rawLine)
            if mobj:
                # SUSE specific change - if the last line added to sectionMLines was a comment with 3 hashes (IE
                # starts with '###', ignoring leading whitespace) *and* also has 'YaST2 identifier:' on the line
                # then it really belongs to the *new* section, so pop it off and add it back after starting the new
                #section
                if lastline and yast_re.search(lastline.rawLine):
                    yast_line = sectionMLines.pop()    
                messages.extend(self._addSection(sectionName,sectionMLines))
                sectionName = mobj.group(1)
                sectionMLines = []
                if yast_line:
                    sectionMLines.append(yast_line)
                    yast_line = None
            sectionMLines.append(mLine)
            lastline = mLine
        messages.extend(self._addSection(sectionName, sectionMLines)) 
        return messages

    def dump_Grub(self, verbose=False):
        """
        Dump all sections, remember that the "" section is all data prior to the first 'title' line.
        Verbose flag adds details on the type of line
        """
        
        for name in [""] + self.__sectionNames:
            if verbose:
                print "[SECTION] -> <%s>" % name
            
            for mLine in self.__sections[name]:
                if verbose:
                    print "\t[TYPE = <%s>, TAG = <%s>]" % (mLine.type, mLine.tag)
                    print "\t\t",
                print "%s" % mLine.rawLine,
                
    def numBootDefs(self):
        """
        How many boot definitions (ie - title sections) do we have?
        
        """
        
        return self.__numTitles
                
    def haveMultiBoot(self):
        """
        Do we have more than one boot definition?
        """
        
        results = False
        num = self.numBootDefs()
        if num > 1:
            result = True         
        
        return results
 
    def setSingleBootSection(self, sectionName=None):
        """
        If possible, comment out all sections *except* this one.
        Determine the current boot default and remember that section name.
        All comments are to be "#OSLockdown " (note space) so we
        can revert them.  If sectionName is an empty string then the 'default'
        section will be the one kept.
        """
        result = False
        messages = []
        
        oldDefault = self.getDefaultSection() 
        
        if sectionName == "":
            sectionName = oldDefault
            
        if sectionName not in self.__sectionNames:
            msg = "setSingleBootSection - unable to find boot def '%s'" % sectionName
            self.logger.warning(self.__moduleName, msg)
            messages.append("WARNING: %s" %msg)
        
        # get the names of the systems to remove
        sections_to_pop = [ section for section in self.__sectionNames if section != sectionName]
        
        #now go through and remove them.  Build a simple dictionary for the change record:
        # { 'sectionNames' = [ sections...]
        # { 'sections' = { 'sectionsName':mLines , ...}
        changerec = {}
        
        changerec['defaultSection'] = oldDefault
        changerec['sectionNames'] = sections_to_pop
        changerec['sections'] = {}
        for section in sections_to_pop:
            secdata = self.__sections.pop(section)
            changerec['sections'][section] = [mLine.rawLine for mLine in secdata] 
            self.__sectionNames.remove(section)

        messages.append("setSingleBootSection - setting section '%s' as default section" % sectionName)
        self._setIndexAsDefault(0)

        return changerec, messages
        
    def _setIndexAsDefault(self, indexNum):
        for mLine in self.__sections[""]:
            if mLine.tag == "default":
            # regular expression for this specific tag is '\d+', and we want to replace the number portion  
                mLine.rawLine = re.sub('\d+',str(indexNum),mLine.rawLine)

    def _setSectionAsDefault(self, sectionName):
        """
        Look for the given section and make it the default boot section
        """
        messages = []
        
        if not sectionName :
            msg = "No boot definition name provided"
            messages.append(msg)
            self.logger.warning(self.__moduleName, msg)
        try:           
            sectNum = self.__sectionNames.index(sectionName)
            self._setIndexAsDefault(sectNum)
            msg = "Boot definition '%s' (index = %d) set as default" % (sectionName, sectNum)
            self.logger.info(self.__moduleName, msg)
            
        except ValueError:
            msg = "No boot definition found for '%s'" % sectionName
            messages.append(msg)
            self.logger.warning(self.__moduleName, msg)
        return messages
             
    def addToLines(self, section, tag, data):
        """
        Add an *exact* text string in data to any tag line if it doesn't exist.  The string will be appended to the end of the line after 
        a space.  If section == None then add to all sections except '', otherwise require a match on the section name.
        """
        
        messages = []
        changerec = {}
        #what regex would indicate a match?
        for sectionName in self.__sectionNames:
            if section != None and sectionName != section:
                continue
            for mLine in self.__sections[sectionName]:
                if mLine.tag != tag:
                  continue
                if data not in mLine.rawLine[mLine.valueStart:].split() :
                    if not sectionName in changerec.keys():
                        changerec[sectionName] = {}
                    mLine.rawLine = mLine.rawLine[:mLine.valueStart] + mLine.rawLine[mLine.valueStart:].rstrip()+" "+data+"\n"
                    if sectionName == "":
                        self.logger.info (self.__moduleName, "Adding '%s' to '%s' line global sectiom" % (data, tag, sectionName))
                    else:
                        self.logger.info (self.__moduleName, "Adding '%s' to '%s' line for boot definition '%s'" % (data, tag, sectionName))
                    
                    changerec[sectionName] = {tag:data} 
        return changerec, messages

    def checkLines(self, section, tag, data, reportMissing=True):
        """
        Look through sections for tags with/without the indicated data.
        If reportMissing == True   log missing lines
        If reportMissing == False  log line with data
         """
        
        messages = []
        haveData = []
        missingData = []
        changerec = {}

        #what regex would indicate a match?
        for sectionName in self.__sectionNames:
            if section != None and sectionName != section :
                continue
            for mLine in self.__sections[sectionName]:
                if mLine.tag != tag:
                  continue
                if data in mLine.rawLine[mLine.valueStart:] :
                    haveData.append("Found '%s' in '%s' tag for boot definition '%s'" % (data, tag, sectionName))
                else:
                    missingData.append("Did not find '%s' in '%s' tag for boot definition '%s'" % (data, tag, sectionName))
        if reportMissing == True:
            return missingData
        else:
            return haveData                                                           
        
    
    def removeFromLines(self, section, tag, data):
        """
        Remove an *exact* text string from any 'kernel' tag line.  The string *must* be word bounded (\b).
        Since we *could* someday have a case where tag and data are the same, we need to locate the tag with a potential change,
        then advance pass the tag field before.  If there is a leading space before the data pull that also
        """
        
        messages = []
        changerec = {}
        #what regex would indicate a match?
        for sectionName in self.__sectionNames:
            if section != None and sectionName != section :
                continue
            for mLine in self.__sections[sectionName]:
                if mLine.tag != tag:
                  continue
                if data in mLine.rawLine[mLine.valueStart:] :
                    if not sectionName in changerec.keys():
                        changerec[sectionName] = {}
                    mLine.rawLine = mLine.rawLine[:mLine.valueStart] + re.sub(" +"+data,"",mLine.rawLine[mLine.valueStart:])
                    if sectionName == "":
                        self.logger.info (self.__moduleName, "Removing '%s' from '%s' line global sectiom" % (data, tag, sectionName))
                    else:
                        self.logger.info (self.__moduleName, "Removing '%s' from '%s' line for boot definition '%s'" % (data, tag, sectionName))
                    changerec[sectionName] = {tag:data} 
        return changerec, messages
                                       
    def getSections(self):
        """
        Return the names of the sections, in order.
        """
        return self.__sectionNames
        
    def _getDefaultSectionIndex(self):
        """
        Look for the default tag in the unlabeled (1st) section and
        return that index + 1, which will be the section number which is
        booted by default.  If the default tag doesn't exist, it is zero
        We *always* reference sections by name, not index
        """
        defaultSect = 0
        for mLine in self.__sections[""]:
            if mLine.tag and mLine.tag == "default":  
                defaultSect = int(mLine.value)
        return defaultSect

    def getDefaultSection(self):
        """
        Look for the default tag in the unlabeled (1st) section and
        return that index + 1, which will be the section number which is
        booted by default.  If the default tag doesn't exist, it is zero
        We *always* reference sections by name, not index
        """
        return self.__sectionNames[self._getDefaultSectionIndex()]

    def _mlines(self):
        """
        Debug only - display all mLines in the file - could be used for writing to disk?
        """
        mlines = []
        for name in [""] + self.__sectionNames:
            for mLine in self.__sections[name]:
                mlines.append(mLine.rawLine)
        return mlines
        
        

