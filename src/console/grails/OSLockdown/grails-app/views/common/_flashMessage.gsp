<!-- Template for displaying flash messages to the user -->

<!-- Due to the fact that webflow (profileBuilder) in grails condenses 
     all scopes down to a single general scope we must check to see if  
     the messages, warnings and errors are in the generic scope as
     well as in the flash specific scope.  -->
     
<g:if test="${flash.message}">    
    <div id="flashMessageDiv" class="flashMessage"><g:render template="/common/flashElement" model="[thisMessage:flash.message, thisType:flash.message.getClass()]"/></div>
</g:if>

<g:if test="${message}">    
    <div id="flashMessageDiv" class="flashMessage"><g:render template="/common/flashElement" model="[thisMessage:message, thisType:flash.message.getClass()]"/></div>
</g:if>	

<g:if test="${flash.warning}">
    <div id="flashWarningDiv" class="flashWarning"><g:render template="/common/flashElement" model="[thisMessage:flash.warning, thisType:flash.message.getClass()]"/></div>
</g:if>

<g:if test="${warning}">
    <div id="flashWarningDiv" class="flashWarning"><g:render template="/common/flashElement" model="[thisMessage:warning, thisType:flash.message.getClass()]"/></div>
</g:if>	

<g:if test="${flash.error}">
    <div id="flashErrorDiv" class="flashError"><g:render template="/common/flashElement" model="[thisMessage:flash.error, thisType:flash.message.getClass()]"/></div>
</g:if>

<g:if test="${error}">
    <div id="flashErrorDiv" class="flashError"><g:render template="/common/flashElement" model="[thisMessage:error, thisType:flash.message.getClass()]"/></div>
</g:if>
