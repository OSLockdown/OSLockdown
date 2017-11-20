#!/usr/bin/env python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import os
import popen2
import shutil
import datetime
import sys
import time
import signal
import shlex
import fcntl 
import select

sys.path.append("/usr/share/oslockdown")
import TCSLogger
import sb_utils.SELinux
import sbProps

class ScanError(Exception): pass
class ScanNotApplicable(Exception): pass
class ActionError(Exception): pass
class ManualActionReqd(Exception): pass
class OSNotApplicable(Exception): pass
class ZoneNotApplicable(Exception): pass
class ModuleNotAvail(Exception): pass
class ModuleUnsupported(Exception): pass
class AbortProfile(Exception): pass

APPLICATION_DATA_DIR = '/var/lib/oslockdown'
FS_DATA_DIR = APPLICATION_DATA_DIR + '/fs-scan'

MODULE_NAME = "sb_utils.misc.tcs_utils"

##############################################################################
def packObjectIntoString(object):
    """
    Pack specified object into string using cPickle and base64
    """
    try:
        import cPickle as pickle
    except:
        import pickle

    from zlib import compress
    try:
        from base64 import b64encode
    
        return b64encode(compress(pickle.dumps(object)))
    except:
        # Fix for RHEL4
        
        from base64 import encodestring
        
        return encodestring(compress(pickle.dumps(object)))
    
##############################################################################
def extractFromString(obj_string):
    """
    Returns object extracted from provided string
    """
    try:
        import cPickle as pickle
    except:
        import pickle

    from zlib import decompress
    try:
        # For RHEL 5
        from base64 import b64decode
    except:
        # For RHEL 4
        from base64 import decodestring as b64decode
    return pickle.loads(decompress(b64decode(obj_string)))


##############################################################################
class TCSException(Exception):
    """
    Extended Exception class for use within the application.  It is intended
    to facilitate inclusion of more information regarding the reason for the
    exception and what action was being performed when the exception occurred.
    """
    def __init__(self, val, message):
        self.err_val = val
        self.message = message
    def __str__(self):
        return self.message

##############################################################################
# Command execution
def tcs_run_cmd_legacy(cmd, capture_err = False, cmdTimeout=15):
    """
    Run a command and capture the return value, command output, and optionally
    the stderr produced by running the command.  The function returns a tuple
    of (return_value, command_output, stderr).
    """

    try:
        logger = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance() 

    if not cmd.startswith('/sbin/ifconfig'):
        msg = "Executing: %s" % cmd.__repr__()
        logger.log_info('ExecuteCommand', msg)

    output = ""
    child_out = []
    start_t = time.time()
    try:
        process = popen2.Popen3(cmd, capture_err)
        status = process.poll()
        while status < 0:
            status = process.poll()
            try:
                if process.fromchild:
                    child_out.append(process.fromchild.read())
            except Exception:
                pass

            if time.time() - start_t > cmdTimeout:
                msg = "%d second timeout. Aborting: %s" % (cmdTimeout, cmd)
                logger.critical('ExecuteCommand', msg)
                msg = "Sending SIGTERM to pid %d..." % process.pid
                logger.critical('ExecuteCommand', msg)
                os.kill(process.pid, signal.SIGTERM)
                status = -1
                break
            if sbProps.ABORT_REQUESTED == True :
                msg = "ABORT REQUESTED : %s" % (cmd)
                logger.critical('ExecuteCommand', msg)
                msg = "Sending SIGTERM to pid %d..." % process.pid
                logger.critical('ExecuteCommand', msg)
                os.kill(process.pid, signal.SIGTERM)
                status = -1
                break

    except KeyboardInterrupt:
        msg = "Keyboard Interrupt caught - aborting: %s" % cmd
        logger.critical('ExecuteCommand', msg)
        status = -1

    except Exception, err:
        msg = "Command error: %s" % err
        logger.error('ExecuteCommand', msg)
        status = -1

    
    # Capture stdout - Make sure there is no more output from the command
    output = ''.join(child_out)
    if process.fromchild:
        child_out.append(process.fromchild.read())
        output = ''.join(child_out)
    process.fromchild.close()

    # Capture stderr
    if process.childerr:
        err = process.childerr.read()
        process.childerr.close()
    else:
        err = ""

    ret = -1
    if os.WIFEXITED(status):
        ret = os.WEXITSTATUS(status)

    #if status != -1:
        #delta = (time.time()-start_t)*1000
        #msg = "Executed command in %0.3f milleseconds and captured %d bytes "\
              #"from stdout" % (delta, len(output))
        #logger.log_debug('ExecuteCommand', msg)

    del child_out
    del logger

    return (ret, output, err)


