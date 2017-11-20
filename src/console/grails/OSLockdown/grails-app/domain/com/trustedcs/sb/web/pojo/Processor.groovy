/*
 * Copyright 2013-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo

import org.apache.log4j.Logger;
import com.trustedcs.sb.util.ClientType;

class Processor implements Serializable {


    // constraints
    static constraints = {
    	name(maxSize:100,blank:false, unique:true);
        description(blank:true, nullable:true, maxSize:200);
        dateAdded(nullable:true);
        clientType(nullable:true);
    }
    
    // Persisted fields
    String name;
    String description;
    ClientType clientType;    
    Date dateAdded = new Date();
    String allInfo() {
    	
        return "id [$id] name[$name] description[$description] clientType[$clientType]";
    }    
    String toString() {
      name;
    }
}
