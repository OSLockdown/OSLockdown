/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo

import com.trustedcs.sb.web.pojo.Group
import com.trustedcs.sb.util.ClientType;

import org.apache.log4j.Logger;

class Client implements Serializable {

    // Missing reports at detachment related constants
    static final String DETACHMENT_MISSING_REPORTS_SEPARATOR = "|"
    static final String DETACHMENT_MISSING_LATEST_ASSESSMENT_REPORT = "assessment-report-LATEST.xml"
    static final String DETACHMENT_MISSING_LATEST_BASELINE_REPORT   = "baseline-report-LATEST.xml"
    static final String DETACHMENT_NOTHING_MISSING                  = "Latest Assessment and Baseline Reports retained"
    static final String DETACHMENT_MISSING_REPORTS_ERROR_PREFIX     = "Error"
    // Detachment filter values
    static final String DETACHMENT_CLIENTS_ALL                      = "all"
    static final String DETACHMENT_CLIENTS_DETACHED                 = "detached"
    static final String DETACHMENT_CLIENTS_ATTACHED                 = "attached"
    // Date format in which the Detachment Date Strings are returned in the ClientService.detachClients() method.
    static final String DETACHED_DATE_FORMAT                        = "MMM-dd-yyyy";
    // Detachment Data Map Keys related constants
    static final String DETACHMENT_MAP_GROUP_NAME_KEY               = "grNm"
    static final String DETACHMENT_MAP_GROUP_NAME_ID_KEY            = "grID"
    static final String DETACHMENT_MAP_SECURITY_PROFILE_NAME_KEY    = "spNm"
    static final String DETACHMENT_MAP_SECURITY_PROFILE_ID_KEY      = "spID"
    static final String DETACHMENT_MAP_BASELINE_PROFILE_NAME_KEY    = "bpNm"
    static final String DETACHMENT_MAP_BASELINE_PROFILE_ID_KEY      = "bpID"
    // Names of the Security and Baseline Profile retained (if any, since Client could not have a Group, or that
    // Group could not have a Security or Baseline Profile or both) in /var/lib/oslockdown/reports/ec/clients/${clientID}/
    // No need to append timestamp to these names since a Client can only be detached once. If it's re-attached, then a brand new
    // Client is created (to eat up one more license from the count) and these are *moved* over from the Old Client to the New Client
    // and used to create a new Group with the Sec and Bas profiles (from these files OR use their state as of time of re-attachment).
    static final String DETACHMENT_SECURITY_PROFILE_FILE_NAME       = "security-profile-at-detachment.xml"
    static final String DETACHMENT_BASELINE_PROFILE_FILE_NAME       = "baseline-profile-at-detachment.xml"

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.web.pojo.Client");

    // Grails 1.3.* supports the isDirty() on the whole domain model object as well as on each of its properties.
    // However, since we are still using 1.2.2 this is the isDirty() implementation which is needed since we don't
    // want to throw "Combination of name and port should be unique" error when the user updates the Client *but does not
    // change either of the name or port* (which happens on the Refresh Detail BTW).
    // Populate the transient persistedName and persistedPort properties during the afterLoad/afterInsert/afterUpdate GORM event hooks,
    // and then use them inside of the validateUniqueNameAndPort() method to check whether during Client update either name or port
    // have changed (and if so run the SQL uniqueness check). During Client creation the SQL check always runs.
    transient private String persistedName
    transient private Integer persistedPort
    def afterLoad = {
        persistedName = name
        persistedPort = port
    }
    def afterInsert = {
        persistedName = name
        persistedPort = port
    }
    def afterUpdate = {
        persistedName = name
        persistedPort = port
    }

