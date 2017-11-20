<%@page contentType="text/xml"%>
<taconite-root xml:space="preserve">
    <taconite-delete contextNodeID="ajaxFlashErrorDiv"/>
    <taconite-replace-children contextNodeID="hostInfoContainer">
        <g:render template="/client/clientInfoDetails"/>
    </taconite-replace-children>

    <g:if test="${ajaxFlash.error}">
    <taconite-append-as-first-child contextNodeID="bd">
        <div id="ajaxFlashErrorDiv" class="ajaxFlashError">${ajaxFlash.error}</div>    
    </taconite-append-as-first-child>
    <taconite-execute-javascript>
      <script type="text/javascript">
          alert("An error occurred - Please consult the error bar at the top of the page.");
      </script>
    </taconite-execute-javascript>          
    </g:if>    
</taconite-root>
