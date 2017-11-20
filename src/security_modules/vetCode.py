import os
import re
import sys

def check_name_in_file(dname, fname,regex):
    # the file name should be the 
    expectedClass = os.path.splitext(fname)[0]
    foundClasses = []
#    print "%s/%s -> %s" % (dname, fname, expectedClass)
    for line in open("%s/%s" % (dname, fname)):
        try:
           foundClasses.append(regex.search(line).group(2))
        except AttributeError:
            pass
    if not expectedClass in foundClasses:
        print "\t","%s/%s - filename not defines as an internal class" % (dname,fname)
        print "\t",foundClasses
        
def check_names():
    regex = re.compile("\s*(class)\s+(\w+)")
    for d in ['fedora', 'generic' ,'redhat', 'redhat6', 'solaris', 'suse']:
        print "Check %s" %d
        for f in os.listdir(d):
            if not f.endswith('.py'):
                continue
            check_name_in_file(d, f, regex)     

if '-name' in sys.argv[1:]:
    check_names()
elif '-syntax' in sys.argv[1:]:
    check_syntax()
