#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# This module is designed to be called from other OS Lockdown
# modules to disable "any" service. This module contains generic
# scan, apply, and undo methods which simply accept the "library"
# name of the module. This module will then look up the associated
# services and packages from the modules cofniguration file.
#
#
##############################################################################
MODULE_REV = "$Rev: 13537 $".strip('$').strip()

import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
from ModuleInfo import getServiceList, getPackageList
from sb_utils.os.info import is_solaris

import sb_utils.os.software
import sb_utils.os.service

# Will this module immediately shutdown the service?
# By default on Linux systems, this module will just configure
# the service to not start at next boot (chkconfig). 
# Setting this flag will cause this module to attempt to stop
# the service now using the service(8) command.

STOP_SERVICE_NOW = False


try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

def stop_service_now():
    if is_solaris() == True:
        return False
    else:
        return STOP_SERVICE_NOW

##########################################################################
def scan(libraryName=None, enable = False, packageList = None, serviceList = None, option=None):

    if serviceList == None:
        (serviceList, serviceProps) = getServiceList(libraryName=libraryName)
    elif type(serviceList) == type(""):
        serviceList = [serviceList]
    elif type(serviceList) != type([]):
        msg = "Invalid service list detected"
        logger.error(libraryName, "Scan Error: " + msg)
        raise tcs_utils.ScanError('%s %s' % (libraryName, msg))
    
    if packageList == None:
        packageList = getPackageList(libraryName=libraryName)
    elif type(packageList) == type(""):
        packageList = [packageList]
    elif type(packageList) != type([]):
        msg = "Invalid package list detected"
        logger.error(libraryName, "Scan Error: " + msg)
        raise tcs_utils.ScanError('%s %s' % (libraryName, msg))

#    print "ServiceList",serviceList
#    print "PackageList",packageList
    if not serviceList and not packageList:
        msg = "No services or packages identified for this module"
        raise tcs_utils.OSNotApplicable('%s %s' % (libraryName, msg))
     
    messages = {}
    messages['messages'] = []

    # Check for each package in the list. If ONE package is missing,
    # report a not applicable
    for pkg_item in packageList:
        results = sb_utils.os.software.is_installed(pkgname=pkg_item) 
        
        
        if results == False and enable == False:
            msg = "'%s' package is not installed" % pkg_item
            logger.warning(libraryName, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (libraryName, msg))
        elif results == False and enable == True:
            msg = "'%s' package is not installed" % pkg_item
            logger.warning(libraryName, 'Admin must install required package first: ' + msg)
            raise tcs_utils.ManualActionReqd('%s %s' % (libraryName, msg))
        else:
            msg = "'%s' package is installed" % pkg_item
            logger.info(libraryName, msg)
            messages['messages'].append(msg)
 
    results_flag = True
    for service_item in serviceList:
        results = sb_utils.os.service.is_enabled(svcname=service_item)
        if enable == False:
            if results == True:  # should be off and is on
                msg = "'%s' service is enabled" % service_item
                logger.notice(libraryName, 'Scan Failed: ' + msg)
                messages['messages'].append("Fail: %s" % msg)
                results_flag = False
            else:                # should be off and is off
                msg = "'%s' service is disabled" % service_item
                logger.notice(libraryName, msg)
                messages['messages'].append(msg)
        else:
            if results == False:  # should be on and is off
                msg = "'%s' service is disabled" % service_item
                logger.notice(libraryName, 'Scan Failed: ' + msg)
                messages['messages'].append("Fail: %s" % msg)
                results_flag = False
            else:                 # should be on and is on 
                msg = "'%s' service is enabled" % service_item
                logger.notice(libraryName, msg)
                messages['messages'].append(msg)


    if results_flag == False:
        if enable == False:
            results_msg = "One or more associated services are enabled"
        else:
            results_msg = "One or more associated services are disabled"
    else:
        if enable == False:
            results_msg = "All associated services are enabled"
        else:
            results_msg = "All associated services are disabled"

    return results_flag, results_msg, messages


