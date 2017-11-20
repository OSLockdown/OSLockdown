
<%@ page import="grails.util.Environment" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <title>General Information</title>
  </head>
  <body id="help">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="General Information">
        <div class="headerLeft">
          <h1>General Information</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <table>
            <tr>
<!--
              <td style="vertical-align:top;width:50%;">
            <g:render template="contact"/>
            </td>
--> 
<td/>
            <td style="vertical-align:top;" rowspan="3">
            <g:render template="standards"/>
            </td>
            </tr>
            <tr>
              <td style="vertical-align:top;">
            <g:render template="documentation"/>
            </td>
            </tr>
            <tr>
            </tr>
          </table>
          <g:if test="${Environment.current == Environment.DEVELOPMENT}">
            <table>
              <tr>
                <td>
              <g:render template="licenseSwap"/>
              </td>
              </tr>
            </table>
          </g:if>
         </div>
      </div>
    </div>
  </body>
</html>
