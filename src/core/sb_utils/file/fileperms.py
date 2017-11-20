#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#Top level 'public' function:
#
#
# change_file_attributes(pathname=None, changes={}, recursive=False)
#   pathname = file or directory name to change
#   changes = dictionary holding items to change
#             'owner','group','if_user_is','if_group_is','dacs' permitted keys
#   recursive = flag to recurse if pathname is a directory
#

import sys
import pwd
import grp
import os
import stat
import tarfile
import glob
import shlex

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils
import sb_utils.os.info
import sb_utils.SELinux
import sb_utils.file.exclusion
import sb_utils.file.dac
import sb_utils.file.whitelists
import sb_utils.acctmgt.users

class ChangeFileAttributes:

    def __init__(self, options={} ):
#        print "INIT_OPTIONS",options
        self._recursive      = self._verify_options(options, 'recursive',      False)      
        self._ignoreExcludes = self._verify_options(options, 'ignoreExcludes', False) 
        self._exactDACs      = self._verify_options(options, 'exactDACs',      False)
        self._checkOnly      = self._verify_options(options, 'checkOnly',      True)       
        self.logger = TCSLogger.TCSLogger.getInstance()

        self.matchMode       = 0
        try:
            self.matchMode = options['matchMode']
        except:
            pass
                    
            
            
    def _verify_options(self, options, optname, defval):
        retval = defval
        try:
            if options[optname] in ["1", True]:
                retval = True
            elif options[optname] in ["0", False]:
                retval = False
        except KeyError:
            pass
        return retval



    ##########################################################################
    # attributes is a dictionary of things to change
    #  *NOTE* INTERNAL ROUTINE - assumes all checking/conversions done prior to being called (each of these are optional)
    #       if_user_is  = only allow change *if* current user matches
    #       if_group_is = only allow change *if* current group matches
    #       owner = comma separated list of allowed unames (if mismatch then chown to first entry) 
    #       group = comma separated list of allowed gnames  ( if mismatch then chown to first entry)
    #       dacs     = discretionary access control settings for the file (as decimal integer number)
    #       macs     = mandatory access control settings will be added later
    #
    #
    # Will return a change_rec (or {} if no changes made) that would restore the item.  Note that the change_rec uses uid, gid, and decimal dacs

    # If pathname is a link, then ownership changes will be made to all entries of the link *without a change record being generated for them*,
    # since the links will be chased again when we're called.  We *will* log a message that we're link chasing however

    def makeChanges(self, pathname, attribs_in={}):
        msg = ""
        rec = ""
        
        # since we potentially alter this, we need to explicitly copy the given value,
        
        attribs = attribs_in.copy()
        change_rec = {}  
        carryBits = 0
        bits = []
        initial_pathname = pathname
        
        # is the given path excluded?
        isExcluded = False
        if not self._ignoreExcludes:
            isExcluded, whyExcluded =  sb_utils.file.exclusion.file_is_excluded(pathname)
        if isExcluded:
            msg = "Excluding %s: %s" % (pathname, whyExcluded)
            self.logger.log_notice('sb_utils.file.fileperms.makeChanges', msg)
            return change_rec

        # first see if the file is even there...
        # and if we're restricting our searches a certain type of files. using the symbolic flags as per the stat module 
        # (IE stat.S_IFREG = regular file, stat.S_IFDIR = directory) flags can be logically added, and then compared to the current mode
        # of the file itself.  Unless otherwise specific, the default mode is ~1, to match any flag.
          
        try:
            statinfo = os.stat(pathname)     # Explicit -> if a link, look at the file being linked to
            if (self.matchMode > 0) and (statinfo.stat & self.matchMode):
                msg = "%s: filemode (%o) does not match search criteria" % (pathname, statinfo.stat)
                self.logger.log_debug('sb_utils.file.fileperms.makeChanges', msg)
                return change_rec
                
        except OSError, err:
            msg = "%s: %s" % (pathname, err)
            self.logger.log_info('sb_utils.file.fileperms.makeChanges', msg)
            return change_rec
        
        if 'owner' in attribs or 'group' in attribs:
            already_seen = []
            if os.path.islink(pathname):
    #            self.logger.log_notice("LINK CHAIN START -> ",pathname)
                pass            
            while os.path.islink(pathname):
    #            self.logger.log_notice("++++",pathname)
                # ok, first things first - split into directory and path
                dirPart, filePart = os.path.split(pathname)
                # reassemble, replacing what looks like the directory name with the *real* directory name (resolving embedded links, etc)
                pathname = os.path.join(os.path.realpath(dirPart), filePart)
                already_seen.append(pathname)
                nextlink = os.readlink(pathname)
                
                if not nextlink.startswith('/'):
                    nextlink = os.path.join(os.path.dirname(pathname), nextlink)
                pathname = os.path.normpath(nextlink)
                if pathname in already_seen:
                    msg = "%s seems to lead into an infinite loop - link chasing done" % initial_pathname
                    self.logger.log_info('sb_utils.file.fileperms.makeChanges', "Link chasing -> " + msg)
                    break
                if not os.path.islink(pathname):
    #                self.logger.log_notice("LINK CHAIN END -> ",pathname)
                    pass                

            # double check to see if we did link chaining.... have we been exluded ?
            ifExcluded = False

            # check to see if we have any restrictions on current ownership or group
            isExcluded, whyExcluded = self.check_current_restrictions(pathname, statinfo, attribs)
                  
            # Ok, we passed phase one exclusion, check the global list if asked...
            
            if not isExcluded and not self._ignoreExcludes:
                isExcluded, whyExcluded =  sb_utils.file.exclusion.file_is_excluded(pathname)

            if isExcluded:
                msg = "Excluding %s: %s" % (pathname, whyExcluded)
                self.logger.log_notice('sb_utils.file.fileperms.makeChange', msg)
                return change_rec
            else:
                rec = self.check_ownership(pathname, statinfo, attribs)
                # Note - chown can strip SUID/SGID bits, but this behavior depends on the kernel.  So we need to check the status
                # before/after any chown command and preserve those bits if they get knackered.
                if rec :
                  newstatinfo = os.stat(pathname)     # Explicit -> if a link, look at the file being linked to
                  if statinfo != newstatinfo:          # Ok, the chown altered the bits, probably removing the SUIG/SGID flags.  We need to preserve them
		    if ((statinfo.st_mode ^ newstatinfo.st_mode) & stat.S_ISUID):
                       carryBits = carryBits | stat.S_ISUID
                       bits.append('SUID')
		    if ((statinfo.st_mode ^ newstatinfo.st_mode) & stat.S_ISGID):
                       carryBits = carryBits | stat.S_ISGID
                       bits.append('SGID')
                    if bits: 
                       msg = "chown call stripped the %s bits from '%s', preserving for later undo" % (', '.join(bits), pathname) 
                       self.logger.log_notice('sb_utils.file.fileperms.makeChange', msg)
                    statinfo = newstatinfo
            change_rec.update(rec)
            
        if rec != "SKIP" and 'dacs' in attribs:
            rec = self.check_dacs(pathname, statinfo, attribs)
            change_rec.update(rec)

        #Ok, consider any carrBits from the chown (if any) and make sure they are preserved in the change record
        if carryBits:
            dacs = 0
            if 'dacs' in change_rec:
              dacs_value = self._convert_dacs(change_rec['dacs'])['dacs_value'] 
              newdacs_value = dacs_value | carryBits
              change_rec['dacs'] = self._convert_dacs(newdacs_value)['dacs_str']
