#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import sys
import pwd
import grp
import os, stat
import re

sys.path.append('/usr/share/oslockdown')
import TCSLogger
import tcs_utils
import sb_utils.os.info

try:
    foobar = set([])
except NameError:
    from sets import Set as set

# Based on simplistic rules the line from /etc/passwd must have 7 fields
# and the username must match '[a-zA-Z][a-zA-Z0-9_]*$' (i.e start with a letter,
# and then only have letters, numbers, or underscores)
validUserNameRegex = re.compile('^([a-zA-Z])([a-zA-Z0-9_])*$')

def getSystemRangeUID():
    """
    Return a tuple (0,systemMax) with the UID range (inclusive) of system accounts.  If we can't find an override
    in the system file(s), then make assumptions based on the OS.  In both cases, once we determine what the
    'lowest' user account should be (as used by the 'useradd' account), anything lower than that will be considered
    a system account.
    
    Linux - these limits are set in the /etc/login.defs file.  Note that 'canned' system accounts range from 0 to 100, 
       and system accounts done using 'useradd' start at 100.  Older *nix boxes would start users at 500, some newer 
       ones start at 1000, and this limit is defined using the UID_MIN value.  We will consider *evertything* below 
       the UID_MIN value to be a system account.  
    Solaris - These are hardcoded for Solaris 10 to be in the range 0, 99.  User accounts start at 100 and work up (with
       a few special UIDs that we're going to treat as 'regular users'
       
    """
    # initial defaults
    if sb_utils.os.info.is_solaris():
        sysuidmin = 0
        sysuidmax = 99
    else:
        sysuidmin = 0
        sysuidmax = 499
        
        if os.path.exists('/etc/login.defs'):
            for line in open('/etc/login.defs'):
                if not line or line.startswith('#'):
                    continue
                try:
                    fields = line.strip().split()
                    if len(fields) == 2 and fields[0] == "UID_MIN":
                        sysuidmax = int(fields[1]) - 1
                except Exception, err: 
                    print  str(err)
                    pass # silently skip any errors.
    return sysuidmin, sysuidmax

def getSystemRangeGID():
    """
    Return a tuple (0,systemMax) with the GID range (inclusive) of system accounts.  If we can't find an override
    in the system file(s), then make assumptions based on the OS.  In both cases, once we determine what the
    'lowest' user account should be (as used by the 'useradd' account), anything lower than that will be considered
    a system account.
    
    Linux - these limits are set in the /etc/login.defs file.  Note that 'canned' system accounts range from 0 to 100, 
       and system accounts done using 'useradd' start at 100.  Older *nix boxes would start groups at 500, some newer 
       ones start at 1000, and this limit is defined using the GID_MIN value.  We will consider *evertything* below 
       the GID_MIN value to be a system account.  
    Solaris - These are hardcoded for Solaris 10 to be in the range 0, 99.  User groups start at 100 and work up (with
       a few special GIDs that we're going to treat as 'regular groups'
       
    """
    # initial defaults
    if sb_utils.os.info.is_solaris():
        sysgidmin = 0
        sysgidmax = 99
    else:
        sysgidmin = 0
        sysgidmax = 499
        
        if os.path.exists('/etc/login.defs'):
            for line in open('/etc/login.defs'):
                if not line or line.startswith('#'):
                    continue
                try:
                    fields = line.strip().split()
                    if len(fields) == 2 and fields[0] == "GID_MIN":
                        sysgidmax = int(fields[1]) - 1
                except: 
                    pass # silently skip any errors.
    return sysgidmin, sysgidmax



##############################################################################
def local_RegularUsers():
    """
    Return an array of local non-system user accounts.  
    """
    
    localusers = []
    sysuidmin,sysuidmax = getSystemRangeUID()
    for line in open('/etc/passwd'):
        fields = line.strip().split(':')
        if len(fields) != 7 or not validUserNameRegex.match(fields[0]): continue
        
        if int(fields[2]) > sysuidmax:
            localusers.append(fields[0])

    return localusers

