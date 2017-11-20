#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

try:
    import cPickle as pickle
except ImportError:
    import pickle
import sys
import base64

sys.path.append("/usr/share/oslockdown")
from sb_utils.misc import TCSLogger
from sb_utils.misc import tcs_utils


class ModuleAggregate:
    """
    Agregates and calls modules. Requires module_name and module list in the
    following format:
    
    SampleList = [{'ModuleFilename': 'KernelModuleUpdate',
                  'ModuleName'    : 'KernelModuleUpdate',
                  'ModuleType'    : 'generic',
                  'ModuleParams'  : {'paramName1' : 'value1', \
                                     'paramName2' : 'value2'}},
                 {'ModuleFilename': 'IPForward',
                  'ModuleName'    : 'IPForward',
                  'ModuleType'    : 'specific',
                  'ModuleParams'  : {'paramName1' : 'value1', \
                                      'paramName2' : 'value2'}},}]
    """

    def __init__(self, module_name, module_list):
        self.module_name = module_name
        self.logger      = TCSLogger.TCSLogger.getInstance()
        self.module_list = self.__initialize_modules(module_list)


   ###########################################################################
    def __initialize_modules(self, list):
      """
      Returns a list of modules on which you can invoke analyze, apply and
      undo functions
      """
      instantiated_module_list = []
       
      for module in list:
         try:   
            if module['ModuleType'] == 'generic':
               exec ('from sb_utils.generic_modules import %s' % \
                                                    module['ModuleFilename'])
               
            elif module['ModuleType'] ==  'specific':
               exec ('from security_modules import %s' % \
                                                    module['ModuleFilename'])
               
            else:
               msg = 'FATAL ERROR, invalid module type: %s' % \
                                                    module['ModuleType']
               self.logger.log_err('Module init error: ' + msg)
               raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))            
         
         except ImportError:
            msg = 'Error Importing: %s' % module['ModuleFilename']   
            self.logger.log_err(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            
           
         paramList = module['ModuleParams'].values()
         paramList.reverse()
         paramString = str(paramList).lstrip('[').rstrip(']')
            
         try:
            # TODO: add some regex here to make this safer
            exec ('instantiated_module_list.append(%s.%s (%s))' %          \
                                             (module['ModuleFilename'],    \
                                              module['ModuleName'],        \
                                              paramString))
         except:
            msg = 'Error Initializing: %s' % module['ModuleFilename']   
            self.logger.log_err(self.module_name, msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
                
      return instantiated_module_list
    
    
    
   ###########################################################################
    def validate_input(self, options_list=None):
      """
      Validates the option list.
      """

      counter = 0
        
      for module in self.module_list:
         if not module.validate_input(options_list[counter]):
            return 1
         counter = counter + 1
      return 0
    
    
   ###########################################################################
    def scan(self, options_list=None):
      """
      Invoke analyze function on list of modules and agreggate results.
      """
      counter    = 0
      pass_flag  = True
      option_ok  = True
      error_list = []
        
      for module in self.module_list:
         if option_ok:
            try:
               value = options_list[counter]
               [result, err_msg] = module.scan(value)
            except TypeError:
               option_ok = False
               [result, err_msg] = module.scan()
         else:
            [result, err_msg] = module.scan()
            
         counter = counter + 1
         if result != 'Pass':
            pass_flag = False
            error_list.append(err_msg)
        
      if pass_flag:
         return 'Pass', ''
      else:
         return 'Fail', ', '.join(error_list)
            

   ###########################################################################
    def apply(self, options_list=None):
      """
      Invoke apply function on list of modules and agreggate action records.
      """
        
      counter    = 0
      pass_flag  = False
      option_ok  = True
      action_records = []
        
      for module in self.module_list:
         if option_ok:
            try:
               value = options_list[counter]
               [result, action_record] = module.apply(value)
            except TypeError:
               option_ok = False
               [result, action_record] = module.apply()
         else:
            [result, action_record] = module.apply()
            
         counter = counter + 1

         if result == 1:
            action_records.append(action_record)
            pass_flag = True
         else:
            action_records.append(None)
        
      if not pass_flag:
         return 0, ''
        
      act_record_string = base64.encodestring(pickle.dumps(action_records))
      return 1, act_record_string
        
    
   ###########################################################################
    def undo(self, action_records=None):
      """
      Undo previous changes.
      """
      action_records = pickle.loads(base64.decodestring(action_records))
      counter = -1
      #warning: due to nature of agreggator, there is no way to ensure
      #         atomic commits. Integrity can not be ensured.

      for module in self.module_list:
         counter += 1

         msg = "Processing change record: %s" % action_records[counter]
         self.logger.log_debug(module['ModuleFilename'], msg)

         if action_records[counter] == None or action_records[counter] == '':
            continue
         if not module.undo(action_records[counter]):
            msg = 'Error Undo: %s' % module['ModuleFilename']   
            self.logger.log_err(self.module_name, msg)
            return 0
      return 1


##############################################################################
#if __name__ == '__main__':
    ## Test Variables used, replace later with command line arguments
    #import pprint
 #
    #TestList = [{'ModuleFilename': 'KernelModuleUpdate',  
                 #'ModuleName'    : 'KernelModuleUpdate',
                 #'ModuleType'    : 'generic',
                 #'ModuleParams'  : {'param1' : 'net.ipv4.conf.all.rp_filter', 
                                    #'param2' : 1,
                                    #'param3' : 'RPFilter',
                                    #'param4' : 'Reverse Path Source Validation (all)',
                                    #'param5' :  True}},
                #{'ModuleFilename': 'KernelModuleUpdate',  
                 #'ModuleName'    : 'KernelModuleUpdate',
                 #'ModuleType'    : 'generic',
                 #'ModuleParams'  : {'param1' : 'net.ipv4.conf.default.rp_filter', 
                                    #'param2' : 1,
                                    #'param3' : 'RPFilter',
                                    #'param4' : 'Reverse Path Source Validation (default)', 
                                    #'param5' :  True}}]
    #pprint.pprint (TestList)
     #
    #
    #TESTOBJECT = ModuleAggregate('RPFilter', TestList)
    #print "Analysis result:            " + str(TESTOBJECT.scan())
    #apply_result = TESTOBJECT.apply()
    #print "Apply result:               " + str(apply_result)
    #print "Post-apply analysis result: " + str(TESTOBJECT.scan())
    #print "Undo result:                " + str(TESTOBJECT.undo(apply_result[1]))
    #print "Post-undo analysis result:  " + str(TESTOBJECT.scan())
