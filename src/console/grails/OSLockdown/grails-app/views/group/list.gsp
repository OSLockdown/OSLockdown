<%@ page import="com.trustedcs.sb.web.pojo.Client" %>

<html>
  <g:set var="selectedList" value="${ request.getParameterValues('groupList').collect { id -> if (id)  {Long.parseLong(id); }}  }"/>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <r:require modules="application"/>
    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="managing-groups" />
    </sbauth:isEnterprise>
    
    <sbauth:isBulk>

      <!-- Below is Lock and Release-specific code only -->

      <meta name="contextSensitiveHelp" content="managing-groups-su" />

      <r:require modules="showedit"/>
      <r:script >

        // Function which is used by the detach.js to process the result of the Ajax detach call.
        // Returns Array[3] , where Array[0] contains the errorMessage, Array[1] contains erroredClientCount, and Array[2] contains successfulClientCount.
        function processDetachClientMapFunc( responseMap ){

          var errorMessage = "";         // overall error message for all failed detachment clients
          var erroredClientCount = 0;    // count of clients that failed detachment
          var successfulClientCount = 0; // count of clients successfully detached

          // responseMap would contain a map for all processed clients of the Group to be detached
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
            }
          }

          // If at least one Client was successfully detached (and hence Group's Number of Clients was > 0)
          // decrement Number of Clients cell for the one Group that Detach Clients ran for
          if( successfulClientCount > 0 ){

            var selectedGroupCheckBox = $("[#groupList]input[type=checkbox]").filter(":checked").filter(":not(#selectionCheckbox)");
            var checkBoxEnclosingTd = $(selectedGroupCheckBox).parent( 'td' );
            var siblingsTds = $(checkBoxEnclosingTd).siblings();
            var lastNumberOfClientsTd = $(siblingsTds[siblingsTds.length-1]);

            var currentClientCount = parseInt( $(lastNumberOfClientsTd).text(), 10 );
            var newClientCount = currentClientCount - successfulClientCount;
            $(lastNumberOfClientsTd).replaceWith( "<td>"+newClientCount+"</td>" );
          }

          // Return results
          var resultArray = new Array(3);
          resultArray[ 0 ] = errorMessage;
          resultArray[ 1 ] = erroredClientCount;
          resultArray[ 2 ] = successfulClientCount;
          return resultArray;
        }

        function checkForDetachmentProgress( groupId ) {

          $.ajax({
              url: "${resource(dir:'')}/group/checkDetachStatus",
              type: "POST",
              data: { groupId: groupId },
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

            if ( checkForNoneSelected('No Group was selected for detachment of its Clients.') ) {

              // See detach.js for logic. Clean prev flash messages and errors
              cleanPrevFlashErrorsAndMessages();

              // grab the selected checkboxes (and only those with id=#groupList), except the selectAll checkbox
              var selectedGroupCheckBoxes = $("[#groupList]input[type=checkbox]").filter(":checked").filter(":not(#selectionCheckbox)");
              if( selectedGroupCheckBoxes && selectedGroupCheckBoxes.length > 0 ){

                if( selectedGroupCheckBoxes.length != 1 ){
                  alert("Exactly one Group should be selected for Detach Clients operation.");
                  return false;
                }
                else {

                  if( confirm('Are you sure you want to detach Clients of the selected Group ?') ){

                    // Grab the logging level which is needed for invoking actions.
                    var loggingLevel = $("#loggingLevel").val();

                    // See detach.js for logic. Passin the name of the message div.
                    showBlockUI( 'detachmentDialog' );

                    // The only one Group id
                    var groupId = $(selectedGroupCheckBoxes[0]).val();

                    // start the detachment progress timer to run every N sec
                    var timerId = setInterval( function() { checkForDetachmentProgress( groupId ) }, 5000 );

                    /* Note #1: type is POST (also configured on the controller, so if a GET is attemped an error page is returned with
                      "The specified HTTP method is not allowed for the requested resource ()" as expected as GET is not allowed.
                       Note #2: this code MUST be invoked from the .gsp and not refactored to a separate .js file as AJAX call needs ShiroSecurityManager.
                       Attempted to do that and got the "No SecurityManager accessible to the calling code, either bound to the
                       org.apache.shiro.util.ThreadContext or as a vm static singleton. This is an invalid application configuration." exception. */
                    $.ajax({
                        url: "${resource(dir:'')}/group/detach",
                        type: "POST",
                                         // The only one Group id
                        data: { groupId: groupId, loggingLevel:loggingLevel },
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
                    return false;
                  }
                }
              }
              else {
                alert("No Group was selected for detachment of its Clients.");
                return false;
              }
            }
            return false;
          });
          
        });

      </r:script>
    
    </sbauth:isBulk>

    <r:script >
      // Below is the common code for Enterprise and Lock and Release

      $(document).ready(function() {

        $("#selectionCheckbox").click(function() {
           if ( $('#selectionCheckbox').attr('checked') ) {
               checkAllBoxes("groupform");
           }
           else {
               uncheckAllBoxes("groupform");
           }
        })

        $("#deleteMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for deletion.') ) {
                 return confirm('Are you sure you want to delete the selected group(s)?');
             }
             return false;
        })

        $("#quickScanMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for quick scanning.') ) {
                 return confirm('Are you sure you want to quick scan the selected group(s)?');
             }
             return false;
        })

        $("#autoUpdateMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for AutoUpdate.') ) {
                 return confirm('An AutoUpdate request will be honored by the client(s) in the group(s) despite any Core Hour or Load Threshold settings.  Are you sure you want initiate an AutoUpdate on the clients in the group(s)?');
             }
             return false;
        })

        $("#scanMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for scanning.') ) {
                 return confirm('Are you sure you want to scan the selected group(s)?');
             }
             return false;
        })

        $("#applyMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for applying.') ) {
                 return confirm('Are you sure you want to apply the selected group(s)?');
             }
             return false;
        })

        $("#undoMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for undoing.') ) {
                 return confirm('Are you sure you want to undo the selected group(s)?');
             }
             return false;
        })

        $("#baselineMulti").click(function() {
             if ( checkForNoneSelected('No groups were selected for baselining.') ) {
                 return confirm('Are you sure you want to baseline the selected group(s)?');
             }
             return false;
        })

        $("#abortMulti").click(function() {
          if ( checkForNoneSelected('No groups were selected for action aborting.') ) {
           return confirm('Are you sure you want to abort the actions running on the selected group(s)?');lo
          }
          return false;
        })


        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( true );
      });
                                        
    </r:script>
    <title>Groups</title>
