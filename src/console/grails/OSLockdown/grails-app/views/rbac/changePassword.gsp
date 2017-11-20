<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="change-password" />
    <title>Change Password</title>
  </head>
  <body id="administration">
    <div id="per_page_container">
      <g:form controller="rbac" action="updatePassword" method="post">
        <div class="container" id="per_page_header" title="List Users">
          <div class="headerLeft">
            <h1>Change Password</h1>
          </div>
          <div class="headerRight">
            <g:if test="${flash.forcePasswordChange}">
              <g:link class="btn btn_blue" controller="dashboard" action="index">Cancel</g:link>
            </g:if>
            <g:else>
              <input type=button class="btninput btninput_blue" value="Cancel" onClick="history.go(-1)">
            </g:else>
          </div>
        </div>
        <div id="yui-main">
          <g:hiddenField name="id" value="${params.id}" />
          <div id="main_content" class="subpage">
            <div class="info half centerDiv">
              <div class="info_body">
                <table>
                  <tbody>
                    <tr>
                      <td>Current Password:</td>
                      <td><input type="password" name="currentPassword" /></td>
                    </tr>
                    <tr>
                      <td>New Password:</td>
                      <td><input type="password" name="newPassword" /></td>
                    </tr>
                    <tr>
                      <td>Re-enter New Password:</td>
                      <td><input type="password" name="reenteredPassword" /></td>
                    </tr>
                    <tr>
                      <td colspan="2" style="text-align:center;padding-bottom:0.5em;"><input type="submit" class="btninput" value="Change Password" /></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
      </g:form>
    </div>
  </div>
</body>
</html>
