<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="manage-users" />  
    <title>List Users</title>
    <g:render template="rbacJavascript"/>
  </head>
  <body id="administration">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="List Users">
        <div class="headerLeft">
          <h1>
            <g:if test="${params.id}">
               Edit ${userRoleRel?.user?.username}
            </g:if>
            <g:else>
               Create User
            </g:else>
          </h1>
        </div>
        <div class="headerRight">
          <g:link class="btn btn_blue" controller="rbac" action="list" event="cancel">Cancel</g:link>
        </div>
      </div>
      <div id="yui-main">
        <g:form controller="rbac" action="update" method="post">
          <g:hiddenField name="id" value="${params.id}" />
          <div id="main_content" class="subpage">
            <div class="info half centerDiv">
              <div class="info_body">
                <g:render template="config"/>
                <div style="padding-top:0.5em;text-align:center;">
                  <input type="submit" value="Update" class="btninput" title="Click to Update" />
                </div>
              </div>
              <div id="showHide" style="cursor:pointer;text-align:center;padding-bottom:0.5em;" title="Display Role Actions Table">
                <h2>Display Actions Table &#x25bc;</h2>
              </div>
            </div>
            <g:render template="/rbac/allowedActions"/>
          </div>
        </g:form>
      </div>
    </div>
  </body>
</html>
