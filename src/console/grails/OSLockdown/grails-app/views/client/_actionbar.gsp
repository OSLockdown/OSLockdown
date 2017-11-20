<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<%@ page import="com.trustedcs.sb.util.AutoUpdateOptions" %>

<!-- ********************************************************** -->
<!-- ACTION BAR -->
<!-- ********************************************************** -->

<div id="actionbar">

  <!--
      For the action bar that applies to only a single Client,
      the g:form tag is in the template and does not need
      to surround any input types outside the template.  The
      Client id is passed in as part of the model by the
      controller.
  -->
  <g:form>
    <input type="hidden" name="id" value="${clientInstance?.id}" />
    <!--input type="hidden" name="group_id" value="${groupInstance?.id}" /-->
    <!-- How to handle both Clients and Groups with this template? -->

    <shiro:hasAnyRole in="['Administrator','User']">
      <div class="actions">
        <div class="action_title">Client</div>
        <ui>
          <li><g:actionSubmit class="action_bar_btn" title="Edit" value="Edit" action="edit" id="${clientInstance.id}"/></li>

          <g:if test="${isBulk}">

            <g:if test="${!clientInstance.dateDetached}">

              <!-- Can't have a g : link as it calls the action specified (of default if none) in addition to the one invoked by Ajax -->
              <!-- and that messes up the Ajax as it expects to work with one request (its own) and not two). Instead, just have an   -->
              <!-- anchor without href, and invoke the Ajax call from jQuery event handler. -->
              <li><a class="action_bar_btn detach" style="cursor:pointer;" title="Detach">Detach</a></li>
            </g:if>
          </g:if>
          <g:else>
            <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to delete this client?');" title="Delete" value="Delete" action="delete" id="${clientInstance.id}"/></li>
          </g:else>

        </ui>
      </div>
    </shiro:hasAnyRole>

    <g:if test="${isEnterprise || (isBulk && !clientInstance.dateDetached)}">

      <div class="actions">
        <div class="action_title">Actions</div>
        <ui>
          <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run a quick scan on this client?');" title="Quick Scan" value="Quick Scan" action="quickScan"/></li>
          <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run a scan on this client?');" title="Scan" value="Scan" action="scan"/></li>
          <shiro:hasAnyRole in="['Administrator','User']">
            <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run an apply on this client?');" value="Apply" action="apply"/></li>
            <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run an undo on this client?');" value="Undo" action="undo"/></li>
          </shiro:hasAnyRole>
          <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to run a baseline on this client?');" value="Baseline" action="baseline"/></li>
          <shiro:hasAnyRole in="['Administrator','User']">
            <ui>
              <li style="padding-top:0.4em;"><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to abort any actions currently running on the client?');" value="Abort" action="abort"/></li>
            </ui>
          </shiro:hasAnyRole>
        </ui>
      </div>

      <shiro:hasAnyRole in="['Administrator']">
        <div class="actions">
          <div class="action_title">Auto-Update</div>
           <ui>
            <div>
             <ui>
              <li><g:select style="margin-left:-1.8em;" name="autoupdateon" from="${AutoUpdateOptions.displayMap().entrySet()}" title="AutoUpdate Options" optionKey="key" optionValue="value" value="0"/></li>
              <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('An AutoUpdate request will be honored by the client despite any Core Hour or Load Threshold settings.  Are you sure you want to initiate an AutoUpdate on this client?');" value="Auto-Update" action="autoUpdate"/></li>
             </ui>
            </div>
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

    <div class="actions">
      <div class="action_title">Reports</div>
      <ui>
        <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to view the most recent assessment report for this client?');" title="View Latest Assessment Report" value="Assessment" action="showAssessmentReport"/></li>
        <li><g:actionSubmit class="action_bar_btn" onclick="return confirm('Are you sure you want to view the most recent baseline report for this client?');" title="View Latest Baseline Report" value="Baseline" action="showBaselineReport"/></li>
      </ui>
    </div>

  </g:form>

</div><!-- navbar -->
