<%@page contentType="text/xml"%>
 
<taconite-root xml:space="preserve">
	<g:if test="${session.notificationCount > 0}">
		<taconite-replace contextNodeID="header_notify">
		  <g:render template="/dashboard/notificationHeader"/>
		</taconite-replace>		
	</g:if>	
</taconite-root>