#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

#
# Functions specific to SUSE 11 such as:
#  - Using the pam-config(8) Utility
#

import sys
import os
import glob
import re

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sbProps
import sb_utils.os.software
import sb_utils.os.info

try:
    logger = TCSLogger.TCSLogger.getInstance(6)
except TCSLogger.SingletonException:
    logger = TCSLogger.TCSLogger.getInstance()

MODULE_NAME = 'sb_utils.os.suse.pam'

cpe = sb_utils.os.info.getCpeName()


##############################################################################
def check_packages():

    for pkg in ['pam', 'pam-config', 'cracklib', 'pam_pwcheck']:
        results = sb_utils.os.software.is_installed(pkgname=pkg) 
        if results != True:
            return False

    return True

##############################################################################
def config(modName=None):

    if modName == None:
        return {}

    pam_config = '/usr/sbin/pam-config'

    config_dict = {}

    if not os.path.exists('/usr/sbin/pam-config') and modName == 'cracklib':
        try:
            in_obj = open('/etc/pam.d/common-password-pc', 'r')
            lines = in_obj.readlines()
        except IOError, err:
            return config_dict

        in_obj.close()
        config_dict = {'password': []}
        for line in lines:
            if not line.startswith('password'):
                continue
            fields = line.split()
            if len(fields) < 4 or fields[2] != 'pam_cracklib.so':
                continue
            config_dict['password'].extend(fields[3:])
            break
        return config_dict

     

    cmd_string = "%s -q --%s" % (pam_config, modName)
    results = tcs_utils.tcs_run_cmd(cmd_string, True)
    if results[0] != 0: 
        logger.log_err(MODULE_NAME, results[2])
        return {}

    for line in results[1].split('\n'):
        try:
            pam_key = line.split(':')[0]
            pam_values = line.split(':')[1].split()
        except IndexError:
            continue

        config_dict[pam_key] = pam_values

    return config_dict

##############################################################################
def enable(modName=None):

    if modName == None:
        return False

    pam_config = '/usr/sbin/pam-config'

    cmd_string = "%s -a --%s" % (pam_config, modName)

    results = tcs_utils.tcs_run_cmd(cmd_string, True)
    if results[0] != 0: 
        logger.log_err(MODULE_NAME, results[2])
        return False

    msg = "PAM Module '%s' enabled %s" % (modName, results[2])
    logger.log_info(MODULE_NAME, msg)

    return True

##############################################################################
def disable(modName=None):

    if modName == None:
        return False

    pam_config = '/usr/sbin/pam-config'

    cmd_string = "%s -d --%s" % (pam_config, modName)

    results = tcs_utils.tcs_run_cmd(cmd_string, True)
    if results[0] != 0: 
        logger.log_err(MODULE_NAME, results[2])
        return False

    msg = "'%s' disabled %s" % (modName, results[1])
    logger.log_info(MODULE_NAME, msg)

    return True

##############################################################################
def passwdqc_configured():

    results = sb_utils.os.software.is_installed(pkgname='pam_passwdqc')    
    if results != True:
        return False

    msg = "Checking to see if pam_passwdqc is configured in /etc/pam.d/*"
    logger.log_info(MODULE_NAME, msg)

    searchPattern = re.compile('.*pam_passwdqc.*')
    for pam_file in glob.glob('/etc/pam.d/*'):
        try:
            in_obj = open(pam_file, 'r')
        except IOError, err:
            msg = "Unable to read %s: %s" % (pam_file, err)
            logger.log_err(MODULE_NAME, msg)
            continue
        for idx, line in enumerate(in_obj.readlines()):
            if line.startswith('#'):
                continue
            if searchPattern.search(line):
                msg = "pam_passwdqc is configured on line "\
                      "%d of %s" % (idx+1, pam_file)
                logger.log_info(MODULE_NAME, msg)
                in_obj.close()
                return True

        in_obj.close()

    msg = "pam_passwdqc is not configured"
    logger.log_info(MODULE_NAME, msg)

    return False

