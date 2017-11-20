<%@ page import="com.trustedcs.sb.web.pojo.Processor" %>
<%@ page import="com.trustedcs.sb.util.ClientType" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <title>Processor Details</title>

    <meta name="contextSensitiveHelp" content="viewing-processor"/>

    <r:require modules="application"/>
    <r:script>
      // Below is the common code for Enterprise and Lock and Release

      $(document).ready(function() {

        // TODO: Move to common JS file and include
        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

      });

		                                      
    </r:script>
  
  </head>
  <body id="processor">
    <div id="per_page_container">

      <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
      <div class="container" id="per_page_header" title="Processor Details">
        <div class="headerLeft">
          <h1>Processor Details</h1>
        </div>
        <div class="headerRight">
          <g:link class="btn btn_blue" controller="processor" action="list" event="back" title="Click to go Back">&laquo; Back</g:link>
        </div>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <div id="actionbar_outer" class="yui-b">
        <g:render template="/processor/actionbar" />
      </div>

      <!-- MAIN PAGE CONTENT, requires two divs for YUI Grids -->
      <div id="yui-main">
        <div id="main_content" class="yui-b">

          <!-- ********************************************************** -->
          <!-- CLIENT DETAILS -->
          <!-- ********************************************************** -->
          <div id="processordetails" class="subpage">
            <g:form method="post" >
              <input type="hidden" name="id" value="${processorInstance?.id}" />
              <div class="info">
                <div class="info_header" title="Configuration">
                  <h2>Configuration</h2>
                </div>
                <div class="info_body">
                  <g:render template="display" />
                </div>
              </div>
            </g:form>
          </div><!-- subpage -->
        </div><!-- yui-b -->
      </div><!-- main_content -->
    </div><!-- per_page_container -->

  </body>
</html>
