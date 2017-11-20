<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="manage-users" />
    <title>Manage Users</title>
    <r:require modules="application"/>
    <r:script>
		 
      $(document).ready(function() {

        $("#selectionCheckbox").click(function() {
          if ( $('#selectionCheckbox').attr('checked') ) {
            checkAllBoxes("rbacForm");
          }
          else {
            uncheckAllBoxes("rbacForm");
          }
        })

        $("#deleteMulti").click(function() {
          if ( checkForNoneSelected('No users were selected for deletion.') ) {
            return confirm('Are you sure you want to delete the selected user(s)?');
          }
          return false;
        })

        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( true );
      });
		                                      
    </r:script>

  </head>
  <body id="administration">
    <div id="per_page_container">
      <g:form name="rbacForm">
        <div class="container" id="per_page_header" title="List Users">
          <div class="headerLeft">
            <h1>Manage Users</h1>
          </div>
        </div>

        <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
        <div id="actionbar_outer" class="yui-b">
          <g:render template="/rbac/actionbar_multi" />
        </div>

        <div id="yui-main">
          <div class="yui-b">
            <div id="main_content" class="subpage">
              <input type="hidden" name="targetUri" value="${targetUri}" />
              <div id="table_border">
                <table>
                  <tr>
                    <th class="selectAll" title="Select All"><input id="selectionCheckbox" type="checkbox"  title="Click here to select all" /></th>
                    <g:sortableColumn property="username" title="Username" />
                    <g:sortableColumn property="role" title="Role" />
                  </tr>
                  <tbody>
                    <g:if test="${userRoleList}">
                      <g:each var="userRoleTuple" status="i" in="${userRoleList}">
                        <tr class="${(i % 2) == 0 ? 'row_odd' : 'row_even'}">
                          <td title="Click to Select">
                        <g:if test="${userRoleTuple.user.username != 'admin' }">
                          <g:checkBox name="idList" checked="${false}" value="${userRoleTuple.id}"/>
                        </g:if>
                        </td>
                        <td title="User Names"><g:link controller="rbac" action="edit" id="${userRoleTuple.id}">${userRoleTuple.user.username}</g:link></td>
                        <td title="Roles">${userRoleTuple.role.name}</td>
                        </tr>
                      </g:each>
                    </g:if>
                  </tbody>
                </table>
              </div>
              <div class="paginateButtons" style="margin: 1%;">
                <g:paginate prev="&laquo; previous" next="next &raquo;" max="${maxPerPage}" total="${userRoleList.totalCount}" />
              </div>
            </div>
            </g:form>
          </div>
        </div>
    </div>
  </body>
</html>
