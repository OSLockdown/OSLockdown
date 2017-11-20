#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import pwd
import os
import re

sys.path.append('/usr/share/oslockdown')
import sbProps
import TCSLogger
try:
    logger = TCSLogger.TCSLogger.getInstance(6) 
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance() 

import tcs_utils

class iniHandler:
    # A restricted handler for 'ini' style configuration files that *preserves*
    # internal comments.  We can add new sections and query/change settings
    # within a section, but currently not delete a section.
     
    def __init__ (self):
        self.__lines = []
        self.__sections = []

    def get_section_names(self):
        return [ sect['name'] for sect in self.__sections if sect['name'] != ""]
        
    def show_sections(self):
        for section in self.__sections:
            if section['name'] == "":
                print "File starts with %d lines of stuff"  % len(section['lines'])
            else:
                print "Section -> %s had %d lines" % (section['name'], len(section['lines']))

    def read_file(self, filename=""):
        self.__lines = []
        self.__sections = []
        
        section = {'lines':[], 'name':"", 'tags':[]}
        section_re = re.compile('^\[\S+\]')  
        for line in open(filename,'r'):
            new_section = section_re.search(line)
            if new_section:
                # first save what we have already
                self.__sections.append(section)
                # extract new section name
                section_name = line[new_section.start()+1:new_section.end()-1]
                section = {'name':section_name, 'lines':[], 'tags':[]}
            else:
                if not line.strip().startswith('#') and line.find('=')>=0:
                    fields = line.split('=')
                    if len(fields)>1 and fields[0] in section['tags']:
#                        print 'Overriding previous value for %s' % fields[0]
                        pass
                    else:
                        section['tags'].append(fields[0])
            section ['lines'].append(line)
        if section['lines'] != []:
            self.__sections.append(section)
             
    def write_file(self, filename=""):
        output = open(filename,"w")
        for section in self.__sections:
            for line in section['lines']:
                output.write(line)
        output.close()

    def get_lines(self):
        lines = []
        for section in self.__sections:
            for line in section['lines']:
                lines.append(line)
        return lines

    def get_section_value(self, changes_to_make):
        #if we've already seen the section, work within it
        retval = None
        section_name, tag = changes_to_make

        for section in self.__sections:
            if section['name'] == section_name:
                for linenum in range(len(section['lines'])):
                    if section['lines'][linenum].startswith("%s=" % tag):
                        oldtag, oldval = section['lines'][linenum].split('=')
                        retval = oldval.rstrip()
        return retval

    def set_section_value(self, changes_to_make):
        #if we've already seen the section, work within it
        section_name, tag, value = changes_to_make
        
        change_rec = None
        foundSection = False
        if value != None:
            value = value.rstrip() + "\n"
        try:
            for section in self.__sections:
                if section['name'] == section_name:
                    foundSection = True
                    for linenum in range(len(section['lines'])):
                        if section['lines'][linenum].startswith("%s=" % tag):
                            oldtag, oldval = section['lines'][linenum].split('=')
                            change_rec = [section_name, tag, oldval.rstrip() ]
                            if value == None:
                                del(section['lines'][linenum])
                            else:
                                section['lines'][linenum] = "%s=%s" % (tag, value)
                            raise UserWarning
                    # create change record to 'delete' the tag
                    change_rec = [section_name, tag, None]
                    # ok, didn't fine the tag, so create it, but walk backward from the last line looking for a 
                    # nonblank space, then insert it just after the blank
                    for linenum in range(len(section['lines'])-1, 0, -1):
                        if section['lines'][linenum].strip() != "":
                            break
                    section['lines'].insert(linenum+1, "%s=%s" % (tag, value))
                    raise UserWarning
                    
            # ok, didn't fine the section, so create it - need a corresponding *deletion*
            if not foundSection:
                section = {'name':section_name, 'lines': ["[%s]\n" %section_name ,"%s=%s" % (tag, value)]}
                self.__sections.append(section)
            change_rec = [section_name, tag, None]

        except UserWarning:
            pass
        return change_rec


##############################################################################
if __name__ == '__main__':
    pass
    # tests for iniHandler
    #IP = IniHandler()
    #IP.read_file('/etc/gdm/custom.conf')
    #IP.show_sections()
    #IP.write_file('/tmp/foobar1')
    #changes = []
    #changes.append(IP.set_section_value(["security", "DisallowTCP", None]))
    #changes.append(IP.set_section_value(["security", "AllowRoot", 'false']))
    #IP.write_file('/tmp/foobar2')
    #
    #for c in changes:
    #    print c
    #    IP.set_section_value(c)
    #IP.write_file('/tmp/foobar3')
