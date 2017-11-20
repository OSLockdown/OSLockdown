#!/usr/bin/env python
#
# Copyright (c) 2013 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")

import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.SELinux

class RetainCipher(Exception): pass
class RejectCipher(Exception): pass

# The setparam routines are specialized copies of the sb_utils.os.config routines, designed to handle ssh/sshd config files.
# We need to iterate *through* them to make the changes, and be aware that the ssh_config file may have host specific settings
# Generated as a 'class' to allow callers to easily specialize things *if* needed.


class Ssh_Sshd_ConfigEditor:
    def __init__(self):
        self.module_name = ""
        self.package = ""
        self.configfile = ""
        self.settings = []
        self.defaultCiphers = ""
        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 


    def checkPkg(self):
        
        if not sb_utils.os.software.is_installed(self.package):
            msg = "'%s' does not appear to be installed on the system" % self.package
            self.logger.warn(self.module_name+".checkPkg", 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))


    def getHostSections(self, configfile=None):
        """
        Go through and return the 'Host' section names.
        Returns a list of names for ssh_config file ( IE [ '*', 'host1', ...])
        Returns an empty list if no 'Host ' sections found
        """

            
        sections = []
        try:
            for line in open(configfile, 'r'):
                try:
                    fields = line.strip().split()
                    if fields[0] == "Host":
                        sections.append(fields[1].strip())
                except IndexError, err:
                    pass
        except IOError, err:
            msg = 'Unable to open %s: %s' % (configfile, err)        
            raise tcs_utils.ActionError(self.module_name, msg)

        # ok, verified access to file, expliticly set the sections if we're
        # processing the sshd_config file
        if configfile.endswith('sshd_config'):
            sections = [None]
        return sections

    ##############################################################################
    def get_list(self, configfile=None, hostSection=None):
        """
        Get list of parameters and return dictionary - if hostSection specificed then values are restricted to the 
        give 'Host' section
        """

        paramdict = {}

        if configfile == None: return None
        if not os.path.isfile(configfile): return None

        currHostSection=None

        try:
            in_obj = open(configfile, 'r')
        except IOError, err:
            msg = 'Unable to open %s: %s' % (configfile, err)        
            self.logger.error(self.module_name+".get_list", msg)
            return None


        for line in in_obj.readlines():
            line = line.strip()

            if line.startswith('#') or line.startswith('\n'): continue

            if hostSection:
                try:
                    fields = line.strip().split()
                    if fields[0] == "Host":
                    # new host section found - if we were just in the correct one, we're done - break out
                        if hostSection == currHostSection :
                            break
                        currHostSection = fields[1].strip()
                        continue
                    if currHostSection != hostSection:
                        continue
                except IndexError,err:
                    pass

            try:
                (param, value) = line.rstrip('\n').split()
            except ValueError:
                continue

            if param:
                param = param.strip()
                if not value: value = ''
                paramdict[param] = value.strip()

        in_obj.close()
        return paramdict


    ##############################################################################
    def setparam(self, param=None, value=None, configfile=None, hostSection=None):
        """
        Set parameter in configuration file.
        Return False on failure or previous value of parameter
                  (return empty string if parameter was not previously set)
        """
        if configfile == None: return None
        configfile_new = configfile + '.new'
        if not os.path.isfile(configfile): return None

        currHostSection=None

        orig_value = ''
        newLines = []
        
        try:
            in_obj = open(configfile, 'r')
        except IOError, err:
            msg = 'Unable to open %s: %s' % (configfile, err)        
            self.logger.error(self.module_name+".setparam", msg)
            return False

        foundit = False
        madeChange = False
        for line in in_obj.readlines():
            
            if hostSection and line.strip().startswith('Host '):
                try:
                    fields = line.strip().split()
                    if fields[0] == "Host":
                        # new host section found - if we were just in the correct one, and still haven't found our variable, we're done - break out
                        if hostSection == currHostSection and not foundit :
                            break
                        currHostSection = fields[1].strip()

                except IndexError,err:
                    pass


            try:
                if (not hostSection or hostSection == currHostSection) and line.strip().split()[0] == param:
                    if value :
                        valStartsAt = line.find(param)+len(param)+1
                        orig_value = line[valStartsAt:].strip()
                        line = line[0:valStartsAt] + value + "\n"
                        foundit = True
                    else:
                        line = ""
                        orig_value = ""
            except IndexError, err:
                pass

            if line:
                newLines.append(line)
                madeChange = True
                
        # If it was not found, append the setting to the end of the file

        if not foundit and value:
            newLines.append(param + " " + value + '\n')
            madeChange = True
        in_obj.close()

        if madeChange == True:
            
            try:
                open(configfile_new, 'w').writelines(newLines)
                shutil.copymode(configfile, configfile_new)
                shutil.copy2(configfile_new, configfile)
                sb_utils.SELinux.restoreSecurityContext(configfile)
                os.unlink(configfile_new)
            except OSError, err:
                self.logger.error(self.module_name+".setparam", err)
                return False
        
            if value:
                msg = "Set '%s' to '%s' in %s" % (str(param), str(value), configfile) 
            else:
                msg = "Removed '%s' from %s" % (str(param),  configfile) 
            self.logger.log_debug(self.module_name+".setparam", msg)

        return orig_value

    def _isEqualTo(self, param, foundValue, requiredValue):
        msgs = []
        retval = foundValue

        if not foundValue:
            retval = requiredValue
            msg = "%s is not set" % (param)
        elif foundValue != requiredValue:
            retval = requiredValue
            msg =  "%s has incorrect setting" % (param)
            msgs.append(msg)
        elif foundValue == requiredValue:
            retval = requiredValue
            msg =  "%s has correct setting" % (param)
            self.logger.debug(self.module_name+"._isEqualTo", msg)
        return retval, msgs

    # test for requiring foundValue to be less than or equal to than requiredValue
    def _noGreaterThan(self, param,foundValue,requiredValue):
        retval = foundValue
        msgs = []
        
        if not foundValue:
            retval = requiredValue
            msg = "%s is not set" % (param)
            msgs.append(msg)
        else:
            int1 = int(foundValue)
            int2 = int(requiredValue)
            if int1 <= int2 :
                msg = "%s of %s is less than or equal to %s" % (param, foundValue, requiredValue)
                self.logger.debug(self.module_name+"._noGreaterThan", msg)
            else:
                retval = requiredValue
                msg = "%s of %s is greater than %s" % (param, foundValue, requiredValue)
                msgs.append(msg)
    
        return retval, msgs

    # test for requiring foundValue to be greater than or equal to requiredValue
    def _noLessThan(self, param,foundValue,requiredValue):
        retval = foundValue
        msgs = []
        
        # test for requiring value to be no more than 10
        if not foundValue:
            retval = requiredValue
            msg = "%s is not set" % (param)
            msgs.append(msg)
        else:
            int1 = int(foundValue)
            int2 = int(requiredValue)
            
            if int1 >= int2 :
                msg = "%s of %s is greater than or equal to %s" % (param, foundValue, requiredValue)
                self.logger.debug(self.module_name+"._noLessThan", msg)
                msg = ''
            else:
                retval = requiredValue
                msg = "%s of %s is less than %s" % (param, foundValue, requiredValue)
                msgs.append(msg)
                
        return retval, msgs
            

    ### Note that the following routines do slightly different things if a 'ssh_config' or 'sshd_config' file is passed
    ### For sshd_config we don't need to call the get_hosts() method to get the list of sections, the file is implicitly a single section
    ### For ssh_config (in scan/apply) we need to iterate over the possible hostSections, collecting possible changes
    ### The undoCfg() method will take the change record and explicitly call back in to setparam to do the right thing
    ### 
    ### cfgList should be a tuple of:
    ###    Configstring to look for
    ###    the 
    def checkFile(self, cfgList, action="scan"):
        messages = []
        changes = []
        
        hostSections = self.getHostSections(configfile=self.configfile)
        for section in hostSections:
            values = self.get_list(configfile=self.configfile, hostSection=section)
            if section != None:
                sectionMsg = "Section 'Host %s' : " % section
            else:
                sectionMsg = ""
                
            for param, requiredValue, verifyMethod in cfgList:
                if verifyMethod == None:
                    verifyMethod = self._isEqualTo
                msg = ''
                foundValue = None
            
                try:
                    foundValue = values[param]
                except KeyError:
                    pass
                                    
                # The real correct value might be a modified version of what we found (ciphers for example), so use what the verifyMethod() returns
                requiredValue, msgs  = verifyMethod(param, foundValue, requiredValue)
                if requiredValue != foundValue:
                    changes.append([section,param, foundValue])
                    
                    # write changes only if we are applying, but we use the changes field to indicate if things needed to change...
                    if action == 'apply':
                        self.setparam(configfile=self.configfile, hostSection=section, param=param, value=requiredValue)
                        reason = "Apply"
                    else:
                        reason = "Scan Failed"
                    
                    for msg in msgs:
                        self.logger.info(self.module_name+".checkFile", '%s: %s' % (reason, sectionMsg + msg))
                        messages.append(sectionMsg + msg)

        return changes, messages
    

    ##########################################################################
    def scanCfg(self, cfgList):
        """
        """

        retval = True
        msg = ''
        self.checkPkg()
        changes, messages = self.checkFile(cfgList, 'scan')

        if changes != []:
            msg = "One or more values were not set correctly"            
            retval = False
        
        return retval, msg, {'messages':messages}

    ##########################################################################
    def applyCfg(self, cfgList):
        """
        Modify  setting for sshd.
        """
        retval = False
        msg = ''
        self.checkPkg()

        changes, messages = self.checkFile(cfgList, 'apply')

        if changes != []:
            retval = True
        
        return retval, str(changes), {'messages':messages}


    ##########################################################################
    def undoCfg(self, change_record=None):
        """Undo the previous action."""


        # note - oldstyle changes records were patches, so try to split out any patches *first*.  Anything after that we need to process as a stringified dictionary
        patches, changeString = tcs_utils.split_patches(change_record)

        if patches:
            # Ok, found at least one patch, pass the whole change record through to the legacy patch apply stuff, it will quietly drop anything at the end
            try:
                tcs_utils.apply_patch(change_record)
            except tcs_utils.ActionError, err:
                msg = "Unable to undo previous changes (%s)." % err 
                self.logger.error(self.module_name+'.undoCfg', 'Undo Error: ' + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name+'.undoCfg', msg))

        # anything else/left should be convert into a dictionary and procesed
        if changeString:
            changeDict = tcs_utils.string_to_dictionary(changeString)
            for section, param, value in changeDict:
                 junk = self.setparam(configfile=self.configfile, param = param, value = value, hostSection=section)

        self.logger.notice(self.module_name+'.undoCfg', 'Undo Performed ')
        return True,'',{}

    def _splitRestrictions(self, restrictions, prefix="", suffix=""):
        allowedOptions = []
        deniedOptions = []
        allowedPattern = ""
        deniedPattern = ""
        
        if restrictions:
            for opt in restrictions:
                if opt.startswith("!"):
                    deniedOptions.append(opt[1:])
                else:
                    allowedOptions.append(opt)
            if allowedOptions:
                allowedPattern = "%s(%s)%s" % (prefix, "|".join(allowedOptions), suffix)
            if deniedOptions:
                deniedPattern = "%s(%s)%s" % (prefix, "|".join(deniedOptions), suffix)

        return allowedPattern, deniedPattern
                

    def _restrictCiphers(self, param, cipherLine, restrictions):
        """
           cipherLine holds the settings from the 'Ciphers' field
           restrictions is a dictionary with:
               mustStartWith = list of allowed starting fields
               mustContain   = list of allowed interior fields
               mustEndWith   = list of allowed ending fields 
           for each list, if an entry starts with '!' then this indicates negation of that entry
           each cipher is evaluated against each element of the list, and a non-matching finding == exclusion of that cipher
    
           For example, 
             startswith = aes 3des
             endswith   = !cbc
             
             would keep any cipher that starts with aes, starts with 3des, and does not end with cbc
             if the processed list winds up with *no* entries, then a "ManualActionRecq" exception is raised.
             
           The method returns the modified list of ciphers, and the list of rejected ciphers
        """

        acceptCiphers  = []
        rejectCiphers  = []
        messages       = []
        
        if not cipherLine:
            cipherLine = self.defaultCiphers
            msg = "No setting found for '%s' - using OS default as per man pages of '%s'" % (param, cipherLine)
            self.logger.info(self.module_name, msg)
            
        cipherList = tcs_utils.splitNaturally(cipherLine, wordAdditions='-:')

        if 'mustStartWith' in restrictions:
            allowedStarts, rejectedStarts = self._splitRestrictions(tcs_utils.splitNaturally(restrictions['mustStartWith'], wordAdditions='-:!'), prefix="^")
        if 'mustContain' in restrictions:
            allowedContains, rejectedContains = self._splitRestrictions(tcs_utils.splitNaturally(restrictions['mustContain'], wordAdditions='-:!'))
        if 'mustEndWith' in restrictions:
            allowedEnds, rejectedEnds = self._splitRestrictions(tcs_utils.splitNaturally(restrictions['mustEndWith'], wordAdditions='-:!'), suffix="$")

        acceptPattern = ".*".join ([pattern for pattern in [allowedStarts, allowedContains, allowedEnds] if pattern ])
        rejectPattern = ".*".join ([pattern for pattern in [rejectedStarts, rejectedContains, rejectedEnds] if pattern ])
                
        acceptRegex = re.compile(acceptPattern)
        rejectRegex = re.compile(rejectPattern)
    
        
        for cipher in cipherList:
            # by default we accept, unless the match fails
            acceptMatch = True
            if acceptPattern and not acceptRegex.search(cipher) : acceptMatch = False
            rejectMatch = False
            if rejectPattern and rejectRegex.search(cipher) : rejectMatch = True
            if acceptMatch and not rejectMatch:
                msg = "Cipher '%s' matched acceptable criteria" % cipher
                self.logger.debug(self.module_name+"._restrictCiphers", str(msg))
                acceptCiphers.append(cipher)
            else:
                msg = "Cipher '%s' did not match acceptable criteria" % cipher
                messages.append(msg)
                rejectCiphers.append(cipher)
            
        if not acceptCiphers:
            msg = "List of acceptable ciphers is empty - please configure '%s' manually " % self.configfile
            raise tcs_utils.ManualActionReqd("%s %s" % (self.module_name, msg))

        return ','.join(acceptCiphers), messages
                    
                    
        
    
