/*
 * Copyright 2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

// File containing all JavaScript logic for the detach operation.
// Note 1: The caller html must include json2.js (in addition to including this file), which is used to handle json on older browsers
// (IE 6, 7, and 8 without a patch) who do not have json in their JavaScript engine. Newer, browsers have json as part of the
// JavaScript engine, and they would *not* use json2.js, but instead use json version within their JavaScript engine.
// ***** NOTE : there is also a jQuery-json plugin which is probably the correct way to go                                                        ******
// ***** See http://code.google.com/p/jquery-json/ for jQuery-json plugin and http://www.grails.org/plugin/jquery-json for a Grails plugin for it *****
// Note 2: The caller html must have a div with id=messageDivName (which is passed to showBlockUI() function) which represents
// what will be shown in the blockUI lightbox.

/**
 * Function clears out previously set flash errors and messages. Gets invoked every time detach
 * button is clicked (mimicing the behavior of actions going through the controller).
 */
function cleanPrevFlashErrorsAndMessages(){
  
    /* if mainBodyDiv contains an error div (error from prev run of detach of prev errors from other actions) OR
    message div and the error div remove it (them). This is needed due to the fact that detach is an Ajax call
    (no call to the server to refresh the page and clear out flashMessageDiv and flashErrorDiv) hence instead
    have to do it here manually here to have no messages and no errors (so new errors from detach will be the first child of mainBodyDiv). */
    var mainBodyDiv = $("#bd");
    var firstChildDiv = mainBodyDiv.children('div:first');
    if( firstChildDiv ){
        // First child is flashErrorDiv (no flashMessageDiv), so just remove flashErrorDiv div
        if( firstChildDiv.attr( 'id' ) == "flashErrorDiv" ){
            firstChildDiv.remove();
        }
        // First child is flashMessageDiv remove it and check if next child is flashErrorDiv, and if there then also remove it as well
        else if( firstChildDiv.attr( 'id' ) == "flashMessageDiv" ){
            // remove flashMessageDiv
            firstChildDiv.remove();

            firstChildDiv = mainBodyDiv.children('div:first');
            // if found flashErrorDiv, remove it as well
            if( firstChildDiv.attr( 'id' ) == "flashErrorDiv" ){
                firstChildDiv.remove();
            }
        }
    }
}

// Shows the blockUI lightbox containing a div with id=messageDivName that the calling page *must* contain and define.
// @param messageDivName - the name of the div for the message (dialog containing the blockUI lightbox)
function showBlockUI( messageDivName ){
    
    // Block the UI -- i.e. show the blockUI lightbox
                                                                                                             // Might want to remove applyPlatformOpacityRules, this is to allow overlay in FFX
    $.blockUI( { message: $( '#'+ messageDivName ), css: { width:'475px', height:'300px', overflow:'auto' }, applyPlatformOpacityRules: false } );
}

// Hides the blockUI lightbox
function hideBlockUI(){
    $.unblockUI();
}

/**
 * Note: when other places (other than this file) will use this method, move it to tcs/common.js
 *
 * xhr    - the AJAX XmlHttpRequest object
 * status - the status of the AJAX call from $.ajax() call using jQuery
 * action - String signifying which action is this (only used for an error case)
 *
 * Parses the XmlHttpRequest responseText which is assumed to be in a JSON format and return an errorMessage
 * and a responseMap which is a JavaScript object containing {key, value} pairs parsed from JSON.
 *
 * Depends on JSON.parse hence needs json2.js be included.
 */
function parseAjaxResponse( xhr, status, action ){

    var errorMessage = "";
    var responseMap;

    if( status == "success" ){

        try {
            responseMap = JSON.parse( xhr.responseText );
        }
        catch( exception ){
            responseMap = null;
            errorMessage = exception + "";
        }
    }
    else {
        errorMessage = action + " failed. "
        if( xhr.responseText ){
            errorMessage = errorMessage + xhr.responseText;
        }
        else {
            errorMessage = errorMessage + "Please make sure the Console is running."
        }
    }

    var resultArray = new Array(2);
    resultArray[ 0 ] = errorMessage;
    resultArray[ 1 ] = responseMap;
    return resultArray;
}

