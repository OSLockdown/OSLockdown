/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.help
import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.util.SBFileSystemUtil;

class HelpController {

    def index = { 
    	redirect(action:'documentation');
    }
    
    def contact = {
    		
    }
    
    def documentation = {
    		
    }
    
    def onlineHelp = {
    		
    }
	
    def info = {
	
        [licenseProperties:SbLicense.getInstance().getProperties()]
	
    }

    /**
     * !!! DEVELOPMENT ONLY !!!
     */
    def changeLicense = {
//        SbLicense.instance.changeProductType(params.productType);
        print params.productType;
        new File("/var/lib/oslockdown/files/ConsoleType.txt").write(params.productType);
	redirect(action:'info');
    }

    
}
