/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.web.pojo.Processor;
import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.web.notifications.Notification;
import com.trustedcs.sb.clientregistration.ClientRegistrationRequest;
import com.trustedcs.sb.web.notifications.NotificationsController;
import com.trustedcs.sb.util.ClientType;

import org.apache.log4j.Logger;
import org.apache.shiro.SecurityUtils;
import org.apache.shiro.crypto.hash.Sha1Hash;

class DashboardController {
	
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.dashboard");

    def dataSource;

    /**
     * Displays the dashboard page
     */
    def index = {

        // redirect if we're in standalone mode
        if ( SbLicense.instance.isStandAlone() ) {
            if ( SecurityUtils.getSubject().hasRole("Management") ) {
                redirect(controller:'report',action:'index');
                return;
            }
            else {
                redirect(controller:'policyApplication',action:'index');
                return;
            }			
        }
			
        // unassociated group count
        def unassociatedGroupCount = Group.withCriteria {
            isNull("profile")
        }.size();
		
        // unassociated client count
        def unassociatedClientCount = Client.withCriteria {
            isNull("group")
        }.size();
	    
                
        // client count
        def clientCount = Client.count()
        
	    
        // client registrations in limbo
        def clientsWaiting = ClientRegistrationRequest.count();

        def notificationList = NotificationsController.getSortedNotificationList( dataSource, params, false )


        // Ok, specifically go get the Lock&Rel Count
        
        // return model
        [groupCount:Group.count(),
            clientCount:clientCount,
            unassociatedGroupCount:unassociatedGroupCount,
            unassociatedClientCount:unassociatedClientCount,
            clientsWaiting:clientsWaiting,
            notificationList:notificationList]
    }
	
    /**
     * Displays the 404 page
     */
    def notfound = {
    	
    }
	
    /**
     * Displays the error page
     */
    def error = {
		
    }
}
