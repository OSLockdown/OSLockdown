#!/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

import sys, os, shlex, getopt

AllFiles = {}
to_show = []

# Break a line with space separated uid,gid,mode, mac, fingerprint, testfile
# Note however that a filename *CAN* contain spaces also, so we've got some parsing to do
# return an array of the fields

    
def read_report(rpt, rtype):
    print "Reading report %s..." % rpt
    global AllFiles 
    num_lines = 0
    for line in open(rpt, 'r'):
        uid, gid, dac, mac, contextMac, fprint, fname = line.strip().split('\t')
        num_lines = num_lines + 1
        if not AllFiles.has_key(fname):
            AllFiles[fname] = {}
        
        if not AllFiles[fname].has_key(rtype):
            AllFiles[fname][rtype] = {}
            
        AllFiles[fname][rtype]["UID"] = uid
        AllFiles[fname][rtype]["GID"] = gid
        AllFiles[fname][rtype]["DAC"] = dac
        AllFiles[fname][rtype]["MAC"] = mac
        AllFiles[fname][rtype]["CONTEXTMAC"] = contextMac
        AllFiles[fname][rtype]["FPRINT"] = fprint
        
    print "Processed %d lines from %s" % (num_lines, rpt)
    
def dump_diffs(label, v1, v2):
    global to_show
    diff = ""
    if (v1 != v2) and label in to_show:
        diff = ["\t%s\t\twas '%s'\tnow '%s'" % (label, v1, v2)]
    return diff
  
def parsemac(mac, full_check):
    if mac and mac != "noMac" and not full_check:  
        mac = ':'.join(mac.split(':')[1:])
    
    return mac      
    
def compare_reports(files, full_check):
    global AllFiles 
    global to_show  
    
    if len(files)==1:
        print "Looking for incorrect MACs in %s" % (files[0])
        read_report(files[0], '1')
    else:
        print "Comparing %s and %s" % (files[0],files[1])
        read_report(files[0], '1')
        read_report(files[1], '2')
    
    first_only = []
    second_only = []
    for fname, stats in AllFiles.items():
        
        if len(files) == 1:
            m1  = parsemac(stats['1']['MAC'], full_check) 
            m1c = parsemac(stats['1']['CONTEXTMAC'], full_check)
            if m1 != m1c:
                print "%s\t%s\t%s" % (fname, m1,m1c)
        else: 
            if stats.has_key('1') and stats.has_key('2'):    # if we have both entries, compare them
                if stats['1'] != stats['2']:
                    diffs = []
                    diffs.extend(dump_diffs('UID', stats['1']['UID'], stats['2']['UID']))
                    diffs.extend(dump_diffs('GID', stats['1']['GID'], stats['2']['GID']))
                    diffs.extend(dump_diffs('DAC', stats['1']['DAC'], stats['2']['DAC']))
                    m1  = parsemac(stats['1']['MAC'], full_check) 
                    m1c = parsemac(stats['1']['CONTEXTMAC'], full_check)
                    m2  = parsemac(stats['2']['MAC'], full_check) 
                    m2c = parsemac(stats['2']['CONTEXTMAC'], full_check)
                    diffs.extend(dump_diffs('MAC', m1, m2))
                    # IMPORTANT - only care about FINAL STATUS - so if the mac differ, and the final mac isn't the default say so
                    if 'MAC' in to_show and m1 != m2 and m1c.find(':') > 0  and  m2 != m1c : 
                            diffs.extend( ["\tPolicy MAC is %s" % m1c ])
                    diffs.extend(dump_diffs('FPRINT', stats['1']['FPRINT'], stats['2']['FPRINT']))
                    if diffs:
                        print fname
                        for diff in diffs:
                            print diff
                    
            elif stats.has_key('1'):                      # only have the file to start with
                first_only.append(fname)
            elif stats.has_key('2'):                      # only have the file to end with
                second_only.append(fname)

    if first_only and '1' in to_show:
        print "\n\n"
        print "The following %d file(s) were found only in the first file  " % (len(first_only))
        for entry in first_only:
            print "\t%s" % entry

    if second_only and '2' in to_show:
        print "\n\n"
        print "The following %d file(s) were found only in the second file  " % (len(second_only))
        for entry in second_only:
            print "\t%s" % entry

    print "\n\nAll done."

def usage():
    print "%s : <rpt1> [-c] [<rpt2> [-u] [-g] [-d] [-m] [-f] [-1|-2]]" % sys.argv[0]
    print "    -c         compare full SELinux context, otherwise ignore the SELinux user field"
    print "    -u         show files with UID differences"
    print "    -g         show files with GID differences"
    print "    -d         show files with DAC (discretionary access controls) differences"
    print "    -m         show files with MAC (mandatory access controls - SELinux contexts) differences"
    print "    -f         show files with fingerprint (internal content) differences"
    print "    -1         show files that only exist in the first report"
    print "    -2         show files that only exist in the second report"
    print "    -h         This message"    

def process_args():
    global to_show
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "cugdmf12h")
    except getopt.GetoptError, err:
        print >> sys.stderr, "Error: %s" % err
        usage()
        sys.exit(1)

    full_check = False

    
    for o, a in opts:
        print o   
        if o == '-h':
            usage()
            sys.exit(0)
        elif o == '-u' and 'UID' not in to_show:
            to_show.append('UID')
        elif o == '-g' and 'GID' not in to_show:
            to_show.append('GID')
        elif o == '-d' and 'DAC' not in to_show:
            to_show.append('DAC')
        elif o == '-m' and 'MAC' not in to_show:
            to_show.append('MAC')
        elif o == '-f' and 'FPRINT' not in to_show:
            to_show.append('FPRINT')
        elif o == '-1' and '1' not in to_show:
            to_show.append('1')
        elif o == '-2' and '2' not in to_show:
            to_show.append('2')
        elif o == '-c':
           full_check = True

        if not to_show:
            to_show =  ['UID', 'GID', 'DAC', 'MAC', 'FPRINT', '1', '2']  

        
        if len(args) == 1:
            print "Differences limited to showing MAC problems."
            to_show = ['MAC']
        elif len(args) != 2:
            print "I need two files to compare."
            sys.exit(1)

        print to_show
    return args,full_check


    
if __name__ == '__main__':
    if len(sys.argv) < 2 :
        print "Usage: %s <rpt1> [-c] [<rpt2> [-u] [-g] [-d] [-m] [-f] [-1|-2]]" % (sys.argv[0])
    else:
        files, full_check = process_args()
        compare_reports(files, full_check)
 
