<table>
  <tbody>
    <tr class="prop">
      <td valign="top" class="propName" title="Client Version"><label for="Client Version">Client Version:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'clientVersion')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Nodename"><label for="Nodename">Nodename:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'nodeName')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Distribution"><label for="Distribution">Distribution:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'distribution')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Kernel"><label for="Kernel">Kernel:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'kernel')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Uptime"><label for="Uptime">Uptime:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'uptime')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Architecture"><label for="Architecture">Architecture:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'architecture')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Load Average"><label for="Load Average">Load Average:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'loadAverage')}</td>
    </tr>
    <tr class="prop">
      <td valign="top" class="name" title="Memory"><label for="Memory">Memory:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'memory')}</td>
    </tr>  			
    <tr class="prop">
      <td valign="top" class="name" title="Core Hours"><label for="Core Hours">Core Hours:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'corehours')}</td>
    </tr>  			
    <tr class="prop">
      <td valign="top" class="name" title="Max Load"><label for="Max Load">Load Threshold:</label></td>
      <td valign="top" class="value">${fieldValue(bean:clientInfo, field:'maxload')}</td>
    </tr>  			
  </tbody>
</table>