##############################################################################
def local_SystemUsers():
    """
    Return an array of local system user accounts.
    """
    
    localusers = []
    sysuidmin,sysuidmax = getSystemRangeUID()
    for line in open('/etc/passwd'):
        fields = line.strip().split(':')
        if len(fields) != 7 or not validUserNameRegex.match(fields[0]): continue

        if  int(fields[2]) <= sysuidmax:
            localusers.append(fields[0])

    return localusers

##############################################################################
def local_AllUsers():
    """
    Return an array of all local accounts.  
    """
    
    localusers = []
    for line in open('/etc/passwd'):
        fields = line.strip().split(':')
        if len(fields) != 7 or not validUserNameRegex.match(fields[0]): continue
        
        localusers.append(fields[0])

    return localusers

##############################################################################
def local_RegularGroups():
    """
    Return an array of local non-system gruop accounts.  
    """
    
    localgroups = []
    sysgidmin,sysgidmax = getSystemRangeGID()
    for line in open('/etc/group'):
        fields = line.strip().split(':')
        if len(fields) != 4 or not validUserNameRegex.match(fields[0]): continue
        if int(fields[2]) > sysgidmax:
            localgroups.append(fields[0])

    return localgroups

##############################################################################
def local_SystemGroups():
    """
    Return an array of local system group accounts.
    """
    
    localgroups = []
    sysgidmin,sysgidmax = getSystemRangeGID()
    for line in open('/etc/group'):
        fields = line.strip().split(':')
        if len(fields) != 4 or not validUserNameRegex.match(fields[0]): continue

        if int(fields[2]) <= sysgidmax:
            localgroups.append(fields[0])

    return localgroups

def local_AllGroups():
    """
    Return an array of all local group accounts. 
    """
    
    localgroups = []
    for line in open('/etc/group'):
        fields = line.strip().split(':')
        if len(fields) != 4 or not validUserNameRegex.match(fields[0]): continue
        
        localgroups.append(fields[0])

    return localgroups

##############################################################################
def cronjob (user=None, command=None, schedule=None):

    logger = TCSLogger.TCSLogger.getInstance()


    if user == None and command == None and schedule == None:
        msg = "Incorrect parameters provided"
        logger.log_crit('sb_utils.acctmgt.users.cronjob', msg)
        return False

    try:
        userdata = pwd.getpwnam(user) 
    except KeyError:
        msg = "Unable to set cronjob for %s" % (user)
        logger.log_crit('sb_utils.acctmgt.users.cronjob', msg)
        return False

    # For undefined schedule parameters, just use an asterisk '*'

    # Minutes (00 to 59)
    if not schedule.has_key('min'): 
        schedule['min'] = '*'
    else:
        fields = schedule['min'].split(',')
        for minutes in fields:
            if int(minutes) < 0 or int(minutes) > 59:
                msg = "Invalid minute parameter"
                return False


    # Let's hope that developers do some basic testing
    # because I don't want to write a bunch of complicated code to check
    # ranges (the use of dashes) here!

    # Hours 
    if not schedule.has_key('hour'): 
        schedule['hour'] = '*'

    # Day of Month 
    if not schedule.has_key('day_of_month'): 
        schedule['day_of_month'] = '*'

    # Day of Week
    if not schedule.has_key('day_of_week'): 
        schedule['day_of_week'] = '*'
        

    #
    # Build the new crontab line entry:
    #
    newentry = "%s %s %s %s %s %s\n" % (schedule['min'],
                                      schedule['hour'],
                                      schedule['day_of_month'],
                                      schedule['month'],
                                      schedule['day_of_week'], 
                                      command)

    os.umask(022)
    try:
        tempcron = open('/tmp/.newcron.' + user, 'w')
    except IOError, err:
        msg = "Unable to create temporary crontab file: %s" % err
        logger.log_err('sb_utils.acctmgt.users.cronjob', msg)
        return False
   
    found_flag = False

    cmd = "/usr/bin/crontab -l %s" % user
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        newcronjob = '# Crontab file for %s\n' % user
        tempcron.write(newcronjob)
        tempcron.write(newentry)
    else:
        for entry in output[1].split('\n'):
            if not entry:
                continue
            if entry == newentry.rstrip('\n'):
                found_flag = True
            tempcron.write(entry + '\n')

        if found_flag == False:
            tempcron.write(newentry)
    
    tempcron.close()
    cmd = """/usr/bin/su - %s -c "/usr/bin/crontab /tmp/.newcron.%s" """ % (user, user)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Unable to update crontab for %s: %s" % (user, output[2])
        logger.log_err('sb_utils.acctmgt.users.cronjob', msg)
        return False

    try:
        os.unlink('/tmp/.newcron.' + user)
    except Exception, err:
        msg = "Unable to remove temporary cron file: %s" % err        
        logger.log_warn('sb_utils.acctmgt.users.cronjob', msg)

    msg = "Updated crontab for %s; with '%s'" % (user, newentry)
    logger.log_info('sb_utils.acctmgt.users.cronjob', msg)
    return True
     
