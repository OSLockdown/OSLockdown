/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public class UpdateSBResponse extends SBResponse {

    private String m_packages;

    /**
     * Empty Constructor
     */
    public UpdateSBResponse() {
    }

    public UpdateSBResponse(int code, String reasonPhrase) {
        super(code, reasonPhrase);
    }

    public String getPackages() {
        return m_packages;
    }

    public void setPackages(String packages) {
        m_packages = packages;
    }
}
