<%@page contentType="text/xml"%>
 
<taconite-root xml:space="preserve">
  <g:set var="isAll" value="${params.filterId == 'all'}"/>
	<g:if test="${isAll}">
		<taconite-delete matchMode="selector" contextNodeSelector="div[filter]" />		
		<taconite-set-attributes matchMode="plain" contextNodeID="clearTextCount" value="0" />
		<taconite-set-attributes matchMode="plain" contextNodeID="tagCount" value="0" />
		<taconite-set-attributes matchMode="plain" contextNodeID="cpeCount" value="0" />
		<taconite-set-attributes matchMode="plain" contextNodeID="compliancyCount" value="0" />
		<taconite-set-attributes matchMode="plain" contextNodeID="filterCount" value="0" />
	</g:if>
	<g:else>	
		<taconite-delete contextNodeID="div.filter.${params.filterId}" />
		<g:set var="typeCount" value="${ Integer.parseInt(request.getParameter(params.type+'Count') ) }"/>					
		<taconite-set-attributes matchMode="plain" contextNodeID="${params.type + 'Count'}" value="${typeCount - 1}" />					
	</g:else>
</taconite-root>