class _ExampleCallingClass(Ssh_Sshd_ConfigEditor):
    def __init__(self):
        Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name = "foo"
        self.package = "sshd-server"
        
        # sshd_config
        if True:
            self.configfile = '/tmp/s/sshd_config'
            self.settings = [ ['GSSAPIAuthentication', 'yes',self._isEqualTo], 
                              ['X11Forwarding', 'no', self._isEqualTo],
                              ['NumVal', '10', self._noGreaterThan]
                        ]
        # ssh_config
        if True:   
            self.configfile = '/tmp/s/ssh_config'
            self.settings = [ ['GSSAPIAuthentication', 'yes',self._isEqualTo], 
                          ['NumVal', '10', self._noGreaterThan]
                        ]
                        
            
    def scan(self,options=None):
        return self.scanCfg(self.settings)
        
    def apply(self, options=None):
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
      
if __name__ == '__main__':
    myLog = TCSLogger.TCSLogger.getInstance()
    myLog.force_log_level (7)
    myLog._fileobj = sys.stdout
    test = _ExampleCallingClass()
    
    # Settings consist of a list of tuples, each tuple is 'param', 'value', VerificationMethod(param, foundValue, desiredValue)
    # VerificationMethod() is a method to call that verifies the paramters against the 'value'.  It returns a tuple (value, msg). If no changes are required, 
    # the return 'value' will be the same as the 'foundValue', and msg will be empty.  Otherwise the value that *should* be there is returned, and msg will have
    # the reason why.
    
    res, msg, messages =  test.scan()
    print "SCAN"
    print res
    print msg
    print messages
    print

    res,changeRec, messages = test.apply()
    print "APPLY"
    print res
    print changeRec
    print messages
    print

    if res == True :  # only undo if we applied (CoreEngine would only call with valid change, so we just look for results)
        res, changeRec, messages = test.undo(changeRec)
        print "UNDO"
        print res
        print changeRec
        print messages
        print

