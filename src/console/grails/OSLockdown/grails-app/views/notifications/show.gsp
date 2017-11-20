
<%@ page import="com.trustedcs.sb.web.notifications.NotificationTypeEnum" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="viewing-notifs" />
    <title>Notification Information</title>    
  </head>
  <body id="notifications">
    <div id="per_page_container">
      <g:form action="delete" method="post">
        <div class="container" id="per_page_header" title="Notification Information">
          <div class="headerLeft">
            <h1>Notification Information</h1>
          </div>
          <div class="headerRight">
            <g:link controller="notifications" action="list" title="Click to go back to listings" class="btn btn_blue">&laquo; Back</g:link>            
          </div>
        </div>
        <div id="yui-main">
          <g:hiddenField name="id" value="${notificationInstance.id}"/>
          <div id="main_content" class="subpage">
            <div style="width:80%;" class="info centerDiv">
              <div class="info_body">
                <div style="width:80%;" class="tableBorder centerDiv">
                  <table>
                    <thead>
                    <th style="text-align:center;" colspan="2">Notification Details</th>
                    </thead>
                    <tr class="row_even">
                      <td class="propName" style="width:50%;"><label for="Received">Received</label>:</td>
                      <td><dateFormat:printDate date="${notificationInstance.timeStamp}"/></td>
                    </tr>
                    <tr class="row_odd">
                      <td class="propName" ><label for="Type">Type</label>:</td>
                      <td>${notificationInstance.typeAsString()}</td>
                    </tr>
                    <tr class="row_even">
                      <td class="propName" ><label for="Type">Source</label>:</td>
                      <td>${notificationInstance.sourceAsString()}</td>
                    </tr>
                    <tr class="row_odd">
                      <td class="propName" ><label for="Info">Info</label>:</td>
                      <td>${notificationInstance.info}</td>
                    </tr>
                    <tr class="row_even">
                      <td class="propName" ><label for="Results">Results</label>:</td>
                    <g:render template="/notifications/resultsCell" model="[notif:notificationInstance]"/>
                    </tr>
                    <g:set var="notifDataMap" value="${notificationInstance.dataMap}"/>
                    <g:if test="${ (notificationInstance.type == NotificationTypeEnum.SCAN.ordinal() ||
notificationInstance.type == NotificationTypeEnum.QUICK_SCAN.ordinal() ||
notificationInstance.type == NotificationTypeEnum.SCHEDULED_SCAN.ordinal() || 
notificationInstance.type == NotificationTypeEnum.SCHEDULED_QUICK_SCAN.ordinal() ) && notificationInstance.successful}">								   
                      <g:render template="/notifications/scanDetails" model="[dataMap:notifDataMap]"/>
                    </g:if>
                    <g:elseif test="${ (notificationInstance.type == NotificationTypeEnum.APPLY.ordinal() ||
notificationInstance.type == NotificationTypeEnum.SCHEDULED_APPLY.ordinal()  ) && notificationInstance.successful}">								   
                      <g:render template="/notifications/applyDetails" model="[dataMap:notifDataMap]"/>
                    </g:elseif>
                    <g:elseif test="${ notificationInstance.type == NotificationTypeEnum.UNDO.ordinal() && notificationInstance.successful}">								   
                      <g:render template="/notifications/undoDetails" model="[dataMap:notifDataMap]"/>
                    </g:elseif>
                    <g:elseif test="${notificationInstance.type == NotificationTypeEnum.SCHEDULED_TASK_COMPLETE.ordinal()}">
                      <g:render template="/notifications/taskCompletedDetails" model="[dataMap:notifDataMap]"/>
                    </g:elseif>
                  </table>
                </div>
                <br/>
                <g:render template="/notifications/notificationExceptions"/>
              </div>
              <div class="buttonsDiv">
                <input class="btninput" type="submit" title="Click to Delete" value="Delete" />
              </div>
            </div>
          </div>
      </g:form>
    </div>
  </div>
</body>
</html>
