#!/usr/bin/env python
#############################################################################
# Copyright (c) 2007-2015 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Master Properties file for OS Lockdown
#
# CAUTION: Before changing attribute names or removing any of them,
#          be sure that no Python source code file requires them!!!
#          
#          Recursively search every Python file in the <root>/src 
#          structure first!!
#
##############################################################################
# Setting this flag enables certain messages to stdout and logging
# Set to FALSE before production release

DEVELOPMENT_MODE = True

PRODUCT_NAME = "OS Lockdown"
VERSION      = "5.0.0"
COPYRIGHT    = "Copyright (c) 2007-2016 Forcepoint LLC" 

XML_ENCODING    = "UTF-8"
SB_BASE         = "/usr/share/oslockdown"
SB_VAR_BASE     = "/var/lib/oslockdown"

# in MB
DISK_SPACE_REQUIRED = 20 

BACKUP_DIR      = "/var/lib/oslockdown/backup"
SB_CONFIG_FILE  = "/usr/share/oslockdown/cfg/security-modules.xml" 
SB_STATE_FILE   = "/var/lib/oslockdown/oslockdown-state.xml" 
SB_STATE_FILE_BACKUP = "/var/lib/oslockdown/backup/oslockdown-state-backup.xml" 
PIDFILE         = "/var/run/oslockdown.pid"
SB_DIR_CERTS    = "/var/lib/oslockdown/files/certs"
BASELINE_CONFIG = "/usr/share/oslockdown/cfg/baseline-modules.xml"

BASELINE_PROFILES  = "/var/lib/oslockdown/baseline-profiles"
SECURITY_PROFILES  = "/var/lib/oslockdown/profiles"
BASELINE_REPORTS   = "/var/lib/oslockdown/reports/standalone/baselines"
ASSESSMENT_REPORTS = "/var/lib/oslockdown/reports/standalone/assessments"
APPLY_REPORTS      = "/var/lib/oslockdown/reports/standalone/apply-reports"
UNDO_REPORTS       = "/var/lib/oslockdown/reports/standalone/undo-reports"

##############################################################################
## Report Locations
SB_DIR_REPORTS = "/var/lib/oslockdown/reports"
SB_DATA        = "/var/lib/oslockdown/reports/standalone"

##############################################################################
## Logging Locations
SB_DIR_LOGS      = "/var/lib/oslockdown/logs"
SB_LOG           = "%s/oslockdown.log" % SB_DIR_LOGS
SB_LOG_MAX       = 5000000
SB_LOG_WARN_SIZE = 2500000
SB_ROTATE_CONF   = "/etc/logrotate.d/oslockdown"

##############################################################################
### Installation specific files for whitelists/fstype/excludes
EXCLUSION_DIRS           = "/var/lib/oslockdown/files/exclude-dirs"
INCLUSION_FSTYPES        = "/var/lib/oslockdown/files/inclusion-fstypes"
SUID_WHITELIST         = "/var/lib/oslockdown/files/suid_whitelist"
SGID_WHITELIST         = "/var/lib/oslockdown/files/sgid_whitelist"

##############################################################################
## XML Schema Definition (XSD) Files
##
XSD_CONFIG_FILE      = "%s/cfg/schema/SecurityModules.xsd" % SB_BASE
XSD_PROFILE          = "%s/cfg/schema/SecurityProfile.xsd" % SB_BASE
XSD_BASELINE_PROFILE = "%s/cfg/schema/BaselineProfile.xsd" % SB_BASE
XSD_BASELINE_REPORT  = "%s/cfg/schema/BaselineReport.xsd" % SB_BASE
XSD_BASELINE_CONFIG  = "%s/cfg/schema/BaselineConfiguration.xsd" % SB_BASE
XSD_STATE_FILE       = "%s/cfg/schema/oslockdown-state.xsd" % SB_BASE

##############################################################################
### Stylesheeets (XSL) - XML Transformations
###
XSL_DIR    = "%s/cfg/stylesheets/"              % SB_BASE

##############################################################################
### Flag to be set True when SIGUSR1 detected, indicating an Abort has 
### requested.  Note that the Abort is not immediate, but for now should be 
### checked between security or baseline modules. 
ABORT_REQUESTED = False

##############################################################################
## Exit Codes
##   The following codes are used as an argument to the 
##   sys.exit(ARG) call. Adjust the integer to meet the needs
##   of the calling component (i.e., agent).
##
EXIT_SUCCESS    = 0
EXIT_FAILURE    = 1
EXIT_ABORT      = 2
EXIT_CONFIG_ERR = 3

EXIT_PYTHON_IMPORT_ERR = 4
