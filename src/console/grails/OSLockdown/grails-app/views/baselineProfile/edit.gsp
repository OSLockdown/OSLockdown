
<%@ page import="com.trustedcs.sb.metadata.baseline.BaselineProfile" %>
<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="contextSensitiveHelp" content="editing-a-base-profile"/>
  <meta name="layout" content="main" />
  <g:set var="entityName" value="${message(code: 'baselineProfile.label', default: 'BaselineProfile')}" />
  <title><g:message code="baselineProfile.edit.label" args="${[baselineProfileInstance.name]}" /></title>
  <g:render template="baselineProfileJavascript"/>
</head>
<body>
  <div id="per_page_container">    
    <div id="per_page_header" class="container">
      <div class="headerLeft">
        <h1><g:message code="baselineProfile.edit.label" args="${[baselineProfileInstance.name]}" /></h1>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:hasErrors bean="${baselineProfileInstance}">
          <div class="errors">
            <g:renderErrors bean="${baselineProfileInstance}" as="list" />
          </div>
        </g:hasErrors>
        <g:form method="post" >
          <g:hiddenField name="id" value="${baselineProfileInstance?.id}" />
          <g:hiddenField name="version" value="${baselineProfileInstance?.version}" />
          <div style="width:80%;" class="info centerDiv">
            <g:render template="config"/>
            <g:render template="baselineSection" collection="${baselineSections}" var="baselineSection"/>
            <div class="buttonsDiv">
              <span class="button"><g:actionSubmit class="save btninput" action="update" value="${message(code: 'default.button.update.label', default: 'Update')}" /></span>
              <span class="button"><g:actionSubmit class="delete btninput" action="delete" value="${message(code: 'default.button.delete.label', default: 'Delete')}" onclick="return confirm('${message(code: 'default.button.delete.confirm.message', default: 'Are you sure?')}');" /></span>
              <span class="button"><g:actionSubmit class="cancel btninput" action="show" value="${message(code: 'default.button.cancel.label', default: 'Cancel')}"/></span>
            </div>
          </div>
        </g:form>
      </div>
    </div>
  </div>
</body>
</html>
