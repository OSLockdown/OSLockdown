/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2012 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo

/**
 * This class contains real-time information obtained from
 * a Client.
 */
class ClientInfo implements Serializable {

    // default information string (moved these here from ClientInfoService whose one method I merged into ClientService)
    static final String UNDETERMINED = "UNDETERMINED";
    static final String CLIENT_VERSION = "ClientVersion";
    static final String NODE_NAME = "Nodename";
    static final String DISTRIBUTION = "Distro";
    static final String KERNEL = "Kernel";
    static final String UPTIME = "Uptime";
    static final String ARCHITECTURE = "Arch";
    static final String LOAD_AVERAGE = "Loadavg"
    static final String MEMORY = "Memory";
    static final String COREHOURS = "CoreHours";
    static final String MAXLOAD = "MaxLoad";

    private static final String UNDETERMINED_DEFAULT = "Undetermined"	
    String clientVersion = UNDETERMINED_DEFAULT;
    String nodeName = UNDETERMINED_DEFAULT;
    String distribution = UNDETERMINED_DEFAULT;
    String kernel = UNDETERMINED_DEFAULT;
    String uptime = UNDETERMINED_DEFAULT;
    String architecture = UNDETERMINED_DEFAULT;
    String loadAverage = UNDETERMINED_DEFAULT;
    String memory = UNDETERMINED_DEFAULT;
    String corehours = UNDETERMINED_DEFAULT;
    String maxload = UNDETERMINED_DEFAULT;
	String errorMsg = null;
    static belongsTo = Client;
	
    static constraints = {
        errorMsg (nullable:true, blank:true);
        clientVersion(nullable:true);
        nodeName(nullable:true);
        distribution(nullable:true);
        kernel(nullable:true);
        uptime(nullable:true);
        architecture(nullable:true);
        loadAverage(nullable:true);
        memory(nullable:true);
        corehours(nullable:true);
        maxload(nullable:true);
    }
    
    
}
