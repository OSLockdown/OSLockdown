<g:if test="${session.registrationCount}">
  <div id="header_register">
    <shiro:hasAnyRole in="['Administrator','User']">
      <g:link controller="clientRegistrationRequest" action="list" title="Click to view the list of client registration requests">
        <g:if test="${session.registrationCount > 1}">
          ${session.registrationCount} New Client Requests Exist
        </g:if>
        <g:else>
          ${session.registrationCount} New Client Request Exists
        </g:else>
      </g:link>
    </shiro:hasAnyRole>
  </div>
</g:if>
<g:else>
  <div id="header_register" style="display:none">
  </div>
</g:else>