#              print "%s ---->   CARRY BITS = %04o   olddac = %04o  newdac = %04o" % (pathname, carryBits, dacs_value, newdacs_value)
         
        if len(change_rec) > 0 :
            return {pathname:change_rec}
        else:
            return {}        

        
    def check_current_restrictions( self, pathname, statinfo, attribs):
        """
        returns True if file is to be excluded because it doesn't match the current restrictions, false otherwise
        if true, then msg holds the text as to why
        This looks at the 'if_user_is' and 'if_group_is' fields of the attribs structure.  All criteria must match to pass
        """

        ifCurrentUname = None
        ifCurrentUID = None
        
        ifCurrentGname = None
        ifCurrentGID = None
        msg = "file changes not restricted to particular user/group ownership"
        try:
            if 'if_user_is' in attribs:
                ifCurrentUname = attribs['if_user_is']
                ifCurrentUID  = self._map_uid_uname(ifCurrentUname)['uid']
            if 'if_group_is' in attribs:
                ifCurrentGname = attribs['if_group_is']
                ifCurrentGID  = self._map_gid_gname(ifCurrentGname)['gid']

        except Exception, err:
            msg = "Skipping %s: %s" % ( pathname, err)
            self.logger.log_info('sb_utils.file.fileperms.check_ownership', link_preface + msg)
            return True, msg
            
