/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public interface UpdateSBService {

    /**
     * Querys the service to find out if a task is up to date.
     * @param query
     * @return
     */
    public byte[] listPackages(String hostName, String pkgRoot, String cpeShortName, String majorVersion, String minorVersion, String arch, Boolean withDocs);
}
