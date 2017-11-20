##############################################################################
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
##############################################################################

#
# Scan Filesystems for
# - Uneven file permissions
# - Unowned files
# - Setuid or Setgid files
# - 
#
# Problem Mask:- The problem mask is a simple 8-byte string with either a dash or 
# an X. The letter X indicates that it is True.
#
# 0 - No owner
# 1 - No group
# 2 - Uneven Perms
# 3 - SUID
# 4 - SGID
# 5 - Sticky bit (shared text bit)
# 6 - World writeable
# 7 - Group writeable
# 8 - no SELinux context (unlabeled_t)
#     note - if SELinux is *disabled* will always be '-', can be 'X' if SELinux permissive or enforcing
#

import sys
import os
import stat
import grp
import pwd
import errno
import glob


sys.path.append('/usr/share/oslockdown')
try:
    import TCSLogger
    import sb_utils.file.exclusion
    import tcs_utils
    import sb_utils.SELinux
except ImportError, merr:
    print "Unable to load modules: %s" % merr
    sys.exit(1)

MODULE_NAME = 'GlobalFileScanner'
SCAN_RESULT = "/var/lib/oslockdown/fs-scan/filesystem-scan-results"


##############################################################################
def perform():
    """Inventory files"""
    
    # create a blank entity so the 'del' command at the end of this routine
    # won't cause an exception if we wind up not looking at anything

    list_of_files = ""

    try:
        logger = TCSLogger.TCSLogger.getInstance(6) 
    except TCSLogger.SingletonException:
        logger = TCSLogger.TCSLogger.getInstance() 

    #
    # Open file for writing results to
    #
    try:
        results = open(SCAN_RESULT, 'w')
    except IOError, err:
        msg = "Unable to write to %s: %s" % (SCAN_RESULT, err)
        logger.error(MODULE_NAME, msg)
        raise
    except Exception:
        raise

    msg = "Writing to %s" % SCAN_RESULT
    logger.debug(MODULE_NAME, msg)

    tcs_utils.update_fs_scanid()


    ############ Directory Starting Points ###############
    start_dirs = []
    for fullpath in os.listdir('/'):
        testdir = os.path.join('/', fullpath)
        if not os.path.isdir(testdir):
            continue

        is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(testdir)
        if not is_excluded:
            start_dirs.append(testdir)

    msg = "Starting directory points: %s" % str(start_dirs)
    logger.info(MODULE_NAME, msg)

    ############ Walk the directories ##########
  
    # Before getting started, let's check / to make sure 
    # everything is cool at the top level

    try:
        statinfo = os.stat('/')
        record = __set_problem_mask(fullpath='/', fileinfo=statinfo)