##########################################################################
def apply(libraryName=None, enable = False, packageList = None, serviceList = None, option=None):
    """
    Disable services associated with this module.

    Returns:
      (update_flag, action_record, messages)

      update_flag   -- Boolean: True = StateHandler will record change record
      action_record -- String: Change record the StateHandler will store
      messages      -- Dictionary: messages to embed into the repord
    """

    # scan first to see if we need to do anything...and don't bother trying
    # to turn things off if they already are
    
    results, reason, messages = scan(libraryName, enable=enable, packageList=packageList, serviceList=serviceList, option=option)
    if results == True:
        return False, reason, messages

    
    if serviceList == None:
        (serviceList, serviceProps) = getServiceList(libraryName=libraryName)
    elif type(serviceList) == type(""):
        serviceList = [serviceList]
    elif type(serviceList) != type([]):
        msg = "Invalid service list detected"
        logger.error(libraryName, "Scan Error: " + msg)
        raise tcs_utils.ScanError('%s %s' % (libraryName, msg))

    if packageList == None:
        packageList = getPackageList(libraryName=libraryName)
    elif type(packageList) == type(""):
        packageList = [packageList]
    elif type(packageList) != type([]):
        msg = "Invalid package list detected"
        logger.error(libraryName, "Scan Error: " + msg)
        raise tcs_utils.ScanError('%s %s' % (libraryName, msg))

    if len(serviceList) < 1:
        msg = "No services identified for this module."
        raise tcs_utils.OSNotApplicable('%s %s' % (libraryName, msg))
     
    messages = {}
    messages['messages'] = []
    action_record = []

    # Check for each package in the list. If ONE package is missing,
    # report a not applicable
    for pkg_item in packageList:
        results = sb_utils.os.software.is_installed(pkgname=pkg_item) 
        if results == False:
            msg = "'%s' package is not installed" % pkg_item
            logger.warning(libraryName, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (libraryName, msg))
        else:
            msg = "'%s' package is installed" % pkg_item
            logger.info(libraryName, msg)
            messages['messages'].append(msg)
    
    service_count = 0
    all_services = len(serviceList)
    update_flag = False
    error_flag = False
    for service_item in serviceList:
        pre_change = ''
        results = sb_utils.os.service.is_enabled(svcname=service_item)
        if results == None:
            msg = "Unable to determine status of the '%s' service" % service_item
            logger.error(libraryName, msg)
            error_flag = True
            messages['messages'].append(msg)
            continue


        if enable == False:
            # Record service's current state before we disable it
            # but DO NOT add it to the change record until we are able
            # actually perform the apply
            if results == False:
                msg = "'%s' service is already disabled" % service_item
                messages['messages'].append(msg)
                continue

            pre_change = "%s|on\n" % service_item

            # Try to disable the service
            results = sb_utils.os.service.disable(svcname = service_item)
            if results != True:
                msg = "Unable to disable service '%s'" % service_item
                logger.error(libraryName, msg)
                error_flag = True
                messages['messages'].append(msg)
            else:
                service_count = service_count + 1
                msg = "'%s' service is now configured to not start during next system boot" % service_item
                logger.notice(libraryName, "Apply Performed: %s" % msg)
                action_record.append(pre_change)
                messages['messages'].append(msg)
                update_flag = True
                if stop_service_now() == False:
                    msg = "To immediately disable the '%s' service either "\
                          "reboot or execute: service %s stop" % (service_item, service_item)
                    messages['messages'].append(msg)
        else: 
            # Record service's current state before we disable it
            # but DO NOT add it to the change record until we are able
            # actually perform the apply
            if results == True:
                msg = "'%s' service is already enabled" % service_item
                messages['messages'].append(msg)
                continue

            pre_change = "%s|off\n" % service_item

            # Try to disable the service
            results = sb_utils.os.service.enable(svcname = service_item)
            if results != True:
                msg = "Unable to enable service '%s'" % service_item
                logger.error(libraryName, msg)
                error_flag = True
                messages['messages'].append(msg)
            else:
                service_count = service_count + 1
                msg = "'%s' service is now configured to start during next system boot" % service_item
                logger.notice(libraryName, "Apply Performed: %s" % msg)
                action_record.append(pre_change)
                messages['messages'].append(msg)
                update_flag = True
                if stop_service_now() == False:
                    msg = "To immediately enable the '%s' service either "\
                          "reboot or execute: service %s stop" % (service_item, service_item)
                    messages['messages'].append(msg)

    if error_flag == True and service_count == 0:
        if enable == False:
            msg = "Unable to disable associated services" 
        else:
            msg = "Unable to enable associated services" 
        raise tcs_utils.ActionError(msg)

    if error_flag == True and service_count != all_services:
        if enable == False:
            msg = "Unable to disable all of the associated services"
        else:
            msg = "Unable to enable all of the associated services"
    else:
        if enable == False:
            msg = "Disabled all of the associated services"
        else:
            msg = "Enabled all of the associated services"

    # When returning our change record, we will reverse the order of the
    # services. This way when the undo method receives it, they will be
    # "undone" in reverse order.
    action_record.reverse()

    return update_flag, ''.join(action_record), messages


