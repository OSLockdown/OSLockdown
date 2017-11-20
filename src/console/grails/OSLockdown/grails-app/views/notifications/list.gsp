<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    
    <meta name="contextSensitiveHelp" content="managing-notifs" />
    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="managing-notifs-su"/>
    </sbauth:isBulk>
    <r:require modules="application"/>
    <r:script >
	   
      $(document).ready(function() {
	             
        $("#selectionCheckbox").click(function() {
          if ( $('#selectionCheckbox').attr('checked') ) {
            checkAllBoxes("notificationsForm");
          }
          else {
            uncheckAllBoxes("notificationsForm");
          }
        })

        $("#deleteMulti").click(function() {
          if ( checkForNoneSelected('No notifications were selected for deletion.') ) {
            return confirm('Are you sure you want to delete the selected notification(s)?');
          }
          return false;
        })
	              
        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

        // Mark first column header as sorted desc, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( false );
      });

    </r:script>
    <title>Notifications</title>
  </head>
  <body id="notifications">
    <div id="per_page_container">
      <g:form name="notificationsForm">
        <div container="container" id="per_page_header" title="Notifications">
          <div class="headerLeft">
            <h1>Notifications</h1>
          </div>
        </div>

        <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
        <div id="actionbar_outer" class="yui-b">
          <g:render template="/notifications/actionbar_multi" />
        </div>

        <div id="yui-main">
          <div class="yui-b">
            <div id="main_content" class="subpage">
              <div id="table_border">
                <g:render template="/notifications/notificationList"/>
              </div>
              <div class="paginateButtons" style="margin: 1%;">
                <g:paginate prev="&laquo; previous" next="next &raquo;" max="${maxPerPage}" total="${totalCount}" />
              </div>
            </div>
          </div>
        </div>
      </g:form>
    </div>
  </body>
</html>
