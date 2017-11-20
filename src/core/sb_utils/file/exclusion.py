##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

#
# Exclusion List
#

import sys
import re
import os

sys.path.append('/usr/share/oslockdown')
try:
    import TCSLogger
    import sb_utils.os.info
    import sb_utils.os.solaris
    import sb_utils.misc.unique
    import sb_utils.filesystem.mount
    import sb_utils.file.fileread
    import sbProps
    
except ImportError, merr:
    print "Unable to load modules: %s" % merr
    sys.exit(1)


MODULE_NAME       = "sb_utils.file.exclusion"

# a few exceptions for our use later
class PathExcluded (Exception):
    pass
   
##############################################################################

class ExclusionList:
    master_list = None
    def __init__(self, refresh=False):
        
        self.local_excludes = []
        
        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 
        
        if ExclusionList.master_list and refresh == True:
            self.logger.log_notice(MODULE_NAME,"Discarding old exclusion list")
            ExclusionList.master_list = None

        if ExclusionList.master_list == None:
            self.logger.log_notice(MODULE_NAME,"Generating fresh exclusion list")
            ExclusionList.master_list = self.exlist_generate()
            msg = "Master exclusion list: %s" % ExclusionList.master_list
            self.logger.log_info(MODULE_NAME, msg)
        else:
