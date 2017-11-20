
<%@ page import="com.trustedcs.sb.metadata.baseline.BaselineProfile" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="contextSensitiveHelp" content="creating-new-baseline-profile"/>
    <meta name="layout" content="main" />
  <g:set var="entityName" value="${message(code: 'baselineProfile.label', default: 'BaselineProfile')}" />
  <title><g:message code="baselineProfile.create.label"/></title>
  <g:render template="baselineProfileJavascript"/>
</head>
<body>
  <div id="per_page_container">
    <!-- Login information and navigation -->    
    <div id="per_page_header" class="container">
      <div class="headerLeft">
        <h1><g:message code="baselineProfile.create.label"/></h1>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:hasErrors bean="${baselineProfileInstance}">
          <div class="errors">
            <g:renderErrors bean="${baselineProfileInstance}" as="list" />
          </div>
        </g:hasErrors>
        <g:form action="save" method="post" >
          <div style="width:80%;" class="info centerDiv">
            <g:render template="config"/>
            <g:render template="baselineSection" collection="${baselineSections}" var="baselineSection"/>
            <div class="buttonsDiv">
              <span class="button"><g:submitButton name="save" class="save btninput" value="${message(code: 'default.button.save.label', default: 'Save')}" /></span>
              <span class="button"><g:actionSubmit name="cancel" action="list" class="cancel btninput" value="${message(code: 'default.button.cancel.label', default: 'Cancel')}" /></span>
            </div>
          </div>
        </g:form>
      </div>
    </div>
  </div>
</body>
</html>
