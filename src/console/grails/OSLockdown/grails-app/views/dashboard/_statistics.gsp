<div class="info">
    <div class="info_header">

        <g:if test="${isBulk}">
          <g:set var="consoleType" value="Lock and Release"/>
        </g:if>
        <g:else> <!-- must be enterprise -->
          <g:set var="consoleType" value="Enterprise"/>
        </g:else>
        <h2>${consoleType} Statistics</h2>
    </div>
    <table class="zebra">                              
        <tbody>                              
            <tr class="stripe">
                <td style="width:50%">Total Client Count:</td>
                <td>${clientCount}</td>
            </tr>
            <tr class="stripe">
                <td>Unassociated Groups:</td>
                <td>${unassociatedGroupCount}</td>
            </tr>

            <tr class="stripe">
                <td>Unassociated Clients:</td>                                
                <td>${unassociatedClientCount}</td>
            </tr>
            <shiro:hasAnyRole in="['Administrator','User']">            
            <tr class="stripe">
                <td>Clients waiting to be approved:</td>
                <td><g:link controller="clientRegistrationRequest" action="list" title="Click to view the list of client registration requests">${clientsWaiting}</g:link></td>
            </tr>
            </shiro:hasAnyRole>
        </tbody>
    </table>                        
</div> <!-- info -->