#            self.logger.log_notice(MODULE_NAME,"Using existing exclusion list")
            pass
            
    def exlist_generate(self):
        # Read a text file which contains a list of directories
        # then return a unique list of directories
        #
        # Each directory path must be:
        # - Absolute path
        # - Contain no wildcards: * or ?
        # - If parent directory was already listed, don't include child
        #   (e.g., if /opt and /opt/h was provided, only return /opt)
        #

        excldirs = sb_utils.file.fileread.read_files_with_custom_changes("excluded directories", sbProps.EXCLUSION_DIRS, True)

        search_pattern = re.compile("(\*|\?)+")

        # Scrub directory entries
        working_list = []
        for exdir in excldirs:
            exdir = os.path.normpath(exdir.rstrip())
            to_add = [ exdir ]

            # comment next 4 lines to not try to resolve symbolic links or non-canonical path names
            real_exdir = os.path.realpath(exdir)
            if exdir != real_exdir :
                self.logger.log_debug(MODULE_NAME,"%s is a symbolic link or is not canonical, adding it and the real endpoint %s" % (exdir, real_exdir))
                to_add.append(real_exdir)
                       
            for entry in to_add:    
                if not os.path.exists(entry):
                    self.logger.log_debug(MODULE_NAME, "Skipped (does not exist): %s" % entry)
                
                if not entry.startswith('/'):
                    self.logger.log_debug(MODULE_NAME, "Skipped (relative path): %s" % entry)
                    continue

                if entry == '/':
                    self.logger.log_debug(MODULE_NAME, "Skipped: / (must include at least top-level!)")
                    continue

                if search_pattern.search(entry):
                    self.logger.log_debug(MODULE_NAME, "Skipped (bad char): %s" % entry)
                    continue
               
                working_list.append(entry)
                self.logger.log_debug(MODULE_NAME, "Added: %s" % entry)

        del search_pattern
        del excldirs

        # Add some default system directories to the list only if they exists
        for entry in ['/proc', '/selinux'] :
            if os.path.exists(entry):
                working_list.append(entry)
                
        ##########################################################################
        # Identify "Acceptable" filesystem types; and then exclude the 
        fstypes_okay = []
        default_flag = False
        
        fstypes_okay = sb_utils.file.fileread.read_files_with_custom_changes("inclusion-fstypes", sbProps.INCLUSION_FSTYPES, True)
        if not fstypes_okay:
            fstypes_okay.append('ext3')
            fstypes_okay.append('ext2')
            fstypes_okay.append('ufs')
            fstypes_okay.append('zfs')
            msg = "Loaded default filesystem type inclusion list: %s" % str(fstypes_okay)
            self.logger.log_info(MODULE_NAME, msg)
        else:
            msg = "Loaded filesystem type inclusion list from %s" % (sbProps.INCLUSION_FSTYPES)
            self.logger.log_debug(MODULE_NAME, msg)

        ##########################################################################
        # Identify all mount points and add "unacceptable" file system mount points
        # to the exclusion list
        mount_points = sb_utils.filesystem.mount.list()
        for entry in mount_points.keys():
            if mount_points[entry] not in fstypes_okay:
                working_list.append(entry)
                msg =  "Added: %s (fstype='%s')" % (entry, mount_points[entry])
                self.logger.log_debug(MODULE_NAME, msg)

        del fstypes_okay

        ##########################################################################
        # Identify non-global, Solaris zone paths
        if sb_utils.os.info.is_solaris() == True:
            for testzone in sb_utils.os.solaris.zonelist():
                pathname = sb_utils.os.solaris.zonepath(zonename=testzone)
                if pathname != None:
                    working_list.append(pathname)
                    msg =  "Added: %s (child zone's root)" % (pathname)
                    self.logger.log_debug(MODULE_NAME, msg)

        ##########################################################################
        # Final Scrub: Remove subdirectory entries which have already been seen
        # First go through and make sure all directories end with a '/'


        for index,exdir in enumerate(working_list):
          if os.path.isdir(exdir) and not exdir.endswith('/'):
            working_list[index] += '/'
        premaster_list = sb_utils.misc.unique.unique(myarray=working_list)
        premaster_list.sort()

        msg = "Loaded %d unique paths out of the %d provided." % \
                                            (len(premaster_list), len(working_list))
        self.logger.log_info(MODULE_NAME, msg)

        lastdir = ''
        working_list = []
        for index, exdir in enumerate(premaster_list):
            if not os.path.exists(exdir):
                msg = "Skipping %s because it doesn't exist!" % (exdir)
                self.logger.log_debug(MODULE_NAME, msg)
                continue
            if lastdir != '':
                if exdir.startswith(lastdir):
                    msg = "Skipping %s because parent directory %s has already "\
                          "been identified." % (exdir, lastdir)
                    self.logger.log_debug(MODULE_NAME, msg)
                    continue
                else:
                    working_list.append(premaster_list[index])
            else:
                working_list.append(premaster_list[index])

            lastdir = exdir

        # Ok, last pass through.  Go through the list and 'normalize' the path (remove double slashes, etc).  If the 
        # path is to a directory, ensure that it ends with a '/'.
        local_master_list = []
        for entry in working_list:
            entry = os.path.normpath(entry)
            if os.path.isdir(entry):
                entry = entry + "/"
            local_master_list.append(entry)

        del working_list


        return local_master_list
        
    ##########################################################################
    def exlist(self):
        return ExclusionList.master_list



    # given a pathname, return an array starting with the absolute pathname, 
    # and all symbolic link components.  Directory entries will be terminated
    # by a '/' character.  Single files will result in a list of size 1.  If a link
    # is a dangling link
    

    def findFileChain(self, pathname):
            # we can assume our path is absolute and normalized to start with
            pathlist = []
            if os.path.islink(pathname):
                while os.path.islink(pathname):
                        # need to know 'where' we are now in case of a relative symlink..
                        pathdir = os.path.dirname(pathname)
                        if pathname in pathlist:
                                self.logger.log_debug(MODULE_NAME,"%s is a symbolic link and winds up in an infinite loop of symlinks" % (pathname))
                                pathname = None
                                break
                        pathlist.append(pathname)
                        # and now form the 'next' link in the chain
                        pathname = os.path.normpath(os.path.join(pathdir, os.readlink(pathname)))
            if pathname:
                    if os.path.isdir(pathname):
                            pathname += "/"
                    pathlist.append(pathname)
            return pathlist


    # Return (False,"") if the filename passed (or its canonical name) is *NOT* in a directory
    # on the exclusion list -OR- if this filename exactly matches a non-directory
    # entry on the exclusion list
    # Returns (True, msg) with msg explaining why the passed filename should be excluded otherwise
    ##########################################################################
    def file_is_excluded_orig(self, filename):
        
        filename = os.path.normpath(filename.strip())
        
        # entries is an array of paths or path components that need to be checked against the exclusion list.
        entries = [ filename ]
        retval = True
        retmsg = "" 

        # comment next 4 lines to not try to resolve symbolic links or non-canonical path names
        real_entry = os.path.realpath(filename)
        toCheck = [filename]
        if real_entry != filename:
            self.logger.log_debug(MODULE_NAME,"%s is a symbolic link or is not canonical, checking it and the real endpoint %s" % (filename, real_entry))
            toCheck.append(real_entry)
        why = ""   
        
        # if either is a link, then walk through link(s) adding those segments just in case we're bouncing through an excluded directory
        for entry in toCheck:
            if entry not in entries:
                entries.append(entry)
            if entry and os.path.islink(entry):
                linkSegment = entry
