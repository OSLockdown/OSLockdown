
<%@ page import="com.trustedcs.sb.license.SbLicense" %>
<html>


  <head>
    <title>OS Lockdown Console &gt; Dashboard</title>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="intro-SB-editions" />
    <r:require modules="application"/>
    <r:script >
      // Below is the common code for Enterprise and Lock and Release

      $(document).ready(function() {
        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( false );

        $("table.zebra").each (function (foo,bar) {
            zebraStripTable(bar);
        });            
 
      });
    </r:script>

  </head>
  <body id="home">

    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Reports">
        <div class="headerLeft">
          <h1>OS Lockdown Console &gt; Dashboard</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <table>
              <tr>
                <td style="text-align:center;vertical-align:center;font-size:20px">
                  <h1><b>Enterprise Console</b></h1>
                </td>
              </tr>
              <tr>
                <td style="padding-bottom:1em; width:95%;">
                  <g:render template="/dashboard/general"/>
                </td>
              </tr>
              <tr>
                <td style="padding-bottom:1em; width:95%;">
                  <g:render template="/dashboard/statistics"/>
                </td>
              </tr>

            <tr>
              <td style="width:60%;">
                <shiro:hasAnyRole in="['Administrator','User','Security Officer']">
                  <div class="info">
                    <div class="info_header">
                      <table>
                        <tr>
                          <td style="text-align:left;">Most Recent Notifications</td>
                          <td style="text-align:right;"><g:link class="btn" controller="notifications" action="list" style="font-weight:normal;" title="View All Notifications">View All</g:link></td>
                        </tr>
                      </table>
                    </div>
                    <g:render template="/notifications/notificationList" model="['isDashboard':true]"/>
                  </div>
                </shiro:hasAnyRole>
              </td>
            </tr>
          </table>
        </div>
        <!-- End of main_content -->
      </div>
    </div>
  </body>
</html>
