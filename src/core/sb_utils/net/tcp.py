#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Functions to perform operations on TCP Sockets
#

import socket
import sys

#sys.path.append('/usr/share/oslockdown')
#import TCSLogger
#import tcs_utils

#try:
#    logger = TCSLogger.TCSLogger.getInstance(6)
#except TCSLogger.SingletonException:
#    logger = TCSLogger.TCSLogger.getInstance()

class MyLogger :
    def __init__(self):
        pass
    def log_err(self,mod, msg):
        print >>sys.stderr, "%s (ERROR): %s" % (mod,msg)
    def log_debug(self,mod, msg):
        print >>sys.stderr, "%s (DEBUG): %s" % (mod,msg)
    
logger = MyLogger()

MODULE_NAME = "Net.Tcp"

##############################################################################
def isAbleToConnect(host='127.0.0.1', tcpPort=None, showText=False):
    """Try to connect to a TCP port"""

    if tcpPort == None or type(tcpPort).__name__ != 'int':
        return None

    retVal = False
    try:
        res = socket.getaddrinfo(host, tcpPort, socket.AF_UNSPEC, socket.SOCK_STREAM )
    except socket.gaierror, (errCode, errMsg):
        if showText:
            if int(errCode) == -2:
                logger.log_err(MODULE_NAME, "Unable to resolve name '%s'" % host)
            logger.log_debug(MODULE_NAME, repr(errMsg))
        return None
    except Exception, errMsg:
        if showText:
            logger.log_debug(MODULE_NAME, repr(errMsg))
        return None
        
    for testSocket in res:
        try:
            af, socktype, proto, canonname, sa = testSocket 
        except ValueError:
            continue

        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, errMsg:
            if showText:
                logger.log_debug(MODULE_NAME, repr(errMsg))
            continue
        except Exception, errMsg:
            if showText:
                logger.log_debug(MODULE_NAME, repr(errMsg))
            continue

        try:
            s.connect(sa)
            #s.settimeout(1.0)
        except socket.error, (errCode, errMsg):
            msg = "Unable to connect to TCP Port %s:%s - Error %s: %s" % (host, tcpPort, errCode, errMsg)
            if showText:
                logger.log_debug(MODULE_NAME, msg)
            s.close()
            continue

        msg = "Connected to TCP Port %s:%s" % (host, tcpPort)
        if showText:
            logger.log_debug(MODULE_NAME, msg)
        s.close()
        retVal = True
        break

    return retVal
##############################################################################

