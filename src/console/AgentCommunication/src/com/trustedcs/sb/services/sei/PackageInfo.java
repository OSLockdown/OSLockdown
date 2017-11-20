/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

import java.io.*;

public class PackageInfo  {

    private String  m_fileName;
    private String  m_fingerprint;
    private String  m_data;
    private Boolean m_isPkg;
    
    /**
     * Empty Constructor
     */
    public PackageInfo() {
        m_fileName = "";
        m_fingerprint = "";
        m_data = null;
        m_isPkg = false;
    }

    
    public String getfileName() {
        return m_fileName;
    }

    public void setfileName(String fileName) {
        m_fileName = fileName;
    }

    public String getdata() {
        return m_data;
    }

    public void setdata(String data) {
        m_data = new String(data);
    }

    public String getfingerprint() {
        return m_fingerprint;
    }

    public void setfingerprint(String fingerprint) {
        m_fingerprint = fingerprint;
    }


    public Boolean getisPkg() {
        return m_isPkg;
    }

    public void setisPkg(Boolean isPkg) {
        m_isPkg = isPkg;
    }

}
