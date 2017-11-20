/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.notifications;

import org.apache.log4j.Logger;

import com.trustedcs.sb.util.SessionAlertUtil;
import com.trustedcs.sb.util.SBGSQLUtil;

import com.trustedcs.sb.exceptions.DispatcherNotificationException;
import org.hibernate.criterion.Order

class NotificationsController {

    // logger
    private static def m_log = Logger.getLogger("com.trustedcs.sb.web.notification.NotificationsController");

    // service injection
    def messageSource;
    def dispatcherNotificationService;
    def dataSource;

    /**
     * List notifications
     */
    def index = { 
        redirect(action:'list');
    }
    
    /**
     * List notifications
     */
    def list = {		
        def newNotificationCount = session.notificationCount ? session.notificationCount : 0;
        session.notificationCount = 0;

        def notificationList = getSortedNotificationList( dataSource, params, true )

    	[notificationList:notificationList, totalCount:Notification.count(),
            notificationList:notificationList, maxPerPage: ( params.max ? params.max : "25" ) ]
    }

    /**
     * Returns the sorted notification list. If
     *
     * @param the params Map
     * @param usePaginationOrTenElementsMax - true if called from NotificationsController, false if called from DashboardController.
     */
    static def getSortedNotificationList( def aDataSource, def params, boolean usePaginationOrTenElementsMax ){

        // Return sorted list of most recent notifications

        // Regular offset and max are *only* used if usePaginationOrTenElementsMax == true. If usePaginationOrTenElementsMax == false
        // max is hardcoded to 10.
        def offset
        def max
        if( usePaginationOrTenElementsMax ){
            offset = params.offset ? params.offset : "0"
            max    = params.max    ? params.max    : "25"
        }
        else {
            // if called from Dashboard hardcode to 10 items max (and no offset, ie. offset=0)
            max    = "10"
        }

        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table. However, only use valid sort and sortOrder in case user enters invalid values
        def sort         = ( params.sort == "timeStamp" || params.sort == "info" || params.sort == "type" ||
                             params.sort == "results" || params.sort == "source" ) ? params.sort : "timeStamp"
        def sortOrder    = ( params.order == "asc" || params.order == "desc" ) ? params.order : "desc"

        def notificationList

        // Direct property of Notification object
        if( sort == "timeStamp" || sort == "info" ){

            if( usePaginationOrTenElementsMax ){

                notificationList =
                    Notification.createCriteria().list( offset:offset, max:max ) {
                        order( new Order(sort, sortOrder=="asc").ignoreCase() ) 
                    }
            }
            else {
                notificationList = Notification.list( sort:sort, order:sortOrder, max:max, ignoreCase:true )
            }
        }
        else if (sort == "source") {
            if( !usePaginationOrTenElementsMax ){
                offset=0
            }

            // HQL can't do this, so spit it out using raw SQL....
            String queryString = """
                    select n.id, g.name as name from Notification n, SBGroup g where n.source_Id = g.id and n.type=5
                    union
                    select n.id, c.name as name from Notification n, Client c where n.source_Id = c.id AND n.type!=5
                    order by name ${sortOrder}"""
        
            
            notificationList = SBGSQLUtil.executeSelectWithIdGSQL( aDataSource, queryString,
                com.trustedcs.sb.web.notifications.Notification.class, max, offset )
            
        }
        // type = dataMap['action'], but can't use
        //      order ( dataMap['action'], sortOrder ).ignoreCase()
        // or
        //      dataMap {
        //          order ( action, sortOrder ).ignoreCase()
        //      }
        else if( sort == "type" ){

            // if Notification.type == NotificationTypeEnum.Group Assessment then dataMap['action'] is null (and not-null for all other types) so
            //    notificationList = Notification.executeQuery( "from Notification order by dataMap['action'] ${sortOrder}", [max:10] )
            // is missing Group Assessment Notifications, so can't use it.
            //
            // Instead, order asc / desc based on the display String of each NotificationTypeEnum as that is what is being shown
            // in the Notification Type column.Here are ALL possible display names ordered by their position which equals type
            //  Display Name                                        Type
            //  ============                                        ====
            //  SCAN("Scan"),                                       0
            //  QUICK_SCAN("Quick-Scan"),                           1
            //  APPLY("Apply"),                                     2
            //  UNDO("Undo"),                                       3
            //  BASELINE("Baseline"),                               4
            //  GROUP_ASSESSMENT("Group Assessment"),               5
            //  BASELINE_COMPARISON("Baseline Comparison"),         6
            //  SCHEDULED_SCAN("Scheduled Scan"),                   7
            //  SCHEDULED_QUICK_SCAN("Scheduled Quick Scan"),       8
            //  SCHEDULED_APPLY("Scheduled Apply"),                 9
            //  SCHEDULED_BASELINE("Scheduled Baseline"),           10
            //  SCHEDULED_TASK_COMPLETE('Task Completed');          11
            //  AUTOUPDATE('AutoUpdate Client');                    12


            String queryString

            if( sortOrder == "asc" ){
                // order "asc" (from lowest to highest) based on Display Name

                //  Display Name                                        Type        Order
                //  ============                                        ====        =====
                //  APPLY("Apply"),                                     2           0
                //  AUTOUPDATE('AutoUpdate Client');                    12          1
                //  BASELINE("Baseline"),                               4           2
                //  BASELINE_COMPARISON("Baseline Comparison"),         6           3
                //  GROUP_ASSESSMENT("Group Assessment"),               5           4
                //  QUICK_SCAN("Quick-Scan"),                           1           5
                //  SCAN("Scan"),                                       0           6
                //  SCHEDULED_APPLY("Scheduled Apply"),                 9           7
                //  SCHEDULED_BASELINE("Scheduled Baseline"),           10          8
                //  SCHEDULED_QUICK_SCAN("Scheduled Quick Scan"),       8           9
                //  SCHEDULED_SCAN("Scheduled Scan"),                   7           10
                //  SCHEDULED_TASK_COMPLETE('Task Completed');          11          11
                //  UNDO("Undo"),                                       3           12

                queryString = """
                    CASE type
                        WHEN 2  THEN 0
                        WHEN 12 THEN 1
                        WHEN 4  THEN 2
                        WHEN 6  THEN 3
                        WHEN 5  THEN 4
                        WHEN 1  THEN 5
                        WHEN 0  THEN 6
                        WHEN 9  THEN 7
                        WHEN 10 THEN 8
                        WHEN 8  THEN 9
                        WHEN 7  THEN 10
                        WHEN 11 THEN 11
                        WHEN 3  THEN 12
                        ELSE         13
                    END
                              """
            }
            else {
                // for sortOrder == "desc" reverse the order

                queryString = """
                    CASE type
                        WHEN 3  THEN 0
                        WHEN 11 THEN 1
                        WHEN 7  THEN 2
                        WHEN 8  THEN 3
                        WHEN 10 THEN 4
                        WHEN 9  THEN 5
                        WHEN 0  THEN 6
                        WHEN 1  THEN 7
                        WHEN 5  THEN 8
                        WHEN 6  THEN 9
                        WHEN 4  THEN 10
                        WHEN 12 THEN 11
                        WHEN 2  THEN 12
                        ELSE         13
                    END
                              """
            }

            if( usePaginationOrTenElementsMax ){

                // 1. Using this query with paginate parameters does not work
                //      notificationList = Notification.executeQuery( "from Notification ORDER BY ${queryString}", [:], [max:max, offset:offset] ) OR
                //      notificationList = Notification.executeQuery( "select id from Notification ORDER BY ${queryString}", [:], [max:max, offset:offset] )
                // result in a errors.GrailsExceptionResolver Invalid query error.
                // 2. Same thing for
                //  notificationList = Notification.findAll( "select id from Notification order by ${queryString}", [:], [max:5, offset:0] /*, offset:offset]*/ )
                // However, not using paginate parameters does work
                //  notificationList = Notification.executeQuery( "from Notification ORDER BY ${queryString}" )
                // (I *think* -- could verify by logging sql) the problem is that Grails also inserts an "order by" which conflicts with our "order by" in the query).
                // BUT the returned object is an ArrayList and not PagedResultList as required here, so instead of using the above use our
                // own method that does return PagedResultList.

                queryString = "select id from Notification order by ${queryString}"

                notificationList = SBGSQLUtil.executeSelectWithIdGSQL( aDataSource, queryString,
                    com.trustedcs.sb.web.notifications.Notification.class, max, offset )
            }
            else {
                // Note that only max parameters does work. But [max:max, offset:offset] does NOT !!
                notificationList = Notification.executeQuery( "from Notification order by ${queryString}", [:], [max:max] )
            }           
        }
        
        else if( sort == "results" ){

            // sort == "results" is based on the views/notifications/_resultsCell.gsp logic, which is
            //
            // if( Notification.successful=TRUE && Notification.dataMap['fileName'] is NOT null &&
            //      Notification.type in (0, 1, 2, 3, 4, 5, 7, 8, 9, 10) ){
            //
            //      show "Report Available" [asc sortOrder=1, descsortOrder=1]
            // }
            // else {
            //  if( Notification.successful=TRUE ){ // and ( Notification.dataMap['fileName'] is null OR Notification.type in (6, 11) )
            //      show "Successful" (message=dispatcher.command.successful) [asc sortOrder=2, descsortOrder=0]
            //  }
            //  else {
            //      show "Failed" (message=dispatcher.command.failed) [asc sortOrder=0, descsortOrder=2]
            //  }
            //
            /*
             * Attempt 1: However, CANNOT just use this query
             *
            String queryString = """
                    ORDER BY CASE
                        WHEN (successful=TRUE AND ( dataMap['fileName'] is NOT null ) AND (type in (0,1,2,3,4,5,7,8,9,10,12)) ) THEN 1
                                """
            queryString = "${queryString} WHEN (successful=TRUE OR (dataMap['fileName'] is NULL) ) THEN ${sortOrder == "asc" ? "2" : "0" }"
            queryString = "${queryString} ELSE ${sortOrder == "asc" ? "0" : "2" } END"
            notificationList = Notification.executeQuery( "from Notification ${queryString}", [max:10] )

            as it *MISSES* the rows that don't have dataMap['fileName'] set, which bad. The SQL query created by Hibernate for sortOrder == "asc" is :

select notificati0_.id as id27_, notificati0_.version as version27_, notificati0_.transaction_id as transact3_27_,
notificati0_.time_stamp as time4_27_, notificati0_.aborted as aborted27_, notificati0_.successful as successful27_,
notificati0_.type as type27_, notificati0_.info as info27_
    from notification notificati0_, notification_data_map datamap1_, notification_data_map datamap2_
    where notificati0_.id=datamap1_.data_map and datamap1_.data_map_idx = 'fileName' and
          notificati0_.id=datamap2_.data_map and datamap2_.data_map_idx = 'fileName' order by case
            when notificati0_.successful=1 and (datamap1_.data_map_elt is not null) and (notificati0_.type in (0 , 1 , 2 , 3 , 4 , 5 , 7 , 8 , 9 , 10, 12)) then 1
            when notificati0_.successful=1 or datamap2_.data_map_elt is null then 2
            else 0 end

            Note that the check for ( dataMap['fileName'] is NULL ) is actually checking whether the *value* in the dataMap is not null
            (ie. datamap2_.data_map_elt is null), however, *ONLY* the rows with ( datamap2_.data_map_idx = 'fileName' ) (ie. ;'fileName' key)
            are ever considered by this query. Hence, can't use this query as it's missing rows that don't have 'fileName' key.

            */

            /* Attempt 2: this fails because Notification_data_map table is NOT mapped (there is not domain class corresponding to
             * it as there is no com.trustedcs.sb.web.notifications.Notification_Data_Map class) so get an error :
             *
             *   nested exception is org.hibernate.hql.ast.QuerySyntaxException: Notification_data_map is not mapped ...
             *
            String queryString = """
                select distinct(n) from Notification n, Notification_data_map datamap
                    where n.id=datamap.data_map
            order by case
            when n.successful=1 and (datamap.data_map_idx = 'fileName' and datamap.data_map_elt is not null) and (n.type in (0 , 1 , 2 , 3 , 4 , 5 , 7 , 8 , 9 , 10, 12)) then 1
                                 """
            queryString = "${queryString} WHEN (n.successful=TRUE) THEN ${sortOrder == "asc" ? "2" : "0" }"
            queryString = "${queryString} ELSE ${sortOrder == "asc" ? "0" : "2" } END"

            notificationList = Notification.executeQuery( "${queryString}", [max:10] )
            */

            /*
            // Attempt 3: So instead, just use a pure GSQL instead. However, this also fails as the query returns ids in the wrong order
            String queryString = """
                select distinct(n.id) from Notification n, Notification_data_map datamap
                    where n.id=datamap.data_map
            order by case
            when n.successful=1 and (datamap.data_map_idx = 'fileName' and datamap.data_map_elt is not null) and (n.type in (0 , 1 , 2 , 3 , 4 , 5 , 7 , 8 , 9 , 10, 12)) then 1
                                 """
            queryString = "${queryString} WHEN (n.successful=TRUE) THEN ${sortOrder == "asc" ? "2" : "0" }"
            queryString = "${queryString} ELSE ${sortOrder == "asc" ? "0" : "2" } END"
            */

            // Attempt 4:
            String queryString = """
            select id from Notification
            order by case
            when
              (id in
                ( select id from Notification n where ( successful=TRUE and
                        (
                          ( 1 = (select count(*) from Notification_data_map where data_map=n.id and data_map_idx = 'fileName' and data_map_elt is not null ) and
                            ( n.type in (0 , 1 , 2 , 3 , 4 , 5 , 7 , 8 , 9 , 10, 12 ) )
                          )
                        )
                                                      )
                 )
              ) then 1
            when
              (id in
                ( select id from Notification n where ( successful=TRUE and
                        (
                          ( 0 = (select count(*) from Notification_data_map where data_map=n.id and data_map_idx = 'fileName' and data_map_elt is not null ) or
                            ( n.type in (6, 11) )
                          )
                        )
                                                      )
                )
              ) then
                                """
            queryString = "${queryString} ${sortOrder == "asc" ? "2" : "0" }"
            queryString = "${queryString} else ${sortOrder == "asc" ? "0" : "2" } end"

            String maxPerPageForSQLCall = null, offsetForSQLCall = null
            if( usePaginationOrTenElementsMax ){
                maxPerPageForSQLCall = max
                offsetForSQLCall     = offset
            }
            else {
                queryString = "${queryString} limit ${max}"
            }

            notificationList = SBGSQLUtil.executeSelectWithIdGSQL( aDataSource, queryString,
                com.trustedcs.sb.web.notifications.Notification.class, maxPerPageForSQLCall, offsetForSQLCall )
        }

        return notificationList
    }

