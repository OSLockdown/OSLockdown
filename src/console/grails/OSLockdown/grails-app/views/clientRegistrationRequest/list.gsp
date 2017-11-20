<html>
  <g:set var="selectedList" value="${ request.getParameterValues('requestList').collect { id -> if (id)  {Long.parseLong(id); } } }"/>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="auto-reg-requests"/>
    </sbauth:isEnterprise>
    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="auto-reg-requests-su"/>
    </sbauth:isBulk>

    <title>Client Auto-Registration Requests</title>  
    <r:require modules="application"/>
    <r:script>
		 
       $(document).ready(function() {
				   	
         $("#denyMulti").click(function() {
           if ( checkForNoneSelected('No requests were selected for denial.') ) {
             return confirm('Are you sure you want to deny the selected request(s)?');
           }
           return false;
         })

         $("#allowMulti").click(function() {
           if ( checkForNoneSelected('No requests were selected for acceptance.') ) {
             return confirm('Are you sure you want to accept the selected client(s)?');
           }
           return false;
         })

         $("#selectionCheckbox").click(function() {
           if ( $('#selectionCheckbox').attr('checked') ) {
             checkAllBoxes("clientform");
           }
           else	{
             uncheckAllBoxes("clientform");
           }
         })

         $('.action_title').corners("5px top-left top-right");
         $('.actions').corners("5px");
       });
		                                      
    </r:script>
  </head>
  <body id="client">
    <div id="per_page_container">
      <g:form name="clientform">
        <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
        <div class="container" id="per_page_header" title="Auto-Registration Requests">
          <div class="headerLeft">
            <h1>Auto-Registration Requests</h1>
          </div>
        </div>
        <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
        <div id="actionbar_outer" class="yui-b">
          <g:render template="/clientRegistrationRequest/actionbar_multi" />
        </div>
        <!-- MAIN PAGE CONTENT, requires two divs for YUI Grids -->
        <div id="yui-main">
          <div id="main_content" class="yui-b">
            <div id="requestlist" class="subpage">
              <div class="tableBorder">
                <div style="text-align:right;padding-top:0.2em;padding-bottom:0.2em;margin-right:1em;">
                  <g:select class="paddedSelect" title="Select Group Name" name="groupId" from="${groupList}" optionKey="id" optionValue="name" noSelection="['':'[- Optional Group Assignment -]']"/>
                </div>
              </div>
              <div class="tableBorder">                
                <div>
                  <table id="t_regrequestlist">
                    <thead>
                      <tr>
                        <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click to select all" /></th>
                        <th title="Received">Received</th>
                        <th title="Name">Name</th>
                        <th title="Client Type">Client Type</th>
                        <th title="Host Address">Host Address</th>
                        <th title="Location">Location</th>
                        <th title="Contact">Contact</th>
                      </tr>
                    </thead>
                    <tbody id="tablebody">
                    <g:if test="${requestInstanceList}">
                      <g:each in="${requestInstanceList}" status="i" var="requestInstance">
                        <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                          <td><g:checkBox name="requestList" value="${requestInstance.id}" checked="${selectedList?.contains(requestInstance.id) ? true : false }" /></td>
                        <td><g:link action="show" id="${requestInstance.id}"><dateFormat:printDate date="${requestInstance.timeStamp}"/></g:link></td>
                        <td>${fieldValue(bean:requestInstance, field:'name')}</td>
                        <td>${fieldValue(bean:requestInstance, field:'displayText')}</td>
                        <td>${fieldValue(bean:requestInstance, field:'hostAddress')}</td>
                        <td>${fieldValue(bean:requestInstance, field:'location')}</td>
                        <td>${fieldValue(bean:requestInstance, field:'contact')}</td>
                        </tr>
                      </g:each>
                    </g:if>
                    <g:else>
                      <tr class="row_even">
                        <td style="text-align:center;" colspan="7">No requests currently exist.</td>
                      </tr>
                    </g:else>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="paginateButtons" style="margin: 1%;">
                <g:paginate prev="&laquo; previous" next="next &raquo;" total="${requestInstanceTotal}" />
              </div>
            </div><!-- requestlist -->
          </div><!-- end yui-b -->
        </div><!-- end yui-main -->
      </g:form>
    </div><!-- end per_page_container -->
  </body>
</html>
