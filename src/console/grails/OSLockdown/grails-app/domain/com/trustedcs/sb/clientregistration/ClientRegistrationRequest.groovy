/*
 * Original file generated in 2010 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.clientregistration;
import com.trustedcs.sb.util.ClientType;

class ClientRegistrationRequest {
	
	Date timeStamp;
	String name;
	String hostAddress;
	String location;
	String contact;
    ClientType clientType;
    String processorName;
    String displayText;    
	int port;
    
    static constraints = {
        name(maxSize:100,blank:false,unique:false);
        processorName(maxSize:24,blank:true,unique:false,nullable:true);
        displayText(maxSize:50,blank:true,unique:false,nullable:true);
        clientType(nullable:true);
        hostAddress(maxSize:100,blank:false,unique:false);
        location(maxSize:200,blank:true,nullable:true);
        contact(maxSize:200,blank:true,nullable:true);
        port(min:1,max:65536);    	
    }    
    
}
