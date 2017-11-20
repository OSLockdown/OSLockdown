/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.auth.shiro;

class ShiroUser implements Serializable {
	
    String username;
    String passwordHash;    
    Date lastChange;
    Date lastLogin;
    SortedSet oldHashes;
    static hasMany = [oldHashes:OldHash]
        
    static constraints = {
        username(nullable: false, blank: false, unique:true); 
        lastChange(nullable: true, blank: true,);       
        lastLogin(nullable: true, blank: true);       
    }
    static mapping = {
        autoTimestamp false
        oldHashes cascade: "all-delete-orphan"

    }
    
    boolean hashUsed(String candidateHash) {
    	 def hashFound = false
         oldHashes.each { if (candidateHash == it.previousHash)  hashFound=true  }
         return hashFound
    }
    
    int countOldHashes() {
      return oldHashes.size()
    }
    
    String toString() {
      return "${id} ${username} ${lastChange} ${lastLogin} ${oldHashes.size()}"
    }
}
