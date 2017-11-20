#!/bin/env python

# A script to update the version number in those files that otherwise
# cannot pick up the version from an environment variable.  For example,
# the SELinux policies have a hardcoded version in the type-enforcement files
# that matches the current OS Lockdown version.
#
# Note that there is a different update piece for each type of file,
# and the going in assumption on *each* change is that we're looking for
# the first non-commented line that matches our regex.  
#
#
# The version information is in the file VERSION_RELEASE.txt, and consists
# of two 'tag=value' lines.
#   SB_VERSION=>X.Y.Z>
#   SB_RELEASE=<text>
#
#   <X.Y.Z> are integer values representing the major/minor/point release numbers
#   <TEXT> is arbitrary freetext with *NO* whitespace representing some info
#       about the release (for example, 'alpha', 'rc1').

import sys
import glob
import re

def get_release_info():
    sb_version = None
    sb_release = None
    try:
        for line in open('VERSION_RELEASE.txt'):
            if '=' not in line:
                continue
            tag,value = [v.strip() for v in line.split('=',1) ]
            if tag == "SB_RELEASE":
	            sb_release = value	   
            elif tag == "SB_VERSION":
                sb_version = value
    except (IOError, OSErro), e:
        print "Unable to open 'VERSION_RELEASE.txt' : %s" % e
        sys.exit(1)
    
    if not sb_version:
        print "Unable to identify SB_VERSION text in file, aborting"
        sys.exit(1)
    if not sb_release:
        print "Unable to identify SB_RELEASE text in file, aborting"
        
    return sb_version, sb_release

def update_selinux_policies(sb_version, sb_release):
    regex = re.compile ('^(?P<head>policy_module\(oslockdown,)(\d+\.\d+\.\d+)(?P<tail>\))$',re.MULTILINE)
    teFiles = glob.glob('src/selinux/*/*.te')
    for fileName in teFiles:
        try:
            print "Inserting version number %s info %s" % (sb_version, fileName)
            text = open(fileName).read()
            text = regex.sub('\g<head>%s\g<tail>' % sb_version, text, 1)         
            open(fileName,"w").write(text)
        except Exception, e:
            print "Unable to version in %s: %s" % (fileName,e)

def update_docs_common_entities(sb_version, sb_release):
    regex = re.compile ('^(?P<head><!ENTITY SB_prodvers\s+")(\d+\.\d+\.\d+)(?P<tail>">)$',re.MULTILINE)
    fileName = "docs/COMMON_ENTITIES.ent"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex.sub('\g<head>%s\g<tail>' % sb_version, text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)

def update_include_version_h(sb_version, sb_release):
    regex = re.compile ('^(?P<head>#define APPLICATION_VERS\s+")(\d+\.\d+\.\d+)(?P<tail>")$',re.MULTILINE)
    fileName = "src/include/version.h"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex.sub('\g<head>%s\g<tail>' % sb_version, text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)

def update_modules_xml_wrapper(sb_version, sb_release):
    regex = re.compile ('^(?P<head><oslockdown version=")(\d+\.\d+\.\d+)(?P<tail>">)$',re.MULTILINE)
    fileName = "src/security_modules/cfg/prod_sources/WRAPPER.xml"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex.sub('\g<head>%s\g<tail>' % sb_version, text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)

def update_core_sbProps(sb_version, sb_release):
    regex = re.compile ('^(?P<head>VERSION\s+=\s+")(\d+\.\d+\.\d+)(?P<tail>")$',re.MULTILINE)
    fileName = "src/core/sbProps.py"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex.sub('\g<head>%s\g<tail>' % sb_version, text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)

def update_default_properties(sb_version, sb_release):
    regex = re.compile ('^(?P<head>product.version\s+=\s+)(\d+\.\d+\.\d+)$',re.MULTILINE)
    fileName = "default.properties"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex.sub('\g<head>%s' % sb_version, text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)

def update_Makefile_common_mk(sb_version, sb_release):
    regex1 = re.compile ('^(?P<head>export\s+SB_VERSION\s+\?=\s+)(\d+\.\d+\.\d+)$',re.MULTILINE)
    regex2 = re.compile ('^(?P<head>export\s+SB_RELEASE\s+\?=\s+)(\S+)$',re.MULTILINE)
    fileName = "Makefile_common.mk"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex1.sub('\g<head>%s' % sb_version, text, 1)         
        text = regex2.sub('\g<head>%s' % sb_release, text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)

def update_console_application_properties(sb_version, sb_release):
    # gets re-written when Console is built, but do it here anyway
    regex = re.compile ('^(?P<head>app.version=)(\d+\.\d+\.\d-\S+)$',re.MULTILINE)
    fileName = "src/console/grails/OSLockdown/application.properties"
    try:
        print "Inserting version number %s info %s" % (sb_version, fileName)
        text = open(fileName).read()
        text = regex.sub('\g<head>%s-%s' % (sb_version,sb_release), text, 1)         
        open(fileName,"w").write(text)
    except Exception, e:
        print "Unable to version in %s: %s" % (fileName,e)
    
if __name__ == "__main__":
    sb_version, sb_release = get_release_info()
    print "SB_VERSION is %s" % sb_version
    print "SB_Release is %s" % sb_release

    update_selinux_policies(sb_version, sb_release)
    update_docs_common_entities(sb_version, sb_release)
    update_include_version_h(sb_version, sb_release)
    update_modules_xml_wrapper(sb_version, sb_release)
    update_core_sbProps(sb_version, sb_release)
    update_default_properties(sb_version, sb_release)
    update_Makefile_common_mk(sb_version, sb_release)
    update_console_application_properties(sb_version, sb_release)
