
<%@ page import="com.trustedcs.sb.metadata.baseline.BaselineProfile" %>
<html>
  <head>
  <nav:resources override="true"/>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="contextSensitiveHelp" content="editing-a-base-profile"/>
  <meta name="layout" content="main" />
  <g:set var="entityName" value="${message(code: 'baselineProfile.label', default: 'BaselineProfile')}" />
  <title><g:message code="baselineProfile.show.label" args="${[baselineProfileInstance.name]}" /></title>
</head>
<body>
  <div id="per_page_container">
    <div id="per_page_header" class="container">
      <div class="headerLeft">
        <h1><g:message code="baselineProfile.show.label" args="${[baselineProfileInstance.name]}" /></h1>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <div style="width:80%;" class="info centerDiv">
          <g:set var="immutable" value="${true}"/>
          <g:render template="display"/>
          <g:each in="${baselineSections}" var="baselineSection">
            <g:render template="baselineSection" model="${[baselineSection:baselineSection,immutable:true]}"/>
          </g:each>
          <g:if test="${!baselineProfileInstance.writeProtected}">
            <div class="buttonsDiv">
              <g:form>
                <g:hiddenField name="id" value="${baselineProfileInstance?.id}" />
                <span class="button"><g:actionSubmit class="edit btninput" action="edit" value="${message(code: 'default.button.edit.label', default: 'Edit')}" /></span>
                <span class="button"><g:actionSubmit class="delete btninput" action="delete" value="${message(code: 'default.button.delete.label', default: 'Delete')}" onclick="return confirm('${message(code: 'default.button.delete.confirm.message', default: 'Are you sure?')}');" /></span>
              </g:form>
            </div>
          </g:if>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
