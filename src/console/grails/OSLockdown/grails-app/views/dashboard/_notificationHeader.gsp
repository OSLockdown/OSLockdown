<g:if test="${session.notificationCount>0}">
  <div id="header_notify" >
    <shiro:hasAnyRole in="['Administrator','User','Security Officer']">
	    <g:link controller="notifications" action="list" title="Click to view the list of notifications">
		    <g:if test="${session.notificationCount > 1}">
		        ${session.notificationCount} New Notifications Exist
		    </g:if>
		    <g:else>
		        ${session.notificationCount} New Notification Exists
		    </g:else>
	    </g:link>    
    </shiro:hasAnyRole>
  </div>
</g:if>
<g:else>
  <div id="header_notify" style="display:none">
  </div>
</g:else>
