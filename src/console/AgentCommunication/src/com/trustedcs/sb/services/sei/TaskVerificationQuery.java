/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class TaskVerificationQuery {

    // task id
    // "${scheduledTask.id}:${client.id}:${group.id}"
    private String m_id;
    // security profile fingerprint
    private String m_securityProfileFingerprint;
    // baseline profile fingerprint
    private String m_baselineProfileFingerprint;

    /**
     * Parameterless constructor
     */
    public TaskVerificationQuery() {
    }

    /**
     * Constructs a query with the given id and fingerprint for the profile
     * @param id
     * @param fingerprint
     */
    public TaskVerificationQuery(String id,
                                 String securityProfileFingerprint,
                                 String baselineProfileFingerprint) {
        m_id = id;
        m_securityProfileFingerprint = securityProfileFingerprint;
        m_baselineProfileFingerprint = baselineProfileFingerprint;
    }

    public String getId() {
        return m_id;
    }

    public void setId(String id) {
        m_id = id;
    }

    public String getSecurityProfileFingerprint() {
        return m_securityProfileFingerprint;
    }

    public void setSecurityProfileFingerprint(String profileFingerprint) {
        m_securityProfileFingerprint = profileFingerprint;
    }

    public String getBaselineProfileFingerprint() {
        return m_baselineProfileFingerprint;
    }

    public void setBaselineProfileFingerprint(String profileFingerprint) {
        m_baselineProfileFingerprint = profileFingerprint;
    }
}
