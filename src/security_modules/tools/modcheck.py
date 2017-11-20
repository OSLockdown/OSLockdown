#!/usr/bin/python

# execute by being in the security_modules directory and typing
# tools/modcheck.py
# scan over *all* module code in oslockdown/src/security-modules/
#   generic/
#   redhat/
#   solaris/
#   suse/
# looking for the scan/apply/undo sections
#
# report if apply/undo call scan
# report if scan/apply/undo call print
# report if scan/apply/undo call return (and with what values
# report if module has main test harness


import os,sys,sets

def vet_file(thisfile):
    lines=[]
    results={"__main__":False}
    section={}
    newsection={'print':False,'raise':sets.Set(),'return':sets.Set()}
    name=""
    in_comment=False
    in_quotes=False
    linetoadd=""
    print "Checking ",thisfile
    for line in open(thisfile):
        if line.startswith("if ") and line.find('__name__') and line.find('__main__'):
            results["__main__"]=True
            if name != "":
                results[name]=section
                section={'print':False,'raise':sets.Set(),'return':sets.Set()}
            name=""
        line=line.strip()
#        print line[0:10],line[-5:],line.startswith("def") ,line.endswith(":)")

        if line.startswith("def ") and line.endswith("):"):
            if name != "":
                results[name]=section
            section={'print':False,'raise':sets.Set(),'return':sets.Set()}
            name=line.split()[1].split('(')[0]
        if name != "":
            if line.startswith('print'):
                section['print']=True
            elif line == 'raise':
                section['raise'].add("reraised")
            elif line.startswith('raise '):
                z=line.split()[1].split('(')[0]
                if z=="":
                    z="re-raised"
                section['raise'].add(z)
            elif line.startswith ('return'):
                z=line.split()[1].split(',')[0]
                section['return'].add(z)

    if name != "":
        results[name]=section
    
    return {thisfile:results} 


    
def vet_dir(thisdir):
    results={}
    for thisfile in os.listdir(thisdir):
        if thisfile.endswith('.py') and not thisfile.startswith('__'):
            pyfile=os.path.join(thisdir,thisfile)
            try:
                res=vet_file(pyfile)
                results.update(res)
            except Exception,err:
                print "Unable to process %s due to %s" % (pyfile,err)
    print "Directory %s had %d entries" % ( thisdir,len(results))
    return results

def dump_results_key(key,res):
    if key == '__main__':
        print "\tTest harness   ->  ",res
    else:
        print "\t%s:"%key
        print "\t\tPrint  ->",res['print']
        print "\t\tRaise  ->",','.join(list(res['raise']))
    if key in ['scan','apply','undo' ] :
        print "\t\tReturn ->",','.join(list(res['return']))

def dump_results(name,results):
    print "\n%s -> Has test harness = %s" % (name,results.has_key('__main__'))
    for key in results.keys():
        if key in ['scan','apply','undo','__main__'] :
            continue
            
        res=results[key]
        dump_results_key(key,res)

    for key in ['scan','apply','undo']:
        if not results.has_key(key):
            if key == '__main__':
                print "\tTest harness   ->  NOT FOUND"
            else:
                print "\t%s: NOT FOUND"%key 
            continue          
        res=results[key]
        dump_results_key(key,res)
        
            
if len(sys.argv) > 1:
    results=vet_file(sys.argv[1])
else:
    results={}
    dirs=['generic','redhat','solaris','suse']
    for thisdir in dirs:
        results.update(vet_dir(thisdir))

print "%d entries to show" % len(results)
print type(results)
print results.keys()
for res in sorted(results.keys()):
    dump_results(res,results[res])
    