##############################################################################
def is_cronjob (user=None, command=None, schedule=None):

    logger = TCSLogger.TCSLogger.getInstance()


    if user == None and command == None and schedule == None:
        msg = "Incorrect parameters provided"
        logger.log_crit('sb_utils.acctmgt.users.cronjob', msg)
        return False

    try:
        userdata = pwd.getpwnam(user) 
    except KeyError, err:
        msg = "Unable to get cronjob for %s: %s" % (user, err)
        logger.log_warn('sb_utils.acctmgt.users.is_cronjob', msg)
        return False


    # Let's hope that developers do some basic testing
    # because I don't want to write a bunch of complicated code to check
    # ranges (the use of dashes) here!

    # Hours 
    if not schedule.has_key('hour'): 
        schedule['hour'] = '*'

    # Day of Month 
    if not schedule.has_key('day_of_month'): 
        schedule['day_of_month'] = '*'

    # Day of Week
    if not schedule.has_key('day_of_week'): 
        schedule['day_of_week'] = '*'
        

    #
    # Build the new crontab line entry:
    #
    newentry = "%s %s %s %s %s %s\n" % (schedule['min'],
                                      schedule['hour'],
                                      schedule['day_of_month'],
                                      schedule['month'],
                                      schedule['day_of_week'], 
                                      command)
                              
    cmd = "/usr/bin/crontab -l %s" % user
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        return False
    else:
        for entry in output[1].split('\n'):
            if not entry or entry.startswith('#'):
                continue

            if entry == newentry.rstrip('\n'):
                return True
    
    return False
     

##############################################################################
def del_cronjob (user=None, command=None, schedule=None):

    logger = TCSLogger.TCSLogger.getInstance()


    if user == None and command == None and schedule == None:
        msg = "Incorrect parameters provided"
        logger.log_crit('sb_utils.acctmgt.users.cronjob', msg)
        return False

    try:
        userdata = pwd.getpwnam(user) 
    except KeyError, err:
        msg = "Unable to set cronjob for %s: %s" % (user, err)
        logger.log_crit('sb_utils.acctmgt.users.cronjob', msg)
        return False

    # For undefined schedule parameters, just use an asterisk '*'

    # Let's hope that developers do some basic testing
    # because I don't want to write a bunch of complicated code to check
    # ranges (the use of dashes) here!

    # Hours 
    if not schedule.has_key('hour'): 
        schedule['hour'] = '*'

    # Day of Month 
    if not schedule.has_key('day_of_month'): 
        schedule['day_of_month'] = '*'

    # Day of Week
    if not schedule.has_key('day_of_week'): 
        schedule['day_of_week'] = '*'
        

    #
    # Build the new crontab line entry:
    #
    newentry = "%s %s %s %s %s %s\n" % (schedule['min'],
                                      schedule['hour'],
                                      schedule['day_of_month'],
                                      schedule['month'],
                                      schedule['day_of_week'], 
                                      command)

    os.umask(022)
    try:
        tempcron = open('/tmp/.newcron.' + user, 'w')
    except IOError, err:
        msg = "Unable to create temporary crontab file: %s" % err
        logger.log_err('sb_utils.acctmgt.users.cronjob', msg)
        return False
   
    cmd = "/usr/bin/crontab -l %s" % user
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        newcronjob = '# Crontab file for %s\n' % user
        tempcron.write(newcronjob)
        tempcron.write(newentry)
    else:
        for entry in output[1].split('\n'):
            if not entry:
                continue
            if entry == newentry.rstrip('\n'):
                continue
            tempcron.write(entry + '\n')

    tempcron.close()
    cmd = """/usr/bin/su - %s -c "/usr/bin/crontab /tmp/.newcron.%s" """ % (user, user)
    output = tcs_utils.tcs_run_cmd(cmd, True)
    if output[0] != 0:
        msg = "Unable to update crontab for %s: %s" % (user, output[2])
        logger.log_err('sb_utils.acctmgt.users.cronjob', msg)
        return False

    try:
        os.unlink('/tmp/.newcron.' + user)
    except Exception, err:
        msg = "Unable to remove temporary cron file: %s" % err        
        logger.log_warn('sb_utils.acctmgt.users.cronjob', msg)

    msg = "Updated crontab for %s; with '%s'" % (user, newentry)
    logger.log_info('sb_utils.acctmgt.users.cronjob', msg)
    return True

