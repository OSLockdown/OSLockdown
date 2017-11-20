<div style="width:60%;" class="info centerDiv">
  <div class="info_header">
    <h2>${fragmentType}</h2>
  </div>
  <div style="padding:0.3em;">
    <table>
      <g:if test="${fragmentCollection}">
        <g:each in="${fragmentCollection.entrySet()}" status="i" var="fragment">
          <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
            <td style="width:45%;" >${fragment.key}:</td>

            <g:if test="${fragment.value == 'successful' }">
              <td>${fragment.value}</td>
            </g:if>
            <g:else>
              <td style="color:#ff2b2b;">${fragment.value}</td>
            </g:else>
          
          </tr>
        </g:each>
      </g:if>
      <g:else>
        <tr class="row_even">
          <td colspan="2" style="text-align:center;">No items found</td>
        </tr>
      </g:else>
    </table>
  </div>
</div>