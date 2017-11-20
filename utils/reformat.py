##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
import textwrap
import sys

replaceset={}
replaceset['\t'] = '    '
replaceset['\x92'] = "'"
replaceset['\x93'] = '-'
replaceset['\x96'] = "'"
replaceset['\xa0'] = ' '


def wrap_file(name):
    text_in = open(name).read()

    # take each line and search/replace from replaceset
    for rpl in replaceset.keys():
        text_in = text_in.replace(rpl, replaceset[rpl])

    subsequent_indent = ""
    break_on_hyphens  = True
    break_long_words  = True
    prefix = ""
    width=70
    expand_tabs = False
    for line in text_in.splitlines():        
    
        if line and line[0].isdigit():
            subsequent_indent = "    "
        if line and line[0] == '"' and line[1].isdigit():
            subsequent_indent = "    "
            prefix="    "
        text_out = textwrap.wrap(line,
            width=width,
            subsequent_indent=subsequent_indent,
            break_long_words=break_long_words,
            break_on_hyphens=break_on_hyphens,
            expand_tabs=expand_tabs)
        if not text_out:
            print
        for y in text_out:
            print "%s%s" % (prefix,y)

        if prefix and line.strip().endswith('"'):
            prefix=""
        subsequent_indent = ""


def histogram(name):
    chars = {}
    puncts = ",.;- \"'()[]/:;%"
    text_in = open(sys.argv[1]).read()
    for rpl in replaceset.keys():
        text_in = text_in.replace(rpl, replaceset[rpl])
    for i in text_in:
        if i.isalnum():
            continue
        if i in puncts:
            continue
        if i == "\t":
            continue
        if i == "\n":
            continue
        if i == "\r":
            continue
        if i in chars:
            chars[i] = chars[i] + 1
        chars[i] = 1
    print "Found %d oddballs " % len(chars)
    for i in chars.keys():
        print "-> %03x (%d)" % (ord(i), chars[i])


wrap_file(sys.argv[1])   

#histogram(sys.argv[1])