#        if record != '':
#            print "d|%s" % record

    except OSError, err:
        msg = "Unable to stat /: %s" % (err)
        logger.error(MODULE_NAME, msg)


    checked_root_files = False
    # Now start traversing all starting points
    try:
        for subdir in start_dirs:
            msg = "Entering %s..." % subdir
            logger.debug(MODULE_NAME, msg)
    
            for root, dirs, files in os.walk(subdir):
    
                # Before stat'ing file, make sure its path isn't in the 
                # excluded path list
                is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(root)
                if is_excluded == True:
                    # mark the directory and file arrays as empty to short circuit iterator
                    dirs[:] = []
                    files[:] = []
                    msg = "Excluding %s and all child directories : %s" % (root, why_excluded)
                    logger.notice(MODULE_NAME, msg)
                    continue
    
                list_of_files = []
                list_of_files.append(root)
                list_of_files.extend(files)

                if checked_root_files == False:
                    extra_files = glob.glob('/*')
                    for test in extra_files:
                        if os.path.isfile(test):
                            list_of_files.append(test)
                    checked_root_files = True
 

                for infile in list_of_files:
                    if infile != root:
                        testfile = os.path.join(root, infile)
                    else:
                        testfile = root

                    # We need to see if this file is a link - and if so, does it point to a directory to skip?
                    if os.path.islink(testfile):
                        is_excluded, why_excluded = sb_utils.file.exclusion.file_is_excluded(testfile)
                        if is_excluded == True:
                            msg = "Excluding %s as it is a link to an excluded directory : %s" % (testfile, why_excluded)
                            logger.notice(MODULE_NAME, msg)
                            continue
                    
                    try:
                        statinfo = os.stat(testfile)
                    except OSError, err:
                        msg = "Unable to stat %s: %s" % (testfile, err)
                        logger.error(MODULE_NAME, msg)
                        if os.path.islink(testfile) and err.errno == errno.ENOENT:
                            msg  = "%s appears to be a broken link; restore the "\
                                   "target file or remove the link" % (testfile)
                            logger.warning(MODULE_NAME, msg)
                        continue

                    record = __set_problem_mask(fullpath=testfile, fileinfo=statinfo)
                    if record != '':
                        if os.path.isfile(testfile):
                            results.write("f|%s\n" % record)
                            #print "f|%s" % record
    
                        elif os.path.isdir(testfile):
                            results.write("d|%s\n" % record)
                            #print "d|%s" % record

                        elif stat.S_ISCHR(statinfo.st_mode):
                            results.write("c|%s\n" % record)
                            #print "d|%s" % record

                        elif stat.S_ISBLK(statinfo.st_mode):
                            results.write("b|%s\n" % record)
                            #print "d|%s" % record
    except KeyboardInterrupt:
        results.close()
        msg = "Aborting: caught keyboard interrupt -- scan NOT completed" 
        logger.critical(MODULE_NAME, msg)

    except IOError, err:
        if err.errno == errno.EPIPE:
            msg = "Ignoring: %s" % err
            logger.error(MODULE_NAME, msg)
        else: 
            results.close()
            raise

    results.close()
    del statinfo
    del record  
    del list_of_files
    del logger

    return

##############################################################################
def __set_problem_mask(fullpath=None, fileinfo=None):
    """Determine any problems with file"""

    mask = []
    for i in range(9):
        mask.append('-')
           

    bad_files = ['.netrc', '.rhosts', '.shosts', '.Xauthority',
                 'hosts.equiv', 'shosts.equiv']

    # Valid user
    testfile_uid = fileinfo.st_uid
    try: 
        testfile_owner = pwd.getpwuid(testfile_uid)[0]
    except KeyError:
        testfile_uid = -1
        mask[0] = 'X'

    # Valid group owner
    testfile_gid = fileinfo.st_gid
    try: 
        testfile_group = grp.getgrgid(testfile_gid)[0]
    except KeyError:
        testfile_gid = -1
        mask[1] = 'X'
                    
    # Test for SETUID or SETGID and "Sticky bit" ISVTX
    setuid = fileinfo.st_mode & stat.S_ISUID
    setgid = fileinfo.st_mode & stat.S_ISGID 
    setvtx = fileinfo.st_mode & stat.S_ISVTX
    if setuid:
        mask[3] = 'X'

    if setgid:
        mask[4] = 'X'

    if setvtx:
        mask[5] = 'X'


    # World Writeable?
    othwrite = fileinfo.st_mode & stat.S_IWOTH
    if othwrite:
        mask[6] = 'X'

    grpwrite = fileinfo.st_mode & stat.S_IWGRP
    if grpwrite:
        mask[7] = 'X'

    # Uneven Permissions 
    testfile_mode  = int(oct(stat.S_IMODE(fileinfo.st_mode)))
    if testfile_mode < 1000:
        mode_string = str("%04d" % testfile_mode)
    else:
        mode_string = str(testfile_mode)

    if int(mode_string[3]) > int(mode_string[2]) or int(mode_string[3]) > int(mode_string[1]):
        mask[2] = 'X'

    if int(mode_string[2]) > int(mode_string[1]):
        mask[2] = 'X'

    context = sb_utils.SELinux.getContext(fullpath)
    if context and 'unlabeled_t' == context.split(':')[2]:
        mask[8] = 'X'
        
    testfile = fullpath.split('/')[-1]
    record = ''
    if ''.join(mask) != "--------" or testfile in bad_files:
        record = "%s|%d|%d|%s|%s" % (''.join(mask), testfile_uid, testfile_gid, mode_string, fullpath)


    return record
    
##############################################################################
if __name__ == '__main__':
    print perform()
