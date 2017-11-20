<%@ page import="com.trustedcs.sb.web.pojo.Processor" %>
<%@ page import="com.trustedcs.sb.util.ClientType" %>

<html>
  <g:set var="selectedList" value="${ request.getParameterValues('processorList').collect { id -> if (id)  {Long.parseLong(id); } } }"/>

  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <title>Processors</title>

    <meta name="contextSensitiveHelp" content="managing-processors"/>
    <r:require modules="application"/>
    <r:script >

      $(document).ready(function() {

        // only Enterprise mode has deleteMulti
        $("#deleteMulti").click(function() {
          if ( checkForNoneSelected('No processors were selected for deletion.') ) {
            return confirm('Are you sure you want to delete the selected processor(s)?');
          }
          return false;
        })


        <!-- Only one Processor may be selected for the Edit action -->
        $("#editMulti").click(function() {
          if ($(":checkbox:checked").length > 1) {
            alert("Only one Processor may be selected to edit");
            return false;
          }
        })
        
        $("#selectionCheckbox").click(function() {
          if ( $('#selectionCheckbox').attr('checked') ) {
            checkAllBoxes("processorform");
          }
          else {
            uncheckAllBoxes("processorform");
          }
        })

        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( true );
      });

  </r:script>
</head>
<body id="processor">
  <div id="per_page_container">
    <g:form name="processorform">

      <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
      <div class="container" id="per_page_header" title="Processors">
        <div class="headerLeft">
          <h1>Processors</h1>
        </div>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <div id="actionbar_outer" class="yui-b">
        <g:render template="/processor/actionbar_multi" />
      </div>

      <!-- MAIN PAGE CONTENT, requires two divs for YUI Grids -->
      <div id="yui-main">
        <div id="main_content" class="yui-b">

          <!-- ********************************************************** -->
          <!-- CLIENT LIST -->
          <!-- ********************************************************** -->

          <div id="processorlist" class="subpage">
            <div id="table_border">

              <!-- Construct a params map to be passed in a. sortableColumn params=, and b. < g : paginate params = -->
              <!-- 1. for non-bulk mode (Enterprise) the Map only contains search:search                                         -->
              <!-- 2. in bulk mode map contains [ search : search, ]                    -->
              <g:set var="paramsMap" value="[search:search]" />

              <table id="t_processorlist">
                <thead>
                  <tr>
                    <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click to select all" /></th>
                    <g:sortableColumn params="${paramsMap}" property="name" title="Name" />
                    <g:sortableColumn params="${paramsMap}" property="clientType" title="Type" />

                  </tr>
                </thead>
                <tbody id="tablebody">
                <g:if test="${processorResultList}">

                  <g:each in="${processorResultList}" status="i" var="processorInstance">
                    <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">

                      <td><g:checkBox name="processorList" value="${processorInstance.id}" checked="${selectedList?.contains(processorInstance.id) ? true : false }" /></td>

                      <td><g:link action="show" id="${processorInstance.id}">${fieldValue(bean:processorInstance, field:'name')}</g:link></td>
                      <g:if test="${processorInstance.clientType}">
                        <td>${fieldValue(bean:processorInstance, field:'clientType.name')}</td>
                      </g:if>
                      <g:else>
                        <td>None</td>
                      </g:else>

                    </tr>
                  </g:each>
                </g:if>
                <g:else>
                  <tr class="row_even">

                    <g:set var="noProcessorsColSpan" value="3" />
                    <td style="text-align:center;" colspan="${noProcessorsColSpan}">No processors currently exist.</td>
                    
                  </tr>
                </g:else>
                </tbody>
              </table>
            </div>

            <div class="paginateButtons" style="margin: 1%;">
              <g:paginate prev="&laquo; previous" next="next &raquo;" total="${processorResultList.totalCount}" max="${maxPerPage}" params="${paramsMap}" />
            </div>

          </div><!-- processorlist -->

        </div><!-- end yui-b -->
      </div><!-- end yui-main -->

    </g:form>

  </div><!-- end per_page_container -->
</body>
</html>