    // constraints
    static constraints = {
    	name(maxSize:100,blank:false,
            // Ensure the *combination of {name, port}* is unique
            validator: { nameValue, client ->

                // nameValue == client.name so can't do any isDirty() checks. In Grails 1.3 there
                // is support for isDirty() and getPersistedValue() for domain object as a whole and each property separately.
                List errorList = validateUniqueNameAndPort( client )
                if( errorList ){
                    return errorList
                }
                else {
                    // Passed validation
                    return true
                }
            }
        );
        description(blank:true, nullable:true, maxSize:200);
    	hostAddress(maxSize:100,blank:false,unique:false);
    	group(nullable:true);    	
    	location(maxSize:200,blank:true,nullable:true);
    	contact(maxSize:200,blank:true,nullable:true);
    	info(nullable:true);
        // Make sure dateCreated is nullable to support existing SB installations -- i.e. don't want to
        // write a DB upgrade code to initialize dateCreated since don't know what to set it to 
        dateCreated(nullable:true);
        dateDetached(nullable:true);
        clientType(nullable:true);
    	port(min:1,max:65536,
            // Ensure the *combination of {name, port}* is unique
            validator: { portValue, client ->

                // portValue == client.port so can't do any isDirty() checks. In Grails 1.3 there
                // is support for isDirty() and getPersistedValue() for domain object as a whole and each property separately.
                List errorList = validateUniqueNameAndPort( client )
                if( errorList ){
                    return errorList
                }
                else {
                    // Passed validation
                    return true
                }
            }
       );
       detachDataMap(nullable:true);
    }

    void setHostAddress(String address) {
        if (address.contains(":")) 
        {
            if (!address.startsWith("[")) {
                address = "[" + address;
            }
            if (!address.endsWith("]")) {
                address = address + "]";
            }
        }        
        hostAddress = address;
    }
        
    
    private static List validateUniqueNameAndPort( Client client )
    {
        List errorList

        // Only run validation if client does not have any errors -- because if client.nonUniqueNameAndPortCombination
        // error was already populated during validation on one side (name OR port), don't re-run the validation
        // on the other (port OR name, respectively).
        // Note: that returning a non-null list (as done below with
        //     errorList = ['client.nonUniqueNameAndPortCombination', aName, aPort+"" ]
        // ) does set that error into the client object and I *don't need to do it on my own* with something similar like
        //    client.errors.reject( "client.nonUniqueNameAndPortCombination",
        //                        [aName, aPort+"" ] as Object[], "")
        if( !client.hasErrors() ){

            boolean validateUniqueNameAndPort = false
            //
            if( !client.id ){
                // Always validate on creates of new Clients
                validateUniqueNameAndPort = true
            }
            else {

                // Replace this section *and* the transient variables at the top of this class and their
                // population inside of afterLoad()/afterInsert()/afterUpdate() with the commented out section below.
                if( client.name != client.persistedName || !client.port.equals( client.persistedPort ) )
                {
                    validateUniqueNameAndPort = true
                }

                //
                //Uncomment after upgrade to Grails 1.3 that has support for isDirty() which is extremely useful
                //in this case, since for non-new clients the check below should *only* run if either name or port have changed.
                //
                //if( client.isDirty( 'name' ) || client.isDirty( 'port' ) )
                //{
                //    validateUniqueNameAndPort = true
                //}
            }

            if( validateUniqueNameAndPort ){

                String name  = client.name
                Integer port = client.port

                String queryString = "select count(*) from Client where name='${name}' and port=${port}"

                def countList = Client.executeQuery( queryString )

                // If there is already one contact with contactType.name, throw validation exception
                if( countList && countList[ 0 ].intValue() >= 1 )
                {
                    errorList = ['client.nonUniqueNameAndPortCombination', name, port+"" ]
                }
            }
        }

        return errorList
    }

    static namedQueries = {
        ascendingList {
            order 'name', 'asc'
        }

        descendingList {
            order 'name', 'desc'
        }
    }

    static mapping = {
        sort 'name';

        // Override out-of-the-box behavior in Grails, and don't auto populate the *dateCreated* field on Client creation.
        // We do it ourselves instead, which allows setting it to something else other than now for the DB import.
        autoTimestamp false
    }
    
    // Persisted fields
    String name;
    String description;
    String hostAddress;
    String location;
    String contact;
    Integer port = 6443;
    ClientInfo info;
    Group group;
    Date dateCreated = new Date(); // Populate it ourselves on creation. Can be overriden for DB import since autoTimestamp false.
    Date dateDetached;
    Map detachDataMap;
    ClientType clientType;    
    String toString() {
    	name
    }
    
    // stub routine - eventually return any procs this Client is *restricted*
    // to run on - if empty run on any
    String allProcs() {
        return "";
    }
    
}
