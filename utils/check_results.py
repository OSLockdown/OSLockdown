#!/usr/bin/env python
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
import sys,os,time, getopt

class SB_OP:
    def __init__(self):
        self.action=""
        self.profile=""
        self.start=""
        self.modules={}
        self.lines=[]
        
all_ops = []
all_modules = []
           
def dump_results():
    print "Processed %d actions" % len(all_ops)
    print "Processed %d modules" % len(all_modules)     

    col_width = []    

    z=len("Module Name\Action")

    o="Module Name\Action"

    for mod in all_modules:
        if len(mod) > z:
            z = len(mod)
            o = mod
    mod_width=z
    
    z=0
    for r in all_ops:
#        print "ACTION ",r.action
        if len(r.action) > z:
            z = max(len(r.action), len(r.date_str)+2)
            o = r.action
        for m,res in r.modules.items():
#           print m,res
            if len(res) > z:
                z = len(res)
                o = res
    res_width = z
    
    
    line = "%*s " % (mod_width,"Module Name")
        
    for i,op in enumerate(all_ops):
        line += "%*s " % (res_width,op.action)
    print line            


    line = "%*s " % (mod_width," ")
    for i,op in enumerate(all_ops):
        line += "%*s " % (res_width,op.profile)
    print line            

    line = "%*s " % (mod_width," ")
        
    for i,op in enumerate(all_ops):
        line += "%*s " % (res_width,op.date_str)
         
    print line            

    print "-" * (mod_width + (res_width+1) *len(all_ops))
                
    for mod in all_modules: 
        line = "%*s " % (mod_width,mod)
        last_scan = None
        last_apply = None
        last_undo = None
        issues = []
        for op in all_ops:
            if op.modules.has_key(mod):
                res = op.modules[mod]
                if res == 'error' :
                    issues.append("ERROR")
                if op.action == 'scan' and res == 'FAIL'  and last_apply and last_apply == 'applied':
                    issues.append("Apply didn't take")
                if op.action == 'scan':
                    last_scan = res
                if op.action == 'apply':
                    last_apply = res
                if op.action == 'undo' and res == 'undone':
                    last_apply = None
                    last_undo = res
                if op.action == 'apply' and res == 'applied' and last_scan and last_scan == 'PASS':
                    issues.append("Apply after PASS")
                if op.action == 'apply' and res == 'not required' and last_scan and last_scan == 'FAIL':
                    issues.append("No Apply after FAIL")
                if op.action == 'undo' and res =='undone' and last_apply and last_apply != 'applied':
                    issues.append("Undo without Apply")
                if op.action == 'scan' and res =='PASS' and last_undo and last_undo == 'undone':
                    issues.append("PASS after undo")
            else:
                res = "----"
            line += "%*s " % (res_width,res.replace(" ","_"))
        if issues != []:
            line += "OOPS " + ", ".join(issues)
        print line
                
def get_date(line):
    rep_date = ' '.join(line.split()[0:4])
    try:
        date_tuple = time.strptime(rep_date.strip(),"%Y %b %d %H:%M:%S")
        date_str = time.strftime("%D %T",date_tuple)
    except Exception, e:
        print "*** ",str(e)
        date_str = rep_date
    return date_str

def dump_op(splitbase, op):
     if splitbase:
        tstart_tm = time.strptime(op.start,"%Y %b %d %H:%M:%S")
        starttime = time.strftime("%Y%m%d_%H%M%S", tstart_tm)
        logfilename = "%s%s_%s" % (splitbase, starttime, op.action)
#        print "\tGenerating log file %s" % logfilename
        open(logfilename, "w").writelines(op.lines)
    
def parse_file(splitbase, logfile):
    op = SB_OP()
    numlines = 0
    for line in open(logfile):
        op.lines.append(line)
        numlines = numlines + 1
        if line.find('.:: Starting OS Lockdown') > 0:
            if op.action :
                all_ops.append(op)
                if op.action and op.start:
                    dump_op(splitbase, op)
#            print "Line %d -> found Starting" % numlines
            op = SB_OP()
            op.start = line[0:20]
            op.date_str = get_date(line)     
        elif line.find('): Action request')>0 :
            op.action = line.split()[12].replace("'","")
            op.profile = line.split()[-1].replace("'","").split('/')[-1]
#            print "\tLine %d -> found action %s" % (numlines,op.action)
        elif line.find('---------------- Initiating Baseline --')>0 :
            op.action = 'baseline'
            op.profile = '---'
#            print "\tLine %d -> found action %s" % (numlines,op.action)
        elif line.find(' results is ')>0:
            fields = line.split()
            modname = fields[6].replace("'","")
            z=line.find('results is')
            modres = line[z+10:].replace("'","").strip()
            if op.action.lower() == "scan":
                modres = modres.upper()
            else:
                modres = modres.lower()
#            modres = fields[9].replace("'","")
            op.modules[modname] = modres  
            if modname not in all_modules:
                all_modules.append(modname)
    if op.action :
        all_ops.append(op)            
    if op.action and op.start:
        dump_op(splitbase, op)
#    print "Read %d" % numlines

def usage():
    print "%s : [-f PREFIX] [-r] [-s] [-h] FILE1 [File...]"
    print "   -r    Dump a table of actions, modules, and results"
    print "   -s    Split the combined logfile in to indivual actions"
    print "   -f    use PREFIX as the prefix when doing the -s action"
    print "         (the default is 'LOG_')"
    print "   -h    this message"
    print "   FILE... One more log files to process, for now they should"
    print "         be entered in oldest to newest order"

def getfirstlinedate(arg):
    firstline=""
    file_epoch = 0
    
    try:
        while not firstline:
            firstline=open(arg).readline()
            file_epoch = str(time.mktime(time.strptime(firstline[0:20], "%Y %b %d %H:%M:%S")))
    except Exception, err:
        print >>sys.stderr,"Unable to process first line of %s for date/time : %s" % (arg, str(err))
    
    return file_epoch
    
if __name__ == '__main__':
#    print "%s %s" % (str(len(sys.argv)),str(os.path.exists(sys.argv[1])))
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "rshf:")
    except getopt.GetoptError, err:
        print >> sys.stderr,"Error: %s" % err
        usage()
        sys.exit(1)
    
    splitbase = "LOG_"
    dosplit = False
    doreport = False

    for o,a in opts:
        if o == '-h':
            usage()
            sys.exit(0)
        elif o == '-f':
            if not a:
                print >>sys.stderr,"Must have at least one character for the prefix "
                sys.exit(1)
            splitbase=a
        elif o == '-s':
            dosplit=True
        elif o == '-r':
            doreport=True
    
    if not dosplit:
        splitbase = ""
    
    if args:
        # first thing, examine each file and put them in order by the timestamp of the first line
        filelist = []
        for i in args:
            firstline_date = getfirstlinedate(i)
            if firstline_date > 0 :
                filelist.append( (firstline_date,i))
        print filelist
        filelist.sort()
        for entry in filelist:
            print i
            i = entry[1]
            if os.path.exists(i):
                parse_file(splitbase,i)
        if doreport :
            dump_results()
    else:
        print "You need to provide a filename that exist to process..."
        sys.exit(1)
