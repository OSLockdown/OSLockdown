#!/usr/bin/env python
#
# Copyright (c) 2013-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys

try:
    foobar = set([])
except NameError:
    from sets import Set as set

sys.path.append("/usr/share/oslockdown")
import tcs_utils
import TCSLogger

class VerifySoftwareCryptoCerts:
    """
    Look for the output of 'rpm -qa gpg-pubkey*' and ensure that the
    required strings are present.  We are unable to remediate this as this
    requires additional packages to be installed, so raise a manual action
    on an apply failure with appropriate messages.  For completeness, if we
    find any certs that *are't* in the required list mention them (EPEL for 
    instance) *IF* requested by the profile.
    """
    ##########################################################################
    def __init__(self):
        self.module_name = "VerifySoftwareCryptoCerts"
        
        self.logger = TCSLogger.TCSLogger.getInstance()

    def validate_input(self, optionDict):
        trueFalse = {'1':True, 'True':True, '0': False, 'False':False}
        
        try:
            self.requiredSet    = set(optionDict['requiredCerts'].splitlines())
            self.showExtraCerts = trueFalse[optionDict['showExtraCerts']]
        except ValueError:
            msg = "Invalid option value -> '%s'" % optionDict
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

                
    ##########################################################################
    def checkCerts(self):
        cmd = 'rpm -qa --queryformat="%{SUMMARY}\n" gpg-pubkey*'
        results = tcs_utils.tcs_run_cmd(cmd, True)
        installedSet = set(results[1].splitlines())
        missingCerts = list(self.requiredSet  - installedSet)
        extraCerts = list(installedSet - self.requiredSet )
        foundCerts = list (self.requiredSet  - set(missingCerts))
        
        for cert in foundCerts:
            msg = "Found required certificate : %s" % cert
            self.logger.info(self.module_name, msg)
        for cert in missingCerts:
            msg = "Missing required certificate : %s" % cert
            self.logger.warning(self.module_name, msg)
        if self.showExtraCerts == True:
            for cert in extraCerts:
                msg = "Found extra certificate : %s" % cert
                self.logger.info(self.module_name, msg)
        
        return missingCerts, extraCerts
        
    ##########################################################################
    def scan(self, optionDict={}):
        """Check to see if /etc/hosts.allow file is correct"""

        messages = []
        retval = True

        self.validate_input(optionDict)
        missingCerts, extraCerts = self.checkCerts()         

        if missingCerts == []:
            retval = True
            msg = "Missing %s required vendor-provided cryptographic certificates" % len(missingCerts) 
        else:
            retval = False
            msg = ""
        messages.extend(["Error Missing cryptographic certificate to provide    : %s" % cert for cert in missingCerts])
        if extraCerts and self.showExtraCerts == True:
            messages.extend(["Found Extra cryptographic certificate providing : %s" % cert for cert in extraCerts])
        
        return retval, msg, {'messages':messages}


    ##########################################################################
    def apply(self, optionDict={}):
        """Create and replace the /etc/hosts.allow configuration if it doesn't match."""

        messages = []
        retval = False

        self.validate_input(optionDict)

        missingCerts, extraCerts = self.checkCerts()         

        messages.extend(["Missing cryptographic certificate to provide    : %s" % cert for cert in missingCerts])
        if extraCerts and self.showExtraCerts == True:
            messages.extend(["Found Extra cryptographic certificate providing : %s" % cert for cert in extraCerts])

        if missingCerts:
            msg = "Missing %d cryptographic certificates - must be installed manually : " % len(missingCerts)
            msg = msg + "\n" + "\n".join(messages)
            raise tcs_utils.ManualActionReqd('%s %s' % (self.module_name, msg))

        return retval, "", {'messages':messages}


    ##########################################################################
    def undo(self, change_record=None):
        """Undo the previous action."""
        
        msg = "Skipping Undo: No change record in state file."
        self.logger.notice(self.module_name, 'Skipping undo: ' + msg)
        return False, msg, {}

if __name__ == "__main__":
    reqdCerts = "gpg(Red Hat, Inc. (release key 2) <security@redhat.com>)\nbogus cert"
    optionDict={'requiredCerts':reqdCerts, 'showExtraCerts':'1'}
    test = VerifySoftwareCryptoCerts()
    test.logger.forceToStdout()
    a,b,c = test.scan(optionDict)
    print "______"
    print a
    print b
    print c
