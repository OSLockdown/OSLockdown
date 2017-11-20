<%@ page import="com.trustedcs.sb.license.SbLicense" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="system-basics-launching-app"/>
  <title>OS Lockdown Console</title>  
</head>
<body>  
  <div id="per_page_container">
    <div class="container" id="per_page_header" title="login">
      <div class="headerLeft">
        <h1>Forcepoint LLC - OS Lockdown Console</h1>
      </div>
    </div>
    <div id="yui-main">
      <g:form action="signIn">
        <div id="main_content" class="subpage">
          <sbauth:isValid>
            <div class="info" style="width: 40%; margin: 2em  auto;">
              <div class="info_header">Login</div>
              <input type="hidden" name="targetUri" value="${targetUri}" />
              <table style="margin-top: 1em; padding-bottom: 1em;">
                <tbody>
                  <tr>
                    <td class="propName"><label for="loginName">Username</label>:</td><!--${username}-->
                    <td><input id="loginName" type="text" name="username" value=""/></td>
                  </tr>
                  <tr>
                    <td class="propName"><label for="loginPassword">Password</label>:</td>
                    <td><input type="password" id="loginPassword" name="password" value=""/></td>
                  </tr>
                <tr>
                  <td colspan="2" style="text-align:center; height: 3em;"><input type="submit" class="btninput" value="Sign in" title="Click to Sign In"/></td>
                </tr>
                </tbody>
              </table>
            </div>
          </sbauth:isValid>
          <g:render template="warning"/>
        </div>
      </g:form>
    </div>
  </div>
</body>
</html>
