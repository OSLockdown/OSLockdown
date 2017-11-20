#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#


#Top level 'public' function:
#
# removeSysAcct(sysAcctName=None, extraDirs=[], extraFiles=[])
#   sysAcctName  : string holding of account to remove
#   extraDirs    : list of directories to search (recursively) for files owned by this owner/group - reown by root
#   extraFiles   : list of strings of extra files/directories to search non-recursively as above
#
# restoreSysAcct(change_rec)
#   change_rec = string holding change record produced by removeSysAcct (either 4.0.1 version or post 4.0.2)
#




import sys
import pwd
import grp
import os, stat
import tarfile
import glob

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils
import sb_utils.os.info
import sb_utils.SELinux
import sb_utils.file.exclusion
import sb_utils.file.fileperms

try:
    foobar = set([])
except NameError:
    from sets import Set as set


##############################################################################
# Attempt to remove a system account - we don't check first to see if it exists!
#
# Return a change record suitable to be resubmitted to restoreSysAcct to return the
# account
# We change file ownership prior to deleting the user account, since we try to do a lookup of the
# username from the actual file uid.  If we deleted the account first, we'd never be able to do the 
# lookup of uname from uid
#
def removeSysAcct(sysAcctName=None, extraDirs=None, extraFiles=None):
    logger = TCSLogger.TCSLogger.getInstance()
    if sysAcctName == None:
        msg = "Unable to remove account, no user name given to remove"
        logger.log_err('sb_utils.acctmgt.files.removeSysAcct', msg)
        return None

    if type(extraFiles) == type(""):
        extraFiles = extraFiles.split()
    elif type(extraFiles) != type([]):
        extraFiles = []

    if type(extraDirs) == type(""):
        extraDirs = extraDirs.split()
    elif type(extraDirs) != type([]):
        extraDirs = []
        
    # get info to rebuild account
    try:
        pwent = pwd.getpwnam(sysAcctName)
    except KeyError:
        msg = "Unable to remove account '%s', no such user" % sysAcctName
        logger.log_err('sb_utils.acctmgt.acctfiles.removeSysAcct', msg)
        return None
    try:
        grent = grp.getgrnam(sysAcctName)
        uname_gname_match = True
    except KeyError:
        grent = None
        msg = "No matching group name for '%s'" % sysAcctName
        logger.log_info('sb_utils.acctmgt.acctfiles.removeSysAcct', msg)
        uname_gname_match = False
        
    acct_user    = pwent.pw_uid
    acct_gid     = pwent.pw_gid
    acct_gecos   = pwent.pw_gecos
    acct_dir     = pwent.pw_dir
    acct_shell   = pwent.pw_shell
    primarygrent = grp.getgrgid(acct_gid)
    acct_group   = primarygrent.gr_name

    grp_mem = []
    for gr in grp.getgrall():
        if sysAcctName in gr.gr_mem:
            grp_mem.append(gr.gr_name)
    

    account_record = {'uname':sysAcctName,
                    'uid':acct_user,
                    'gname':acct_group,
                    'gid':acct_gid,
                    'gecos':acct_gecos,
                    'homedir': acct_dir,
                    'shell': acct_shell,
                    'gr_mem': grp_mem}
                    
    # Corner case: detect accounts like 'games', where there is a username 'games', and a group 'games'
    # but the primary group of the user does *not* match the group name.  Otherwise when we delete the
    # user account the *group* will also be delete, but we won't be able to restore things correctly
    # when we undo what we did.  So in the case where there are both a user and group with this name,
    # but the user primary GID is not that of the group (ie GID(user) != GID(group) where user==group)
    # we need supplemental info to recreate the group (if it didn't exists later).     

    if sysAcctName != acct_group and grent != None:
        account_record['supgname'] = grent.gr_name
        account_record['supgid']   = grent.gr_gid
        

    change_attrs = {'owner':'root', 'group':'root', 'if_user_is':sysAcctName, 'dacs':'0000'}

    # Do we have a group whose name *matches* this host name?  If so, then pass that through as well to match for ownership
    # as some files may be owned by either by the uid or gid matching this account name.  I really don't want to have to 
    # implement different behaviors for RH(4/5), SUSE11, and Fed(10/11/12/...)
    
    if uname_gname_match == True:
        change_attrs.update({'if_group_is':sysAcctName})

    # add potential mail, spool,  and other stuff in /var files if not already in the extrafiles fields
    
    for spoolbasedir in [ "/var/spool" , "/var/mail", "/var/log", "/var/run" ] :
        spooldir = "%s/%s" % (spoolbasedir, sysAcctName)
        if spooldir not in extraDirs:
            extraDirs.append(spooldir)
    
    # alter file ownerships..
    msg = "Changing ownership of files owned by '%s' in the home account (%s) to root:root, with perms of 000." % (sysAcctName, acct_dir) 
    logger.log_info('sb_utils.acctmgt.acctfiles.removeSysAcct',  msg)
    options = {'recursive':True, 'checkOnly':False, 'exactDACs':True}
    file_changes = sb_utils.file.fileperms.change_file_attributes(pathname=acct_dir , changes=change_attrs, options=options)

    for extraDir in extraDirs:
        if extraDir == acct_dir : 
            continue 
        thisrec = sb_utils.file.fileperms.change_file_attributes(pathname=extraDir, changes=change_attrs, options=options)
        if thisrec != None:
            file_changes.update(thisrec)
    # Ok, regardless now of whether or not a file is or is not a directory, do *not* recurse for extrafiles
    options['recursive'] = False
    for extraFile in extraFiles:
        if extraFile == acct_dir : 
            continue 
        thisrec = sb_utils.file.fileperms.change_file_attributes(pathname=extraFile, changes=change_attrs, options=options)
        if thisrec != None:
            file_changes.update(thisrec)


    # go delete the account itself
    cmd = "/usr/sbin/userdel %s" % sysAcctName
    output_tuple = [0]
    output_tuple = tcs_utils.tcs_run_cmd(cmd, True)

    if output_tuple[0] != 0:
        msg = 'Attempt to delete %s account failed.' % sysAcctName
        logger.log_err('sb_utils.acctmgt.acctfiles.removeSysAcct', 'Apply Error: ' + msg)
        msg = 'Reverting file renames'
        logger.log_err('sb_utils.acctmgt.acctfiles.removeSysAcct', 'Apply Error: ' + msg)
        # we have an exact set, so call directly in to alter the files
        sb_utils.file.fileperms.change_bulk_file_attributes(file_changes)
        return None
     
    return  {'acctinfo':account_record, 'filelist':file_changes}




