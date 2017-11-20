<%@page defaultCodec="none" %>
<!--
<div>${thisMessage.getClass()}</div>
<div>${thisMessage}</div>
-->
<g:if test="${thisMessage.getClass().toString().contains('String')}"><g:each in="${thisMessage.split('<br/>')}"><li>${it}</it></g:each></g:if>
<g:else><g:each in="${thisMessage}"><li>${it}</li></g:each></g:else>