#        print "\npathname       " , pathname
#        print "ifCurrentUname " , ifCurrentUname
#        print "ifCurrentUID   " , ifCurrentUID
#        print "ifCurrentGname " , ifCurrentGname
#        print "ifCurrentGID   " , ifCurrentGID
#        print "uid            " , statinfo.st_uid
#        print "gid            " , statinfo.st_gid
            
#       assume we skip *unless* we match 
        # if we don't either check, then assume are skipping unless we match
        # if there are no checks to do, then do not skip....
        
        if ifCurrentUname or ifCurrentUID:
            skip = True
            if ifCurrentUname and ifCurrentUID == statinfo.st_uid: 
                skip = False                                       
        
            if ifCurrentGname and ifCurrentGID == statinfo.st_gid: 
                skip = False                                       
        else:
            skip = False    
        if skip:
            msg = "%s: doesn't match requested owner/group criteria" % ( pathname )
        
#        print skip, msg
        return skip, msg    

    def check_ownership(self, pathname, statinfo, attribs):
        msg = ""
        change_rec = {}    
        skip = False
        what_changed = []
        instead_of = []
        
        ifCurrentUname = None
        ifCurrentUID = None
        allowedUnames = []
        allowedUIDs = []
        
        ifCurrentGname = None
        ifCurrentGID = None
        allowedGnames = []
        allowedGIDs = []
        
        if os.path.islink(pathname):
            link_preface = "Link chasing -> "
        else:
            link_preface = ""
            
        #extract pieces
        try:
            if 'owner' in attribs:
                userList = attribs['owner']
                if type(userList) == type(1):
                    userList = "%d" % userList
                userList = tcs_utils.splitNaturally(userList, wordAdditions="<>*-_", whitespaceAdditions=",", uniq=True)
                try:
                    idx = userList.index('<SYSTEM>')
                    userList = userList [0:idx] + sb_utils.acctmgt.users.local_SystemUsers() + userList[idx+1:]
                    userList = tcs_utils.splitNaturally(userList, wordAdditions="<>*-_", whitespaceAdditions=",", uniq=True)
                except ValueError, e:
                    pass
                
                for entry in userList:
                    try:
                        allowedUIDs.append(self._map_uid_uname(entry)['uid'])
                        allowedUnames.append(entry)
                    except KeyError,e:
                        msg = "allowed username '%s' not found in local user list - ignoring" % entry
                        self.logger.warn('sb_utils.file.fileperms.check_ownership',msg)
                # ok, user was given, do we *have* any acceptable entries?  If not punt without doing anything
                if not allowedUnames:
                    msg = "No valid unames found for acceptable file ownership - skipping %s" % pathname
                    raise tcs_utils.ActionError(msg)

            if 'if_user_is' in attribs:
                ifCurrentUname = attribs['if_user_is']
                ifCurrentUID  = self._map_uid_uname(ifCurrentUname)['uid']

            if 'group' in attribs:
                groupList = attribs['group']
                if type(groupList) == type(1):
                    groupList = "%d" % groupList
                groupList = tcs_utils.splitNaturally(groupList, wordAdditions="<>*-_", whitespaceAdditions=",", uniq=True)
                try:
                    idx = groupList.index('<SYSTEM>')
                    groupList = groupList [0:idx] + sb_utils.acctmgt.users.local_SystemGroups() + groupList[idx+1:]
                    groupList = tcs_utils.splitNaturally(groupList, wordAdditions="<>*-_", whitespaceAdditions=",", uniq=True)
                except ValueError, e:
                    pass

                for entry in groupList:
                    try:
                        allowedGIDs.append(self._map_gid_gname(entry)['gid'])
                        allowedGnames.append(entry)
                    except KeyError,e:
                        msg = "allowed groupname '%s' not found in local group list - ignoring" % entry
                        self.logger.warn('sb_utils.file.fileperms.check_ownership',msg)
                if not allowedGnames:
                    msg = "No valid gnames found for acceptable file ownership - skipping %s" % pathname
                    raise tcs_utils.ActionError(msg)
            
            if 'if_group_is' in attribs:
                ifCurrentGname = attribs['if_group_is']
                ifCurrentGID  = self._map_gid_gname(ifCurrentGname)['gid']

        except Exception, err:
            msg = "Skipping %s: %s" % ( pathname, err)
            self.logger.log_info('sb_utils.file.fileperms.check_ownership', link_preface + msg)
            return change_rec
            
        # Are we changing ownership? Record the original values of whatever is being changed, but use the symbolic
        # name if the system knows it.

