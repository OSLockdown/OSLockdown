/*
 * Copyright 2009-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * Function toggles the visiblity of an element based on the id passed
 * @param {String} the id of the element that is to be toggled
 * will be sent.
 */
function showHideElement(id) 
{
	$("#"+id).toggle();
}

/**
 * Checks all checkboxes that have the prefix of the id passed as a parameter
 * @param id the prefix of the checkboxes ids
 * @return
 */
function checkAll(id) {				
	$("input[id^='"+id+"']").attr('checked', true);
}

/**
 * Unchecks all checkboxes that have the prefix of the id passed as a parameter
 * @param id the prefix of the checkboxes ids
 * @return
 */
function uncheckAll(id) {				
	$("input[id^='"+id+"']").attr('checked', false);
}
 
/**
 * Disables all input possibilities on the screen
 * @return
 */
function disableAll() {
   	$("input").each(function(i) {  this.disabled = true;  } );
   	$("textarea").each(function(i) {  this.disabled = true;  } );
   	$("select").each(function(i) {  this.disabled = true;  } );
}

function selectAll(formName) {
	alert(formName);
    if ( $('#selectionCheckbox').attr('checked') )
    {
  	  checkAllBoxes(formName);
    }    		              
    else
    {
  	  uncheckAllBoxes(formName);
    }
}

function checkForNoneSelected(alertText) {   	
   	if ( $(":checkbox:checked").length == 0 ) {
   	    alert(alertText);
   	    return false;
   	}   	
   	return true;
}

function limitText(limitField, limitNum) {
	if (limitField.value.length > limitNum) {
		limitField.value = limitField.value.substring(0, limitNum);
	} 
}

/**
 * xhr is the XmlHttpRequest object used for the Ajax call.
 * 
 * - Returns true for a successful xhr.responseText.
 * - Returns false if xhr.responseText contains either "Unauthorized" OR "ExpiredLicense" strings that signify that user was not
 *  authorized to perform this Ajax action OR license expired while the (long-running) Ajax action has been running (such as
 *  a Detach operation that could be very lengthy), respectively; also in either of these cases this method changes the browser
 *  location (which is comparable to a redirect in a non-Ajax call) to either /auth/unauthorized or /auth/expiredLicense
 */
function checkAjaxResponseForValidity( xhr ){

    var returnValue = true;

    if( xhr ){

        var responseText = xhr.responseText;
        if( responseText == "unauthorized" || responseText == "expiredLicense" ){
            
            var actionToRedirectTo;
            if( responseText == "unauthorized" ){
                actionToRedirectTo = "/auth/unauthorized";
            }
            else {
                actionToRedirectTo = "/auth/expiredLicense";
            }

            // location looks like this https://localhost:8443/OSLockdown/client/show/12
            // Need to redirect to https://localhost:8443/OSLockdown /auth/unauthorized or /auth/expiredLicense.
            var newLocation = location + "";

            // DO NOT assume /OSLockdown since with url redirecting it might be something else (like /sb or /foo)
            // but rather calculate it as the string value between the first 2 forward slashes (after initial https:// or http://)
            //  var indexOfOSLockdown = newLocation.lastIndexOf( "/OSLockdown" );
            //
            // index of // -- works for both https and http
            var indexOfDoubleSlashes = newLocation.indexOf( "//" );
            // index of first / after https:// or http://
            var startingIndexOfFirstRealSlash = indexOfDoubleSlashes + 2;
            var indexOfFirstRealSlash = newLocation.indexOf( "/", startingIndexOfFirstRealSlash );
            // index of second / after https:// or http://
            var startingIndexOfSecondRealSlash = indexOfFirstRealSlash + 1;
            var indexOfSecondRealSlash = newLocation.indexOf( "/", startingIndexOfSecondRealSlash );

            var newURL = newLocation.substring( 0, indexOfSecondRealSlash ) + actionToRedirectTo;

            // If there was anything on the url after the https://localhost:8443/OSLockdown,
            // include it in the targetUri parameter
            var leftOverURLAndParameterString = newLocation.substring( indexOfSecondRealSlash );
            if( leftOverURLAndParameterString && leftOverURLAndParameterString.length > 0 ){

                // I don't think that need to url-encode leftOverURLAndParameterString with encodeURIComponent()
                // but could if this does not work (see http://www.javascripter.net/faq/escape.htm).
                newURL = newURL + "/?targetUri=" + leftOverURLAndParameterString;
            }

            // Actually replace the browser window to newURL
            window.location.replace( newURL );

            // Set to false to indicate user was not authorized or their license have expired.
            returnValue = false;
        }
    }
    return returnValue;
}

/**
 * Only applies to column headers which are configured as sorteable through Grails (ie. setup
 * with < g : sortableColumn and hence have class=sortable on them.
 *
 * If there are no user sorted column headers, then make the very first column header sorted
 * by adding "sorted asc" classes to it and setting the desc sort on the anchor which is 1st child of header.
 * @param ascOrDesc - if ascOrDesc==true then the default sort will be asc, else then the default sort will be desc
 */
function markFirstColumnAsSortedIfNotUserSorted( ascOrDesc ){

    if( $(".sorted").length == 0 ){
      // If there are no user-sortable columns, then

      // 1.show sorted asc indicator for the Name column (which is the very first column)
      var firstTh = $(".sortable")[0];

      if( ascOrDesc ){

          $(firstTh).addClass( "sorted asc" );

          // 2. change the href in the anchor (which is th's only child) to do a desc sort upon next sort (click on header)
          var anchor = $(firstTh).children(":nth-child(1)");
          var hrefAttr = anchor.attr( 'href' );
          hrefAttr = hrefAttr.replace('asc','desc');
          anchor.attr( 'href', hrefAttr );
      }
      else {
          $(firstTh).addClass( "sorted desc" );

          // No need to change the href in the anchor as it's already set up to do asc by default
      }
    }
}

/**
 *  Given a table, zebra strip the elements therein, where each stripable row has a zebra class
 */
 function zebraStripTable( table) {
//        alert ("striping "+ table + " " + $(".stripe",table).size());
        $(".stripe",table).each (function (foo, bar) { 
            if( (foo % 2 ) != 0 ) {
                $(bar).addClass("row_odd") ;
            } else {
                $(bar).addClass("row_even") ;
            }
        });       
 }
 
function checkAllBoxes(objectName)
{
  console.log("checkAllBoxes called for "+objectName);
  $("#" + objectName + " input[type=checkbox]").prop('checked', true);
}

function uncheckAllBoxes(objectName)
{
  console.log("uncheckAllBoxes called for "+objectName);
  $("#" + objectName + " input[type=checkbox]").prop('checked', false);
}

