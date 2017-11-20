/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class TaskVerificationResponse extends SBResponse {

    // 0 valid execute
    // 1 valid keep/no-op
    // 2 invalid remove
    // 3 valid new profile configuration        
    private int m_queryResultCode;
    // information / reason phrase in the response
    private String m_queryResultInfo;
    // the dispatcher task
    private DispatcherTask m_task;

    /**
     * Empty Constructor
     */
    public TaskVerificationResponse() {
    }

    public TaskVerificationResponse(int code, String reasonPhrase) {
        super(code, reasonPhrase);
    }

    public int getQueryResultCode() {
        return m_queryResultCode;
    }

    public void setQueryResultCode(int code) {
        m_queryResultCode = code;
    }

    public String getQueryResultInfo() {
        return m_queryResultInfo;
    }

    public void setQueryResultInfo(String info) {
        m_queryResultInfo = info;
    }

    public DispatcherTask getTask() {
        return m_task;
    }

    public void setTask(DispatcherTask task) {
        m_task = task;
    }
}
