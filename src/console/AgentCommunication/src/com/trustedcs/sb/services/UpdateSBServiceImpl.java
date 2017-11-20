/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import javax.jws.WebParam;
import javax.jws.WebService;

//import com.trustedcs.sb.services.sei.UpdateSBQuery;
import com.trustedcs.sb.services.sei.PackageInfo;
import com.trustedcs.sb.services.sei.UpdateSBService;
import com.trustedcs.sb.updatesb.UpdateSBEngine;

@WebService
public class UpdateSBServiceImpl implements UpdateSBService {

    /**
     * Returns if a task is up to date and if it still is valid
     * @param query
     */
    public byte[] listPackages( @WebParam(name = "hostName") String hostName,
                                  @WebParam(name = "pkgRoot") String pkgRoot,
                                  @WebParam(name = "cpeShortName") String cpeShortName,
                                  @WebParam(name = "majorVersion") String majorVersion,
                                  @WebParam(name = "minorVersion") String minorVersion,
                                  @WebParam(name = "arch") String arch,
                                  @WebParam(name = "withDocs") Boolean withDocs) {
        return UpdateSBEngine.getInstance().listPackages(hostName, pkgRoot, cpeShortName, majorVersion, minorVersion, arch, withDocs);
    }
}