##############################################################################
def cracklib_get(option=None):

    if option == None:
        return ''

    settings = config(modName='cracklib')

    if not settings.has_key('password'):
        msg = "PAM cracklib is not configured for 'password'"
        return ''

    for pw_opt in settings['password']:
        try:
            (pw_key, pw_val) = pw_opt.split('=')
        except (ValueError, IndexError):
            pw_key = str(pw_opt)
            pw_val = ''
            
        if pw_key == str(option):
            msg = "GET Value: cracklib '%s' option is set to '%s' " % (pw_key, pw_val)
            logger.debug(MODULE_NAME, msg)
            return pw_val

    return ''

##############################################################################
def cracklib_set(option=None, optValue=None):

    if option == None or optValue == None:
        return False

    if os.path.exists('/usr/sbin/pam-config'):
        pam_config = '/usr/sbin/pam-config'
        cmd_string = "%s -a --cracklib-%s=%s" % (pam_config, str(option), str(optValue))
        results = tcs_utils.tcs_run_cmd(cmd_string, True)
        if results[0] != 0: 
            logger.log_err(MODULE_NAME, results[2])
            return False
        msg = "SET Value: cracklib '%s' option now set to '%s' " % (option, optValue)
        logger.debug(MODULE_NAME, msg)
        return True

    try:
        in_obj = open('/etc/pam.d/common-password-pc', 'r')
        lines = in_obj.readlines()
        in_obj.close()
        out_obj = open('/etc/pam.d/common-password-pc', 'w')
    except IOError, err:
        logger.err(MODULE_NAME, str(err))
        return False

    for line in lines:
        if not line.startswith('password'):
            out_obj.write(line)
            continue
        fields = line.split()
        if fields[2] != 'pam_cracklib.so':
            out_obj.write(line)
            continue

        if len(fields) < 4:
            line = "%s %s=%s\n" % (line.strip(), option, optValue)
            out_obj.write(line)
            have_set = True
            continue

        have_set = False
        for token in fields[3:]:
            if token.startswith("%s=" % option):
                newvalue = "%s=%s" % (option, optValue)
                line = line.replace(token, newvalue)            
                out_obj.write(line)
                have_set = True
                break

        if have_set == False:
            line = "%s %s=%s\n" % (line.strip(), option, optValue)
            out_obj.write(line)

    out_obj.close()
    
    return True

def cracklib_unset(option=None):

    if option == None:
        return False

    if os.path.exists('/usr/sbin/pam-config'):
        return disable("cracklib-%s" % str(option))


    try:
        in_obj = open('/etc/pam.d/common-password-pc', 'r')
        lines = in_obj.readlines()
        in_obj.close()
        out_obj = open('/etc/pam.d/common-password-pc', 'w')
    except IOError, err:
        logger.err(MODULE_NAME, str(err))
        return False

    for line in lines:
        if not line.startswith('password'):
            out_obj.write(line)
            continue
        fields = line.split()
        if len(fields) < 4 or fields[2] != 'pam_cracklib.so':
            out_obj.write(line)
            continue

        for token in fields[3:]:
            if token.startswith("%s=" % option):
                line = line.replace(token, '')            
                out_obj.write(line)
                break

    out_obj.close()
    
    return True



##############################################################################
def pwcheck_get(option=None):

    if option == None:
        return ''

    settings = config(modName='pwcheck')

    if not settings.has_key('password'):
        msg = "pwcheck is not configured for 'password'"
        return ''

    for pw_opt in settings['password']:
        try:
            (pw_key, pw_val) = pw_opt.split('=')
        except (ValueError, IndexError):
            pw_key = str(pw_opt)
            pw_val = ''
        if pw_key == str(option):
            msg = "GET Value: pwcheck '%s' option is set to '%s' " % (pw_key, pw_val)
            logger.debug(MODULE_NAME, msg)
            return pw_val

    return ''

##############################################################################
def pwhistory_get(option=None):

    if option == None:
        return ''

    settings = config(modName='pwhistory')

    if not settings.has_key('password'):
        msg = "pwhistory is not configured for 'password'"
        return ''

    for pw_opt in settings['password']:
        try:
            (pw_key, pw_val) = pw_opt.split('=')
        except (ValueError, IndexError):
            pw_key = str(pw_opt)
            pw_val = ''
        if pw_key == str(option):
            msg = "GET Value: pwhistory '%s' option is set to '%s' " % (pw_key, pw_val)
            logger.debug(MODULE_NAME, msg)
            return pw_val

    return ''


