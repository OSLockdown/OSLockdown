<table>                             
  <tbody>
  <g:if test="${statusMap}">
    <g:each in="${statusMap.entrySet()}" var="entry">
      <tr>
        <td style="width:50%;" valign="top" class="name"><label>${entry.key}:</label></td>
        <td valign="top" class="value">${entry.value}</td>
      </tr>
    </g:each>
  </g:if>
  <g:else>
    <tr>
      <td style="width:50%;" valign="top" class="name"><label>Dispatcher Status:</label></td>
      <td valign="top" class="value">Unknown</td>    
    </tr>
  </g:else>
</tbody>
</table>