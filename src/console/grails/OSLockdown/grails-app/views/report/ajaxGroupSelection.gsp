<%@page contentType="text/xml"%>

<taconite-root xml:space="preserve">   
  <taconite-replace contextNodeID="reportSelectList">
    <g:select class="paddedSelect" id="reportSelectList" name="report" from="${reportMap.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'[-Choose a Report-]']"/>
  </taconite-replace>
</taconite-root>