/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.web.notifications;
import com.trustedcs.sb.util.ConsoleTaskPeriodicity;

/**
 *  Note - these enumeration values *MUST* kept for historical 
 *    If a flag is no longer used, change the setting to *deprecated*
 */
 
public enum UpstreamNotificationTypeEnum {
   // ENUM_NAME          = name to use internally in *IN CODE*
   // defaultPeriodicity = default delay minutes/hours
   // displayed string   = text to show for log files/GUI - probably should be localized....
   // quartzJobName      = string that if not empty indicates the name for scheduling dynamic tasking

   // ENUM_NAME          defaultPeriodicity,                          defaultEnable  Enterprise Only,  'display string',                                       LogString                   userCanChangeTime   quartzJobName)
    APP_START_STOP     ( ConsoleTaskPeriodicity.ON_OCCURANCE,         false,         false,            'Report application startup/shutdown',                  "App start/stop",                 false,        "ReportAppStartStop" ),
    APP_LICENSE        ( ConsoleTaskPeriodicity.ON_OCCURANCE,         false,         false,            'Check and report license changes',                     "License status",                 false,        "CheckLicense" ),
    USER_AUTH          ( ConsoleTaskPeriodicity.ON_OCCURANCE,         false,         false,            'Report Admin Console authentication events',           "Authentication",                 false,        "ReportUserAuth" ),
    TASK_COMPLETION    ( ConsoleTaskPeriodicity.ONCE_EVERY_5_MINUTES, false,         true,             'Check Scheduled Task completions',                     "Scheduled Task Completion",      true,         "CheckTasks" ),
    CLIENT_STATUS      ( ConsoleTaskPeriodicity.ONCE_EVERY_HOUR,      false,         false,            'Ping Client(s)',                                       "Client ping",                    true,         "CheckClients" ),
    TASK_RPT_STATUS    ( ConsoleTaskPeriodicity.ON_OCCURANCE,         false,         true,             'Report Clients with new findings in a scheduled task', "Scheduled Task New Findings",    false,        "ReportNewFindings" ),
    
    ConsoleTaskPeriodicity defaultPeriodicity;
	String displayString;
	String logString;
	String quartzJobName;
	Boolean userCanChangeTiming;
	Boolean defaultEnabled;
	Boolean enterpriseOnly;
    
	UpstreamNotificationTypeEnum(ConsoleTaskPeriodicity defaultPeriodicity, Boolean defaultEnabled, Boolean enterpriseOnly, String display, String logString, Boolean userCanChangeTiming, String quartzJobName) {
        this.defaultPeriodicity = defaultPeriodicity
		this.displayString = display
        this.quartzJobName = quartzJobName
        this.userCanChangeTiming = userCanChangeTiming
        this.defaultEnabled = defaultEnabled
        this.logString = logString
        this.enterpriseOnly = enterpriseOnly
	}

    public String getQuartJobName() {
        return quartzJobName;
    }	
	public String getDisplayString() {
		return displayString;
	}

	public String getLogString() {
		return logString;
	}
	
	/**
	 * Returns the string representation of the given enum ordinal
	 * @param ordinal
	 * @return the string
	 */
	public static String getDisplayString(int ordinal) {
		def tmp = getEnumFromOrdinal(ordinal);
		if ( tmp ) {
			return tmp.getDisplayString();
		}
		return "Unknown"
	}

    static UpstreamNotificationTypeEnum byQuartzJobName(String enumString) {
        values().find {it.quartzJobName == enumString}
    }
	
	/**
	 * Returns an enum for the given ordinal
	 * @param ordinal
	 * @return the enum
	 */
	public static UpstreamNotificationTypeEnum getEnumFromOrdinal(int ordinal) {
		for (UpstreamNotificationTypeEnum n : UpstreamNotificationTypeEnum.values() ) {
			if ( n.ordinal() == ordinal ) {
                return n;
            }
		}
		return null;		
	}
    String toString()
    {
      return "-> ${displayString} quartzJobname(${quartzJobName}) userCanChangeTiming(${userCanChangeTiming}) defaultPeriodicity(${defaultPeriodicity})"
    }
}
