/**
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 * Include header holding path locations and other top level information
 * Roughly analogous to the standalone/sbProps.py
 *
 */

#ifndef _SB_PROPS_H
#define _SB_PROPS_H

#define APPLICATION_HOME             	  "/usr/share/oslockdown"
#define APPLICATION_PID_FILE         	  "/var/run/OSL_Dispatcher.pid"
#define APPLICATION_DATA             	  "/var/lib/oslockdown"
#define APPLICATION_ASSESSMENTS      	  APPLICATION_DATA"/reports/standalone/assessments"
#define APPLICATION_BASELINES        	  APPLICATION_DATA"/reports/standalone/baselines"
#define APPLICATION_ASSESSMENT_COMPS      APPLICATION_DATA"/reports/standalone/assessment_reports"
#define APPLICATION_BASELINE_COMPS        APPLICATION_DATA"/reports/standalone/baseline_reports"

/**
 * New in v4.0.3
 */
#define APPLICATION_APPLY_REPORTS      	  APPLICATION_DATA"/reports/standalone/apply-reports"
#define APPLICATION_UNDO_REPORTS      	  APPLICATION_DATA"/reports/standalone/undo-reports"
#define APPLICATION_STATEFILE             APPLICATION_DATA"/oslockdown-state.xml"

/*
#define APPLICATION_LOGFILES         	  APPLICATION_DATA"/logs"
*/
#define APPLICATION_SSL_CERTS        	  APPLICATION_DATA"/files/certs"
#define APPLICATION_DISPATCHER_LOG   	  "/var/log/oslockdown-dispatcher.log"
#define APPLICATION_TASKS	     	  APPLICATION_DATA"/reports/standalone/tasks"
#define APPLICATION_CMD_PATH         	  "/usr/sbin/oslockdown"
#define APPLICATION_EXECNAME              "oslockdown"
#define APPLICATION_SECURITY_MODULES_XML  APPLICATION_HOME"/cfg/security-modules.xml"
#define APPLICATION_LOG_FILE_MAX_MB			  5
#endif
