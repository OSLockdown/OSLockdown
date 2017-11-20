<%@ page import="com.trustedcs.sb.web.pojo.Client" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="edit-client"/>
    </sbauth:isEnterprise>
    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="edit-client-su"/>
    </sbauth:isBulk>

    <title>Edit Client</title>
</head>
<body id="client">
  <div id="per_page_container">
    <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
    <div class="container" id="per_page_header" title="New Client">
      <div class="headerLeft">
        <h1>Edit Client > ${clientInstance}</h1>
      </div>
      <div class="headerRight">
        <g:link class="btn btn_blue" controller="client" action="show" id="${clientInstance?.id}" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:form action="update" method="post">
          <g:hiddenField name="id" value="${clientInstance.id}"/>
          <div class="info half centerDiv">
            
            <g:if test="${!clientInstance.dateDetached}">
              <div class="info_header" title="Edit ${clientInstance?.name}">
                <span class="required" title="* indicates required field">* indicates required field</span>                            
              </div>
            </g:if>
            
            <g:render template="config" />
            <div class="buttonsDiv">
              <input class="save btninput" type="submit" value="Update" title="Click to update Client" />
            </div>
          </div>
        </g:form>
      </div><!-- main_content -->
    </div><!-- yui-main -->
  </div><!-- per_page_container -->
</body>
</html>