#        print "\npathname       " , pathname
#        print "allowedUnames  " , allowedUnames
#        print "allowedUIDs    " , allowedUIDs
#        print "allowedGnames  " , allowedGnames
#        print "allowedGIDs    " , allowedGIDs
#        print "ifCurrentUname " , ifCurrentUname
#        print "ifCurrentUID   " , ifCurrentUID
#        print "ifCurrentGname " , ifCurrentGname
#        print "ifCurrentGID   " , ifCurrentGID

        if allowedUnames  or allowedGnames :
            try:
                fileowner = statinfo.st_uid
                groupowner = statinfo.st_gid
                
                temprec = {}

                # only allow owner change *IF* 
                #  uid change requested (IE allowedUnames != None) 
                #  current uid != desired uid 
                #  -and one of-
                #      'if_user_is'(IE ifCurrentUname) is None 
                #      uid matches 'if_user_is'              
                
                if allowedUnames and (statinfo.st_uid not in allowedUIDs):
                    fileowner = allowedUIDs[0]
                    temprec['owner'] = self._map_uid_uname(statinfo.st_uid)['uname']
                    what_changed.append("uname=%s(%d)" % (str(self._map_uid_uname(allowedUnames[0])['uname']), fileowner))
                    instead_of.append("uname=%s(%d)"   % (str(self._map_uid_uname(statinfo.st_uid)['uname']) , statinfo.st_uid))
                
                
                if allowedGnames and (statinfo.st_gid not in allowedGIDs) :
                    groupowner = allowedGIDs[0]
                    temprec['group'] = self._map_gid_gname(statinfo.st_gid)['gname']
                    what_changed.append("gname=%s(%d)" % (str(self._map_gid_gname(allowedGnames[0])['gname']), groupowner))
                    instead_of.append("gname=%s(%d)"   % (str(self._map_gid_gname(statinfo.st_gid)['gname']) , statinfo.st_gid))
                
                if temprec :
                    if self._checkOnly == False:  
                        os.chown(pathname, fileowner, groupowner)  # explicitly get the status of the file being linked, not the link itself
                        sb_utils.SELinux.restoreSecurityContext(pathname)
                        msg = "%s - Changed file ownership to %s instead of %s" % (pathname, ", ".join(what_changed), ", ".join(instead_of))
                        self.logger.log_notice('sb_utils.file.fileperms.check_ownership', link_preface + msg)
                    else:
                        msg = "%s - File ownership should be %s instead of %s" % (pathname, ", ".join(what_changed), ", ".join(instead_of))
                        self.logger.log_notice('sb_utils.file.fileperms.check_ownership', link_preface + msg)
                    change_rec.update(temprec)     
                
                else :
                    msg = "%s: no ownership changes need to be made" % ( pathname )
                    self.logger.log_debug('sb_utils.file.fileperms.check_ownership', link_preface + msg)
            except OSError, err:
                msg = "%s: %s" % (pathname, err)
                self.logger.log_err('sb_utils.file.fileperms.check_ownership', link_preface + msg)
     

        return change_rec

    def check_dacs(self, pathname, statinfo, attribs):
        msg = ""
        suid_msg = ""
        sgid_msg = ""
        svtx_msg = ""
        
        change_rec = {}    
