/*
 * Copyright 2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.util

// Pre SB4.1.2 code used an basic Java enum defined in the AgentCommunicator packages 
// that was supposed to indicate the *product type*.  So we need to honor that 
// ordering, even though we're superceding this with a Groovy enum that indicates the
// *client type* (as well as overloading it to indicate what clients a *processor* can 
// use).  So we need to keep the first 3 enums in the orginal order.
//        STANDALONE, ENTERPRISE, BULK

enum ClientType {
    // discrete elements
    //  'enum'          name                 propName        isDiscrete  needsArg   usableAsProcType
    CLIENT_STANDALONE(  "Standalone"       , "standalone"  , false     , false    , false),              
    CLIENT_ENTERPRISE(  "Enterprise"       , "enterprise"  , true      , true     , false),  
    CLIENT_BULK      (  "Lock and Release" , "bulk"        , true      , true     , false),  
    CLIENT_ZSERIES   (  "zSeries"          , "zSeries"     , false     , true     , true),   
	CLIENT_AIX       (  "AIX",             , "AIX"         , false     , true     , true),   
	
    // attributes
	String name
    String propName
    boolean isDiscrete
    boolean needsArg
    boolean usableAsProcType
	
    // look up id by name
    static ClientType byName(String name) {
        values().find {it.propName == name || it.name == name}
    }


    // get list of types able to be used for processor type
    static ArrayList<ClientType> userAllowed() {
        values().findAll {(it.usableAsProcType) }
    }

    // get list of types able to be used for processor type
    static ArrayList<ClientType> discreteClientTypes() {
        values().findAll {(it.isDiscrete) }
    }
    
    // constructor per element
    ClientType(String name, String propName, boolean isDiscrete, boolean needsArg, boolean usableAsProcType) {
	  this.name = name;
      this.propName = propName;
      this.needsArg = needsArg;
      this.isDiscrete = isDiscrete
      this.usableAsProcType = usableAsProcType;
	}
}