##############################################################################
def pwcheck_set(option=None, optValue=None):

    if option == None or optValue == None:
        return False

    pam_config = '/usr/sbin/pam-config'

    cmd_string = "%s -a --pwcheck-%s=%s" % (pam_config, str(option), str(optValue))

    results = tcs_utils.tcs_run_cmd(cmd_string, True)
    if results[0] != 0: 
        logger.log_err(MODULE_NAME, results[2])
        return False

    msg = "SET Value: pwcheck '%s' option now set to '%s' " % (option, optValue)
    logger.debug(MODULE_NAME, msg)

    
    return True

def pwcheck_unset(option=None):

    if option == None:
        return False

    return disable("pwcheck-%s" % str(option))

##############################################################################
def pwhistory_set(option=None, optValue=None):

    if option == None or optValue == None:
        return False

    pam_config = '/usr/sbin/pam-config'

    cmd_string = "%s -a --pwhistory-%s=%s" % (pam_config, str(option), str(optValue))

    results = tcs_utils.tcs_run_cmd(cmd_string, True)
    if results[0] != 0: 
        logger.log_err(MODULE_NAME, results[2])
        return False

    msg = "SET Value: pwhistory '%s' option now set to '%s' " % (option, optValue)
    logger.debug(MODULE_NAME, msg)

    
    return True

def pwhistory_unset(option=None):

    if option == None:
        return False

    return disable("pwhistory-%s" % str(option))


##############################################################################
def backup():

    backupfile =  os.path.join(sbProps.BACKUP_DIR, "pre-sb-pamfiles.tar.gz")
    if os.path.isfile(backupfile):
        msg = "%s already exists" % backupfile
        logger.log_info(MODULE_NAME, msg)
        return True

    try:
        import tarfile
    except ImportError, err:
        msg = "Unable to import 'tarfile' module: %s" % err
        logger.debug(MODULE_NAME, msg)
        return False

    try:
        tar = tarfile.open(backupfile, "w:gz")
    except tarfile.TarError, err:
        msg = "Unable to create backup of /etc/pam.d/* to %s (%s)" % (backupfile, err)
        logger.log_err(MODULE_NAME, msg)
        return False

    try:
        os.chdir('/etc')
    except (OSError, IOError):
        msg = "Unable to go into /etc: %s" % err
        logger.log_err(MODULE_NAME, msg)
        return False
 
    for name in glob.glob('pam.d/*'):
        tar.add(name)
    tar.close()

    try: 
        os.chmod(backupfile, 0600)
    except (IOError, OSError), err:
        msg = "Unable to set permissions of %s to 0600 (%s)" % (backupfile, err)
        logger.log_err(MODULE_NAME, msg)
        
    msg = "Created backup of /etc/pam.d/* to %s" % (backupfile)
    logger.log_info(MODULE_NAME, msg)
    return True

##############################################################################
def convert_to_cracklib():

    # Sample output from pam-config -q --pwcheck
    # password: debug cracklib cracklib_path=/usr/lib/cracklib_dict minlen=5 tries=5
    pam_minlen   = '5'
    pam_retry    = ''
    pam_dictpath = ''

    msg = "Converting PAM password from pwcheck to crackib; preserving settings where possible"
    logger.log_err(MODULE_NAME, msg)

    settings = config(modName='pwcheck')
    disable(modName='pwcheck')
    results = enable(modName='cracklib')
    if results == False:
        return False

    if settings.has_key('password'):
        for libopt in settings['password']:

            if libopt.startswith('minlen='):
                try:
                    pam_minlen = libopt.split('=')[1]
                except IndexError:
                    pam_minlen = '5'
                cracklib_set(option='minlen', optValue=str(pam_minlen))

            if libopt.startswith('tries='):
                try:
                    pam_retry = libopt.split('=')[1]
                except IndexError:
                    pass
                if pam_retry != '':
                    cracklib_set(option='retry', optValue=str(pam_retry))

            if libopt.startswith('cracklib_path='):
                try:
                    pam_dictpath = libopt.split('=')[1]
                    cracklib_set(option='dictpath', optValue=str(pam_dictpath))
                except IndexError:
                    continue
    
    return True

if __name__ == '__main__':
    #convert_to_cracklib()
    print cracklib_get('ucredit')
    print cracklib_set(option='ucredit', optValue='-1')
