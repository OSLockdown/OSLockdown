#!/usr/bin/env python
#############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

import sys
import os
import datetime
import shutil

sys.path.append('/usr/share/oslockdown')
import sbProps
import sb_utils.SELinux

# Singleton implementation courtesy of Gary Robinson
## By Gary Robinson, grobinson@transpose.com. No rights reserved -- 
## placed in the public domain -- which is only reasonable considering
## how much it owes to other people's version which are in the
## public domain. The idea of using a metaclass came from 
## a  comment on Gary's blog (see 
## http://www.garyrobinson.net/2004/03/python_singleto.html#comments). 
## Other improvements came from comments and email from other
## people who saw it online. (See the blog post and comments
## for further credits.)

class SingletonException(Exception):
    pass

class MetaSingleton(type):
    def __new__(metaclass, strName, tupBases, dict):
        if dict.has_key('__new__'):
            raise SingletonException, 'Can not override __new__ in a Singleton'
        return super(MetaSingleton, metaclass).__new__(metaclass, strName, 
                                                       tupBases, dict)
        
    def __call__(cls, *lstArgs, **dictArgs):
        raise SingletonException, 'Singletons may only be instantiated through getInstance()'
        
class Singleton(object):
    __metaclass__ = MetaSingleton
    
    def getInstance(cls, *lstArgs):
        """
        Call this to instantiate an instance or retrieve the existing instance.
        If the singleton requires args to be instantiated, include them the first
        time you call getInstance.        
        """
        if cls._isInstantiated():
            if len(lstArgs) != 0:
                raise SingletonException, 'If no supplied args, singleton must already be instantiated, or __init__ must require no args'
        else:
            if cls._getConstructionArgCountNotCountingSelf() > 0 and len(lstArgs) <= 0:
                raise SingletonException, 'If the singleton requires __init__ args, supply them on first instantiation'
            instance = cls.__new__(cls)
            instance.__init__(*lstArgs)
            cls.cInstance = instance
        return cls.cInstance
    getInstance = classmethod(getInstance)
    

    def _isInstantiated(cls):
        return hasattr(cls, 'cInstance')
    _isInstantiated = classmethod(_isInstantiated)  


    def _getConstructionArgCountNotCountingSelf(cls):
        return cls.__init__.im_func.func_code.co_argcount - 1
    _getConstructionArgCountNotCountingSelf = classmethod(_getConstructionArgCountNotCountingSelf)


    def _forgetClassInstanceReferenceForTesting(cls):
        """
        This is designed for convenience in testing -- sometimes you 
        want to get rid of a singleton during test code to see what
        happens when you call getInstance() under a new situation.
        
        To really delete the object, all external references to it
        also need to be deleted.
        """
        try:
            delattr(cls,'cInstance')
        except AttributeError:
            # run up the chain of base classes until we find the one that has 
            # the instance and then delete it there
            for baseClass in cls.__bases__: 
                if issubclass(baseClass, Singleton):
                    baseClass._forgetClassInstanceReferenceForTesting()
    _forgetClassInstanceReferenceForTesting = classmethod(_forgetClassInstanceReferenceForTesting)


###############################################################################
class TCSLogger(Singleton):
    """
    The TCSLogger class provides an interface for operation logging.
    """
    def __init__(self, *myargs):
        super(TCSLogger, self).__init__()
        self._log_filename = sbProps.SB_LOG
        self._modName = ""
        self.messages = []
        self.messageError = None
        
        import time
        if '-z' in sys.argv:
            # ok, we're in shim mode - so *all* output is to /dev/stdout
            self._fileobj = sys.stdout
            self._log_level = 7   # default log level
        
        else:
            # ok, writing to a *regular* file - so check for rotate and all that jazz...
            if len(myargs) > 0:
                self._log_level = myargs[0]
            else:
                self._log_level = 4   # default log level
        
        
            ####################################
            # Rotate log file if it is too big.
            ####################################
            set_context = False
            if os.path.isfile(self._log_filename):
                try:
                    statinfo = os.stat(self._log_filename)
                    if statinfo.st_size > sbProps.SB_LOG_MAX:
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%Y%m%d_%H%M%S")
                        new_log_file = "%s-%s" % (self._log_filename, timestamp) 
                        del statinfo
                        shutil.copy2(self._log_filename, new_log_file)
                        sb_utils.SELinux.restoreSecurityContext(new_log_file)
                        os.unlink(self._log_filename)
                        set_context = True
                except:
                    pass
            else:
                set_context = True                                                   
            try:
                self._fileobj = open(self._log_filename, 'a')
            except:
                # Unable to open the log file so fall back to stdout
                self._fileobj = sys.stdout

            if set_context:
                sb_utils.SELinux.restoreSecurityContext(self._log_filename)
                set_context = False    

    def force_log_level(self, newloglevel):
        self._log_level = newloglevel
        self._log_write("INFO", 'TCSLogger', "Log level reset to %d" % newloglevel)
        
    def _get_timestamp(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y %b %d %H:%M:%S")
        return timestamp



    def _log_write(self, level, name, msg):
        # "2007 May 16 3:33:14 [ConfigManager] message"

        if self._modName and name != self._modName:
            line = "%s [%s|%s] %s: %s" % (self._get_timestamp(), self._modName, name, level, msg)
        else:
            line = "%s [%s] %s: %s" % (self._get_timestamp(), name, level, msg)

        try:
            self._fileobj.write('%s\n' % line)
            self._fileobj.flush()
        except:
            print line

    def inModule(self, modName):
        # Designed to add Module Name to caller's Name *if* not already there
        # This should help with tracking down *where* a utility message
        # actually came from when doing searches from GUI
        # If name is None, then we assume we're outside of a Module now.
        
        self._modName =  modName

        #clear module messages *if* we were passed a valid module name (IE - not blank/null)
        if modName:
            self.messages = []
            self.messageError = None
            
    def moduleMessage(self, message):
        # if we haven't had an error with the message list and we're in a module, 
        print >>sys.stderr,"ERROR=%s ModName='%s' MSG = %s" % (self.messageError, self._modName,message)
        if not self.messageError and self._modName:
            try:
                self.messages.append(message)
            except Exception, err:
                self.messageError = str(err)
        
    def getMessages(self):
        return self.messages, self.messageError
        
    ###############################
    ####### Logging Levels ########
    ###############################
    def critical(self, name, msg):
        if self._log_level >= 1:
            self._log_write("CRITICAL", name, msg)
            
    def error(self, name, msg):
        if self._log_level >= 2:
            self._log_write("ERROR", name, msg)

    def warning(self, name, msg):
        if self._log_level >= 3:
            self._log_write("WARNING", name, msg)

    def notice(self, name, msg):
        if self._log_level >= 4:
            self._log_write("NOTICE", name, msg)

    def info(self, name, msg):
        if self._log_level >= 5:
            self._log_write("INFO", name, msg)

    def debug(self, name, msg):
        if self._log_level >= 6:
            self._log_write("DEBUG", name, msg)


    # Older method names were confusing and are being phased out
    def log_crit(self, name, msg):   self.critical(name, msg)
    def log_err(self, name, msg):    self.error(name, msg)
    def log_warn(self, name, msg):   self.warning(name, msg)
    def log_notice(self, name, msg): self.notice(name, msg)
    def log_info(self, name, msg):   self.info(name, msg)
    def log_debug(self, name, msg):  self.debug(name, msg)

    def warn(self, name, msg):   self.warning(name, msg)

    # DEVELOPMENT ONLY - WRITE TO STDOUT AT DEBUG
    def forceToStdout(self):
        self.force_log_level(7)
        self._fileobj = sys.stdout

