<%@ page import="com.trustedcs.sb.web.pojo.Client" %>
<%@ page import="com.trustedcs.sb.web.pojo.ClientInfo" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />

    <title>Client Details</title>

    <r:require modules="application"/>
    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="viewing-client"/>
    </sbauth:isEnterprise>

    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="viewing-client-su"/>

      <r:require modules="showedit"/>
      <r:script >

        // Function which is used by the detach.js to process the result of the Ajax detach call.
        // Returns Array[3] , where Array[0] contains the errorMessage, Array[1] contains erroredClientCount, and Array[2] contains successfulClientCount.
        function processDetachClientMapFunc( responseMap ){

          var errorMessage = "";         // overall error message for all failed detachment clients
          var erroredClientCount = 0;    // count of clients that failed detachment
          var successfulClientCount = 0; // count of clients successfully detached

          // responseMap should contain just one {key,value} pair with key being the clientId
          var valueString = responseMap[ ${clientInstance.id}+"" ];

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

            // 1. Remove the Detach li in the Client actions area
            $('.detach').parent('li').remove();

            // 2. Remove the Entire Actions + Logging Level divs
            // allActionsDivs[0]=Client, allActionsDivs[1]=Actions, allActionsDivs[2]=Logging Level, allActionsDivs[3]=Reports
            var allActionsDivs = $('div.actions', $('#actionbar') );
            if( $(allActionsDivs).length == 4 ){
              $(allActionsDivs[1]).remove();
              $(allActionsDivs[2]).remove();
            }

            var inputButtons = $('button.btninput');
            var buttonsRow =  $(inputButtons[0]).parent('td').parent('tr');

            //
            // 3.  a. Insert (or refresh) the Details, as the Client.info (as map of all client detail properties) was included in the responseMap
            // and b. rename the "Details" header div to "Details at Detachment"
            //
            if( responseMap[ "${ClientInfo.CLIENT_VERSION}" ] ){

              // a. Insert (or refresh) the Details
              var clientDetailsRow = $(buttonsRow).siblings()[0];
              // Remove the 2nd td (for Dispatcher Status)
              $(clientDetailsRow).children(":nth-child(2)").remove();
              // 1st TD actually containing the clients details
              var clientDetailsTd = $(clientDetailsRow).children(":nth-child(1)");
              // Clear the style (border-right and width). This should remove style="border-right: 1px solid black; width: 50%;"
              $(clientDetailsTd).css( 'border-right', '' );
              $(clientDetailsTd).css( 'width', '' );
              // Descendent TDs, where TDs at even indecies are TD of the label, and TDs at odd indecies are TDs containing the actual respective cell values.
              // Replace odd TD (actual values) with those obtained from the clientInfo passed in.
              var tdDescendentsActualClientDetails = $(clientDetailsTd).find( "td" );
              $( $(tdDescendentsActualClientDetails)[1] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.CLIENT_VERSION}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[3] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.NODE_NAME}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[5] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.DISTRIBUTION}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[7] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.KERNEL}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[9] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.UPTIME}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[11] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.ARCHITECTURE}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[13] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.LOAD_AVERAGE}" ] + "</td>" );
              $( $(tdDescendentsActualClientDetails)[15] ).replaceWith( "<td valign='top' class='value'>" + responseMap[ "${ClientInfo.MEMORY}" ] + "</td>" );

              // b. rename the "Details" header div to "Details at Detachment"
              // $(clientDetailsRow).closest( '#statusDiv div' ) did not work, but losest( 'div' ) worked.
              var statusDiv = $(clientDetailsRow).closest( 'div' );
              var detailsHeaderDiv = $(statusDiv).siblings()[0];
              // 1st child of detailsHeaderDiv is h2 which is changed to be appended 'at Detachment'
              var detailsH2 = $(detailsHeaderDiv).children(":nth-child(1)");
              $(detailsH2).replaceWith( "<h2>Details at Detachment</h2>" );
            }

            // 4. Remove the whole row with Refresh Details and Refresh Dispatcher Status
            if( $(inputButtons).length == 2 ){
              $(buttonsRow).remove();
            }

            //
            // 5. Set Detached date
            //
            var lastAddedSiblingTrs = $('td.clientLastAddedDate').parent().siblings();
            var groupTr             = $(lastAddedSiblingTrs[2]);
            var secProfileTr        = $(lastAddedSiblingTrs[3]);
            var basProfileTr        = $(lastAddedSiblingTrs[4]);
            var lastDetachedTr      = $(lastAddedSiblingTrs[lastAddedSiblingTrs.length-1]);

            // Could also do this which is crugy (nth-child(2) selects 2nd child, and is 1-based)
            //    $($(lastDetachedTr).children()[1]).replaceWith( "<td>" + valueString + "</td>" );
            $(lastDetachedTr).children(":nth-child(2)").replaceWith( "<td>" + valueString + "</td>" );

            // 6. Add new rows for : a. Group at Detachment=Group value (not a link), b. Security Profile at Detachment=Sec Prof value (not a link)
            // and c. Baseline Profile at Detachment=Bas Prof value (not a link)

            // Html template which is searched and replaced below to replace 3 occurrences of LABEL, and 1 occurrence of VALUE.
            // LABEL is the XXX At Detachment, and VALUE is the name of the Group/Sec or Bas/Profile.
            var newRowHTMLTemplate =
              '<tr class="prop"><td valign="top" class="propName" title="LABEL"><label for="LABEL">LABEL:</label></td><td valign="top">VALUE</td></tr>';

            var groupAtDetachmentName = $(groupTr).children(":nth-child(2)").children(":nth-child(1)").text();
            var groupAtDetachmentRowHTML = newRowHTMLTemplate.replace( /LABEL/g, "Group at Detachment" );
            groupAtDetachmentRowHTML = groupAtDetachmentRowHTML.replace( "VALUE", groupAtDetachmentName );

            var secProfileAtDetachmentName = $(secProfileTr).children(":nth-child(2)").children(":nth-child(1)").text();
            var secProfileAtDetachmentRowHTML = newRowHTMLTemplate.replace( /LABEL/g, "Security Profile at Detachment" );
            secProfileAtDetachmentRowHTML = secProfileAtDetachmentRowHTML.replace( "VALUE", secProfileAtDetachmentName );

            var basProfileAtDetachmentName = $(basProfileTr).children(":nth-child(2)").children(":nth-child(1)").text();
            var basProfileAtDetachmentRowHTML = newRowHTMLTemplate.replace( /LABEL/g, "Baseline Profile at Detachment" );
            basProfileAtDetachmentRowHTML = basProfileAtDetachmentRowHTML.replace( "VALUE", basProfileAtDetachmentName );

            // Finally update the DOM by appending the new 3 rows at the bottom of the table for Group Sec Profile and Baseline Profile at detachment
            $(lastDetachedTr).parent().append( groupAtDetachmentRowHTML + secProfileAtDetachmentRowHTML + basProfileAtDetachmentRowHTML );

            // 7. Change Group/SecProfile/BasProfile from link to Unassociated text
            $(groupTr).children(":nth-child(2)").replaceWith( "<td>Unassociated</td>" );
            $(secProfileTr).children(":nth-child(2)").replaceWith( "<td>Unassociated</td>" );
            $(basProfileTr).children(":nth-child(2)").replaceWith( "<td>Unassociated</td>" );
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

          $('.detach').click(function() {

            if( confirm('Are you sure you want to detach this client?') ){

              // See detach.js for logic. Clean prev flash messages and errors
              cleanPrevFlashErrorsAndMessages();

              // Grab the logging level which is needed for invoking actions.
              var loggingLevel = $("#loggingLevel").val();

              // See detach.js for logic. Passin the name of the message div.
              showBlockUI( 'detachmentDialog' );

              var clientIdListStringified = "["+${clientInstance.id}+"]";

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
                  data: { clientIdList: clientIdListStringified, loggingLevel:loggingLevel, fromClientShow: true },
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

      function updateInfo() {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest( "${resource(dir:'')}/client/updateClientInfo" );
        ajaxRequest.addNameValuePair('clientId',${clientInstance?.id});
        //Send the request
        ajaxRequest.sendRequest();
      }

      function updateStatus() {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest( "${resource(dir:'')}/client/updateClientStatus" );
        ajaxRequest.addNameValuePair('clientId',${clientInstance?.id});
        //Send the request
        ajaxRequest.sendRequest();
      }
		                                      
    </r:script>
  
  </head>
  <body id="client">
    <div id="per_page_container">

      <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
      <div class="container" id="per_page_header" title="Client Details">
        <div class="headerLeft">
          <h1>Client Details</h1>
        </div>
        <div class="headerRight">
          <g:link class="btn btn_blue" controller="client" action="list" event="back" title="Click to go Back">&laquo; Back</g:link>
        </div>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <div id="actionbar_outer" class="yui-b">
        <g:render template="/client/actionbar" />
      </div>

      <!-- MAIN PAGE CONTENT, requires two divs for YUI Grids -->
      <div id="yui-main">
        <div id="main_content" class="yui-b">

          <!-- ********************************************************** -->
          <!-- CLIENT DETAILS -->
          <!-- ********************************************************** -->
          <div id="clientdetails" class="subpage">
            <g:form method="post" >
              <input type="hidden" name="id" value="${clientInstance?.id}" />
              <input type="hidden" name="version" value="${clientInstance?.version}" />              
              <div class="info">
                <div class="info_header" title="Configuration">
                  <h2>Configuration</h2>
                </div>
                <div class="info_body">
                  <g:render template="display" />
                </div>
              </div>
            </g:form>
            <g:render template="/client/details"/>            
          </div><!-- subpage -->
        </div><!-- yui-b -->
      </div><!-- main_content -->
    </div><!-- per_page_container -->

    <!-- Detachment progress dialog -->
    <g:render template="/client/detachmentProgressDialog" />

  </body>
</html>
