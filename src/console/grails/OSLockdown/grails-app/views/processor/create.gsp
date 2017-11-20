<%@ page import="com.trustedcs.sb.web.pojo.Processor" %>
<%@ page import="com.trustedcs.sb.util.ClientType" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="creating-new-processor" />
    <title>New Processor</title>  
</head>
<body id="processor">
  <div id="per_page_container">
    <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
    <div class="container" id="per_page_header" title="New Processor">
      <div class="headerLeft">
        <h1>New Processor</h1>
      </div>
      <div class="headerRight">
        <g:link class="btn btn_blue" controller="processor" action="list" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:form action="save" method="post">

          <div class="info half centerDiv">
            <div class="info_header" title="Create New Processor">Create New Processor
              <span class="required" title="* indicates required field">* indicates required field</span>
            </div>
            <g:render template="config" model="[processorInstance:processorInstance, editable:true]"/>
            <div id="new" class="buttonsDiv">
              <input class="save btninput" type="submit" value="Create Processor" title="Click to Create New Processor" />
            </div>
          </div>
        </g:form>
      </div><!-- main_content -->
    </div><!-- yui-main -->
  </div><!-- per_page_container -->
</body>
</html>
