<%@page contentType="text/xml"%>

<taconite-root xml:space="preserve">
  <taconite-delete contextNodeID="ajaxFlashErrorDiv"/>
  <taconite-delete contextNodeID="ajaxFlashWarningDiv"/>

  <taconite-replace-children contextNodeID="dataSetDiv">
    <g:render template="/report/dataSet"/>
  </taconite-replace-children>

  <g:if test="${ajaxFlash.warning}">
    <taconite-append-as-first-child contextNodeID="bd">
      <div id="ajaxFlashWarningDiv" class="ajaxFlashWarning">${ajaxFlash.warning}</div>
    </taconite-append-as-first-child>
  </g:if>

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