##########################################################################
def undo(libraryName=None, change_record=None):

    (serviceList, serviceProps) = getServiceList(libraryName=libraryName)
    packageList = getPackageList(libraryName=libraryName)

    # Not needed
    del serviceList 
    error_flag = False
    messages = {}
    messages['messages'] = []

    if not change_record:
        msg = "No change record in state file."
        logger.notice(libraryName, 'Skipping undo: ' + msg)
        messages['messages'].append(msg)
        return False, msg, messages

    # Check for each package in the list. If ONE package is missing,
    # report a not applicable
    
# Commenting out package/service check - base the undo solely on the change record
#   for pkg_item in packageList:
#       results = sb_utils.os.software.is_installed(pkgname=pkg_item) 
#       if results == False:
#           msg = "'%s' package is not installed" % pkg_item
#           logger.warning(libraryName, 'Not Applicable: ' + msg)
#           messages['messages'].append(msg)
#       else:
#           msg = "'%s' package is installed" % pkg_item
#           logger.info(libraryName, msg)
#           messages['messages'].append(msg)

    service_count = 0
    all_services = 0
    for change in change_record.split('\n'):
        if not change:
            continue

        all_services += 1
        try:
            (service_item, service_state) = change.split('|')
        except:
            msg = "Malformed change record: %s" % change
            logger.error(libraryName, msg)
            continue
        
        # a few older modules inverted the item/state relation, so try to sanity check the results
        if service_item in ['on' ,'off'] and service_state not in ['on', 'off']:
            msg = "Detected reversed change record, fixing on the fly..."
            logger.notice(libraryName, msg)
            temp_swap = service_item
            service_item = service_state
            service_state = service_item
            
        
        if service_state == 'on':
            results = sb_utils.os.service.enable(svcname=service_item)
            if results != True:
                msg = "Unable to enable the '%s' service" % service_item
                logger.error(libraryName, msg)
                error_flag = True
                messages['messages'].append(msg)
            else:
                msg = "'%s' service is now configured to start during next system boot" % service_item
                logger.notice(libraryName, "Undo Performed: %s" % msg)
                messages['messages'].append(msg)
                service_count = service_count + 1
        else:
            results = sb_utils.os.service.disable(svcname=service_item)
            if results != True:
                msg = "Unable to disable the '%s' service" % service_item
                logger.error(libraryName, msg)
                error_flag = True
                messages['messages'].append(msg)
            else:
                msg = "'%s' service is now configured to not start during next system boot" % service_item
                logger.notice(libraryName, "Undo Performed: %s" % msg)
                messages['messages'].append(msg)
                service_count = service_count + 1

    if error_flag == True and service_count == 0:
        msg = "Unable to restore associated services their previous states." 
        raise tcs_utils.ActionError(msg)

    if error_flag == True and service_count != all_services:
        msg = "Unable to restore the state of all associated services"
    else:
        msg = "Restored the state of all associated services"
            

    return True, msg, messages


if __name__ == '__main__':

    enable = True
    module="DisableWebServer_apache"
    (scan_flag, scan_msg, scan_msgs) = scan(libraryName=module, enable=enable)
    print "scan_flag " , scan_flag
    print "scan_msg  ",scan_msg
    print "scan_msgs " , scan_msgs
   
    print "------"
    (apply_flag, change_record, apply_msgs) = apply(libraryName=module, enable=enable)
    print "Apply_flag    " , apply_flag
    print "change_record ",change_record
    print "apply_msgs    " , apply_msgs
 
    print "------"
    if apply_flag and change_record:
      print undo(libraryName=module, change_record=change_record)
    else:
      print "No need to undo anything"
