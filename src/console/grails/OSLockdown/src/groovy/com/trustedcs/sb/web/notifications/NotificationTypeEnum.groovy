/*
 * Copyright 2009-2012 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.web.notifications;

/**
 * @author amcgrath
 *
 */
public enum NotificationTypeEnum {
	
	SCAN("Scan"),
	QUICK_SCAN("Quick-Scan"),
	APPLY("Apply"),	
	UNDO("Undo"),
	BASELINE("Baseline"),
	GROUP_ASSESSMENT("Group Assessment"),
	BASELINE_COMPARISON("Baseline Comparison"),
	SCHEDULED_SCAN("Scheduled Scan"),
	SCHEDULED_QUICK_SCAN("Scheduled Quick Scan"),
	SCHEDULED_APPLY("Scheduled Apply"),
	SCHEDULED_BASELINE("Scheduled Baseline"),
	SCHEDULED_TASK_COMPLETE('Task Completed'),
	AUTOUPDATE('AutoUpdate Client');

	private final String displayString;
	
	NotificationTypeEnum(String display) {
		displayString = display
	}
	
	public String getDisplayString() {
		return displayString;
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
	
	/**
	 * Returns an enum for the given ordinal
	 * @param ordinal
	 * @return the enum
	 */
	public static NotificationTypeEnum getEnumFromOrdinal(int ordinal) {
		for (NotificationTypeEnum n : NotificationTypeEnum.values() ) {
			if ( n.ordinal() == ordinal ) {
                return n;
            }
		}
		return null;		
	}
}