##############################################################################
# Attempt to restore a given system account and optional files following the passed
# change record.  We'll first see if the change_record looks like a dictionary, then 
# we'll process it as a string to see if contains a dictionary, then we'll finally
# try to see if it an 'old' style record from 4.0.1 (this routine emerges in 4.0.1)
#
#
# This routine uses several helper routines below to validate the desired username,UID,acctGroup,GID fields
# Should the indicated UID/GID be unavailable, find the next available UID/GID and use it.
# Returns a 1 if successful, 0 otherwise, with errors being logged

def restoreSysAcct(change_record=None):
    logger = TCSLogger.TCSLogger.getInstance()

    if type(change_record) == type({}):
#        print change_record.keys()
        accountData = change_record
    else:
        msg = "Converting string to dictionary..." 
        logger.log_info('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)            
        try:
            accountData = tcs_utils.string_to_dictionary(change_record)
        except SyntaxError:
            accountData = _change_old_restore_to_new_restore(change_record)              
    
    try:
        accountInfo = accountData['acctinfo']
        filelist    = accountData['filelist']
    except KeyError, err:
        msg = "Unable to process restore dictionary: %s" % (err)
        logger.log_err('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)            
        return False    
        
    
    ## quickly verify that we have all of the pieces we need to restore the Account

    for key in ['uname', 'uid', 'gname', 'gid', 'gecos', 'homedir', 'shell' ]:
        if not accountInfo.has_key(key):
            msg = "Unable to restore account - missing required '%s' field." % (key)
            logger.log_err('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
            return False    

    acctName   = accountInfo['uname'] 
    acctUID    = accountInfo['uid'] 
    acctGroup  = accountInfo['gname'] 
    acctGID    = accountInfo['gid'] 
    acctGECOS  = accountInfo['gecos'] 
    acctDir    = accountInfo['homedir'] 
    acctShell  = accountInfo['shell'] 
    
    if acctName == None or acctUID == None or acctGroup == None or acctGID == None :
        if acctName == None : 
            msg = "acctName must not be None"
        elif acctUID == None :
            msg = "acctUID must not be None"
        elif (acctGroup == None) :
            msg = "acctGroup must not be None" 
        elif (acctGID == None) :
            msg = "acctGID must not be None" 

        logger.log_err('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
        return False

    
    # Validate the requested username/uid acctGroup/gid entries, or allocate new uid/gid if there's a conflict
    # If we can't identify the correct uig/gid to use (or can't create the numbers) punt
    #
    # NOTE - Entries to the password and group files are *not* made by the two routines below!
    #
    thisUID, msg = _verify_acct_uid(acctName, acctUID)
    if thisUID == None:
        logger.log_err('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
        return False
        
    thisGID, msg = _verify_acct_gid(acctGroup, acctGID)
    if thisGID == None:
        logger.log_err('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
        return False
    
    if accountInfo.has_key('supgname') and accountInfo.has_key('supgid'):
        supGroup = accountInfo['supgname']
        supGID = accountInfo['supgid']
        thissupGID, msg = _verify_acct_gid(supGroup, supGID)
        if thisGID == None:
            logger.log_err('sb_utils.acctmgt.acctfiles.restoreSysAcct', '(Supplimental group) ' + msg)
        
        msg = "Supplimental group info found for '%s'" % (acctName)
        logger.log_info('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
    else:
        supGroup = None
        thissupGID = None
    
    if accountInfo.has_key('gr_mem'):
        gr_mem = accountInfo['gr_mem']
    else:
        gr_mem = []
                
    msg = "Asked to restore account '%s' with group '%s'" % (acctName, acctGroup)
    logger.log_info('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
    if thisUID != acctUID :
        msg = "Account '%s' :original UID not available, using next available system UID" % acctName
        logger.log_info('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
    if thisGID != acctGID :    
        msg = "Group '%s' :original GID not available, using next available system GID" % acctGroup
        logger.log_info('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)

    # Borrowed the rest of this from the 'RemoveFTPaccount.py' code, modified to use thisUID/thisGID and acctName,acctGroup 
    
    msg = "Trying to restore %s" % acctName
    logger.log_info('sb_utils.acctmgt.acctfiles.restoreSysAcct', msg)
    if _restore_account_info(acctName, thisUID, acctGroup, thisGID, acctGECOS, acctDir, acctShell, gr_mem, supGroup, thissupGID) == False:
        return False
       
    ignore_results = sb_utils.file.fileperms.change_bulk_file_attributes(filelist)

    return True


def _verify_acct_uid(acctName, acctUID): 
    # check to see if account already exists
    thisUID = None
    msg = ''
    try :
        # expliticly check with all 'potential' providers of user ID's to prevent masking of an external one...
        ents = pwd.getpwall()
        acct_inuse = False
        id_inuse   = False
        for ent in ents:
            if ent.pw_name == acctName:
                acct_inuse = True
            if ent.pw_uid == acctUID:
                id_inuse = True
        if acct_inuse :       
            # Bail if username is already in use
            msg = "User '%s' already exists" % acctName
            acctUID = None
        elif  id_inuse or acctUID < 0:  
            if id_inuse :
                msg = "UID %s in use, will use next available system UID" % acctUID
            elif acctUID < 0 :
                msg = "UID unspecified, will use next available system UID"
            
            # find the next available 'system' id
            if sb_utils.os.info.is_solaris() == True:
                sysid_min = 10
                sysid_max = 100
            else:
                sysid_min = 10
                sysid_max = 500

            # find a list of all 'system' uids that aren't in use
            sys_uids  = range(sysid_min, sysid_max)
            uids      = [ent.pw_uid for ent in ents]
            free_uids = [ uid for uid in set(sys_uids)-set(uids)]
            free_uids.sort()
            if len(free_uids) == 0 :
                msg = "No unused system UID's available"
                thisUID = None
            else:
                thisUID = free_uids[0]
        else:
            # account name and desired UID free, so use it
            thisUID = acctUID
            
    except Exception, e:
        msg = e
        thisUID = None

    return thisUID, msg
    
# If the group already exists, then return that acctGID, we'll use it 
# If not, and the acctGID isn't already in use we'll use that
# Otherwise try to find the first available group number and return it
#
# NOTE - DOES NOT CREATE GROUP ENTRY!
#
# Returns <num>,<string>  where num==None on fail

def _verify_acct_gid (acctGroup, acctGID):
    thisGID = None
    msg = ""
    try:
        gname_inuse = False
        gid_inuse = False
        thisGID = None
        ents = grp.getgrall()
        for ent in ents:
            if ent.gr_name == acctGroup:
                thisGID = ent.gr_gid
                gname_inuse = True
                gid_inuse = True
                break
            if ent.gr_gid == acctGID:
                gid_inuse = True
        if gname_inuse :
            pass
        elif gid_inuse == True or acctGID < 0:
            if gid_inuse :
                msg = "GID %s in use, will use next available system GID" % acctGID
            elif acctGID < 0 :
                msg = "GID unspecified, will use next available system GID"
        # find first available system group id
            if sb_utils.os.info.is_solaris() == True:
                sysgid_min = 10
                sysgid_max = 100
            else:
                sysgid_min = 10
                sysgid_max = 500

            # find a list of all 'system' uids that aren't in use
            sys_gids  = range(sysgid_min, sysgid_max)
            gids      = [ent.gr_gid for ent in ents]
            free_gids = [ gid for gid in set(sys_gids) - set(gids)]
            free_gids.sort()
            if len(free_gids) == 0 :
                msg = "No unused system GID's available"
                thisGID = None
            else:
                thisGID = free_gids[0]
        else:
            thisGID = acctGID
    except Exception, e:
        msg = e
        thisGID = None

    return thisGID, msg



def _restore_account_info(acctName, thisUID, acctGroup, thisGID, acctGECOS, acctDir, acctShell, gr_mem, supGroup, supGID):
    logger = TCSLogger.TCSLogger.getInstance()
    msg = ""
    try:
        new_gid = int(grp.getgrnam(acctGroup)[2])
        if new_gid != thisGID:
            msg = "Newly added GID does not match requested GID, files restored using requested GID"
            logger.log_notice('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
    except KeyError:
        if sb_utils.os.info.is_solaris() == True:
            cmd = "/usr/sbin/groupadd -g %s %s" % (str(thisGID), acctGroup)
        else:
            cmd = "/usr/sbin/groupadd -r -g %s %s" % (str(thisGID), acctGroup)
        output_tuple = tcs_utils.tcs_run_cmd(cmd, True)
        if output_tuple[0] != 0:
            msg = "Attempt to add '%s' group account failed: %s" % (acctGroup, output_tuple[2])
            logger.log_err('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
            return False
    
    # 
    try:
        ftp_grp_struct = grp.getgrnam(acctGroup)
    except KeyError:
        msg = "Attempt to add '%s' group account failed: %s" % (acctGroup, output_tuple[2])
        logger.log_err('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
        return False

    if sb_utils.os.info.is_solaris() == True:
        cmd = "/usr/sbin/useradd -u %s -g %d -s '%s' -d %s -c '%s' %s " % (str(thisUID), ftp_grp_struct.gr_gid, acctShell, acctDir, acctGECOS, acctName)
    else:
        cmd = "/usr/sbin/useradd -u %s -g %d -s '%s' -M -d %s -c '%s' %s" % (str(thisUID), ftp_grp_struct.gr_gid, acctShell, acctDir, acctGECOS, acctName)

    output_tuple = tcs_utils.tcs_run_cmd(cmd, True)
    if output_tuple[0] != 0:
        msg = "Attempt to add '%s' account failed: %s" % (acctName, output_tuple[2])
        logger.log_err('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
        return False

    if supGroup != None and supGID != None:
        
        if sb_utils.os.info.is_solaris() == True:
            cmd = "/usr/sbin/groupadd -g %s %s" % (str(supGID), supGroup)
        else:
            cmd = "/usr/sbin/groupadd -r -g %s %s" % (str(supGID), supGroup)
        output_tuple = tcs_utils.tcs_run_cmd(cmd, True)
        if output_tuple[0] != 0:
            msg = "Attempt to add '%s' supplimental group account failed: %s" % (supGroup, output_tuple[2])
            logger.log_warn('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
    
    # 
        try:
            ftp_grp_struct = grp.getgrnam(supGroup)
        except KeyError:
            msg = "Attempt to add '%s' supplimental group account failed: %s" % (supGroup, output_tuple[2])
            logger.log_warn('sb_utils.acctmgt.acctfiles._restore_account_info', msg)

    if gr_mem != []:
        # get a list of all groups, so we can verify that all of the groups that this user was a member of still exist
        all_group = [ gr.gr_name for gr in grp.getgrall() ]
        grp_to_append = []
        grp_missing = []
        for gr in gr_mem:
            if gr in all_group:
                grp_to_append.append(gr)
            else:
                grp_missing.append(gr)
            
        if grp_missing:
            msg = "Unable to add user '%s' to missing groups %s" % (acctName, ','.join(grp_missing))
            logger.log_warn('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
        if grp_to_append:
            msg = "Adding user '%s' to following groups %s" % (acctName, ','.join(grp_to_append))
            cmd = "/usr/sbin/usermod -G %s %s" % (','.join(grp_to_append), acctName)
            output_tuple = tcs_utils.tcs_run_cmd(cmd, True)
            if output_tuple[0] != 0:
                msg = "Unable to add '%s' to one or more groups: %s" % (acctName, output_tuple[2])
                logger.log_warn('sb_utils.acctmgt.acctfiles._restore_account_info', msg)
                    
            
    return True
    

### An old restore record consists of an array of lines
### Line one is the account name info, with the rest being files to rename/restore
### Line one should be "uid|gname|gid|gecos|homedir|shell"
### subsequent lines should be "uid|gid|filename"
### we do make assumptions here that *only* filelines have 3 elements here in the conversion
### we assume that the uid/gid from the file list *matches* the uid/gid from the userinfo

### a new restore record is a dictionary with acctinfo,filelist
### the acctinfo is a dictionary with keys uname,uid,gname,gid,gecos,homedir,shell
### the filelist is a dictionary of fileinfo elements keyed by filename
### each fileinfo is a dictionary with keys uname,gname,dacs,macs
###
### Note that each of uname,gname,dacs, and macs are *OPTIONAL*, and the appropriate chown/chgrp/chmod/ <mac change> operations
### will not be done if the field is not present.

def _change_old_restore_to_new_restore(old_rec=None):
    if old_rec == None:
        return None
    
    uname = ""
    gname = ""
    acctinfo = {}
    filelist = {}
    for line in old_rec.splitlines():
        fields = line.split('|')
        if len(fields) == 7:   # assume user info
            acctinfo = {}
            acctinfo['uname']   = fields[0]
            acctinfo['uid']     = int(fields[1])
            acctinfo['gname']   = fields[2]
            acctinfo['gid']     = int(fields[3])
            acctinfo['gecos']   = fields[4]
            acctinfo['homedir'] = fields[5]
            acctinfo['shell']   = fields[6]
            uname = fields[0]
            gname = fields[2]
        elif len(fields) == 3:   # assume file data
            filelist[fields[2]] = {'owner':uname, 'group':gname}
        else:
            newrec = {}
    newrec = {'acctinfo':acctinfo, 'filelist':filelist}
    return newrec
    
