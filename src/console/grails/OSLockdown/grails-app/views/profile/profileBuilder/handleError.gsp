<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <title>Grails Runtime Exception</title>    
  </head>
  <body id="profiles">
    <div id="per_page_container">
      <div id="per_page_header" title="Error">
        <h1>Grails Runtime Exception</h1>
        <h2>Error Details</h2>
      </div>
      <div id="yui-main">
        <div class="yui-b">
          <div id="main_content" class="subpage">
            <div class="actionHolder">
              <g:link class="btn" controller="profile" action="profileBuilder" event="back" title="Click to go Back">Back</g:link>
            </div>
            <div class="info">
              <div class="message" title="Error Details">
                <strong>Error ${request.'javax.servlet.error.status_code'}:</strong> ${request.'javax.servlet.error.message'.encodeAsHTML()}<br/>
                <strong>Servlet:</strong> ${request.'javax.servlet.error.servlet_name'}<br/>
                <strong>URI:</strong> ${request.'javax.servlet.error.request_uri'}<br/>
                <g:if test="${exception}">
                  <strong>Exception Message:</strong> ${exception.message?.encodeAsHTML()} <br />
                  <strong>Caused by:</strong> ${exception.cause?.message?.encodeAsHTML()} <br />
                  <strong>Class:</strong> ${exception.className} <br />
                  <strong>At Line:</strong> [${exception.lineNumber}] <br />
                  <strong>Code Snippet:</strong><br />
                  <div class="snippet">
                    <g:each var="cs" in="${exception.codeSnippet}">
                      ${cs?.encodeAsHTML()}<br />
                    </g:each>
                  </div>
                </g:if>
              </div>
              <g:if test="${exception}">
                <h2>Stack Trace</h2>
                <div class="stack">
                  <pre><g:each in="${exception.stackTraceLines}">${it.encodeAsHTML()}<br/></g:each></pre>
                </div>
              </g:if>
            </div>
          </div>
        </div>
      </div>
    </div
  </body>
</html>