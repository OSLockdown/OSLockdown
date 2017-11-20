<%@ page import="com.trustedcs.sb.util.SyslogAppenderLevel" %>
<%@ page import="com.trustedcs.sb.util.SyslogFacility" %>
<%@ page import="com.trustedcs.sb.util.ConsoleTaskPeriodicity" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Manage Upstream Notification Preferences</title>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="man-acct-prefs" />  
    <r:require modules="application"/>
</head>
<body id="administration">
  <div id="per_page_container">
    <div id="per_page_header" title="Manage Upstream Notification Preferences">
      <h1>Manage Upstream Notification Preferences</h1>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:hasErrors>
          <div class="errors">
            <g:renderErrors bean="${upstreamprefs}" as="list" />
          </div>
        </g:hasErrors>
        <g:form controller="rbac" action="updateUpstreamNotificationPreferences">
          <div class="threequarters centerDiv">
            <div class="table_border">
              <fieldset>
                <legend>Upstream Notification Preferences</legend>
                <table class="zebra info centerDiv">
                   <tbody>
                     <tr class="stripe half">
                       <td>Upstream notifications enabled</td>
                       <td><g:checkBox name= "syslogEnabled" value="${upstreamprefs.syslogEnabled}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Upstream log host</td>
                       <td><g:field name = "syslogHost" value="${upstreamprefs.syslogHost}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Upstream log port</td>
                       <td><g:field name = "syslogPort" type="number" min="1" max="65535" value="${upstreamprefs.syslogPort}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Syslog facility</td>
                       <td><g:select name="syslogFacility" from="${SyslogFacility.values()}" value="${upstreamprefs.syslogFacility}" optionKey="key" /></td>
                     </tr>
                   </tbody>
                </table>
              </fieldset>
            </div>
            <div class="table_border">
              <fieldset>
                <legend>Upstream Notification Triggers</legend>
                <table class="zebra ">
                   <tr> 
                       <th>Trigger</th>
                       <th>Notification Enabled</th>
                   </tr>
                   <tbody>
                     <g:each var="flag" status="i" in="${triggerFlags}">
                       <tr class="${(i % 2) == 0 ? 'row_odd' : 'row_even'}">
                          <td>${flag.upstreamNotificationType.getDisplayString()}</td>
                          <td><g:checkBox name="flagList_${flag.id}.enabled" checked="${flag.enabled}" value="${flag.upstreamNotificationType}"/></td>
                        </tr>
                    </g:each>
                   </tbody>
                </table>
              </fieldset>
            </div>
            <div class="table_border">
              <fieldset>
                <legend>Upstream Notification Periodic Actions</legend>
                <table class="zebra ">
                   <tr> 
                       <th>Action</th>
                       <th>Notification Enabled</th>
                       <th>Periodicity</th>
                   </tr>
                   <tbody>
                     <g:each var="flag" status="i" in="${periodicFlags}">
                       <tr class="${(i % 2) == 0 ? 'row_odd' : 'row_even'}">
                          <td>${flag.upstreamNotificationType.getDisplayString()}</td>
                          <td><g:checkBox name="flagList_${flag.id}.enabled" checked="${flag.enabled}" value="${flag.upstreamNotificationType}"/></td>
                          <td><g:select name="flagList_${flag.id}.periodicity" from="${ConsoleTaskPeriodicity.listTimingOptions()}" value="${flag.periodicity}" optionKey="key" /></td>
                        </tr>
                    </g:each>
                   </tbody>
                </table>
              </fieldset>
            </div>
            <div class="pad1TopBtm" style="text-align:center;">
                <g:submitButton name="exportButton" value="Update Upstream Notification Preferences" class="btninput" title="Click to update the upstream notification preferences"/>
            </div>
          </g:form>
        </div>
      </div> <!-- End of main_content -->
    </div> <!-- End of yui-main -->
  </div> <!-- End of per_page_container -->
</body>
</html>