// Post-processes the AJAX detach call by :
// 1. doing common error/exception handling (which might include changing the window location to an error page if user
//      is not authorized to do the action or their license expired in the middle of the action (such as might happen for Detach operation)
// 2. delegating the actual processing of the detach call to Function processDetachClientMapFunc (which is page specific) and passed by the caller
// 3. displaying success/failure into the flash message and error
// 4. hiding the blockUI lightbox
function postProcessDetach( xhr, status, processDetachClientMapFunc ){

    // If get an unauthorized or licenseExpired special String then checkAjaxResponseForValidity() redirects to the approprtiate
    // error page so don't bother processing the AJAX response by returning from this method.
    if( ! checkAjaxResponseForValidity( xhr ) ){
        return;
    }

    // Parse the result of the ajax call
    var resultOfAjaxResponse = parseAjaxResponse( xhr, status, "Detach" );
    var errorMessage = resultOfAjaxResponse[ 0 ];
    var responseMap  = resultOfAjaxResponse[ 1 ];
    var erroredClientCount = 0;
    var successfulClientCount = 0;

    // Ajax call returned a success and with at least one client.
    if( responseMap && errorMessage.length == 0 ){
        // Method processDetachClientMapFunc accepts the map and returns an Array[2].
        var resultOfFuncCall = processDetachClientMapFunc( responseMap );
        errorMessage          = resultOfFuncCall[0];
        erroredClientCount    = resultOfFuncCall[1];
        successfulClientCount = resultOfFuncCall[2];
    }

    // If at there was at least one success, show success *count* in flashMessageDiv.
    var successMessageDivHtml = ( successfulClientCount == 0 ) ? "" :
        "<div class=\"flashMessage\" id=\"flashMessageDiv\">" + successfulClientCount + " Client" +
        (( successfulClientCount > 1 ) ? "s were" : " was" ) + " successfully detached.</div>";


    // If there was at least one failure, show *each failure* in flashErrorDiv. Show up to 10 entries as is,
    // but if there are >=11 entries (i.e. either 11 failures or at least 1 success and at least 10 failures) show vertical scrollbar.
    var needToShowErrorVerticalScrollBar = false;
    if( erroredClientCount >= 11 || ( successfulClientCount > 0 && erroredClientCount >= 10 ) ){
        needToShowErrorVerticalScrollBar = true;
    }
    var failureErrorDivHtml = ( errorMessage.length == 0 ) ? "" :
        "<div " + ( needToShowErrorVerticalScrollBar ? "style=\"overflow:auto;height:180px\" " : "" ) +
            "class=\"flashError\" id=\"flashErrorDiv\">" + errorMessage + "</div>";

    /* Main Body Div. Add success message div or a failure error div based accordingly. At the very beginning of this callback method
    the flashMessageDiv and flashErrorDiv were removed from mainBodyDiv, ensuring that at this point it doesn't have either and
    that whatever is added below is THE VERY FIRST CHILD(REN) OF mainBodyDiv. */
    var mainBodyDiv = $("#bd");

    var completionMessage = "Detachment completed";

    // All clients were detached successfully (there was no errorMessage)
    if( successMessageDivHtml.length > 0 && failureErrorDivHtml.length == 0 ){
        $(mainBodyDiv).prepend( successMessageDivHtml );

        completionMessage = completionMessage + " successfully for " + successfulClientCount + " Client(s)."
    }
    // All clients failed detachments (successfulClientCount == 0)
    else if( successMessageDivHtml.length == 0 && failureErrorDivHtml.length > 0 ){
        $(mainBodyDiv).prepend( failureErrorDivHtml );

        completionMessage = completionMessage + " with failures."
    }
    /* There is a mix : at least one client successfully detached and at least one client had errors. Insert success message div
    followed by a failure error div as children of mainBodyDiv; since using prepand() do in reverse order (prepand error, then message divs) */
    else {
        $(mainBodyDiv).prepend( failureErrorDivHtml );
        $(mainBodyDiv).prepend( successMessageDivHtml );

        completionMessage = completionMessage + " successfully for " + successfulClientCount + " Client(s) and with failures for the rest."
    }

    if( failureErrorDivHtml.length > 0 ){
        completionMessage = completionMessage + " Please consult the error bar at the top of the page."
    }
   
    // Completion message to be displayed inside detachProgressMessage
    completionMessage = completionMessage + " Please press Close button to close this dialog."
    $("#detachProgressMessage").replaceWith(
        '<div style="text-align:left;vertical-align:middle;margin:10px;" id="detachProgressMessage">' + completionMessage + '</div>' );

    var detachButton = $("#detachAbort");

    // If detachButton was disabled (such as after Stopping Detach, make it enabled again for the OK button
    if( $(detachButton).text() == "Stopping Detach ..." /* && $(detachButton).attr( "disabled" ) == "true" */ ){
        $(detachButton).removeAttr("disabled");
    }

    // Change the text on the Stop Detachment button to Close
    $(detachButton).text( "Close" );
    $(detachButton).css( { 'margin-bottom':'10px;', 'margin-top':'20px' } );

    // Hide the progress icon
    $("#detachProgressIcon").hide();

    // Hide the warning message as
    $("#detachWarningMessage").hide();

    // Reduce the height of the whole dialog window down to 130px
    $("#detachmentDialog").parent().css( 'height', '130px' );
}

// Post-processes the AJAX checkDetachStatus call by :
// 1. doing common error/exception handling
// 2. displaying returned status map in the progress div of the progress dialog in a consistent fashion
function postProcessCheckDetachmentProgress( xhr, status ){

    // Note: don't need to call checkAjaxResponseForValidity() here, since if detach opeation is
    // in progress don't want to terminate it here. If detach is not in progress, the timer
    // SecurityFilters catches that and sends in a predefined error Strings ending the detach Ajax request
    // and stopping the timer that calls this method.

    // Parse the result of the ajax call
    var resultOfAjaxResponse = parseAjaxResponse( xhr, status, "Checking detach progress" );
    var errorMessage = resultOfAjaxResponse[ 0 ];
    var responseMap  = resultOfAjaxResponse[ 1 ];

    var statusProgressString = "";

    // Ajax call returned a success and with at least one client.
    if( responseMap && errorMessage.length == 0 ){

        // key=Client name, value=message to display (either just phaseName (success) or phaseName had an error [actualErrorMessage]
        var counter = 1;
        var key;
        for ( key in responseMap ) {
            var valueString = responseMap[key];
                                                                  // Note adding 2 breaks to separate errors between clients
            statusProgressString = statusProgressString + "<b>" + counter + ". " + key + "</b> - " +valueString+"<br><br>";

            counter++;
        }
    }
    else {
        // There was an error, display it
        statusProgressString = errorMessage
    }

    var detachmentProgressMessage = '<div style="text-align:left;vertical-align:middle;margin:10px;" id="detachProgressMessage">' +
        statusProgressString + '</div>';
    $("#detachProgressMessage").replaceWith( detachmentProgressMessage );
}