#        print pathname, statinfo, attribs
        #extract pieces
        try:
            if 'dacs' in attribs:
                dacs_required = self._convert_dacs(attribs['dacs'])

                # If we are a directory, *and* we are not setting exact DACs, verify that execute perms are allowed whereever read perms are
                if stat.S_ISDIR(statinfo.st_mode) and not self._exactDACs:
                    oldPerms = dacs_required['dacs_value']
                    newPerms = oldPerms
                    # Ok, do we have user read?
                    if (dacs_required['dacs_value'] & stat.S_IRUSR) and not (dacs_required['dacs_value'] & stat.S_IXUSR):
                        newPerms = newPerms | stat.S_IXUSR
                    if (dacs_required['dacs_value'] & stat.S_IRGRP) and not (dacs_required['dacs_value'] & stat.S_IXGRP):
                        newPerms = newPerms | stat.S_IXGRP
                    if (dacs_required['dacs_value'] & stat.S_IROTH) and not (dacs_required['dacs_value'] & stat.S_IXOTH):
                        newPerms = newPerms | stat.S_IXOTH
                    if newPerms != oldPerms:
                        oldStr = dacs_required['dacs_str']
                        dacs_required = self._convert_dacs(newPerms)
                        newStr = dacs_required['dacs_str']
                        msg = "'%s' is a directory, allowing execute perms to match read perms - allowed DACs is now %s instead of %s" % (pathname,newStr, oldStr)
                        self.logger.info('sb_utils.file.fileperms.check_dacs', msg)
            # Ok, allow for SUID/SGID if the file is on the respective list and we're not setting exact dacs
                if not self._exactDACs:
                    whitelisted, reason = sb_utils.file.whitelists.is_SUID_whitelisted(pathname)
                    if whitelisted:
                        msg = "Found '%s' on SUID whitelist - allowing SUID bit" % pathname
                        self.logger.info('sb_utils.file.fileperms.check_dacs', msg)
                        oldPerms = dacs_required['dacs_value'] | stat.S_ISUID
                        dacs_required = self._convert_dacs(oldPerms)
                    whitelisted, reason = sb_utils.file.whitelists.is_SGID_whitelisted(pathname)
                    if whitelisted:
                        msg = "Found '%s' on SGID whitelist - allowing SGID bit" % pathname
                        self.logger.info('sb_utils.file.fileperms.check_dacs', msg)
                        oldPerms = dacs_required['dacs_value'] | stat.S_ISGID
                        dacs_required = self._convert_dacs(oldPerms)
        except Exception, err:
            msg = "Skipping %s: %s, problem converting new DAC value" % ( pathname, err)
            self.logger.error('sb_utils.file.fileperms.check_dacs', msg)
            return change_rec

        try:
            dacs_oldval = self._convert_dacs(statinfo.st_mode)
        except Exception, err:
            msg = "Skipping %s: %s, problem converting existing DAC value" % ( pathname, err)
            self.logger.error('sb_utils.file.fileperms.check_dacs', msg)
            return change_rec
            
        # are we changing the DACS?  If so, and we not told to use exactDacs, do a check to see if the user/group/other permissions are 
        # 'good enough'.

        make_changes = False
        if dacs_required['dacs_value'] != dacs_oldval['dacs_value']:
            make_changes = True
            dacs_newval = dacs_required
            if not self._exactDACs:            
                if sb_utils.file.dac.isPermOkay(pathname, dacs_required['dacs_str']):
