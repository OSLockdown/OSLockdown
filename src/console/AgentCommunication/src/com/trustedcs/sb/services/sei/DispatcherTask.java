/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class DispatcherTask {

    // the id of the task ( taken from the DB id )
    // ${taskId}:${clientId}:${groupId}
    private String m_id = null;

    // the list of actions strings in combination of 's','a','b'
    private String m_actions = null;

    // the logging level the actions should be executed at
    private int m_loggingLevel = 4;

    // 0 = daily
    // 1 = weekly
    // 2 = monthly
    private int m_periodType = 0;

    // days of the week starts at 0
    // day of the month starts at 1
    private int m_periodIncrement = 0;

    // time
    private int m_hour = 0;
    private int m_minute = 0;
    
    // profiles
    private String m_securityProfile;
    private String m_baselineProfile;

    /**
     *
     */
    public DispatcherTask() {
    }

    /**
     *
     * @param id
     * @param actions
     * @param loggingLevel
     * @param periodType
     * @param periodIncrement
     * @param hour
     * @param minute
     */
    public DispatcherTask(String id,
                          String actions,
                          int loggingLevel,
                          int periodType,
                          int periodIncrement,
                          int hour,
                          int minute,
                          String securityProfile,
                          String baselineProfile) {
        super();
        m_id = id;
        m_actions = actions;
        m_loggingLevel = loggingLevel;
        m_periodType = periodType;
        m_periodIncrement = periodIncrement;
        m_hour = hour;
        m_minute = minute;
        m_securityProfile = securityProfile;
        m_baselineProfile = baselineProfile;
    }

    public String getId() {
        return m_id;
    }

    public void setId(String id) {
        m_id = id;
    }

    public String getActions() {
        return m_actions;
    }

    public void setActions(String actions) {
        m_actions = actions;
    }

    public void setLoggingLevel(int level) {
        m_loggingLevel = level;
    }

    public int getLoggingLevel() {
        return m_loggingLevel;
    }

    public int getPeriodType() {
        return m_periodType;
    }

    public void setPeriodType(int periodType) {
        m_periodType = periodType;
    }

    public int getPeriodIncrement() {
        return m_periodIncrement;
    }

    public void setPeriodIncrement(int periodIncrement) {
        m_periodIncrement = periodIncrement;
    }

    public int getHour() {
        return m_hour;
    }

    public void setHour(int hour) {
        m_hour = hour;
    }

    public int getMinute() {
        return m_minute;
    }

    public void setMinute(int minute) {
        m_minute = minute;
    }

    public void setSecurityProfile(String securityProfile) {
        m_securityProfile = securityProfile;
    }

    public String getSecurityProfile() {
        return m_securityProfile;
    }

    public void setBaselineProfile(String baselineProfile) {
        m_baselineProfile = baselineProfile;
    }

    public String getBaselineProfile() {
        return m_baselineProfile;
    }
}
