<%@page contentType="text/xml"%>
 
<taconite-root xml:space="preserve">		
	
	<!-- Increment filter count -->
	<g:set var="currentFilterCount" value="${Integer.parseInt(params.filterCount) + 1 }" />
	
	<!-- Filter Types -->
	<g:if test="${params.type == 'clearText'}">
		<g:if test="${params.clearTextCount == '0'}">
			<taconite-set-attributes matchMode="plain" contextNodeID="clearTextFilterContainer" style="display:true;" />	
		</g:if>		
		<g:set var="clearTextCount" value="${Integer.parseInt(params.clearTextCount) + 1 }" />
		<taconite-append-as-children contextNodeID="clearTextFilterContainer">
			<div class="pad3top" id="div.filter.${currentFilterCount}" filter="tag">				
				<a class="btn" title="Click to remove keyword search criteria." href="javascript:removeFilter('clearText','${currentFilterCount}');">-</a>
                <g:textField name="module.clearText.id" size="40"/>								
            </div>
		</taconite-append-as-children>
		<taconite-set-attributes matchMode="plain" contextNodeID="clearTextCount" value="${clearTextCount}" />		
	</g:if>	
	<g:elseif test="${params.type == 'tag'}">
		<g:if test="${params.tagCount == '0'}">
			<taconite-set-attributes matchMode="plain" contextNodeID="tagFilterContainer" style="display:true;" />	
		</g:if>		
		<g:set var="tagCount" value="${Integer.parseInt(params.tagCount) + 1 }" />
		<taconite-append-as-children contextNodeID="tagFilterContainer">
			<div class="pad3top" id="div.filter.${currentFilterCount}" filter="tag">				
				<a class="btn" title="Click to remove category search criteria." href="javascript:removeFilter('tag','${currentFilterCount}');">-</a>
                <g:select name="module.tag.id" from="${tagList}" optionKey="id" />				
			</div>
		</taconite-append-as-children>
		<taconite-set-attributes matchMode="plain" contextNodeID="tagCount" value="${tagCount}" />		
	</g:elseif>	
	<g:elseif test="${params.type == 'cpe'}">
		<g:if test="${params.cpeCount == '0'}">
			<taconite-set-attributes matchMode="plain" contextNodeID="cpeFilterContainer" style="display:true;" />	
		</g:if>
		<g:set var="cpeCount" value="${Integer.parseInt(params.cpeCount) + 1 }" />			
		<taconite-append-as-children contextNodeID="cpeFilterContainer">
			<div class="pad3top" id="div.filter.${currentFilterCount}" filter="cpe">				
				<a class="btn" title="Click to remove platform search criteria." href="javascript:removeFilter('cpe','${currentFilterCount}');">-</a>
                <g:select name="module.cpe.id" from="${cpeList}" optionKey="id"/>
			</div>
		</taconite-append-as-children>
		<taconite-set-attributes matchMode="plain" contextNodeID="cpeCount" value="${cpeCount}" />
	</g:elseif>
	<g:elseif test="${params.type == 'compliancy'}">
		<g:if test="${params.compliancyCount == '0'}">
			<taconite-set-attributes matchMode="plain" contextNodeID="compliancyFilterContainer" style="display:true;" />	
		</g:if>		
		<g:set var="compliancyCount" value="${Integer.parseInt(params.compliancyCount) + 1 }" />
		<taconite-append-as-children contextNodeID="compliancyFilterContainer">
			<div class="pad3top" id="div.filter.${currentFilterCount}" filter="compliancy">				
				<a class="btn" title="Click to remove compliancy search criteria." href="javascript:removeFilter('compliancy','${currentFilterCount}');">-</a>
                <g:select name="module.compliancy.id" from="${compliancyList}" optionKey="id"/>
			</div>
		</taconite-append-as-children>
		<taconite-set-attributes matchMode="plain" contextNodeID="compliancyCount" value="${compliancyCount}" />
	</g:elseif>
	
	<!-- Set the hidden count to the latest value -->						
	<taconite-set-attributes matchMode="plain" contextNodeID="filterCount" value="${currentFilterCount}" />
		
</taconite-root>