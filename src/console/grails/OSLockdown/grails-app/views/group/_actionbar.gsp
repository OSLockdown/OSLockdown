<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<%@ page import="com.trustedcs.sb.util.AutoUpdateOptions" %>

<!-- ********************************************************** -->
<!-- ACTION BAR -->
<!-- ********************************************************** -->

<div id="actionbar">

  <!--
      For the action bar that applies to only a single group,
      the g:form tag is in the template and does not need
      to surround any input types outside the template.  The
      Group id is passed in as part of the model by the
      controller.
  -->
  <g:form>
    <input type="hidden" name="id" value="${groupInstance?.id}" />
    <!--input type="hidden" name="group_id" value="${groupInstance?.id}" /-->
    <!-- How to handle both Clients and Groups with this template? -->

    <shiro:hasAnyRole in="['Administrator','User']">
      <div class="actions">
        <div class="action_title">Group</div>
        <ui>
          <li><g:actionSubmit class="action_bar_btn" title="Edit" value="Edit" action="edit" id="${groupInstance.id}"/></li>
          <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to delete this group?');" title="Delete" value="Delete" action="delete" id="${groupInstance.id}"/></li>

          <!-- show Detach Clients only if group has at least one Client -->
          <g:if test="${isBulk && groupInstance?.clients}">

            <!-- Can't have a g : link as it calls the action specified (of default if none) in addition to the one invoked by Ajax -->
            <!-- and that messes up the Ajax as it expects to work with one request (its own) and not two). Instead, just have an   -->
            <!-- anchor without href, and invoke the Ajax call from jQuery event handler. -->
            <li style="padding-top:0.4em;"><a class="action_bar_btn detach" style="cursor:pointer;font-size:87%;" title="Detach All Group's Clients">Detach Clients</a></li>
          </g:if>

        </ui>
      </div>
    </shiro:hasAnyRole>


    <div class="actions">
      <div class="action_title">Actions</div>
      <ui>
        <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run a quick scan on the clients in this group?');" title="Quick Scan" value="Quick Scan" action="quickScan"/></li>
        <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run a scan on the clients in this group?');" title="Scan" value="Scan" action="scan"/></li>
        <shiro:hasAnyRole in="['Administrator','User']">
          <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run an apply on the clients in this group?');" value="Apply" action="apply"/></li>
          <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run an undo on the clients in this group?');" value="Undo" action="undo"/></li>
        </shiro:hasAnyRole>
        <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run a baseline on the clients in this group?');" value="Baseline" action="baseline"/></li>
        <shiro:hasAnyRole in="['Administrator','User']">          
          <ui>
            <li style="padding-top:0.4em;"><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to abort any actions currently running on the clients in the group?');" value="Abort" action="abort"/></li>
          </ui>
        </shiro:hasAnyRole>
      </ui>
    </div>
        
        
    <shiro:hasAnyRole in="['Administrator']">          
      <div class="actions">
        <div class="action_title">Auto-Update</div>
          <ui>
            <li><g:select style="margin-left:-1.8em;" name="autoupdateon" from="${AutoUpdateOptions.displayMap().entrySet()}" title="AutoUpdate Options" optionKey="key" optionValue="value" value="0"/></li>
            <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('An AutoUpdate request will be honored by the client(s) in this group despite any Core Hour or Load Threshold settings.  Are you sure you want initiate an AutoUpdate on the clients in the group?');" value="Auto-Update" action="autoUpdate"/></li>
          </ui>
        </ui>
      </div>
    </shiro:hasAnyRole>

    <div class="actions">
      <div class="action_title">Logging Level</div>
      <ui>
        <li><g:select name="loggingLevel" from="${LoggingLevel.displayMap().entrySet()}" title="Logging Level" optionKey="key" optionValue="value" value="${params.loggingLevel ? params.loggingLevel : 5}"/></li>
      </ui>
    </div>

  </g:form>

</div><!-- navbar -->
