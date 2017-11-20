<%@page contentType="text/xml"%>

<taconite-root xml:space="preserve">

  <g:set var="forensic" value="${0}"/>
  <g:set var="systemLoad" value="${0}"/>
  <g:if test="${moduleCount > 0 }">
    <g:set var="forensic" value="${estimatedForensicImportance / moduleCount}"/>
    <g:set var="systemLoad" value="${estimatedSystemLoad / moduleCount}"/>
  </g:if>

  <taconite-replace-children contextNodeID="estimatedForensicImportance">
    <label:importanceLevel type="number" value="${forensic}"/>
  </taconite-replace-children>

  <taconite-replace-children contextNodeID="estimatedSystemLoad">
    <label:importanceLevel type="number" value="${systemLoad}"/>
  </taconite-replace-children>

</taconite-root>