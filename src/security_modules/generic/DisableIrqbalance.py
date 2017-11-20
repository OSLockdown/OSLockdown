##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Disable the Interrupt Distribution on Multiprocessor Systems (irqbalance)
#
# NOTE: Disabling 'irqbalance' on single CPU systems is recommended, but *not* required.
#       On multi-CPU systems it *should* be on, but again, it is not recommended.
#
#
#
##############################################################################
 
import sys
sys.path.append('/usr/share/oslockdown')
import TCSLogger
import sb_utils.hardware
import tcs_utils
import sb_utils.os.info

try:
    import Enable_Disable_Any_Service
except ImportError:
    raise
 
class DisableIrqbalance:
 
    def __init__(self):
        self.module_name = self.__class__.__name__
        self._package = 'irqbalance'
        
        if sb_utils.os.info.is_LikeSUSE():
            self._service = 'irq_balancer'
        else:
            self._service = 'irqbalance'
        self._multiCPU = False
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 
        
    def _getCurrent(self):
        
        packageInstalled = sb_utils.os.software.is_installed(pkgname=self._package) 
        if packageInstalled == False:
            msg = "'%s' package is not installed" % self._package
            self.logger.warning(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "'%s' package is installed" % self._package
            self.logger.info(self.module_name, msg)

        serviceOn = sb_utils.os.service.is_enabled(svcname=self._service)
        if serviceOn == None:
            msg = "Unable to determine status of the '%s' service" % self._service
            self.logger.error(self.module_name, msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        elif serviceOn == False:
            msg = "The '%s' service is not configured to start" % self._service
            self.logger.info(self.module_name, msg)
        elif serviceOn == True:
            msg = "The '%s' service is configured to start" % self._service
            self.logger.info(self.module_name, msg)
        
        cpuinfo = sb_utils.hardware.getCpuInfo()

        multiCPU = False        
        cpuCount = 0
        for cpu in cpuinfo.keys():
            cpuCount += cpuinfo[cpu]
            
        if cpuCount > 1  :
            multiCPU = True
            msg = "Multi CPU system identified" 
            self.logger.info(self.module_name, msg)
        else:
            msg = "Single CPU system identified" 
            self.logger.info(self.module_name, msg)
        
        # set this in our instance so 'apply' can use it
        self._multiCPU = multiCPU    
        
        return multiCPU, serviceOn
        


    def scan(self, option=None):
        retval = True
        messages = {'messages':[]}
        
        # check our current state - if not applicable this will raise an exception
        
        multiCPU, serviceOn = self._getCurrent()
        
        # we have 4 cases:
        #  cpu_count < 2  and irqbalance off   =  ok
        #  cpu_count < 2  and irqbalance on    =  turn irqbalance off
        #  cpu_count >=2  and irqbalance off   =  turn irqbalance on
        #  cpu_count >=2  and irqbalance on    =  ok
        
        
        if multiCPU == False:
            if serviceOn == False:
                msg = "Single CPU system - irqbalance is disabled"
            else:
                msg = "Single CPU system - irqbalance is ENABLED - should be disabled"
                messages['messages'] = msg
                retval = False
        else:
            if serviceOn == False:
                msg = "Multi CPU system - irqbalance is DISABLED - should be enabled"
                messages['messages'] = msg
                retval = False
            else:
                msg = "Multi CPU system - irqbalance is enabled"
        
        if retval:
            self.logger.info(self.module_name, msg)
        else:
            self.logger.warning(self.module_name, msg)            
        return retval, msg, messages   
 
    def apply(self, option=None):
        
        retval , msg, messages = self.scan(option)
        if retval == True:
            return False, msg, messages
        
        messages = {'messages':[]}
        changeRec = ""
        retval = False
        
        # if the scan failed then either turn irqbalance on (multiCPU==True) or off (MultiCPU==False)
        # remember to save the previous status so we can revert.  Remember also that the scan() method calls
        # _getCurrent(), which sets self._multiCPU
        if self._multiCPU:
            results = sb_utils.os.service.enable(self._service)
            if results != True:
                msg = "Unable to enable the '%s' service" % self._service
                self.logger.error(self.module_name, msg)
                messages['messages'].append(msg)
            else:
                changeRec = "%s|off" 
        else:
            results = sb_utils.os.service.disable(self._service)
            if results != True:
                msg = "Unable to disable the '%s' service" % self._service
                self.logger.error(self.module_name, msg)
                messages['messages'].append(msg)
            else:
                changeRec = "%s|on"        

        if changeRec:
            retval = True        
        return  retval,changeRec, messages
 
    def undo(self, change_record=None):

        msg = ""
        messages = {'messages':[]}
        
        service, previousState = change_record.split("|")
        if previousState == "on":
            results = sb_utils.os.service.enable(self._service)
            if results != True:
                msg = "Unable to enable the '%s' service" % self._service
                self.logger.error(self.module_name, msg)
                messages['messages'].append(msg)
        else:
            results = sb_utils.os.service.disable(self._service)
            if results != True:
                msg = "Unable to disable the '%s' service" % self._service
                self.logger.error(self.module_name, msg)
                messages['messages'].append(msg)

        if not msg:
            msg = "Previous status of '%s' restored" % self._service
            retval = True
            
        return retval, msg, messages
        

if __name__ == '__main__':
    TEST = DisableIrqbalance()
    print TEST.apply()
