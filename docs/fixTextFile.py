import codecs
import sys
import getopt

# some canned replacements that we'll do.  We know the input is a text file (UTF-8)

replaceset={}
replaceset['\t'] = '    '
replaceset['\xe2\x94\x81'] = '='
replaceset['\xe2\x97\x8b'] = '*'
replaceset['\xe2\x97\x8f'] = '*'
replaceset['\xe2\x96\xa1'] = '*'
replaceset['\xe2\x80\x9c'] = '"'
replaceset['\xe2\x80\x9d'] = '"'
replaceset['\xe2\x80\x99'] = '\''
replaceset['\xe2\x84\xa2'] = '(TM)'
replaceset['\xc2\xa9'] = '(C)'
replaceset['\xc2\xae'] = '(R)'
replaceset['\xc2\xa0'] = ' '

def fixText(text_in):
    # take each line and search/replace from replaceset
    inLen = len(text_in)
    for rpl in replaceset.keys():
        text_in = text_in.replace(rpl, replaceset[rpl])
    outLen = len(text_in)
    return text_in
    
def histogram(validate, text_in):
    oddBalls = {}

    # Leave all chars that are in the range 0-127 as 'standard' ascii'
    oddBallCount = 0
    for i in text_in:
        if 0 < ord(i) < 127:
            continue
        if i in oddBalls:
            oddBalls[i] = oddBalls[i] + 1
        else:
            oddBalls[i] = 1
        oddBallCount = oddBallCount + 1
    if validate:
        print "Found %d oddballs types - total %d" % (len(oddBalls),oddBallCount)

    return oddBalls
    
validate = False
inputFile = None
outputFile = None
opts,args = getopt.gnu_getopt(sys.argv[1:],"i:o:v")

try:
    for o,a in opts:
        if o == "-i":
            inputFile = a
        elif o == "-o":
            outputFile = a
        elif o == "-v":
            validate = True
except getopt.GetoptError, err:
    print e
    sys.exit(1)

if not inputFile:
    print >> sys.stderr,"Must provide input filename"
    sys.exit(1)

text_in = open(inputFile).read()
initialCount = len(text_in)
text_in = fixText(text_in)
finalCount = len(text_in)
if validate:
    print "Initially read %d bytes in file" % initialCount
    print "Have %d bytes after replacments" % finalCount

if outputFile:
    open(outputFile,"w").write(text_in);


if validate:
    (oddBalls) = histogram(validate,text_in)
    
    for i in text_in:
        if 0 < ord(i) < 127:
            sys.stdout.write(i)
        else:
            sys.stdout.write( "<%02x>" % ord(i))
    
    print "Initially read %d bytes in file" % initialCount
    print "Have %d bytes after replacments" % finalCount
    print "\nFound %d possible oddities" % len(oddBalls)
    for i in oddBalls.keys():
        print "-> %03x (%d)" % (ord(i), oddBalls[i])



