<%@ page import="com.trustedcs.sb.web.notifications.NotificationTypeEnum" %>
<table>
    <thead>
       <tr>             
           <g:if test="${!isDashboard}">
            <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click to Select All" /></th>
           </g:if>                              
           <g:sortableColumn property="timeStamp" title="Received" />
           <g:sortableColumn property="source" title="Source" />
           <g:sortableColumn property="type" title="Type" />
           <g:sortableColumn property="results" title="Results" />
           <g:sortableColumn property="info" title="Info" />
       </tr>
    </thead>
    <tbody>
        <g:if test="${notificationList}">
            <g:each in="${notificationList}" status="i" var="notif">
                <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                    <g:if test="${!isDashboard}">
                      <td><g:checkBox name="notificationIds" value="${notif.id}" checked="${false}" /></td>
                    </g:if>                                               
                    <td style="text-align:left;">                    
                        <g:link controller="notifications" action="show" id="${notif.id}"><dateFormat:printDate date="${notif.timeStamp}"/></g:link>
                    </td>
                    <td>${notif.sourceAsString()}</td>
                    <td>${notif.typeAsString()}</td>                    
                    <g:render template="/notifications/resultsCell" model="[notif:notif]"/>
                    <td>${notif.info}</td>                                                                                  
                </tr>   
            </g:each>
        </g:if>
        <g:else>
            <tr class="row_even">
                <g:if test="${isDashboard}">
                <td colspan="5" style="text-align:center;">No notifications since last login.</td>                          
                </g:if>                    
                <g:else>
                <td colspan="6" style="text-align:center;">No notifications currently exist.</td>                        
                </g:else>                                                                     
            </tr>
         </g:else>
    </tbody>
</table>