#                    msg = "%s: file DACs of %s satisfy requirement of %s" % (pathname, dacs_oldval['dacs_str'], dacs_required['dacs_str'])  
#                    self.logger.log_info('sb_utils.file.fileperms.check_dacs', msg)
                    make_changes = False
                
                acceptableDAC = sb_utils.file.dac.findMaximumPermittedDACs(dacs_oldval['dacs_value'], dacs_required['dacs_value'])
                dacs_newval = self._convert_dacs(acceptableDAC)
                
        if make_changes:       
            try:
                # do appropriate logging if adding/removing SGID/SUID bits
                if (dacs_newval['dacs_value'] & stat.S_ISUID) != 0 and (dacs_oldval['dacs_value'] & stat.S_ISUID) == 0 :
                    suid_msg = "- Setting SUID flag" 
                elif (dacs_newval['dacs_value'] & stat.S_ISUID) == 0 and (dacs_oldval['dacs_value'] & stat.S_ISUID) != 0 :
                    suid_msg = " - Removing SUID flag" 

                if (dacs_newval['dacs_value'] & stat.S_ISGID) != 0 and (dacs_oldval['dacs_value'] & stat.S_ISGID) == 0 :
                    sgid_msg = " - Setting SGID flag" 
                elif (dacs_newval['dacs_value'] & stat.S_ISGID) == 0 and (dacs_oldval['dacs_value'] & stat.S_ISGID) != 0 :
                    sgid_msg = " - Removing SGID flag" 
                
                if (dacs_newval['dacs_value'] & stat.S_ISVTX) != 0 and (dacs_oldval['dacs_value'] & stat.S_ISVTX) == 0 :
                    svtx_msg = " - Setting S_ISVTX flag" 
                elif (dacs_newval['dacs_value'] & stat.S_ISVTX) == 0 and (dacs_oldval['dacs_value'] & stat.S_ISVTX) != 0 :
                    svtx_msg = " - Removing S_ISVTX flag" 

                if self._checkOnly == False:  
                    os.chmod(pathname, dacs_newval['dacs_value'])
                    msg = "%s - Changed file mode bits from %s(%s) to %s(%s) %s%s%s" % (pathname, 
                        dacs_oldval['dacs_flags'], dacs_oldval['dacs_str'], 
                        dacs_newval['dacs_flags'], dacs_newval['dacs_str'],
                        suid_msg,
                        sgid_msg,
                        svtx_msg)
                else:
                    msg = "%s - need to change file mode bits from %s(%s) to %s(%s) %s%s" % (pathname, 
                        dacs_oldval['dacs_flags'], dacs_oldval['dacs_str'], 
                        dacs_newval['dacs_flags'], dacs_newval['dacs_str'],
                        suid_msg, sgid_msg)
                        
                change_rec['dacs'] = dacs_oldval['dacs_str']
                self.logger.log_notice('sb_utils.file.fileperms.check_dacs', msg)

            except OSError, err:
                msg = "%s: %s" % (pathname, err)
                self.logger.log_err('sb_utils.file.fileperms.check_dacs', msg) 
        else:
            msg = "%s: no permission changes need to be made" % ( pathname )
            self.logger.log_debug('sb_utils.file.fileperms.check_dacs', msg)

        return change_rec

    # construct a map from uid (interger) to uname (str), based on the input field
    # returns {'uid': <int> , 'uname' : <str>}
    # If unable to map UID to uname returns uname as uname=uid , with uid being an INTEGER 
    # Throws an KeyError exception if unable to map uname to UID, with text holding reason


    def _map_uid_uname(self, user_info):
        usermap = {}
        if user_info == None:
            raise KeyError ("_map_uid_uname -> no user information given to map")
        if type(user_info) == type('string'):
            try:
                uid = pwd.getpwnam(user_info)[2]
                usermap = {'uname':user_info, 'uid':uid}
            except KeyError:
                if user_info.isdigit():
                    return self._map_uid_uname(int(user_info))
                else:
                    raise KeyError ("_map_uid_uname -> unable to map user '%s' to a UID" % (user_info))
        elif type(user_info) == type(0):
            try:
                uname = pwd.getpwuid(user_info)[0]
                usermap = {'uname':uname, 'uid':user_info}
            except KeyError:
                usermap = {'uname':user_info, 'uid':user_info}
    #            raise KeyError ("_map_uid_uname -> unable to map user '%s' to a UID" % (user_info))
        else:
            raise KeyError ("_map_uid_uname -> invalid information given to map")
        return usermap

    # construct a map from gid (interger) to gname (str), based on the input field
    # returns {'gid': <int> , 'gname' : <str>}
    # If unable to map GID to gname, return  gname as GID (as an integer) 
    # Throws an KeyError exception if unable to map gname to gid, with text holding reason
    def _map_gid_gname(self, group_info):
        groupmap = {}
        if group_info == None:
            raise KeyError ("_map_gid_gname -> no group information given to map")
        if type(group_info) == type('string'):
            try:
                gid = grp.getgrnam(group_info)[2]
                groupmap = {'gname':group_info, 'gid':gid}
            except KeyError:
                if group_info.isdigit():
                    return self._map_gid_gname(int(group_info))
                else:
                    raise KeyError ("_map_gid_gname -> unable to map group '%s' to a gid" % (group_info))
        elif type(group_info) == type(0):
            try:
                gname = grp.getgrgid(group_info)[0]
                groupmap = {'gname':gname, 'gid':group_info}
            except KeyError:
                groupmap = {'gname':group_info, 'gid':group_info}
    #            raise KeyError ("_map_gid_gname -> unable to map group '%s' to a gid" % (group_info))
        else:
            raise KeyError ("_map_gid_gname -> invalid information given to map")
        return groupmap

    # constructs a map holding the string and decimal representations of a particular dac set
    # return {'dacs_str':<str>, 'dacs_value':<int>, 'dacs_flags':<str>}
    # raises keyerror if unable to interpret dacs as a decimal number -or- as a string holding an octal number

    def _convert_dacs(self, dacs):
        dacval = 0
        if dacs == None:
            raise KeyError("_convert_dacs -> no DAC data given to translate")
        elif type(dacs) == type('string'):
            dacval = int(dacs, 8)
        elif type(dacs) == type(0):
            dacval = dacs
        else :
            raise KeyError ("_convert_dacs -> invalid data given ")

        dacval &= 07777  # strip off 'type' info, keeping values suitable for chmod
        dacs_map = {}
        dacs_map['dacs_value'] = dacval
        dacs_map['dacs_str']     = oct(dacval)
        dacs_map['dacs_flags']   = tarfile.filemode(dacs_map['dacs_value'])
        return dacs_map
        

