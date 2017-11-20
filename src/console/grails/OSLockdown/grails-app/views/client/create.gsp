<%@ page import="com.trustedcs.sb.web.pojo.Client" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="creating-new-client" />
    <title>New Client</title>  
</head>
<body id="client">
  <div id="per_page_container">
    <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
    <div class="container" id="per_page_header" title="New Client">
      <div class="headerLeft">
        <h1>New Client</h1>
      </div>
      <div class="headerRight">
        <g:link class="btn btn_blue" controller="client" action="list" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:form action="save" method="post">

          <div class="info half centerDiv">
            <div class="info_header" title="Create New Client">Create New Client
              <span class="required" title="* indicates required field">* indicates required field</span>
            </div>
            <g:render template="config" />
            <div id="new" class="buttonsDiv">
              <input class="save btninput" type="submit" value="Create Client" title="Click to Create New Client" />
            </div>
          </div>
        </g:form>
      </div><!-- main_content -->
    </div><!-- yui-main -->
  </div><!-- per_page_container -->
</body>
</html>
