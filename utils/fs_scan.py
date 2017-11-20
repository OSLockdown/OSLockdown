#!/bin/env python
##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

#
# Modified from baseline fingerprinter to look over all files and give us
# name/DAC/MAC/hash values
#

import sys
import os
import stat
import errno
import sha
import platform
import getopt
import commands

have_selinux = False
try:
    import selinux
    have_selinux = True
except ImportError:
    pass

MODULE_NAME = "fs_scan"
excludes = ['/proc' , '/selinux' ]
outputname = None

def is_excl(filename):
    result = False
    for excl in excludes:
        if filename.startswith(excl): 
            result = True
            break
    return result

def usage(execname):
    print "%s : [-f OUTPUT] [-e EXCL] [-h ]"
    print "    -f OUTPUT  Write to file OUTPUT"
    print "    -e EXCL    Add EXCL to list of files/dirs not to scan"
    print "    -h         This message"    
    sys.exit(0)
    
def process_args():
    global outputname
    filesystems = ['/']
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "f:e:h")
    except getopt.GetoptError, err:
        print >> sys.stderr, "Error: %s" % err
        usage_message()
        sys.exit(1)

    
    for o, a in opts:
        print o, a
        if o == '-h':
            usage(sys.argv[0])
        elif o == '-e':
            if os.path.exists(a):
                if a not in excludes:
                    excludes.append(a)
                else:
                    print "%s already excluded from scan" % a
            else:
                print "%s does not exist" % a
        elif o == '-f':
            outputname = a

# DO a Scan/Apply/Undo or Baseline operation, with filesystem scan at the end.
# If the profile file is blank, skip that op
    if args:
        filesystems = args

    return filesystems
    
##############################################################################
def perform(start_dirs=None, outputname=None):
    """Inventory files"""

#    print "Dirs = ", start_dirs
#    print "Excl = ", excludes
#    print "Output=",outputname
    if outputname:
        output = open(outputname,"w")
    else:
        output = sys.stdout

    if start_dirs == None or type(start_dirs).__name__ != 'list':
        msg = "Error: Starting directory "
        print >> sys.stderr, "ERROR - %s" % msg
        return False, ''

    master_fingerprint = sha.new()

    ############ Walk the directories ##########

    # Before getting started, let's check / to make sure 
    # everything is cool at the top level

    # Now start traversing all starting points
    try:
        for subdir in start_dirs:
            if not os.path.isdir(subdir):
                msg = "%s does not exist - skipping" % subdir
                print >> sys.stderr, "ERROR - %s" % msg
                continue

   
            for root, dirs, files in os.walk(subdir):
    
                # Before stat'ing file, make sure its path isn't in the 
                # excluded path list
    
                if is_excl(root):
                    print >> sys.stderr, "Skipping %s" % root
                    dirs[:] = []
                    files[:] = []
                    continue
                    
#                print >> sys.stderr, "Entering %s " % root
                list_of_files = []
                list_of_files.append(root)
                list_of_files.extend(files)

                for infile in list_of_files:
                    if infile != root:
                        testfile = os.path.join(root, infile)
                    else:
                        testfile = root

                    try:
                        statinfo = os.lstat(testfile)
                    except OSError, err:
                        msg = "Unable to stat %s: %s" % (testfile, err)
                        print >> sys.stderr, "ERROR - %s" % msg
                        if os.path.islink(testfile) and err.errno == errno.ENOENT:
                            msg  = "%s appears to be a broken link; restore the "\
                                   "target file or remove the link" % (testfile)
                            print >> sys.stderr, "ERROR - %s" % msg
                        continue

                    fingerprint = ""
                    if stat.S_ISREG(statinfo.st_mode) == False:
                        if stat.S_ISBLK(statinfo.st_mode) == True :
                            fingerprint = "--IS_BLK_DEVICE--"
                        elif stat.S_ISCHR(statinfo.st_mode) == True : 
                            fingerprint = "--IS_CHAR_DEVICE--"
                        elif stat.S_ISSOCK(statinfo.st_mode) == True :
                            fingerprint = "--IS_SOCKET--"
                        elif stat.S_ISFIFO(statinfo.st_mode) == True:
                            fingerprint = "--IS_FIFO--"
                        elif stat.S_ISDIR(statinfo.st_mode) == True:
                            fingerprint = "--IS_DIRECTORY--"
                        else:
                           # skip it
                            continue

                    if fingerprint == "":
                        # Now, compute the SHA1 digest
                        digest_key = sha.new()
                        try:
                            fdes = open(testfile, 'rb')
                            try:
                                try:
                                    while True:
                                        block = fdes.read(1048576)
                                        if not block:
                                            break
                                        digest_key.update(block)
                                except IOError, err:
                                    fingerprint = "IOError"
                            finally:
                                fdes.close()
                        except (OSError, IOError), err:
                            msg = "Unable to read %s: %s" % (testfile, err)
                            print >> sys.stderr, "ERROR - %s" % msg
                            fingerprint = "unable_to_read"
                
            
                    if fingerprint == "":
                        fingerprint = digest_key.hexdigest()

                    mode =  "%04o" % (stat.S_IMODE(statinfo.st_mode))
                    mode2 = statinfo.st_mode

                    uid    = str(statinfo.st_uid)
                    gid    = str(statinfo.st_gid)
                
                    mac = "noMAC"
                    contextMac = "noMac"
                    
                    if have_selinux:
                        # use the python API to get the MAC
                        try:
                            mac = selinux.getfilecon(testfile)[1]
                        except:
                            mac = "problemMac"

                        try:
                          status, contextMac = selinux.matchpathcon(testfile, mode2)
                        except:
                          contextMac = "probleMac"
                        if not mac:
                            mac = "noMAC"
                        if not contextMac:
                            contextMac = mac
                    else:
                        # Ok, do a long listing, remove the filename, and the MAC should be the last field
                        try:
                            longlist = commands.getoutput("ls -Zd '%s'" % testfile).splitlines()[0]
                            wherename = longlist.find(testfile)
                            withoutname = longlist[0:wherename].split()
                            if len(withoutname) == 4:
                                mac = withoutname[3]
                            contextMac = commands.getoutput("/sbin/restorecon -F -n -v %s | awk -F'>' '{print $NF}'" % testfile)
                        except:
                            mac = "unable"
                            contextMac = "unable"                
                        if not contextMac:
                            contextMac = mac
                    fileline = "\t".join([uid, gid, mode, mac, contextMac, fingerprint, testfile])
                    output.write("%s\n" % fileline)
    except KeyboardInterrupt:
        msg = "Aborting: caught keyboard interrupt -- fingerprinting NOT completed" 
        print >> sys.stderr, "ERROR - %s" % msg
        return False, ''

    except IOError, err:
        if err.errno == errno.EPIPE:
            msg = "Ignoring: %s" % err
            print >> sys.stderr, "ERROR - %s" % msg
        else: 
            raise

    output.close()

##############################################################################
if __name__ == '__main__':

    filesystems = process_args()
    outfile = None

    z = len(sys.argv)
    
    perform(filesystems, outputname)
