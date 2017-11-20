<%@ page import="com.trustedcs.sb.web.pojo.Client" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />

    <r:require modules="application"/>
    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="edit-group"/>
    </sbauth:isEnterprise>

    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="edit-group-su"/>
      <r:require modules="showedit"/>
      <r:script >

        // Function which is used by the detach.js to process the result of the Ajax detach call.
        // Returns Array[3] , where Array[0] contains the errorMessage, Array[1] contains erroredClientCount, and Array[2] contains successfulClientCount.
        function processDetachClientMapFunc( responseMap ){

          var errorMessage = "";         // overall error message for all failed detachment clients
          var erroredClientCount = 0;    // count of clients that failed detachment
          var successfulClientCount = 0; // count of clients successfully detached

          var detachedClientIdArray   = [];

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

              // Store clientId (as a String) in an array
              detachedClientIdArray.push( key );
            }
          }

          var detailsClientsValueTd = $("#groupDetails table tr:last").children(":nth-child(2)");
          var groupClientsDiv       = $("#groupClients");

          // All Clients of the Group were successfully detached
          if( errorMessage.length == 0 && successfulClientCount > 0 ){

            // 1. Remove the Detach Clients li in the Client actions area
            $('.detach').parent('li').remove();

            // 2. In the Details section change Clients from a number > 0 to None
            detailsClientsValueTd.replaceWith( "<td>None</td>" );

            // 3. In the Group Clients section remove all of the Clients (divs) and replace them with <h2>No clients are associated with this group</h2>
            $(groupClientsDiv).children().remove();
            $(groupClientsDiv).append( "<h2>No clients are associated with this group</h2>" );
          }
          else { // There was an error and 0 or more successes
            // Leave the Detach Clients button (i.e. don't remove it)

            if( successfulClientCount > 0 ){

              // 1. In the Details section decrement Clients by successfulClientCount (if any)
              // groupInstance.clients.size() OR Client: value in the td is guaranteed to be > 0, as otherwise Detach Clients button wouldn't show
              // Could do $ { groupInstance.clients.size() }, however, it is still the value before the Detach was done and is the same
              // as displayed in the td, so just grab from the td.
              var currentClientCount = parseInt( $(detailsClientsValueTd).text(), 10 );
              var newClientCount = currentClientCount - successfulClientCount;
              detailsClientsValueTd.replaceWith( "<td>"+newClientCount+"</td>" );

              // 2. Remove the Clients (divs) that were successfully detached from the Group Clients
              $(groupClientsDiv).children().each( function(){

                // Anchor with an href is the first (and only child) of each Client div
                var hrefAttr = $(this).children(":nth-child(1)").attr('href');

                //                                         clientId extraced from the href
                var clientIdFromHref = hrefAttr.substring( hrefAttr.lastIndexOf( "/" ) + 1 );

                // if clientIdFromHref was successfully detached then delete this div
                if( $.inArray( clientIdFromHref, detachedClientIdArray ) != -1 ){
                  $(this).remove();
                }
              });
            }
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

          // Only happens for the Single use case (i.e. when Detach Clients button is visible).
          $('.detach').click(function() {

            if( confirm('Are you sure you want to detach Clients of this Group?') ){

              // See detach.js for logic. Clean prev flash messages and errors
              cleanPrevFlashErrorsAndMessages();

              // Grab the logging level which is needed for invoking actions.
              var loggingLevel = $("#loggingLevel").val();

              // See detach.js for logic. Passin the name of the message div.
              showBlockUI( 'detachmentDialog' );

              // The only one Group id
              var groupId = ${groupInstance.id};

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
          });

        });

      </r:script>
    
    </sbauth:isBulk>

    <r:script >
      // Below is the common code for Enterprise and Lock and Release

      $(document).ready(function() {

        // TODO: Move to common JS file and include
        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");

      });

    </r:script>
  
    <title>Show > ${fieldValue(bean:groupInstance,field:'name')}</title>    
  </head>
  <body id="group">
    <div class="container" id="per_page_container">
        <div class="container" id="per_page_header" title="${ params.id ? 'Edit Group' : 'New Group' }">
          <div class="headerLeft">
            <h1>Show > ${fieldValue(bean:groupInstance,field:'name')}</h1>
          </div>
          <div class="headerRight">
          </div>
        </div>
        <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
        <div id="actionbar_outer" class="yui-b">
          <g:render template="/group/actionbar" />
        </div>
        <div id="yui-main">
          <div id="main_content" class="yui-b">
            <div class="subpage">
              <g:hiddenField name="id" value="${fieldValue(bean:groupInstance,field:'id')}" />
              <div style="width:70%;"class="info centerDiv">
                <div class="info_body">
                  <fieldset>
                    <legend>Details</legend>
                    <div id="groupDetails">
                      <table>
                        <tr>
                          <td class="clientName" style="height: 40px; vertical-alignment: bottom;" title="Name"><label for="Name">Name:</label></td>
                          <td>${fieldValue(bean:groupInstance,field:'name')}</td>
                        </tr>
                        <tr>
                          <td class="clientName" title="Description"><label for="Description">Description:</label></td>
                          <td>${fieldValue(bean:groupInstance,field:'description')}</td>
                        </tr>
                        <tr style="height: 32px;">
                          <td class="clientName" title="Security Profile"><label for="Security Profile">Security Profile:</label></td>
                          <g:if test="${groupInstance.profile}">
                            <td><g:link title="Groups's associated security profile." controller="profile" action="profileBuilder" event="start" class="profiles" id="${groupInstance.profile.id}">${groupInstance.profile.name}</g:link></td>
                          </g:if>
                          <g:else>
                            <td>Unassociated</td>
                          </g:else>
                        </tr>
                        <tr style="height: 32px;">
                          <td class="clientName" title="Baseline Profile"><label for="Baseline Profile">Baseline Profile:</label></td>
                          <g:if test="${groupInstance.baselineProfile}">
                            <td><g:link title="Groups's associated baseline profile." controller="baselineProfile" action="show" id="${groupInstance.baselineProfile.id}">${groupInstance.baselineProfile.name}</g:link></td>
                          </g:if>
                          <g:else>
                            <td>Unassociated</td>
                          </g:else>
                        </tr>
                        <tr style="height: 32px;">
                          <td class="clientName" title="Clients"><label for="Clients">Clients:</label></td>
                          <td title="Number of Clients">${groupInstance?.clients ? groupInstance?.clients.size() : 'None'}</td>
                        </tr>
                      </table>
                    </div>
                  </fieldset>
                  <fieldset>
                    <legend>Group Clients</legend>
                    <div id="groupClients" style="height:12em;overflow:auto;" class="info_body">
                      <g:if test="${groupInstance.clients}">
                        <g:each in="${groupInstance.clients}" status="i" var="clientInstance">
                          <div class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                            <g:link controller="client" action="show" id="${fieldValue(bean:clientInstance,field:'id')}">${fieldValue(bean:clientInstance,field:'name')}</g:link>
                          </div>
                        </g:each>
                      </g:if>
                      <g:else>
                        <h2>No clients are associated with this group</h2>
                      </g:else>
                    </div>
                  </fieldset>

                  <!-- Groups tab is visible for Enterprise and Bulk (not visible for Standalone). However, since the -->
                  <!-- Scheduler is hidden in Bulk mode, only show Group Scheduled Tasks for the Enterprise mode, and hide for Bulk -->
                  <sbauth:isEnterprise>
                    <fieldset>
                      <legend>Group Tasks</legend>
                      <div style="height:8em;overflow:auto;" class="info_body">
                        <g:if test="${groupInstance.tasks}">
                          <g:each in="${groupInstance.tasks}" status="i" var="scheduledTask">
                            <div class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                              <g:link controller="scheduledTask" action="edit" id="${fieldValue(bean:scheduledTask,field:'id')}">${scheduledTask.verboseDescription}</g:link>
                            </div>
                          </g:each>
                        </g:if>
                        <g:else>
                          <h2>No tasks are associated with this group</h2>
                        </g:else>
                      </div>
                    </fieldset>
                  </sbauth:isEnterprise>

                </div>
              </div>              
            </div>
          </div>
        </div>
    </div>

    <!-- Detachment progress dialog -->
    <g:render template="/client/detachmentProgressDialog" />

  </body>
</html>
