/*
 * Copyright 2014-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.auth.shiro;

class OldHash implements Serializable, Comparable {
    ShiroUser shiroUser;
    String previousHash;
    Date lastChange;
    
    static belongsTo = [shiroUser:ShiroUser] 
    static mapping = {
            autoTimestamp false
            
    }
    static constraints = {
        shiroUser(nullable: false); 
        lastChange(nullable: false, blank: true,);       
    }
    String toString() {
      return "${id} ${shiroUser.username} ${lastChange}  "
    }
    int compareTo(obj) {
      lastChange.compareTo(obj.lastChange)
    }
}
