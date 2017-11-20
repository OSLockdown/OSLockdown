<%@page contentType="text/xml"%>
 
<taconite-root xml:space="preserve">
    <!-- check to see if the module has become selected -->    
	<g:if test="${dependencies.size() > 0}">
		<g:each in="${dependencies}">			
			<taconite-execute-javascript>
				<script type="text/javascript">
					$("input[id='module.selected.${it.key}']").attr('checked', ${it.value});
				</script>	
			</taconite-execute-javascript>								
		</g:each>
		<taconite-execute-javascript>
			<script type="text/javascript">
				alert("${alertString}");
			</script>	
		</taconite-execute-javascript>		
	</g:if>
</taconite-root>
