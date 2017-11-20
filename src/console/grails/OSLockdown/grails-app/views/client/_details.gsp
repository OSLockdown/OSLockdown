<div class="info">
  <div class="info_header">

    <g:set var="detailsMessage" value="Details" />

    <!-- Can only be true for Bulk -->
    <g:if test="${isBulk && clientInstance && clientInstance.dateDetached}">
      <g:set var="detailsMessage" value="Details at Detachment" />
    </g:if>

    <h2>${detailsMessage}</h2>
  </div>
  <div id="statusDiv" class="info_body">
    <table>

      <!-- Can only be true for Bulk -->
      <g:if test="${isBulk && clientInstance && clientInstance.dateDetached}">

        <tr>
          <td id="hostInfoContainer">
            <g:render template="/client/clientInfoDetails"/>
          </td>
        </tr>

      </g:if>
      <g:else>

        <tr>
          <td id="hostInfoContainer" style="width:50%;border-right:1px solid black;">
            <g:render template="/client/clientInfoDetails"/>
          </td>
          <td id="dispatcherStatusContainter" style="width:50%;">
            <g:render template="/client/clientStatus"/>
          </td>
        </tr>

        <tr>
          <td style="text-align:center;"><button onClick="javascript:updateInfo();" class="btninput" title="Click to Update Details">Refresh Details</button></td>
          <td style="text-align:center;"><button onClick="javascript:updateStatus();" class="btninput">Refresh Dispatcher Status</button></td>
        </tr>
        
      </g:else>
      
    </table>    
  </div>
</div>
