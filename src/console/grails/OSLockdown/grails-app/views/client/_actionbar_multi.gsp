<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<%@ page import="com.trustedcs.sb.util.AutoUpdateOptions" %>

<!-- ********************************************************** -->
<!-- ACTION BAR FOR MULTIPLE SELECTED CLIENTS -->
<!-- ********************************************************** -->

<div id="actionbar">

  <!--
            		For the action bar that applies to multiple Clients,
            		the g:form tag is in the main page (not the template)
            		since checkboxes from the list must be inside the form.

            		TODO: how to handle both a client and group?
            	-->            

  <shiro:hasAnyRole in="['Administrator','User']">

    <g:if test="${isBulk}">

      <g:if test="${atLeastOneUndetachedClient}">
        <div class="actions">

          <div class="action_title">Client</div>
          <ui>

              <!-- Can't have a g : link as it calls the action specified (of default if none) in addition to the one invoked by Ajax -->
              <!-- and that messes up the Ajax as it expects to work with one request (its own) and not two). Instead, just have an   -->
              <!-- anchor without href, and invoke the Ajax call from jQuery event handler. -->
              <li><a class="action_bar_btn detachMulti" style="cursor:pointer;" title="Detach">Detach</a></li>
          </ui>
        </div>
      </g:if>
      
    </g:if>
    <g:else> <!-- Enterprise -->
        <div class="actions">

          <div class="action_title">Client</div>
          <ui>
            <li><g:actionSubmit class="action_bar_btninput" id="deleteMulti" title="Delete"  value="Delete" action="deleteMulti"/></li>
          </ui>
        </div>
    </g:else>
    
  </shiro:hasAnyRole>

  <g:if test="${isEnterprise || (isBulk && atLeastOneUndetachedClient)}">

    <div class="actions">
      <div class="action_title">Actions</div>
      <ui>
        <li><g:actionSubmit class="action_bar_btninput" id="quickScanMulti" title="Scan" value="Quick Scan" action="quickScanMulti"/></li>
        <li><g:actionSubmit class="action_bar_btninput" id="scanMulti" title="Scan" value="Scan" action="scanMulti"/></li>
        <shiro:hasAnyRole in="['Administrator','User']">
          <li><g:actionSubmit class="action_bar_btninput" id="applyMulti" title="Apply" value="Apply" action="applyMulti"/></li>
          <li><g:actionSubmit class="action_bar_btninput" id="undoMulti" title="Undo" value="Undo" action="undoMulti"/></li>
        </shiro:hasAnyRole>
        <li><g:actionSubmit class="action_bar_btninput" id="baselineMulti" title="Baseline" value="Baseline" action="baselineMulti"/></li>
      </ui>
      <shiro:hasAnyRole in="['Administrator','User']">
        <ui>
          <li style="padding-top:0.4em;"><g:actionSubmit class="action_bar_btninput" id="abortMulti" title="Abort" value="Abort" action="abortMulti"/></li>
        </ui>
      </shiro:hasAnyRole>
    </div>

    <shiro:hasAnyRole in="['Administrator']">
      <div class="actions">
        <div class="action_title">Auto-Update</div>
          <ui>
            <li><g:select style="margin-left:-1.8em;" name="autoupdateon" from="${AutoUpdateOptions.displayMap().entrySet()}" title="AutoUpdate Options" optionKey="key" optionValue="value" value="0"/></li>
            <li><g:actionSubmit class="action_bar_btninput" id="autoUpdateMulti" title="AutoUpdate" value="Auto-Update" action="autoUpdateMulti"/></li>
          </ui>
      </div>
    </shiro:hasAnyRole>

    <div class="actions">
      <div class="action_title">Logging Level</div>
      <ui>
        <li><g:select name="loggingLevel" from="${LoggingLevel.displayMap().entrySet()}" title="Logging Level" optionKey="key" optionValue="value" value="${params.loggingLevel ? params.loggingLevel : 5}"/></li>
      </ui>
    </div>
    
  </g:if>

</div><!-- end actionbar -->
