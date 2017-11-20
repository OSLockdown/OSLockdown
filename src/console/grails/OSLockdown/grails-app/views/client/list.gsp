<%@ page import="com.trustedcs.sb.web.pojo.Client" %>

<html>
  <g:set var="selectedList" value="${ request.getParameterValues('clientList').collect { id -> if (id)  {Long.parseLong(id); } } }"/>

  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <title>Clients</title>
    <r:require modules="application"/>
    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="managing-clients"/>
      <r:script>

        $(document).ready(function() {

          // only Enterprise mode has deleteMulti
          $("#deleteMulti").click(function() {
            if ( checkForNoneSelected('No clients were selected for deletion.') ) {
              return confirm('Are you sure you want to delete the selected client(s)?');
            }
            return false;
          })

        });

      </r:script>

    </sbauth:isEnterprise>
    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="managing-clients-su"/>
    
      <!-- json2.js is needed to handle json on older browsers (IE 6, 7, and 8 without a patch) who do not have json in their JavaScript engine. -->
      <!-- json2.js is used by detach.js, but is not included in it and MUST be included only once here. -->
      <r:require module="showedit"/>
      <r:script>

        // Function which is used by the detach.js to process the result of the Ajax detach call.
        // Returns Array[3] , where Array[0] contains the errorMessage, Array[1] contains erroredClientCount, and Array[2] contains successfulClientCount.
        function processDetachClientMapFunc( responseMap ){

          var errorMessage = "";         // overall error message for all failed detachment clients
          var erroredClientCount = 0;    // count of clients that failed detachment
          var successfulClientCount = 0; // count of clients successfully detached

          var key;
          for ( key in responseMap ) {

            var valueString = responseMap[key];

            /* If valueString starts with Error, then there was an error for client with id key. Append
            the error message to the errorMessage. */
            if( valueString.substr(0, "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}".length) ===
                "${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}" ){

                errorMessage = errorMessage
                  + valueString.substr("${Client.DETACHMENT_MISSING_REPORTS_ERROR_PREFIX}".length, valueString.length) + "<br>";

                erroredClientCount++;
            }
            /* There was no error. The valueString should be the String representation of the detachment date.
            Here need to : a. find the td with the key (clientId), and then find its last sibling (Last Detached) td and
            replace (set) its value to the date passed, b. make the checkbox disabled (c. optional if this is the last
            Client and *all* Client are detached disable the Client (with Detach), Actions (with all Actions) and Logging Level) */
            else {
              successfulClientCount++;

              /* One and exactly one checkbox corresponding to a successfully detached clientId (key). This is doing
              find all elements with id=clientList AND input[type=checkbox] (not don't enclose it in [])_AND value="clientID" */
              var checkBoxForClient = $('[#clientList]input[type=checkbox][value="'+key+'"]');
              var checkBoxEnclosingTd = $(checkBoxForClient).parent( 'td' );
              var siblingsTds = $(checkBoxEnclosingTd).siblings();
              var groupTd = $(siblingsTds[3]);
              var lastDetachTd = $(siblingsTds[siblingsTds.length-1]);

              // Remove checkBoxForClient from its td, as the Client now is detached
              $(checkBoxEnclosingTd).replaceWith( "<td></td>" );

              // Change Group name to none
              groupTd.replaceWith( "<td>none</td>" );

              // Set the last detached date into last td (detached date column)
              $(lastDetachTd).replaceWith( "<td>" + valueString + "</td>" );
            }
          }

          // Return results
          var resultArray = new Array(3);
          resultArray[ 0 ] = errorMessage;
          resultArray[ 1 ] = erroredClientCount;
          resultArray[ 2 ] = successfulClientCount;
          return resultArray;
        }

        function checkForDetachmentProgress( clientIdListStringified ) {

          $.ajax({
              url: "${resource(dir:'')}/client/checkDetachStatus",
              type: "POST",
              data: { clientIdList: clientIdListStringified },
              cache: false,
              complete: function( xhr, status ) {

                // Noticed that if press Stop Detach right before checkForDetachmentProgress()
                // runs inside a timer will get status updated and then progress area immediately closed
                // as the detach completed. If this is a problem will need to declare var timerId
                // as global and call clearInterval( timerId ); upon Stop Detach button being clicked.

                // See detach.js for logic.
                postProcessCheckDetachmentProgress( xhr, status );
              }
          });
        }

        $(document).ready(function() {

          $("#detachAbort").live( 'click', function(){

            var detachButton = $(this);

            var buttonText = $(detachButton).text();
            if( buttonText == "Close" ){

              // Close the dialog
              hideBlockUI();

              var button = $(this);

              // hideBlockUI takes like a sec to really hide. Only after it hides revert back to values
              // and styles for all components in_detachmentProgressDialog.gsp
              setTimeout(
                  function(){

                      // Revert button text
                      $(detachButton).text( "Stop Detach" );
                      // Clear margin-top:20px set at the end of postProcessDetach() in detach.js
                      $(detachButton).css( { 'margin-bottom':'10px;', 'margin-top':'0px' } );

                      // Unhide the progress icon
                      $("#detachProgressIcon").show();

                      // Unhide the warning message as
                      $("#detachWarningMessage").show();

                      // Reset the progress message
                      var resetProgressMessage =
                        '<div style="text-align: center;vertical-align: middle;" id="detachProgressMessage">Starting to Detach Clients ...</div>';
                      $("#detachProgressMessage").replaceWith( resetProgressMessage );
                  },
                  500 );
            }
            else if( buttonText == "Stop Detach" ){

                // When user clicks on the Stop Detach button

                // 1. change the text on the button to indicate stop is in progress.
                $(detachButton).text( "Stopping Detach ..." );

                // 2. make stop button disabled
                $(detachButton).attr( "disabled", "disabled" );

                // Make a call to stop of detachment.
                $.ajax({
                    url: "${resource(dir:'')}/client/stopDetachClients",
                    type: "POST",
                    cache: false,
                    complete: function( xhr, status ) {

                      // After Stop Detach call completes (it is a short call)
                    }
                });
            }
            // else Ignore all others. Detachment might be in progress so block UI should still be displayed
          })

          $('.detachMulti').click(function() {

            if ( checkForNoneSelected('No clients were selected for detachment.') ) {

              if( confirm('Are you sure you want to detach the selected client(s)?') ){

                // See detach.js for logic. Clean prev flash messages and errors
                cleanPrevFlashErrorsAndMessages();

                // grab the selected checkboxes (and only those with id=#clientList), except the selectAll checkbox
                var selectedClientCheckBoxes = $("[#clientList]input[type=checkbox]").filter(":checked").filter(":not(#selectionCheckbox)");
                if( selectedClientCheckBoxes && selectedClientCheckBoxes.length > 0 ){

                  // Use this js Array to populate the clients user wants to detach ...
                  var clientIdList = [];

                  var i = 0;
                  for (; i < selectedClientCheckBoxes.length; i++){
                    var selectedClientId = $(selectedClientCheckBoxes[i]).val();
                                     /* if use String selectedClientId then it actually gets put into the Array with double quotes
                                     which then causes grief at the server side, since need to strip then down. Instead, just use
                                     ints and store them into the array. */
                    clientIdList.push( parseInt( selectedClientId, 10 ) );
                  }
                  // Stringify the list of clientIds
                  var clientIdListStringified = JSON.stringify( clientIdList );

                  // Grab the logging level which is needed for invoking actions.
                  var loggingLevel = $("#loggingLevel").val();

                  // See detach.js for logic. Passin the name of the message div.
                  showBlockUI( 'detachmentDialog' );

                  // start the detachment progress timer to run every N sec
                  var timerId = setInterval( function() { checkForDetachmentProgress( clientIdListStringified ) }, 5000 );

                  /* Note #1: type is POST (also configured on the controller, so if a GET is attemped an error page is returned with
                    "The specified HTTP method is not allowed for the requested resource ()" as expected as GET is not allowed.
                     Note #2: this code MUST be invoked from the .gsp and not refactored to a separate .js file as AJAX call needs ShiroSecurityManager.
                     Attempted to do that and got the "No SecurityManager accessible to the calling code, either bound to the
                     org.apache.shiro.util.ThreadContext or as a vm static singleton. This is an invalid application configuration." exception. */
                  $.ajax({
                      url: "${resource(dir:'')}/client/detach",
                      type: "POST",
                      data: { clientIdList: clientIdListStringified, loggingLevel:loggingLevel },
                      cache: false,
                      complete: function( xhr, status ) {

                          // 1. stop the detachment progress timer
                          clearInterval( timerId );

                          // See detach.js for logic. Process the results of the ajax call and populate the UI elements dynamically by using
                          // processDetachClientMapFunc defined in this file. This also includes calling unblockUI() to close it.
                          postProcessDetach( xhr, status, processDetachClientMapFunc );
                      }
                  });
                }
                else {
                  alert("No clients were selected for detachment.");
                  return false;
                }
              }
              else {
                return false;
              }
            }
            return false;
          });

        });

      </r:script>

    </sbauth:isBulk>

    <r:script disposition="head">
      // Below is the common code for Enterprise and Lock and Release

      $(document).ready(function() {

        <!-- Only one Client may be selected for the Edit action -->
        $("#editMulti").click(function() {
          if ($(":checkbox:checked").length > 1) {
            alert("Only one Client may be selected to edit");
            return false;
          }
        })
        
        $("#quickScanMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for quick scanning.') ) {
            return confirm('Are you sure you want to quick scan the selected client(s)?');
          }
            return false;
        })

        $("#scanMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for scanning.') ) {
           return confirm('Are you sure you want to scan the selected client(s)?');
          }
          return false;
        })

        $("#applyMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for applying.') ) {
           return confirm('Are you sure you want to apply the selected client(s)?');
          }
          return false;
        })

        $("#undoMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for undoing.') ) {
           return confirm('Are you sure you want to undo the selected client(s)?');
          }
          return false;
        })

        $("#baselineMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for baselining.') ) {
           return confirm('Are you sure you want to baseline the selected client(s)?');
          }
          return false;
        })

        $("#abortMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for action aborting.') ) {
           return confirm('Are you sure you want to abort the actions running on the selected client(s)?');
          }
          return false;
        })

        $("#autoUpdateMulti").click(function() {
          if ( checkForNoneSelected('No clients were selected for AutoUpdate.') ) {
           return confirm('An AutoUpdate request will be honored by the client(s) despite any Core Hour or Load Threshold settings.  Are you sure you want to initiate an AutoUpdate on the client(s)?');
          }
          return false;
        })

        $("#selectionCheckbox").click(function() {
          if ( $('#selectionCheckbox').prop('checked') ) {
            checkAllBoxes("clientform");
          }
          else {
            uncheckAllBoxes("clientform");
          }
        })

        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( true );
      });

  </r:script>