</head>
<body id="group">
  <div id="per_page_container">
    <g:form name="groupform">
      <div class="container" id="per_page_header" title="Groups">
        <div class="headerLeft">
          <h1>Groups</h1>
        </div>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <div id="actionbar_outer" class="yui-b">
        <g:render template="/group/actionbar_multi" />
      </div>

      <div id="yui-main">
        <div class="yui-b">
          <div id="main_content" class="subpage">
            <div id="table_border">
              <div id="groupList">
                <table>
                  <thead>
                    <tr>
                      <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click to select all" /></th>
                      <g:sortableColumn property="name" title="Name" />
                      <g:sortableColumn property="profile" title="Security Profile" />
                      <g:sortableColumn property="baselineProfile" title="Baseline Profile" />
                      <g:sortableColumn property="description" title="Description" />
                      <g:sortableColumn class="groupNumberOfClientsColumn" property="clients" title="Number of Clients" />
                    </tr>
                  </thead>
                  <tbody>
                  <g:if test="${groupList}">
                    <g:each in="${groupList}" status="i" var="groupInstance">
                      <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                        <td><g:checkBox name="groupList" value="${groupInstance.id}" checked="${selectedList?.contains(groupInstance.id) ? true : false }" /></td>
                        <td><g:link action="show" id="${fieldValue(bean:groupInstance,field:'id')}">${fieldValue(bean:groupInstance,field:'name')}</g:link></td>

                        <g:if test="${groupInstance.profile}">
                          <td><g:link controller="profile" action="profileBuilder" event="modify" id="${groupInstance.profile.id}">${groupInstance.profile.name}</g:link></td>
                        </g:if>
                        <g:else>
                          <td>none</td>
                        </g:else>

                        <g:if test="${groupInstance.baselineProfile}">
                          <td><g:link controller="baselineProfile" action="show" id="${groupInstance.baselineProfile.id}">${groupInstance.baselineProfile.name}</g:link></td>
                        </g:if>
                        <g:else>
                          <td>none</td>
                        </g:else>

                        <td>${fieldValue(bean:groupInstance,field:'description')}</td>
                        <td class="groupNumberOfClientsColumn">${groupInstance.clients ? groupInstance.clients.size() : 0}</td>
                      </tr>
                    </g:each>
                  </g:if>
                  <g:else>
                    <tr class="row_even">
                      <td style="text-align:center;" colspan="6">No groups currently exist.</td>
                    </tr>
                  </g:else>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="paginateButtons" style="margin: 1%;">
              <g:paginate prev="&laquo; previous" next="next &raquo;" max="${maxPerPage}" total="${totalCount}" />
            </div>
          </div>
        </div>
      </div>
    </g:form>
  </div>

  <!-- Detachment progress dialog -->
  <g:render template="/client/detachmentProgressDialog" />

</body>
</html>
