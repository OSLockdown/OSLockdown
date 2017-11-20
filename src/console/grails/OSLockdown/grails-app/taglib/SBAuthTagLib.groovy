/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
import com.trustedcs.sb.license.SbLicense; 

class SBAuthTagLib {
	
    static namespace = 'sbauth'
	
    def isEnterprise = { attrs, body ->
        if( SbLicense.instance.isEnterprise() ) {
            out << body();
        }
    }

    def isBulk = { attrs, body ->
        if( SbLicense.instance.isBulk() ) {
            out << body();
        }
    }

    def isEnterpriseOrBulk = { attrs, body ->
        if( SbLicense.instance.isEnterprise() || SbLicense.instance.isBulk() ) {
            out << body();
        }
    }

    def isStandalone = { attrs, body ->
        if( SbLicense.instance.isStandAlone() ) {
            out << body();
        }
    }
	
    def version = { attrs, body ->
        out << SbLicense.instance.getVersion();
    }
	
    def isValid = { attrs, body ->
        if ( SbLicense.instance.isValid() ) {
            out << body();
        }
    }
	
    def isInvalid = { attrs, body ->
        if ( ! (SbLicense.instance.isValid()) ) {
            out << body();
        }
    }
	
    def product = { attrs, body ->
        if ( SbLicense.instance.isEnterprise() ) {
            out << SbLicense.ENTERPRISE_LICENSE;
        }
        else if ( SbLicense.instance.isBulk() ) {
            out << SbLicense.LOCK_AND_RELEASE_LICENSE;
        }
        else {
            out << SbLicense.STANDALONE_LICENSE;
        }
    }

}