##############################################################################
def status(user=None):
    """
    Getting the correct 'status' of a user's password varies from system to system, and is more complicated than it looks at
    first blush.  The 'command line' way is to use 'passwd -S'/'passwd -r files -s', but this has problems.  On RHEL4/RHEL5 
    systems the return code can't be trusted, and the *text* returned is also misleading.  For accounts that actually don't have 
    a password it claims that they are locked.  So we'll need to process the file ourselves and *what* text 
    is returned.  Solaris very neatly lays out what is expected in the man page, and I looked through several Linux source
    files to see what they require.  To wrap it all together in one place we will have this routine.  
    Remember also, for status of *local* accounts (set up in /etc/passwd, /etc/shadow) we need to look at both files.   
    Linux:
       if field is empty: No password
       if field starts with '!', 'x', or '*' : locked
       otherwise : password protected account 
    Solaris:
       if field is empty: No password
       if field starts with *LK* : Locked
       otherwise : password protected account
       
    So we will return one of :
        'NP'  - No Password
        'PS'  - valid password
        'LK'  - account locked/blocked
         None - No such user, unable to process /etc/shadow
    """
    retval = None
    
    if not user:
        return retval

    logger = TCSLogger.TCSLogger.getInstance()

    # read passwd file to see if user is a 'local' user
    candidate = None
    for line in open('/etc/passwd'):
        line = line.strip().split(':')
        if line[0] != user:
            continue
        candidate = line

    # ok, we found a line for this user locally, does it have an *internal* password?    
    if candidate:
        # we'll assume a password, and change it if not...
        retval = 'PS'
        candidatePWD = candidate[1]
        #if the password field in /etc/password is an 'x', go read /etc/shadow
        if candidatePWD=='x':
            for line in open('/etc/shadow'):
                line = line.strip().split(':')
                if line[0] != user:
                    continue
                candidatePWD = line[1]
        #now check what the value of the password is...
        if sb_utils.os.info.is_solaris() == False:
            if candidatePWD == "" :    # No password
                retval = "NP"
            elif candidatePWD[0] == "*":  # Locked like a system account
                retval = "LK" 
            elif candidatePWD[0] == "!" :  # Locked by the 'passwd -L' command
                retval = "LK"
            elif candidatePWD[0] == "x":  # hmmm, legacy lock?  Reference from libuser.c/passwd.c Linux source  
                retval = "LK"
        else:      
            if candidatePWD == "":     #No password
                retval = "NP"
            elif candidatePWD.startswith("*LK*"):  # Locked account
                retval = "LK"
            elif candidatePWD == "NP":  # Blocked account (no login allowed - but *can* run) - solaris 'passwd' would return 'LK'
                retval = "LK"
    else:
        msg = "No such user '%s'" % user
        logger.log_warn('sb_utils.acctmgt.users.status', msg)

    msg = "Account '%s' status is '%s'" % (user, retval)
    logger.log_debug('sb_utils.acctmgt.users.status', msg)
    return retval

##############################################################################
def is_locked(user=None):
    if user == None:
        return None

    results = status(user)
    if results == None:
        return None

    if results in ['LK']:
        return True
    else:
        return False

