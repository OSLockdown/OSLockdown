<html>
  <head>
    <title>OS Lockdown Error</title>
    <meta name="layout" content="main" />
  </head>
  <body id="home">
    <div id="per_page_container">
      <div id="per_page_header" title="OS Lockdown Error">
        <h1>OS Lockdown Error</h1>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="actionHolder">
            <input type=button class="btninput" value="Back" onClick="history.go(-1)">
          </div>
          <div class="info">
            <div class="info_header">
              <h2>Error Information</h2>
            </div>
            <table class="message">
              <tr>
                <td class="tdname">Code:</td>
                <td>${request.'javax.servlet.error.status_code'}</td>
              </tr>
              <tr>
                <td class="tdname">Message:</td>
                <td>${request.'javax.servlet.error.message'.encodeAsHTML()}</td>
              </tr>
              <tr>
                <td class="tdname">Servlet:</td>
                <td>${request.'javax.servlet.error.servlet_name'}</td>
              </tr>
              <tr>
                <td class="tdname">URI:</td>
                <td>${request.'javax.servlet.error.request_uri'}</td>
              </tr>
            </table>
          </div>
          <g:if test="${exception}">
            <div class="info">
              <div class="info_header">
                <h2>Exception Details</h2>
              </div>
              <table class="message">
                <tr>
                  <td class="tdname">Message:</td>
                  <td>${exception.message?.encodeAsHTML()}</td>
                </tr>
                <tr>
                  <td class="tdname">Caused by:</td>
                  <td>${exception.cause?.message?.encodeAsHTML()}</td>
                </tr>
                <tr>
                  <td class="tdname">Class:</td>
                  <td>${exception.className}</td>
                </tr>
                <tr>
                  <td class="tdname">At Line:</td>
                  <td>[${exception.lineNumber}]</td>
                </tr>
              </table>
            </div>
            <div class="info">
              <div class="info_header">
                <h2>Code Snippet</h2>
              </div>
              <div class="snippet">
                <g:each var="cs" in="${exception.codeSnippet}">
${cs?.encodeAsHTML()}<br />
                </g:each>
              </div>
            </div>
            <div class="info">
              <div class="info_header">
                <h2>Stack Trace</h2>
              </div>
              <div id="stack">
                <pre><g:each in="${exception.stackTraceLines}">${it.encodeAsHTML()}<br/></g:each></pre>
              </div>
            </div>
          </g:if>
        </div> <!-- End of main_content -->
      </div> <!-- End of yui-main -->
    </div> <!-- End of per_page_container -->
  </body>
</html>