    /**
     * Delete multiple notifications at once
     */
    def deleteMulti = {
        clearFlash();
        m_log.info("params ${params}");

        // get the ids as longs
    	def ids = request.getParameterValues('notificationIds').collect { id ->
            id.toLong();
    	}
    	
        // delete each notification
        Notification notification;
    	m_log.info("notification ids ${ids}");
    	ids.each { id ->
            try {
                notification = Notification.get(id);
                dispatcherNotificationService.delete(notification);
            }
            catch ( DispatcherNotificationException dispatcherNotificationException ) {
                m_log.error("Unable to delete notification",dispatcherNotificationException);
                dispatcherNotificationException.notificationInstance.errors.allErrors.each { error ->
                    flash.error += messageSource.getMessage(error,null);
                }
            }	
    	}
    	redirect(action:'list');
    }
    
    /**
     * Delete the currently displayed notification
     */
    def delete = {
        clearFlash();
    	Notification notification = Notification.get(params.id);
    	try {
            dispatcherNotificationService.delete(notification);
    	}
    	catch ( DispatcherNotificationException dispatcherNotificationException ) {
            m_log.error("Unable to delete notification",dispatcherNotificationException);
            dispatcherNotificationException.notificationInstance.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
            redirect(action:'show',params:params);
            return;
    	}
    	redirect(action:'list');
    }
    
    /**
     * Show the notification for the specified id
     */
    def show = {
        Notification notif = Notification.get(params.id);
    	[notificationInstance:notif]    	
    }
	
    /**
     * ajax check to see if any new notifications have happened since the last
     * time that this page was accessed.
     */
    def hasNew = {
        // use the session utils to update the counts of notifications
        SessionAlertUtil.updateNotificationCount(session);
    }

    /**
     * Clear the flash of all messages
     */
    def clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }
}
