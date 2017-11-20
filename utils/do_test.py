#!/bin/env python
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
import sys,os,shutil

import fs_scan
import getopt
import commands
import os


def vet_profile(fname,defaultprefix, option):
    errors = []
    if not fname.endswith('.xml'):
        fname = fname + '.xml'
    
    if os.path.exists(fname):
#        print "Option '%s' : located '%s'" % (option, fname)
        return fname
    
    errors.append( "Option '%s' : Unable to find '%s' " % (option, fname))
    
    if defaultprefix :
        testname = "%s/%s" % (defaultprefix, fname)
        if os.path.exists(testname):
#            print "Option '%s' : located '%s'" %  (option, testname)
            return testname
        errors.append( "Option '%s' : Unable to find '%s'" %  (option, testname))
    for err in errors:
        print err    
    sys.exit(1)
    

def usage():
    print "%s : [-s NAME] [-b NAME] [-f PATH] [-B ] [-h ]" % sys.argv[0]
    print "    -s NAME    Use NAME as the Security Profile"
    print "    -b NAME    Use NAME as the Baseline Profile"
    print "    -f PATH    Use PATH as the root of all filesystem scans for MAC/DAC/hash checks - no scan done if missing"
    print "    -B         Do not do an OS Lockdown 'Baseline'"
    print "    -p         Do fine postprocessing of the results of any filesystem scans"
    print "    -h         This message"    
    sys.exit(0)

def is_exec(filename):
    retval = False
    if os.path.exists(filename) and os.access(filename, os.X_OK):
      retval = True
    return retval
    
def process_args():
    if len(sys.argv) < 2:
	usage()
    myargs = {}
    myargs['security'] = "/var/lib/oslockdown/profiles/DISAUNIXSTIG.xml"
    myargs['baseline'] = "/var/lib/oslockdown/baseline-profiles/Default.xml"
    myargs['fileroot'] = None
    myargs['post'] = False
    myargs['avc_clear'] = True
    myargs['results'] = {}
    myargs['selinux'] = False
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "s:b:f:h:Bpa")
    except getopt.GetoptError, err:
        print >> sys.stderr, "Error: %s" % err
        usage()

    force = False

    if len(opts)>0:
        myargs['security'] = None
        myargs['baseline'] = None
    
    for o, a in opts:
        if o == '-h':
            usage()
        if o == '-s':
            myargs['security'] = vet_profile(a,'/var/lib/oslockdown/profiles', '-s')
        elif o == '-b':
            myargs['baseline'] = vet_profile(a,'/var/lib/oslockdown/baseline-profiles', '-b')
        elif o == '-f':
            if not os.path.isdir(a) :
                print "Option '-f' : No such directory '%s'" % a
                sys.exit(1)
            myargs['fileroot'] = a
        elif o == '-B':
            myargs['baseline'] = None
        elif o == '-p':
            myargs['post'] = True
        elif o == '-a':
            myargs['avc_clear'] = False
    return myargs
    
# DO a Scan/Apply/Undo or Baseline operation, with filesystem scan at the end.
# If the profile file is blank, skip that op

def perform_sbop(SB_Op, opName, myargs):
    #Operation check:
    opcmd = ""
    print "\nOperation -> %s (%s)" % (SB_Op, opName)
    if SB_Op in ['s', 'a', 'u' ] :
        profile = myargs['security'] 
    elif SB_Op in ['b' ]:
        profile = myargs['baseline']
    if profile and  os.path.exists(profile) :
        opcmd = "/usr/sbin/oslockdown -v -l 7 -f -%s %s 2>&1" % (SB_Op, profile)
    
    if opcmd:
        print "\tExecuting -> %s" % opcmd
        status,output = commands.getstatusoutput(opcmd)
    	print "\t\tCompleted with status code %d" % status
        outfile = "SBOUTPUT_%s" % opName.upper()
        open(outfile,"w").write(output)
        shutil.copy("/var/lib/oslockdown/logs/oslockdown.log","SBLOG_%s"%opName.upper())
        os.unlink("/var/lib/oslockdown/logs/oslockdown.log")
    else:
        print "\tSkipping -> %s(%s) - profile is '%s'" % (SB_Op,opName, profile) 
        return 
        

