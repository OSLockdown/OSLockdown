#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

try:
   import cPickle as pickle
except:
   import pickle
import sys
import zlib
import os.path
import shutil

sys.path.append("/usr/share/oslockdown")

#
# TODO: implement logger functionality, implement UID/GID and perms storage
#

import sb_utils.SELinux
from sb_utils.misc.TCSLogger import TCSLogger
from sb_utils.misc import tcs_utils

# TODO: cleanup and exception handling

class TemplateStore:
   """
   Storage class for various files and templates.
   """

   def __init__(self):
      self.backupEnabled     = True
      self.__filestore_path = '/usr/share/oslockdown/sb_utils/file/store.dat'
      self.__logger          = TCSLogger.getInstance()
      self.__filestore       = self.__initialize_filestore()


   def __initialize_filestore(self):
      """
      Initialize the filestore
      """
      
      if not os.path.exists(self.__filestore_path):
         self.__create_empty_filestore()
        
      try:
         file_obj = open(self.__filestore_path, 'r')
      except:
         msg = 'FATAL ERROR: error opening filestore'
         self.__logger.log_err('Filestore engine error: ' + msg)
         raise tcs_utils.ActionError(msg)
        
      try:
         object = pickle.loads(zlib.decompress(file_obj.read()))
         file_obj.close()

      except:
         # Corrupted datastore, recreating
         msg = 'ERROR: corrupted filestore detected, creating new filestore'
         self.__logger.log_err('Filestore engine error: ' + msg)
         self.__create_empty_filestore()
         object = {}
            
      return object
        
   def __create_empty_filestore(self):
      """
      Create an empty filestore
      """
      #Ensure our filestore has the correct permissions
      os.umask(077)
        
      if os.path.exists(self.__filestore_path):
         os.unlink(self.__filestore_path)
        
      try:
         file_obj = open(self.__filestore_path, 'w')
      except:
         msg = 'FATAL ERROR: error creating template filestore'
         self.__logger.log_err('TemplateStore ' , msg)
         raise tcs_utils.ActionError(msg)
            
      emptyDict = {}
      objectStr = zlib.compress(pickle.dumps(emptyDict))
      file_obj.truncate()
      file_obj.write(objectStr)
      file_obj.close()
            
        
   def read_from_path (self, file_path):
      """
      Read in data into data store from file system
      """
        
      origfile = open(file_path, 'r')
      self.add_to_filestore(file_path, origfile.read())
      origfile.close()

   def __update(self):
      """
      Update the datastore file
      """
      objectStr = zlib.compress(pickle.dumps(self.__filestore))

      file_obj = open(self.__filestore_path, 'w')
      file_obj.truncate()
      file_obj.write(objectStr)
      file_obj.close()
        
   def write_to_path (self, file_path):
      """
      Read in data into data store from file system
      """
        
      # Check if file exists and backup
      if os.path.exists(file_path) and self.backupEnabled:
         shutil.copy2(file_path, file_path + '.backup')
         shutil.copymode(file_path, file_path + '.backup')
         sb_utils.SELinux.restoreSecurityContext(file_path + '.backup')
         os.unlink(file_path)
           
      newfile = open(file_path, 'w')
      newfile.write(self.read_from_filestore(file_path))
      newfile.close()
        
   def delete_from_filestore(self, file_path):
      """
      Delete specified file from filestore
      """
        
      if self.__filestore.has_key(file_path):
         del self.__filestore[file_path]
         self.__update()
         return True
        
      return False
        
        
   def add_to_filestore(self, file_path, contents):
      """
      Add string to filestore, using destination path as key for data access
      """
        
      try:
         file_obj = open(self.__filestore_path, 'w+')
      except:
         print 'FATAL ERROR: error initializing template filestore'
         sys.exit(1)
        
      self.__filestore[file_path] = contents
      file_obj.close()
      self.__update()
    
   def read_from_filestore(self, file_path):
      """
      Read string from filestore, using destination path as key for
      data access
      """
      if not self.has_key(file_path):
         return None
      return self.__filestore[file_path]
    
   def list_files(self):
      """
      List contents of filestore
      """
        
      return self.__filestore.keys()
   
   def has_key(self, file_path):
      """
      Returns true if datastore contains specified file, else False
      """
      
      return self.__filestore.has_key(file_path)



if __name__ == '__main__':
   # Test Variables used, replace later with command line arguments
    
   sampleFilePath = '/etc/sysctl.conf' 
   sampleFile     = """
   # Created by OSLockdown\n"
   # Kernel sysctl configuration file for Red Hat Linux
   #
   # For binary values, 0 is disabled, 1 is enabled.See sysctl(8) and
   # sysctl.conf(5) for more details
    
   # Controls IP packet forwarding
   net.ipv4.ip_forward = 0
    
   # Controls source route verification
   net.ipv4.conf.default.rp_filter = 1
    
   # Do not accept source routing
   net.ipv4.conf.default.accept_source_route = 0
    
   # Controls the System Request debugging functionality of the kernel
   kernel.sysrq = 0
    
   # Controls whether core dumps will append the PID to the core filename
   # Useful for debugging multi-threaded applications
   kernel.core_uses_pid = 1
    
   # Controls the use of TCP syncookies
   net.ipv4.tcp_syncookies = 1
    
   # Controls the maximum size of a message, in bytes
   kernel.msgmnb = 65536
    
   # Controls the default maxmimum size of a mesage queue
   kernel.shmmax = 4294967295
    
   # Controls the maximum number of shared memory segments, in pages
   kernel.shmall = 268435456
   """
        
   testobj = TemplateStore()
   print 'Contents of filestore: ', str(testobj.list_files())
   print 'Adding contents to filestore: '
   testobj.add_to_filestore(sampleFilePath, sampleFile)
   print 'Contents of filestore: ', str(testobj.list_files())
