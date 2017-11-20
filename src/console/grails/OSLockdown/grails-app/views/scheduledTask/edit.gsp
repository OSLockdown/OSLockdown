
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="schedule-task" />
    <title>Edit Scheduled Task</title>
  <g:render template="taskJavascript"/>
</head>
<body id="scheduler">
  <div id="per_page_container">
    <div class="container" id="per_page_header" title="listTasks">
      <div class="headerLeft">
        <h1>Edit Scheduled Task</h1>
      </div>
      <div class="headerRight">
        <g:link class="btn btn_blue" controller="scheduledTask" action="list" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <div class="info half centerDiv">
          <div class="info_header" title="Scheduled Task">Scheduled Task</div>
          <g:form controller="scheduledTask" action="update" method="post">
            <g:hiddenField name="id" value="${task?.id }" />
            <g:render template="config"/>
            <div style="padding-bottom:0.5em;text-align:center;">
              <input type="submit" class="btninput" value="Update" title="Click to Update" />
            </div>
          </g:form>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
