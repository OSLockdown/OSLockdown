
<%@ page import="com.trustedcs.sb.web.notifications.NotificationTypeEnum" %>
<%@ page import="com.trustedcs.sb.reports.util.ReportType" %>

<g:set var="sourceId"   value="${notif.dataMap.sourceId}"/>
<g:set var="reportName" value="${notif.dataMap.fileName}"/>
<g:set var="successful" value="${notif.successful}"/>

<g:if test="${ successful && reportName &&
               (notif.type == NotificationTypeEnum.SCAN.ordinal() ||
                notif.type == NotificationTypeEnum.QUICK_SCAN.ordinal() ||
                notif.type == NotificationTypeEnum.SCHEDULED_SCAN.ordinal() ||
                notif.type == NotificationTypeEnum.SCHEDULED_QUICK_SCAN.ordinal() ) }">
  <td><g:link controller="report" action="${ReportType.ASSESSMENT.viewLocation}" params="[clientId:sourceId,dataSet:reportName]" title="Click to view the report">Report Available</g:link></td>
</g:if>
<g:elseif test="${ successful && reportName &&
                   (notif.type == NotificationTypeEnum.BASELINE.ordinal() ||
                    notif.type == NotificationTypeEnum.SCHEDULED_BASELINE.ordinal() ) }">
  <td><g:link controller="report" action="${ReportType.BASELINE.viewLocation}" params="[clientId:sourceId,dataSet:reportName]" title="Click to view the report">Report Available</g:link></td>
</g:elseif>
<g:elseif test="${ successful && reportName &&
                    (notif.type == NotificationTypeEnum.APPLY.ordinal() ||
                     notif.type == NotificationTypeEnum.SCHEDULED_APPLY.ordinal() ) }">
  <td><g:link controller="report" action="${ReportType.APPLY.viewLocation}" params="[clientId:sourceId,dataSet:reportName]" title="Click to view the report">Report Available</g:link></td>
</g:elseif>
<g:elseif test="${ successful && reportName && notif.type == NotificationTypeEnum.UNDO.ordinal() }">
  <td><g:link controller="report" action="${ReportType.UNDO.viewLocation}" params="[clientId:sourceId,dataSet:reportName]" title="Click to view the report">Report Available</g:link></td>
</g:elseif>
<g:elseif test="${ successful && reportName && notif.type == NotificationTypeEnum.GROUP_ASSESSMENT.ordinal() }">
  <td><g:link controller="report" action="${ReportType.GROUP_ASSESSMENT.viewLocation}" params="[group:sourceId,reportSource:'existingReportOnDisk',report:reportName]" title="Click to view the report">Report Available</g:link></td>
</g:elseif>
<g:else>
  <g:if test="${successful}">
    <td><g:message code="dispatcher.command.successful"/></td>
  </g:if>
  <g:else>
    <td class="sbRed"><g:message code="dispatcher.command.failed"/></td>
  </g:else>
</g:else>