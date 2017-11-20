<%@page contentType="text/xml"%>

<taconite-root xml:space="preserve">
  <taconite-delete contextNodeID="ajaxFlashErrorDiv"/>

  <taconite-replace-children contextNodeID="reportDiv${params.comparisonId}">
    <g:select class="paddedSelect" name="${'report'+params.comparisonId}" from="${reportMap.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'-Select a Report-']"/>
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