#                print "%s is a link .. adding each linksegment to checklist..." % entry
                try:
                    while True:
#                        print entries
                        # readlink throws an error if the argument is *not* a link, so this breaks us out of the loop
                        # we need to get the real path of any link, since that may be a relative link. If the first character
                        # of the link itself is not a '/', then combine the contents with the dirname of the link itself, since
                        # we know *that* is an absolute path already
                        linkContents = os.readlink(linkSegment)
                        if not linkContents.startswith('/'):
                            linkContents = os.path.join(os.path.dirname(linkSegment),linkContents)
                        linkSegment = os.path.realpath(linkContents)
#                        print "\t->%s" % linkSegment
                        if not linkSegment in entries:
                            entries.append(linkSegment)
                        else:
                            if os.path.islink(linkSegment):
                                self.logger.log_debug(MODULE_NAME,"%s is a symbolic link and winds up in an infinite loop of symlinks" % (filename))
                            break
                        
                except OSError, err:
#                    print err
                    pass
#        print entries   
        # so we now know that everything in entries is either the given filename, the *final* canonical name, or intralink names
        # all directories in entries terminate in a '/'


        try:
            for entry in entries:

                if entry == filename or entry==real_entry:
                    canonicalName = ""
                else:
                    canonicalName = " (canonical name %s)" % real_entry

                if os.path.isdir(entry):
                    entry = entry +"/"
                    
                for excl_entry in ExclusionList.master_list + self.local_excludes:
#                    print "%s - %s - %s - %s" % (filename, entry, canonicalName, excl_entry)
                    if not os.path.isdir(excl_entry) and entry == excl_entry:
                        why = "%s %s excluded: Exact match for file %s found in the exclusion list" % (filename, canonicalName, excl_entry)
                    elif entry.startswith(excl_entry) :
                        if entry == excl_entry:
                            why = "%s %s excluded: Exact match for directory %s is on the exclusion list" % (filename, canonicalName, excl_entry) 
                        elif os.path.islink(filename):
                            why = "%s %s excluded: link component %s is on the exclusion list" % (filename, canonicalName, excl_entry)
                        else:
                            why = "%s %s excluded: path component %s is on the exclusion list" % (filename, canonicalName, excl_entry)
                    if why:
                        raise PathExcluded(why)
                
            # ok, walked through the excluded list, this file is not excluded.
            retval = False
            retmsg = ""
        # and now deal with any exclusion messages
        except PathExcluded, why:
            retval = True
            retmsg = str(why)

        return retval, retmsg    


    # Return (False,"") if the filename passed (or its canonical name) is *NOT* in a directory
    # on the exclusion list -OR- if this filename exactly matches a non-directory
    # entry on the exclusion list
    # Returns (True, msg) with msg explaining why the passed filename should be excluded otherwise
    ##########################################################################
    def file_is_excluded(self, filename):
        
        filename = os.path.normpath(filename.strip())
        
        # entries is an array of paths or path components that need to be checked against the exclusion list.
        retval = True
        retmsg = "" 

        # get array with the absolute path of each possible link segment and the final file
        entries = self.findFileChain (filename)
        real_entry = os.path.realpath(filename)
        toCheck = [filename]
        if real_entry != filename:
            self.logger.log_debug(MODULE_NAME,"%s is a symbolic link or is not canonical, checking it and the real endpoint %s" % (filename, real_entry))
            toCheck.append(real_entry)
        why = ""   
        