# External interface to do/undo changes to a set of files.  If the first argument is a string, then it will be converted
# to a dictionary before continuing
# 
# The bulchanges dictionary is keyed on filename, with each value being a dictionary holding the changes to make
# We default the options to make the changes, and force the DACs to be exact
# Return is a dictionary that could be used to undo what was just done

def change_bulk_file_attributes(bulkchanges, options={'checkOnly':False, 'exactDACs': True}):
    revert = {}
    changeFileAttributes = ChangeFileAttributes(options)
    if type(bulkchanges) == type("string"):
        bulkchanges = tcs_utils.string_to_dictionary(bulkchanges)    
    if type(bulkchanges) != type ({}):
        raise SyntaxError("%s - expected a string or dictionary as argument, got %s" % ("change_bulk_file_attributes", str(type(bulkchanges))))
    
    for thisfile in bulkchanges:
        revert.update(changeFileAttributes.makeChanges(thisfile, bulkchanges[thisfile]))
    return revert
        
##########################################################################
##
## External interface to change_file_attributes - expects a filename/path, a dictionary of what to change, and a flag to do recursion
## The dictionary will be evaluated and any strings values converted to the correct *integer* values for uid, gid, or permissions
## Available dictionary keys:
#   owner = comma separated list of permitted/required unames 
#   group = comma separated list of permitted/required gnames
#   if_user_is = uname of *current* owner - if no match, then nothing done
#   if_group_is = uname of *current* owner - if no match, then nothing done
#   dacs     = if type is string, interpret as DAC permissions for owner,group,world
#              if type is integer, pass through quietly
#   if unable to translate an element, log an error and do no changes
#   create a suitable change record with *strings* for any changed uid,gid,perms
#   By default, the options are to be in 'scan' mode, and not to be recursive
#   acceptable options are:
#    checkOnly = True/False
#    recursive = True/False
#    exactDacs = True/False
#    matchMode = optional = if present = mode flags to match files on (logical OR of stat flags (IE S_IFREG | S_IFDIR, etc)

