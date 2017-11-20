<%@ page import="com.trustedcs.sb.web.pojo.Processor" %>
<%@ page import="com.trustedcs.sb.util.ClientType" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="edit-processor"/>
    </sbauth:isEnterprise>

    <title>Edit Processor</title>
</head>
<body id="processor">
  <div id="per_page_container">
    <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
    <div class="container" id="per_page_header" title="New Processor">
      <div class="headerLeft">
        <h1>Edit Processor > ${processorInstance.name}</h1>
      </div>
      <div class="headerRight">
        <g:link class="btn btn_blue" controller="processor" action="show" id="${processorInstance?.id}" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:form action="update" method="post">
          <g:hiddenField name="id" value="${processorInstance.id}"/>
          <g:hiddenField name="clientType" value="${processorInstance.clientType}"/>
          <div class="info half centerDiv">
            
            
            <g:render template="config" model="[processorInstance:processorInstance, editable:false]" />
            <div class="buttonsDiv">
              <input class="save btninput" type="submit" value="Update" title="Click to update Processor" />
            </div>
          </div>
        </g:form>
      </div><!-- main_content -->
    </div><!-- yui-main -->
  </div><!-- per_page_container -->
</body>
</html>