##############################################################################
# Command execution - rewrote tcs_run_cmd to use select for doing non-blocks
#      input/timeout checks

def tcs_run_cmd(cmd, capture_err = False, cmdTimeout=15):
    """
    Run a command and capture the return value, command output, and optionally
    the stderr produced by running the command.  The function returns a tuple
    of (return_value, command_output, stderr).
    """

    routineName = "tcs_run_cmd"
    try:
        logger = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance() 

    if not cmd.startswith('/sbin/ifconfig'):
        msg = "Executing: %s" % cmd.__repr__()
        logger.log_info(routineName, msg)
        logger.debug (routineName, "STDERR capture = %s, cmdTimeout = %d" % (capture_err, cmdTimeout))

    output = ""
    child_out = []
    child_out_len = 0
    child_err = []
    child_err_len = 0
    output_str = ""
    err_str = ""
    deltaTime=0
    start_t = time.time()
    try:
        process = popen2.Popen3(cmd, capture_err)
        # mark non-blocking

        flags = fcntl.fcntl(process.fromchild.fileno(), fcntl.F_GETFL)
        fcntl.fcntl(process.fromchild.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

        if (capture_err):
            flags = fcntl.fcntl(process.childerr.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(process.childerr.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        EOF_FOUND=False
        lastTick = -1
        tickInterval = 30
        while not EOF_FOUND:

            deltaTime = int(time.time() - start_t)
            thisTick = int(deltaTime / tickInterval)
            if thisTick > lastTick:
                lastTick = thisTick
                logger.debug (routineName, "Time remaining = %d -> Total read = %d %d" % ( (cmdTimeout - deltaTime),child_out_len, child_err_len ))
            

            readFrom = [ process.fromchild.fileno()]
            if capture_err:
                readFrom.append(process.childerr.fileno())
            ret = select.select(readFrom, [], [], 1)

            try:
                if process.fromchild.fileno() in ret[0]:
                    buf = process.fromchild.read()
                    buflen = len(buf)
                    if buflen == 0:
                        EOF_FOUND=True
                    elif buflen>0:
                        child_out_len = child_out_len + buflen
                    child_out.append(buf)
                    logger.debug (routineName,'Read %d bytes from process STDOUT' % buflen)
            except Exception:
                pass


            try:
                if capture_err and process.childerr.fileno() in ret[1]:
                    buf=process.childerr.read()
                    buflen = len(buf)
                    if buflen == 0:
                        EOF_FOUND=True
                    elif buflen>0:
                        child_err_len = child_err_len + buflen
                    child_err.append(buf)
                    logger.debug (routineName,'Read %d bytes from process STDERR' % len(buf))
            except Exception:
                pass

            if deltaTime > cmdTimeout:
                msg = "%d second timeout. Aborting: %s" % (cmdTimeout, cmd)
                logger.critical('ExecuteCommand', msg)
                msg = "Sending SIGTERM to pid %d..." % process.pid
                logger.critical('ExecuteCommand', msg)
                os.kill(process.pid, signal.SIGTERM)
                status = -1
                break
            if sbProps.ABORT_REQUESTED == True :
                msg = "ABORT REQUESTED : %s" % (cmd)
                logger.critical('ExecuteCommand', msg)
                msg = "Sending SIGTERM to pid %d..." % process.pid
                logger.critical('ExecuteCommand', msg)
                os.kill(process.pid, signal.SIGTERM)
                status = -1
                break
            
    except KeyboardInterrupt:
        msg = "Keyboard Interrupt caught - aborting: %s" % cmd
        logger.critical('ExecuteCommand', msg)
        status = -1

    except Exception, err:
        msg = "Command error: %s" % err
        logger.error('ExecuteCommand', msg)
        status = -1

    
    # Capture stdout - Make sure there is no more output from the command
    try:
        if process.fromchild.fileno() in ret[0]:
            child_out.append(process.fromchild.read())
        process.fromchild.close()
        output_str = ''.join(child_out)
    except Exception:
        pass

    # Capture stderr
    try:
        if process.childerr.fileno() in ret[1]:
            child_err.append(process.childerr.read())
            process.childerr.close()
        err_str = ''.join(child_err)
    except Exception:
        pass

    ret = -1

    # ok, we may have the end of output before the subprocess finished
    # wait 1/10 second up to 3 times before reporting a problem
    
    waitForExit = 3
    while waitForExit > 0 :
        status = process.poll()
        if os.WIFEXITED(status):
            ret = os.WEXITSTATUS(status)
            break
        waitForExit = waitForExit - 1
        time.sleep(0.1)

    #if status != -1:
        #delta = (time.time()-start_t)*1000
        #msg = "Executed command in %0.3f milleseconds and captured %d bytes "\
              #"from stdout" % (delta, len(output))
        #logger.log_debug('ExecuteCommand', msg)

    logger.debug (routineName, "Completed status = %d ->ReqTime %s  Total read = %d %d" % (ret,deltaTime,child_out_len, child_err_len ))
    return (ret, output_str, err_str)



##############################################################################
def octal_perms(filepath):
    """
    Provided with a path to a file, return the permissions in octal format.
    """
    return oct(os.lstat(filepath).st_mode & 0777)

##############################################################################
def return_owner_uid(filepath):
    """
    Provided with a path to a file, return the file owner's uid
    """
    return os.lstat(filepath).st_uid

##############################################################################
def return_owner_gid(filepath):
    """
    Provided with a path to a file, return the file owner's gid
    """
    return os.lstat(filepath).st_gid

##############################################################################
def load_module(module_name):
    """
    Given a name of a module import the module and create an instance
    of the class in the module.  Returns the class object.
    Will raise ImportError if the import of the module name fails.
    """
    # Make sure the module_name does not contain any extraneous characters
    module_to_import = module_name
    if module_name.count('"') != 0:
        newstr = module_to_import.replace('"', '')
        module_to_import = newstr
    if module_name.count("'") != 0:
        newstr = module_to_import.replace("'", '')
        module_to_import = newstr
    try:
        if '/usr/share/oslockdown/security_modules' not in sys.path:
            sys.path.append('/usr/share/oslockdown/security_modules')
        module = __import__(module_to_import)
    except ImportError, err:
        raise Exception("Unable to import module %s" % module_to_import)
    methodlist = [method for method in dir(module) if callable(getattr(module,
                  method))]
    if len(methodlist) != 1:
        raise Exception("no method found")
    return vars(module)[methodlist[0]]

##############################################################################
def generate_diff_record(fromfilename, tofilename):
    """
    Generate a string containing a unified diff between the specified files.
    We'll generate the diff record, and overwrite "fromfilename" with "tofilename",
    preserving ownership and DAC information (eventually MAC as well), then remove
    "tofilename" so the individual modules do not have to.
    """

    # import when we get called to avoid loops
    import sb_utils.acctmgt.acctfiles
    action_record = ""
    cmd = "/usr/bin/diff -ur " + fromfilename + ' ' + tofilename
    out = tcs_run_cmd(cmd, True)
    if out[0] == 2:
        msg = "ERROR: Unable to generate diff record."
        raise ActionError(msg)
    elif out[0] == 1:
        action_record = out[1]

    return action_record

def _dumpPatchLines(patchFile, patchLines):
    trash = open(patchFile,"w")
    for line in patchLines:
        trash.write(line + "\n")
    trash.close()
    
##############################################################################
def apply_patch(change_record):
    """
    Apply a patch using the system's patch command.
    This function is intended to be used with a module's undo
    method. Solaris and Linux patch commands are different
    """
    import sb_utils.os.info
    
    # import when we get called to avoid loops
    import sb_utils.acctmgt.acctfiles

    try:
        logger = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance() 


    workfile = "/tmp/.trash"

    if not change_record:
        msg = "Can apply patch for undo without a change record"
        raise ActionError(msg)

    try:
        tmp_file = open(workfile, 'w').write("")
    except IOError, err:
        msg = 'Unable to create temporary file: %s' % str(err)
        raise ActionError(msg)

    if sb_utils.os.info.is_solaris() == True:
        patchCmd = "/usr/bin/patch -p0 -s < "
    else:
        patchCmd = "/usr/bin/patch -p0 -t -s < "
    patch_targets, remainder = split_patches(change_record)
    logger.warn("APPLYPATCHES","Found %d patchentries" % len(patch_targets))
    for target in patch_targets.keys():
        
        logger.warn("APPLYPATCHES","-- Apply patch for '%s'" % target)
        _dumpPatchLines(workfile, patch_targets[target])
        _dumpPatchLines("/tmp/.trash_%s" % os.path.basename(target), patch_targets[target])
        cmd = patchCmd + workfile
        ret = tcs_run_cmd(cmd, True)
        if ret[0] != 0:
            msg = 'Unable to use patch command: %s' % ret[2]
            raise ActionError(msg)
        sb_utils.SELinux.restoreSecurityContext(target)
    try:
        os.unlink(workfile)
    except Exception:
        pass
    return 1

    

def split_patches(rawtext=""):
    """
    Given a text string, assume that all patch data ('unified diff' output from the
    'diff -ru' command) is at the begining, with possible extra data contained afterwards.
    Split string into lines, and see if there is a patch entry starting at the first line.
    If it does look like a patch file, extract the *entire* patch for that file and add it
    to a dictionary (key is the name of the file being patched).  Rinse and repeat.  If the
    line does not appear to be a patch (for whatever reason), create a new string from that point
    one.  Return a tuple of the dictionary and this string.
    We're reraising any exception just so we have a scaffold if we'd like to 
    try and handle them ourselves later.  
    """
    linenum        = 0
    raw_lines      = rawtext.splitlines()
    patches        = {}
    remaining_text = ""
   
    # Patch format (so far as we're concerned)
    # each *segment* starts with '@@'
    # each *file* starts with '---'
    # ignore all other lines.  We do some sanity checking for each *file* start.
    try:
        in_patch = True
        segments = 0
        
        while linenum < len(raw_lines)-2 and in_patch:
#            print "Linenum is %d of %d" % (linenum, len(raw_lines))
#            print "\t\t"
#            print "%d -> %s" % (linenum,raw_lines[linenum])
#            print "%d -> %s" % (linenum+1,raw_lines[linenum+1])
#            print "%d -> %s" % (linenum+2,raw_lines[linenum+2])

            if raw_lines[linenum].startswith('--- ') and \
                        raw_lines[linenum+1].startswith('+++ ') :

                patchline = linenum+2
                segments = 0
                while in_patch and patchline < len(raw_lines) and raw_lines[patchline].startswith('@@ '):
                    segments = segments + 1
                    fields = raw_lines[patchline].split()
                    
                    # if we're not a patch then bail - should be regular text behind us
                    if len(fields) != 4:
                        in_patch = False
                        break
                    else:
                        firsthunk = 1
                        secondhunk = 1
                        if fields[1].find(',')>0:
                            firsthunk = int(fields[1].split(',')[1])
                        if fields[2].find(',')>0:
                            secondhunk = int(fields[2].split(',')[1])
                        
                        patchline = patchline + 1
                        
                        while patchline < len(raw_lines) and (firsthunk > 0 or secondhunk > 0):
                            if raw_lines[patchline][0] == ' ':
                                firsthunk = firsthunk - 1
                                secondhunk = secondhunk -1
                            elif raw_lines[patchline][0] == '+':
                                secondhunk = secondhunk -1
                            elif raw_lines[patchline][0] == '-':
                                firsthunk = firsthunk -1
#                            print "line %d   first = %d  second = %d" % (patchline,firsthunk,secondhunk)
                            patchline = patchline + 1
                            
                        if firsthunk == 0 and secondhunk == 0:
                            patchlen = patchline - linenum
            else:
                linenum = linenum + 1
                continue
            if patchlen > 0:
                target = raw_lines[linenum+1][4:].split('\t')[0]
#                print "%s had %d segments" % (target, segments)
                patches[target] = raw_lines[linenum: patchline]
                linenum = patchline
        remaining_text = ''.join(raw_lines[linenum:])
    except Exception, e:
        raise
#    print "Last line is %d -> %s" %(linenum, raw_lines[linenum])      
    return patches, remaining_text    
    

##############################################################################
def protect_file(pathname):
    """
    Check to see if a copy has been made for the specified file in the
    application's backup directory.  If the file exist then do nothing.
    Otherwise, make a copy of the file.
    """
    # Make sure the source file exist
    statinfo = None
    try:
        statinfo = os.lstat(pathname)
    except OSError:
        return
    if not statinfo:
        return

    # Check to see if it has already been backed up
    statinfo = None
    try:
        statinfo = os.lstat(APPLICATION_DATA_DIR + '/backup' + pathname)
    except OSError:
        pass
    if statinfo:
        return

    dirpath = os.path.dirname(APPLICATION_DATA_DIR + '/backup' + pathname)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
        shutil.copy2(pathname, APPLICATION_DATA_DIR + '/backup' + pathname)
        sb_utils.SELinux.restoreSecurityContext(APPLICATION_DATA_DIR + '/backup' + pathname)
    return

##############################################################################
def get_timestamp():
    """
    Returns a string containing the current date and time in the following
    format %Y %b %d %H:%M:%S.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y %b %d %H:%M:%S")
    return timestamp

##############################################################################
# Update token for new system scan
def update_sys_scanid():
    """
    Update the token on disk for a new system scan.
    """
    sys_scan_path = APPLICATION_DATA_DIR + '/sys-scanid'
    if os.path.exists(sys_scan_path):
        # get existing token
        old_token = get_sys_scanid()
        new_token = old_token + 1
    else:
        new_token = 1

    token_file = open(sys_scan_path, 'w')
    line = "%s" % new_token
    token_file.write(line)
    token_file.close()

    return

##############################################################################
# Retrieve token for current system scan
def get_sys_scanid():
    """
    Retrieve the token on disk representing the latest system scan.
    """
    sys_scan_path = APPLICATION_DATA_DIR + '/sys-scanid'

    # return 0, if the file doesn't exist
    if not os.path.exists(sys_scan_path):
        return 0

    token_file = open(sys_scan_path, 'r')
    lines = token_file.readlines()
    token_file.close()
    version = int(lines[0])
    return version

##############################################################################
# Check fs-scan token to determine if a new fs scan is needed
def fs_scan_is_needed():
    """
    Check if fs token is equal to the system scan token.
    """
    scanid_file = FS_DATA_DIR + '/fs-scanid'
    if not os.path.exists(scanid_file):
        return True

    fs_token = get_fs_scanid()
    sys_token = get_sys_scanid()

    if fs_token != sys_token:
        return True
    return False

##############################################################################
# Update fs-scan token to current system scan token
def update_fs_scanid():
    """
    Update the token on disk for a new fs scan.
    """
    fs_scan_path = FS_DATA_DIR + '/fs-scanid'
    # get the latest system scan token
    sys_token = get_sys_scanid()

    token_file = open(fs_scan_path, 'w')
    line = "%s" % sys_token
    token_file.write(line)
    token_file.close()

    return

##############################################################################
# Retrieve fs-scan token
def get_fs_scanid():
    """
    Retrieve the token on disk representing the latest fs scan.
    """
    fs_scan_path = FS_DATA_DIR + '/fs-scanid'

    # return 0, if the file doesn't exist
    if not os.path.exists(fs_scan_path):
        return 0

    token_file = open(fs_scan_path, 'r')
    lines = token_file.readlines()
    token_file.close()
    version = int(lines[0])
    return version


from xml.sax import make_parser, SAXException 
from xml.sax.handler import ContentHandler


##############################################################################
#a little SAX parser helper to get the a particular attr from a particular section of an xml
class GetXmlAttr(ContentHandler):
    def  __init__(self, section, attr):
        self.attr_value = None
        self.section = section
        self.attr = attr
    def startElement(self, name, attrs):
        if name == self.section :
            self.attr_value = attrs.get(self.attr).strip()
            raise SAXException("Found")

    def endElement(self, name):
        return

    def characters(self, chars):
        return

    def return_value(self):
        return self.attr_value

##############################################################################
def find_xml_attr(name=None, section=None, attr=None):
    if not name or not section or not attr:
        return None

    handler = GetXmlAttr(section, attr)
    parser = make_parser()
    parser.setContentHandler(handler)
    try:
        parser.parse(open(name))

    except SAXException:
        return handler.return_value()

    return None


##############################################################################
def validateXML(xmlDoc=None, xmlSchema=None):
    """
    Validate XML document against given schema (.xsd)
    """
    
    if xmlDoc == None or xmlSchema == None:
        return None

    try:
        import libxml2
    except ImportError:
        return None

    try:
        ctxt = libxml2.schemaNewParserCtxt(xmlSchema)
        schema = ctxt.schemaParse()
        del ctxt
        
        validationCtxt = schema.schemaNewValidCtxt()
        doc = libxml2.parseFile(xmlDoc)
        
        instance_Err = validationCtxt.schemaValidateDoc(doc)
        del validationCtxt
        del schema
        doc.freeDoc()

    except Exception, err:
        return None

    if instance_Err != 0:
        return False
    else:
        return True

##############################################################################
def transformXML(xmlDoc=None, output=None, xslFile=None):
    """
    Transform xmlDoc to "output" using xslFile
    """

    try:
        logger = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance() 

    if xmlDoc == None or output == None or xslFile == None:
        return False

    try:
        import libxml2
    except ImportError, err:
        logger.error('transformXML', err)
        print >>sys.stderr,str(err)
        return False

    try:
        import libxslt
    except ImportError, err:
        logger.error('transformXML', err)
        msg = "You must install the 'libxslt-python' (Solaris 'SUNWlxsl-python') "\
              "package in order to generate text reports from the command line." 
        print >>sys.stderr,(msg)
	logger.error('transformXML', msg)
        return False

        
    try:
        styledoc = libxml2.parseFile(xslFile)
        style = libxslt.parseStylesheetDoc(styledoc)
        doc = libxml2.parseFile(xmlDoc)
        result = style.applyStylesheet(doc, None)
        style.saveResultToFilename(output, result, 0)
        style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()
    except Exception, err:
        logger.error('transformXML', err)
        print >>sys.stderr,"Unable to render report.\nSee /var/lib/oslockdown/logs/oslockdown.log\nfor more information.\n"
	return False

    return True

##############################################################################
def rotateReports(days=30):

    try:
        logger = TCSLogger.TCSLogger.getInstance(6)
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance()

    try:
        import libxml2
        import sbProps
        import time
        from datetime import date
    except ImportError:
        return False

    try:
        days = int(days)
    except (ValueError, TypeError):
        return False

    if not os.path.isdir(sbProps.ASSESSMENT_REPORTS):
        return False

    today = date.today()

    print >> sys.stdout, "\nRemoved Old Reports (XML Only):"
    print >> sys.stdout, "-" * 70
    ## Assessment Reports
    for xmlFile in os.listdir(sbProps.ASSESSMENT_REPORTS):
        if not xmlFile.endswith('.xml'):
            continue
        xmlFile = os.path.join(sbProps.ASSESSMENT_REPORTS, xmlFile)
        try:
            xmldoc = libxml2.parseFile(xmlFile)
            reportDate = xmldoc.xpathEval("/AssessmentReport/report[@created]")[0]
            timeObj = time.strptime(reportDate.prop("created")[0:10], "%Y-%m-%d")
            xmldoc.freeDoc()

            timeObj = datetime.date(timeObj.tm_year, timeObj.tm_mon, timeObj.tm_mday)
            delta = today - timeObj
            if int(delta.days) > days:
                print >> sys.stdout, "[ DELETE ] %4d days old - %s" % (int(delta.days), xmlFile)
                try:
                    os.unlink(xmlFile)
                    msg = "Removed %s (%d days old)" % (xmlFile, int(delta.days))
                    logger.log_notice('Report Management', msg)
                except (OSError, IOError), err:
                    msg = "Removed %s (%d days old)" % (xmlFile, int(delta.days))
                    logger.log_notice('Report Management', msg)
                    print >> sys.stderr, err
            
            else:
                print >> sys.stdout, "[   OK   ] %4d days old - %s" % (int(delta.days), xmlFile)
        except:
            pass

    ## Baseline Reports
    for xmlFile in os.listdir(sbProps.BASELINE_REPORTS):
        if not xmlFile.endswith('.xml'):
            continue
        xmlFile = os.path.join(sbProps.BASELINE_REPORTS, xmlFile)
        try:
            xmldoc = libxml2.parseFile(xmlFile)
            reportDate = xmldoc.xpathEval("/BaselineReport/report[@created]")[0]
            timeObj = time.strptime(reportDate.prop("created")[0:10], "%Y-%m-%d")
            xmldoc.freeDoc()

            timeObj = datetime.date(timeObj.tm_year, timeObj.tm_mon, timeObj.tm_mday)
            delta = today - timeObj
            if int(delta.days) > days:
                print >> sys.stdout, "[ DELETE ] %4d days old - %s" % (int(delta.days), xmlFile)
                try:
                    os.unlink(xmlFile)
                    msg = "Removed %s (%d days old)" % (xmlFile, int(delta.days))
                    logger.log_notice('Report Management', msg)
                except (OSError, IOError), err:
                    msg = "Removed %s (%d days old)" % (xmlFile, int(delta.days))
                    logger.log_notice('Report Management', msg)
                    print >> sys.stderr, err
            
            else:
                print >> sys.stdout, "[   OK   ] %4d days old - %s" % (int(delta.days), xmlFile)
        except:
            pass
   
    print >> sys.stdout, " "

#### Following two routines ( _parse, and string_to_dictionary) are slightly modified from the following URL
#### http://mail.python.org/pipermail/python-list/2005-November/350811.html
#### Written by Fredrik Lundh (fredrik@pythonware.com)

import cStringIO
import tokenize

def _parse(token, src):
    if token[1] == "{":
        out = {}
        token = src.next()
        while token[1] != "}":
            key = _parse(token, src)
            token = src.next()
            if token[1] != ":":
                raise SyntaxError("malformed dictionary")
            value = _parse(src.next(), src)
            out[key] = value
            token = src.next()
            if token[1] == ",":
                token = src.next()
        return out
    elif token[1] == "[":
        out = []
        token = src.next()
        while token[1] != "]":
            out.append(_parse(token, src))
            token = src.next()
            if token[1] == ",":
                token = src.next()
        return out
    elif token[0] == tokenize.STRING:
        return token[1][1:-1].decode("string-escape")
    elif token[0] == tokenize.NUMBER:
        try:
            return int(token[1], 0)
        except ValueError:
            return float(token[1])
    elif token[1] == 'True':
        return True
    elif token[1] == 'False':
        return False
    elif token[1] == 'None':
        return None
    else:
        raise SyntaxError("malformed expression detecting while converting string to dictionary")

def string_to_dictionary(source):
    src = cStringIO.StringIO(source).readline
    src = tokenize.generate_tokens(src)
    return _parse(src.next(), src)

def splitNaturally( entry, whitespaceAdditions=',', wordAdditions="", uniq=True):
    if type(entry) == type(""):
        elements = []
        lexer = shlex.shlex(entry,posix=True)
        if whitespaceAdditions:
            lexer.whitespace += whitespaceAdditions
        if wordAdditions:
            lexer.wordchars += wordAdditions
        for item in lexer:
            
            if uniq and item in elements:
                continue
            elements.append(item)
        return elements
    elif type(entry) == type([]):
        return entry
        
    else:
        msg = "Unable to parse '%s'" % entry
        raise ActionError('%s %s' % ("tcs_utils.splitNaturally", msg) )

if __name__ == '__main__':
    rotateReports()
