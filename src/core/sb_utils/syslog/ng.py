#!/usr/bin/python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#


import re

def getDict():

    config_file = '/etc/syslog-ng/syslog-ng.conf'
    try:
        in_file = open(config_file, 'r')
    except IOError:
        return None

    lines = in_file.readlines()
    in_file.close()
    
    re_keyword = re.compile('^filter\s+(\S+)\s+(.*)$')
    re_ignore = re.compile('^(#|$)')
    re_endofblock = re.compile('\};$')
    
    syslogng = {}
    syslogng['filter'] = {}
    syslogng['destination'] = {}
    
    syslogng_key = ''
    prev_line = []
    broken_line = False
    for tline in lines:
        line = tline.strip()
        if re_ignore.search(line):
            continue
     
        if broken_line == True:
            prev_line.extend(re.split(r'\s+', line))
            filter_rule = ' '.join(prev_line)
            if re_endofblock.search(line):
                print "Continue: ", filter_rule
                if syslogng['filter'].has_key(syslogng_key):
                    syslogng['filter'][syslogng_key] = filter_rule
                prev_line = []
                syslogng_key = ''
                broken_line = False
            continue
            
        #####################################
        # Get Filter tags
        m_filter = re_keyword.search(line)
        if m_filter:
            if re.search(r'\};$', line):
                broken_line = False
                filter_rule = ' '.join(re.split(r'\s+', m_filter.group(2)))
                print broken_line, m_filter.group(1), filter_rule
                if not syslogng['filter'].has_key(m_filter.group(1)):
                    syslogng['filter'][m_filter.group(1)] = filter_rule
            else:
                broken_line = True
                prev_line = re.split(r'\s+', m_filter.group(2))
                syslogng_key = m_filter.group(1)
                if not syslogng['filter'].has_key(m_filter.group(1)):
                    syslogng['filter'][m_filter.group(1)] = ''
    
                #print broken_line, m_filter.group(1), ' '.join(prev_line)
    
    
    #print syslogng['filter']['f_iptables']
    return syslogng
