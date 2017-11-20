<%@page contentType="text/xml"%>
 
<taconite-root xml:space="preserve">
	<g:if test="${session.registrationCount > 0}">
		<taconite-replace contextNodeID="header_register">
		  <g:render template="/dashboard/clientRegistrationHeader"/>
		</taconite-replace>		
	</g:if>	
</taconite-root>