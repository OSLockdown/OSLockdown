<%@ page import="com.trustedcs.sb.license.SbLicense" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <title>OS Lockdown Console &gt; Dashboard </title>
    <r:require modules="application"/>
    <r:script>
        $(document).ready(function() {
          // TODO: Move to common JS file and include
          $('.action_title').corners("5px top-left top-right");
          $('.actions').corners("5px");
        });

        function updateStatus() {
          <g:if test="${clientInstance}">
            //Create AjaxRequest object
            var ajaxRequest = new AjaxRequest("${resource(dir:'')}/client/updateClientStatus");
            ajaxRequest.addNameValuePair('clientId',${clientInstance?.id});
            //Send the request
            ajaxRequest.sendRequest();
          </g:if>
        }

        function updateInfo() {
          <g:if test="${clientInstance}">
            //Create AjaxRequest object
            var ajaxRequest = new AjaxRequest("${resource(dir:'')}/client/updateClientInfo");
            ajaxRequest.addNameValuePair('clientId',${clientInstance?.id});
            //Send the request
            ajaxRequest.sendRequest();
          </g:if>
        }

        <g:if test="${sendQueries}">
        $(document).ready(function() {
          <g:if test="${clientInstance}">
            updateStatus();
            updateInfo();
          </g:if>
          
        });
        </g:if>
    </r:script>
  </head>
  <body id="home">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Standalone Dashboard">
        <div class="headerLeft">
          <h1>OS Lockdown Console &gt; Dashboard</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <table>
            <tr>
                 <td style="text-align:center;vertical-align:center;font-size:20px;">
                  <h1><b>Standalone Console</b></h1>
		 </td>
            </tr>
            <tr>
              <td style="vertical-align:top;">
                <g:form controller="policyApplication" action="standAloneAction" method="post">
                  <g:render template="/policyApplication/standaloneConfig"/>
                </g:form>
              </td>
            </tr>

            <tr>
              <td style="vertical-align:top;">
                <g:render template="/client/details"/>
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  </body>
</html>
