/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

public enum OSLockdownCommunicationType {

    AGENT("agent"),
    CONSOLE("console"),
    REPORTS("reports"),
    SCHEDULER("scheduler"),
    TASK_VERIFICATION("taskverification"),
    CLIENT_REGISTRATION("clientregistration"),
    UNKNOWN("unknown");
    private String m_urlPiece = null;

    private OSLockdownCommunicationType(String urlPiece) {
        m_urlPiece = urlPiece;
    }

    public String getUrlString() {
        return m_urlPiece;
    }
}