</head>
<body id="client">
  <div id="per_page_container">
    <g:form name="clientform">

      <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
      <div class="container" id="per_page_header" title="Clients">
        <div class="headerLeft">
          <h1>Clients</h1>
        </div>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <div id="actionbar_outer" class="yui-b">
        <g:render template="/client/actionbar_multi" />
      </div>

      <!-- MAIN PAGE CONTENT, requires two divs for YUI Grids -->
      <div id="yui-main">
        <div id="main_content" class="yui-b">

          <!-- ********************************************************** -->
          <!-- CLIENT LIST -->
          <!-- ********************************************************** -->

          <div id="clientlist" class="subpage">
            <div id="table_border">
              <div id="table_control" style="text-align: right;">
                <div id="searchForm">

                  <!-- In Bulk mode show detached filters -->
                  <g:if test="${isBulk}">

                    <g:if test="${ detachFilter == Client.DETACHMENT_CLIENTS_DETACHED }">
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="All Clients"             value="${Client.DETACHMENT_CLIENTS_ALL}" /><span style="vertical-align:middle;margin-right:10px;">All Clients</span>
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="Only Attached Clients"   value="${Client.DETACHMENT_CLIENTS_ATTACHED}" /><span style="vertical-align:middle;margin-right:10px;">Only Attached Clients</span>
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="Only Detached Clients"   value="${Client.DETACHMENT_CLIENTS_DETACHED}" checked="true" /><span style="vertical-align:middle;margin-right:10px;">Only Detached Clients</span>
                    </g:if>
                    <g:elseif test="${ detachFilter == Client.DETACHMENT_CLIENTS_ATTACHED }">
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="All Clients"             value="${Client.DETACHMENT_CLIENTS_ALL}" /><span style="vertical-align:middle;margin-right:10px;">All Clients</span>
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="Only Attached Clients"   value="${Client.DETACHMENT_CLIENTS_ATTACHED}" checked="true" /><span style="vertical-align:middle;margin-right:10px;">Only Attached Clients</span>
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="Only Detached Clients"   value="${Client.DETACHMENT_CLIENTS_DETACHED}" /><span style="vertical-align:middle;margin-right:10px;">Only Detached Clients</span>
                    </g:elseif>
                    <g:else> <!-- default is all or if detachFilter is not passed -->
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="All Clients"             value="${Client.DETACHMENT_CLIENTS_ALL}" checked="true" /><span style="vertical-align:middle;margin-right:10px;">All Clients</span>
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="Only Attached Clients"   value="${Client.DETACHMENT_CLIENTS_ATTACHED}" /><span style="vertical-align:middle;margin-right:10px;">Only Attached Clients</span>
                      <g:radio style="vertical-align:middle;" name="detachFilter" title="Only Detached Clients"   value="${Client.DETACHMENT_CLIENTS_DETACHED}" /><span style="vertical-align:middle;margin-right:10px;">Only Detached Clients</span>
                    </g:else>

                  </g:if>

                  <g:textField name="search" id="search" value="${search}" ></g:textField>
                  <g:actionSubmit class="btninput" value="Search" action="search" title="Click to Search" />
                </div>
              </div>

              <!-- Construct a params map to be passed in a. sortableColumn params=, and b. < g : paginate params = -->
              <!-- 1. for non-bulk mode (Enterprise) the Map only contains search:search                                         -->
              <!-- 2. in bulk mode map contains [ search : search, detachFilter : detachFilter ]                    -->
              <g:if test="${isEnterprise}">
                <g:set var="paramsMap" value="[search:search]" />
              </g:if>
              <g:elseif test="${isBulk}">
                <g:set var="paramsMap" value="[search:search,detachFilter:detachFilter]" />
              </g:elseif>
              <g:else>
                <!-- not applicable to Standalone -->
              </g:else>

              <table id="t_clientlist">
                <thead>
                  <tr>
                    <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click to select all" /></th>
                    <g:sortableColumn params="${paramsMap}" property="name" title="Name" />
                    <g:sortableColumn params="${paramsMap}" property="clienttype" title="Client Type" />
                    <g:sortableColumn params="${paramsMap}" property="hostAddress" title="Host Address" />
                    <g:sortableColumn params="${paramsMap}" property="location" title="Location" />
                    <g:sortableColumn params="${paramsMap}" property="group" title="Group" />

                    <g:if test="${isBulk}">
                      <g:sortableColumn params="${paramsMap}" property="dateCreated" title="Attached On" />
                      <g:sortableColumn params="${paramsMap}" property="dateDetached" title="Detached On" />
                    </g:if>
                  </tr>
                </thead>
                <tbody id="tablebody">
                <g:if test="${clientResultList}">

                  <g:each in="${clientResultList}" status="i" var="clientInstance">
                    <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">

                      <g:if test="${isBulk && clientInstance.dateDetached}">
                        <td></td>
                      </g:if>
                      <g:else>
                        <td><g:checkBox name="clientList" value="${clientInstance.id}" checked="${selectedList?.contains(clientInstance.id) ? true : false }" /></td>
                      </g:else>

                      <td><g:link action="show" id="${clientInstance.id}">${fieldValue(bean:clientInstance, field:'name')}</g:link></td>
                      <td>${fieldValue(bean:clientInstance, field:'clientType.name')}</td>
                      <td>${fieldValue(bean:clientInstance, field:'hostAddress')}</td>

                      <!-- Show up to 30 characters unaltered; if longer than 30, show its 26 characters 
                      followed by " ..." for a total of 30 characters and show the full value of the location on the mouse over -->
                      <g:set var="displayLocation" value="${fieldValue(bean:clientInstance, field:'location')}" />
                      <g:if test="${displayLocation && displayLocation.size() >= 31 }">
                        <g:set var="displayLocation" value="${displayLocation.substring(0, 26)}" />
                        
                        <td style="cursor:pointer;" title="${fieldValue(bean:clientInstance, field:'location')}">${displayLocation} ...</td>
                      </g:if>
                      <g:else>
                        <td>${displayLocation}</td>
                      </g:else>

                      <td>
                        <g:if test="${clientInstance.group}">
                          <g:link controller="group" action="show" id="${clientInstance.group.id}">${clientInstance.group.name}</g:link>
                        </g:if>
                        <g:else>
                          none
                        </g:else>
                      </td>

                      <g:if test="${isBulk}">

                        <g:if test="${clientInstance.dateCreated}">
                          <td style="cursor:pointer;" title="${clientInstance.dateCreated}"><g:formatDate format="MMM-dd-yyyy" date="${clientInstance.dateCreated}"/></td>
                        </g:if>
                        <g:else>
                          <td></td>
                        </g:else>
                        
                        <g:if test="${clientInstance.dateDetached}" >
                          <td style="cursor:pointer;" title="${clientInstance.dateDetached}"><g:formatDate format="MMM-dd-yyyy" date="${clientInstance.dateDetached}"/></td>
                        </g:if>
                        <g:else>
                          <td></td>
                        </g:else>
                      </g:if>
                    </tr>
                  </g:each>
                </g:if>
                <g:else>
                  <tr class="row_even">

                    <g:set var="noClientsColSpan" value="6" />
                    <g:if test="${isBulk}">
                      <g:set var="noClientsColSpan" value="8" />
                    </g:if>
                    <td style="text-align:center;" colspan="${noClientsColSpan}">No clients currently exist.</td>
                    
                  </tr>
                </g:else>
                </tbody>
              </table>
            </div>

            <div class="paginateButtons" style="margin: 1%;">
              <g:paginate prev="&laquo; previous" next="next &raquo;" total="${clientResultList.totalCount}" max="${maxPerPage}" params="${paramsMap}" />
            </div>

          </div><!-- clientlist -->

        </div><!-- end yui-b -->
      </div><!-- end yui-main -->

    </g:form>

  </div><!-- end per_page_container -->

  <!-- Detachment progress dialog -->
  <g:render template="/client/detachmentProgressDialog" />

</body>
</html>
