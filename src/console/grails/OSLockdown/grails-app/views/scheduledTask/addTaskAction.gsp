<%@page contentType="text/xml"%>

<taconite-root xml:space="preserve">		

  <!-- Increment filter count -->
  <g:set var="currentActionCount" value="${Integer.parseInt(params.actionCount) + 1 }" />

  <taconite-append-as-children contextNodeID="actionContainer">
    <div class="pad3top" style="padding-left:1em;" id="div.action.${currentActionCount}">
      <a class="btn" title="Click to remove action." href="javascript:removeAction('${currentActionCount}');">-</a>
      <g:select style="width:9em;clear: right;" name="taskAction" from="${taskActions.entrySet()}" optionKey="key" optionValue="value" />
    </div>
  </taconite-append-as-children>

  <!-- Set the hidden count to the latest value -->
  <taconite-set-attributes matchMode="plain" contextNodeID="actionCount" value="${currentActionCount}" />

</taconite-root>