def change_file_attributes(pathname=None, changes={}, options={'checkOnly':False, 'recursive':False}):
    changeFileAttributes = ChangeFileAttributes(options)
    
#    print "Pathname",pathname
#    print "Changes",changes
#    print "options",options
    if pathname == None or pathname == "":
        raise tcs_utils.ActionError ("No path, or empty path, given to change attributes on")
    elif pathname == '/' :
        raise tcs_utils.ActionError ("Asked to change attributes on '/' directory, refusing.")

    change_rec = {} 

    record = changeFileAttributes.makeChanges(pathname=pathname, attribs_in=changes)
    if record != None:
        change_rec.update(record)
    if os.path.isdir (pathname) and changeFileAttributes._recursive == True:
        for root, dirs, files in os.walk(pathname):
            for thisfile in files + dirs:
                fullfile = os.path.join(root, thisfile)
                record = changeFileAttributes.makeChanges(pathname=fullfile, attribs_in=changes)
                if record != None:
                    change_rec.update(record)
    return change_rec


def splitStringIntoFiles( files, globbing=False):
    """SPlit the text string given by 'files' into an array of actual files, honoring quoted fields, but splitting on 
       natural boundaries such as commas, newlines, spaces, tabs, and whatnot.  Make sure that globbing characters are
       allowed as part of the filename.  Quoted names with spaces should be preserved.
    """
    allFiles = []
    lexer = shlex.shlex(files, posix=True)
    lexer.whitespace += ","
    lexer.wordchars += "*/[]().-_;:"
    expandedFiles = []
    for name in lexer:
        if globbing == True:
            expandedFiles.extend(glob.glob(name))
        else:
            expandedFiles.append(name)
#    print "splitStringInfoFiles -DEBUG - " ,expandedFiles
    return expandedFiles
    
####
# External interface to walk through a comma separated list of filenames, potentially glob-expanding them for wildcards,
# and then calling change_file_attributes to see if changes should/would be made.  
# options = dictionary
#         recursive, ignoreExcludes, globNames, checkOnly

def search_and_change_file_attributes(pathString, changes = {}, options={}):

    # booleans come in from the profile as "1" or "0", so convert to logicals
    combined_changes = {}
    
    globbing = False
    try:        
        if options['globNames'] in  [True, 1, "True", "1"]:
            globbing = True
    except:
        pass
    
    # now we need to split the list into filenames, but honor quotes, and split on natural boundaries
    for entry in splitStringIntoFiles(pathString, globbing=globbing):
        combined_changes.update(change_file_attributes(entry, changes=changes, options=options) )
    return combined_changes

if __name__ == '__main__':
    loggerInst = TCSLogger.TCSLogger.getInstance()
    loggerInst.force_log_level(7)
    loggerInst._fileobj = sys.stdout
    if len(sys.argv) in [3,4]:
        options = {}
        changes = {}
        options['checkOnly'] = True
        fileName = sys.argv[1]
        if fileName.endswith('/'):
            options['recursive'] = True
        changes['dacs'] = sys.argv[2]
        if len (sys.argv) == 4:
            options['exactDACs'] = True
        print fileName
        print changes
        print options
        print search_and_change_file_attributes(fileName, changes, options)
    else:
        print "Arg mismatch"