##############################################################################
def lock(user=None, doSysAccounts = False):

    if user == None:
        return None
    lockUser = False
    
    logger = TCSLogger.TCSLogger.getInstance()

    if user == 'root':
        msg = "Will NOT lock 'root'; ignoring request"
        logger.log_notice('sb_utils.acctmgt.users.lock', msg)
        return False

    if user in local_RegularUsers():
        lockUser = True
    elif user in local_SystemUsers():
        if doSysAccounts == False:
            msg = "'%s' is a system account, Will NOT lock system accounts" % user
            logger.log_notice('sb_utils.acctmgt.users.lock', msg)
            return None
        lockUser = True
    
    if not lockUser:
        msg = "'%s' does not appear to be a valid local user, account not locked" % user
        logger.log_notice('sb_utils.acctmgt.users.lock', msg)
        return None
        
    results = status(user)
    if results == None:
        return None

    if results in ['LK', 'NP', 'NL']:
        msg = "'%s' is already blocked (%s)" % (user, results)
        logger.log_info('sb_utils.acctmgt.users.lock', msg)
        return True

    if sb_utils.os.info.is_solaris() == True:
        cmd = "/usr/bin/passwd -r files -l %s " % user
    else:
        cmd = "/usr/sbin/usermod -L %s " % user

    results = tcs_utils.tcs_run_cmd(cmd, True)
    if results[0] != 0:
        msg = "Unable to lock account %s: %s" % (user, results[2])
        logger.log_err('sb_utils.acctmgt.users.lock', msg)
        return None

    msg = "Account '%s' is now locked" % user
    logger.log_info('sb_utils.acctmgt.users.lock', msg)

    return True


##############################################################################
def unlock(user=None, doSysAccounts=False):

    if user == None:
        return None
    unlockUser = False

    logger = TCSLogger.TCSLogger.getInstance()

    if user in local_RegularUsers():
        unlockUser = True
    elif user in local_SystemUsers():
        if doSysAccounts == False:
            msg = "'%s' is a system account, Will NOT perform functions on system accounts" % user
            logger.log_notice('sb_utils.acctmgt.users.unlock', msg)
            return None
        unlockUser = True

    if not unlockUser:
        msg = "'%s' does not appear to be a valid local user, account not unlocked" % user
        logger.log_notice('sb_utils.acctmgt.users.unlock', msg)
        return None

    results = status(user)
    if results == None:
        return None

    if results in ['PS']:
        msg = "'%s' is not blocked (%s)" % (user, results)
        logger.log_info('sb_utils.acctmgt.users.unlock', msg)
        return True

    if sb_utils.os.info.is_solaris() == True:
        cmd = "/usr/bin/passwd -r files -u %s " % user
    else:
        cmd = "/usr/bin/passwd -u %s " % user

    results = tcs_utils.tcs_run_cmd(cmd, True)
    if results[0] != 0:
        msg = "Unable to unlock account %s: %s" % (user, results[2])
        logger.log_err('sb_utils.acctmgt.users.lock', msg)
        return None

    msg = "Account '%s' is now unlocked" % user
    logger.log_info('sb_utils.acctmgt.users.lock', msg)

    return True


def showStatus(text, userList):
    print text
    for user in userList:
        print "\t%s -> %s" % (user, status(user))
        
##############################################################################
if __name__ == '__main__':
    #theschedule = {    'min':  '0',
                      #'hour': '12',
              #'day_of_month': '12',
                     #'month': '1',
               #'day_of_week': '*'    }

    #results = cronjob(user='root', command='nothing', schedule = theschedule)
    #print results

    #results = is_cronjob(user='root', command='nothing', schedule = theschedule)
    #print results

    #print lock(user='toor')
    print "SystemUIDs range" , getSystemRangeUID()    
    print "SystemGIDs range" , getSystemRangeGID()    
    showStatus("Local Reguler Users",local_RegularUsers())
    showStatus("Local System Accounts", local_SystemUsers())
    showStatus("Local All Users", local_AllUsers())
    print "Local Reguler Groups",local_RegularGroups()
    print "Local System Groups", local_SystemGroups()
    print "Local All Groups", local_AllGroups()
    showStatus("Bogus User",["this_is_a_bogus_user_name"])
#    showStatus("----",['avahi'])
