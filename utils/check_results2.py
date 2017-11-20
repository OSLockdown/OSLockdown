#!/usr/bin/env python
import sys,os,time, getopt
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

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
    foundOps = []
    for r in all_ops:
        foundOps.append(r.action.lower())
#        print "ACTION ",r.action
        if len(r.action) > z:
            z = max(len(r.action), len(r.date_str)+2, len(r.hour_str)+2)
            o = r.action
        for m,res in r.modules.items():
#           print m,res
            if len(res) > z:
                z = len(res)
                o = res
    res_width = z
    
    if foundOps == ['scan','apply','scan','apply','scan', 'undo','scan','undo','scan']:
        print "VALID TEST SEQUENCE"
        SCAN1  = 0
        APPLY1 = 1
        SCAN2  = 2
        APPLY2 = 3
        SCAN3  = 4
        UNDO1  = 5
        SCAN4  = 6
        UNDO2  = 7
        SCAN5  = 8
        
        
    else: 
        foundOpts = None
        
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

    line = "%*s " % (mod_width," ")
        
    for i,op in enumerate(all_ops):
        line += "%*s " % (res_width,op.hour_str)
    print line            

    print "-" * (mod_width + (res_width+1) *len(all_ops))
                
    for mod in all_modules: 
        line = "%*s " % (mod_width,mod)
        res = []
        issues = ""
        for op in all_ops:
            if op.modules.has_key(mod):
                resval = op.modules[mod].lower().replace(" ","_")
            else:
                resval = '---'
            res.append(resval)
            line += "%*s " % (res_width,resval)
        
        # if we found the correct sequence for a test set, then do analysis....
        if foundOps:
            
            # now we can check for result state, using either statements like res[SCAN1]=='fail', -or- by 
            # explicit comparison of the array - IE if res == ['fail','applied','pass','not_required','undone','fail','not_required','fail']
            
            # try and catch known good stuff early
            #            scan    apply          scan   apply            scan     undo          scan           undo             scan
            if res == ['fail', 'applied'     , 'pass', 'not_required', 'pass',  'undone',       'fail',         'not_required', 'fail'         ] :
                # expected response if module fails and can be corrected
                issues = "Ok"
            elif res == ['manual_action', 'manual_action', 'manual_action', 'manual_action', 'manual_action', 'not_required' ,'manual_action', 'not_required', 'manual_action']:
                # expected response if module is a manual action only module
                issues = "Ok"
            elif res == ['pass', 'not_required', 'pass', 'not_required', 'pass',  'not_required', 'pass',         'not_required', 'pass'         ]:
                # expected response if module passes and no changes are required
                issues = "Ok"
            elif res == ['fail', 'manual_action', 'fail', 'manual_action', 'fail',  'not_required', 'fail',         'not_required', 'fail'         ]:
                # expected response if module requires manual action
                issues = "Ok"
            elif res == ['na', 'na', 'na', 'na', 'na',  'not_required', 'na', 'not_required', 'na'         ]:
                # expected response if module is not applicable and does not apply
                issues = "Ok"
            elif res == ['os_na', 'os_na', 'os_na', 'os_na', 'os_na',  'os_na', 'os_na', 'os_na', 'os_na'         ]:
                # expected response if module is not applicable (based on metadata) and does not apply
                issues = "Ok"
            elif res == ['os_na', 'os_na', 'os_na', 'os_na', 'os_na',  'not_required', 'os_na', 'not_required', 'os_na'         ]:
                # expected response if module is not applicable (determined by *Module* and did not apply
                issues = "Ok"
            elif res == ['module_unsupported', 'module_unsupported', 'module_unsupported', 'module_unsupported', 'module_unsupported',  'not_required', 'module_unsupported', 'not_required', 'module_unsupported'         ]:
                # expected response if module is returns an unsupported result from scan/apply
                issues = "Ok"
            elif res == ['pass', 'applied', 'pass', 'applied', 'pass',  'undone', 'pass', 'not_required', 'pass' ] and mod.startswith('Profile') and mod.endswith('Additions'):
                # expected response for 'meta-modules' which alter suid/sgid/exclude/inclusion files
                issues = "Ok"

            elif res == ['na', 'not_required', 'na', 'not_required', 'na',  'not_required', 'na',         'not_required', 'na'         ]:
                issues = "Applies should return NA also"

            elif res == ['fail', 'applied', 'pass', 'applied', 'pass',  'undone', 'fail',         'not_required', 'fail'         ]:
                issues = "Applied twice!"
            elif res == ['fail', 'applied', 'fail', 'not_required', 'fail',  'undone', 'fail',         'not_required', 'fail'         ]:
                issues = "Applied, failed next scan, then *not* applied again"
            elif res == ['fail', 'applied', 'pass', 'applied', 'pass',  'undone', 'pass',         'not_required', 'pass'         ]:
                issues = "Applied twice, undo does not revert changes "
            elif res == ['fail', 'not_required', 'fail', 'not_required', 'fail',  'not_required', 'fail',         'not_required', 'fail'         ]:
                issues = "Scan fails, but apply indicates not required "
            elif res == ['fail', 'not_required', 'pass', 'not_required', 'pass',  'not_required', 'fail',         'not_required', 'fail'         ]:
                issues = "Possible module interaction - goes from fail to pass without intervening apply, and back to fail w/o undo "
            elif 'error' in res:
                issues = "ERROR RETURNED DURING MODULE ACTION"
            else :
                issues = "unrecognized pattern found for s/a/s/a/s/u/s/u/s series"

            #ok, given our actions of sasasusus, the second and third scans should match, and the first, fourth and fifth scans should match
            if res[SCAN2] != res[SCAN3]:
                issues += "; scans after apply don't match"
            if res[SCAN4] != res[SCAN5]:
                issues += "; scans after undo don't match"
            if res[SCAN1] != res[SCAN4] or res[SCAN1] != res[SCAN5]:
	        issues += "; initial scans don't match scans after undo"            

        if issues != "Ok":
            line +=  "OOPS " + issues
        print line
                
def get_date(line):
    rep_date = ' '.join(line.split()[0:4])
    try:
        date_tuple = time.strptime(rep_date.strip(),"%Y %b %d %H:%M:%S")
        date_str = time.strftime("%D %T",date_tuple)
    except Exception, e:
        print "*** ",str(e)
        date_str = rep_date
    return date_str.split(' ')

def dump_op(splitbase, op):
     if splitbase:
        tstart_tm = time.strptime(op.start,"%Y %b %d %H:%M:%S")
        starttime = time.strftime("%Y%m%d_%H%M%S", tstart_tm)
        logfilename = "%s%s_%s" % (splitbase, starttime, op.action)
#        print "\tGenerating log file %s" % logfilename
        open(logfilename, "w").writelines(op.lines)
    


def parse_file(splitbase, logfile):
    """
    """
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
            op.date_str, op.hour_str = get_date(line)     
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
    if op.action and op.action.lower() in ['scan', 'apply', 'undo']:
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
