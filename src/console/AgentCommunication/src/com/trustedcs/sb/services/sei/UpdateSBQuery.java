/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class UpdateSBQuery {

    private String m_cpeShortName;

    /**
     * Parameterless constructor
     */
    public UpdateSBQuery() {
    }

    /**
     * Constructs a query with the given id and fingerprint for the profile
     * @param id
     * @param fingerprint
     */
    public UpdateSBQuery(String cpeShortName) {
        m_cpeShortName = cpeShortName;
    }

    public String getCpeShortName() {
        return m_cpeShortName;
    }

    public void setCpeShortName(String cpeShortName) {
        m_cpeShortName = cpeShortName;
    }

}
