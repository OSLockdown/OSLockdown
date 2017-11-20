<div style="width:80%;" class="centerDiv tableBorder">                                                     
  <table>
    <thead>
    <th style="text-align:center;" colspan="2">Notification Exceptions</th>
    </thead>
    <g:if test="${notificationInstance.exceptions}">
      <g:each in="${notificationInstance.exceptions}" status="i" var="exception">
        <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
          <td class="propName" style="width:10%;"><label for="Level">${exception.level}</label>:</td>
          <td>${exception.message}</td>
        </tr>
      </g:each>
    </g:if>
    <g:else>
      <tr class="row_even">
        <td style="text-align:center;" colspan="2">None</td>
      </tr>
    </g:else>
  </table>
</div>