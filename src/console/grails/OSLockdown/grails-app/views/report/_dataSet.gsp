<fieldset>
    <legend>Report</legend>
    <div class="pad1TopBtm">

      <!-- show noSelection portion if there are none OR 2 or more reports; don't show if there is exactly 1 report -->
      <g:if test="${!dataSetMap || dataSetMap.size() > 1}">
        <g:select class="paddedSelect" name="dataSet" from="${dataSetMap.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'[-Select a Report-]']" value="${params.dataSet}"/>
      </g:if>
      <g:else>
        <g:select class="paddedSelect" name="dataSet" from="${dataSetMap.descendingMap().entrySet()}" optionKey="key" optionValue="value" value="${params.dataSet}"/>
      </g:else>
   
    </div>
</fieldset>