/*
 * Original file generated in 2011 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2011-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.preferences;

class AppDBPreferences {

    String dbApplicationVersion
    String prevDbApplicationVersion
    Date dbLastUpgradedOn

    static constraints = {
        dbApplicationVersion(nullable:false,blank:false)
        prevDbApplicationVersion(nullable:true)
        dbLastUpgradedOn(nullable:true)
    }

    static mapping = {
        // Override out-of-the-box behavior in Grails and don't add the dateCreated and lastUpdated
        autoTimestamp false
    }
}