def perform_fs_scan(opName, myargs):
    #Operation check:
    fs_results = "FS_RES_%s" % opName.upper()
    print "\nFS_SCAN Operation -> %s" % opName

    if  myargs['fileroot'] and os.path.isdir(myargs['fileroot']):
        print "\tDoing MAC/DAC/Hask scan to -> %s " %fs_results
        fs_scan.perform([myargs['fileroot']], fs_results)

def check_avc(opName):
    if not is_exec('/usr/bin/audit2allow'):
        print "\tAudit2allow not found"
        return
    
    status,output = commands.getstatusoutput('/usr/bin/audit2allow -a -l')
#    print status, len(output),output
    if status != 0 and status != 256 :
        print "\tUnable to check AVC for violations"
    else:
        lines = output.splitlines()
        outfile = "AVC_%s" % opName.upper()
        print "\tAVC cache checked - found %d entries - written to %s" % (len(lines), outfile)
        open(outfile,"w").write(output)
        
    clear_avc()
    
def clear_avc():
    if not is_exec('/usr/sbin/semodule'):
      return
    status,output = commands.getstatusoutput('semodule -R')
    if status != 0:
        print "\tUnable to clear AVC"
    else:
        print "\tAVC Cleared"


def do_postprocess():
    status, output = commands.getstatusoutput('./compare_fs_scan.py AFTER_SCAN AFTER_UNDO -m > FS_SCAN.REPORT')
    if status != 0:
        print "\tUnable to perform fs_scan comparison -> %s",output
    else:
        print "\tWrote report from fs_scan comparison on MACs to 'FS_SCAN.REPORT'"
        
                
def main(myargs):

    clear_avc()

    perform_sbop('b','op_01_baseline', myargs)
    if myargs['avc_clear'] == True:
        check_avc('op_01_bbaseline')
    perform_fs_scan('op_01_initial_scan', myargs)

    perform_sbop('s','op_02_scan', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_02_scan')

    perform_sbop('a','op_03_apply', myargs)
    perform_fs_scan('op_03_apply', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_03_apply')

    perform_sbop('s','op_04_scan', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_04_scan')

    perform_sbop('a','op_05_apply', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_05_apply')

    perform_sbop('s','op_06_scan', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_06_scan')

    perform_sbop('u','op_07_undo', myargs)
    perform_fs_scan('op_07_undo', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_07_undo')

    perform_sbop('s', 'op_08_scan', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_08_scan')

    perform_sbop('u','op_09_undo', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_09_undo')

    perform_sbop('s', 'op_10_scan', myargs)
    if myargs['avc_clear'] == True:
      check_avc('op_10_scan')
     
    perform_sbop('b','op_11_baseline', myargs)
    if myargs['avc_clear'] == True:
        check_avc('op_11_bbaseline')

def ask_yes_or_no(text):
    retval = None
    while retval == None:
        raw = raw_input(text)
        print "RAW is ->",raw
        yes_or_no = raw.strip().split()[0]
        print "Answer is ",yes_or_no
        if yes_or_no in ['y', 'yes']:
            retval = True
        elif yes_or_no in ['n', 'no']:
            retval = False
    return retval
        
        
  
if __name__ == '__main__':
    myargs=process_args()
    print myargs
    print "---"
    if os.path.exists('/var/lib/oslockdown/logs/oslockdown.log'):
        if ask_yes_or_no("Found existing /var/lib/oslockdown/oslockdown.logs file!\nDelete it?"):
            os.unlink("/var/lib/oslockdown/logs/oslockdown.log")
    if os.path.exists('/var/lib/oslockdown/logs/oslockdown.log'):
        if not ask_yes_or_no("Use existing /var/lib/oslockdown/oslockdown.logs file ?"):
            print "Aborting test"
            sys.exit(1)

    print "Security Profile  = %s" % myargs['security']
    print "Baseline Profile  = %s" % myargs['baseline']
    print "MAC/DAC/Hash root = %s" %myargs['fileroot']
    print "---"
    main(myargs)  
  
