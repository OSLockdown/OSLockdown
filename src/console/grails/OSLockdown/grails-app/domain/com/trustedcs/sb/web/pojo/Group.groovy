/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo;

import com.trustedcs.sb.metadata.Profile;
import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.scheduler.ScheduledTask;
import org.apache.log4j.Logger;

class Group implements Serializable {

    static def m_log = Logger.getLogger("com.trustedcs.sb.web.pojo.Group");

    static mapping = {
        table 'SBGroup' // Table name of 'Group' not allowed, so use SBGroup
        clients sort:'name';
    }

    static constraints = {
        name(maxSize:20, blank:false, unique:true);
        description(blank:true, maxSize:200);
        profile(nullable:true);
        baselineProfile(nullable:true);
    }

    String name;
    String description;
    Profile profile;
    BaselineProfile baselineProfile;

    static hasMany = [clients:Client,
                      tasks:ScheduledTask]
    
    
    String toString() {
    	return "id [$id] name[$name] description[$description] profile[$profile] clients[$clients]";
    }
}