#        print entries   

        # walk this chain looking for some match to an entry in the exclusion list.
        

        try:
            for entry in entries:

                if entry == filename or entry==real_entry:
                    canonicalName = ""
                else:
                    canonicalName = " (canonical name %s)" % real_entry

                if os.path.isdir(entry):
                    entry = entry +"/"
                    
                for excl_entry in ExclusionList.master_list + self.local_excludes:
#                    print "%s - %s - %s - %s" % (filename, entry, canonicalName, excl_entry)
                    if not os.path.isdir(excl_entry) and entry == excl_entry:
                        why = "%s %s excluded: Exact match for file %s found in the exclusion list" % (filename, canonicalName, excl_entry)
                    elif entry.startswith(excl_entry) :
                        if entry == excl_entry:
                            why = "%s %s excluded: Exact match for directory %s is on the exclusion list" % (filename, canonicalName, excl_entry) 
                        elif os.path.islink(filename):
                            why = "%s %s excluded: link component %s is on the exclusion list" % (filename, canonicalName, excl_entry)
                        else:
                            why = "%s %s excluded: path component %s is on the exclusion list" % (filename, canonicalName, excl_entry)
                    if why:
                        raise PathExcluded(why)
                
            # ok, walked through the excluded list, this file is not excluded.
            retval = False
            retmsg = ""
        # and now deal with any exclusion messages
        except PathExcluded, why:
            retval = True
            retmsg = str(why)

        return retval, retmsg    

        
    def add_excludes(self, extra_excludes):
        for entry in extra_excludes:
            isExcluded, whyExcluded = self.file_is_excluded(entry)
            if not isExcluded:
                self.local_excludes.append(entry)
            else:
                self.logger.log_notice(MODULE_NAME, whyExcluded)
                
# The following two methods *only* reference the 'general' exclusion list as provided in 
# /var/lib/oslockdown/files/exclude-dirs.  If you need to add additional directories/files
# to the list you must instantiate the class, then call the class 'add_excludes' method to add
# the extra files, then call the class 'file_is_excluded' method to do the check


# Return master exclusion list
##########################################################################
def exlist(refresh = False):
    exclusionList = ExclusionList(refresh=refresh)
    return exclusionList.exlist()

# Returns False,"" if the Filename is *not* excluded
# Returns True, text, with text = a message why the filename should be excluded
##########################################################################
def file_is_excluded(filename):
    exclusionList = ExclusionList()
    return exclusionList.file_is_excluded(filename)
    
if __name__ == '__main__':
    try:
       logger = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
       logger = TCSLogger.TCSLogger.getInstance() 
    logger.forceToStdout()
    print exlist()
    print file_is_excluded("/dev/snd")
    print file_is_excluded("/dev/stdin")
    print file_is_excluded("/proc/self/fd/0")
    print file_is_excluded("/proc")
    print file_is_excluded("/proc/sys")
    print file_is_excluded("/z1")
    print file_is_excluded("/usr/sbin/alsactl")   
    print file_is_excluded("/tmp/linktest/a")   
    print file_is_excluded("/dev/foobtest")   
    print file_is_excluded("/dev/null")
