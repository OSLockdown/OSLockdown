/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
var descriptionsOpened = false;
var optionsOpened = false;

function dependencyCheck(id) {
    if ( $('input[name="module.selected.'+id+'"]').is(':checked') ) {
        // create the ajax request
        var ajaxRequest = new AjaxRequest('dependencyCheck');
        // add the module id to the request
        ajaxRequest.addNameValuePair('moduleId',id);
        // send the request
        ajaxRequest.sendRequest();
    }
}

function toggleModuleOptions() {
    if ( optionsOpened ) {
        $('tr[id^="display_module_options_"]').hide();
    }
    else {
        $('tr[id^="display_module_options_"]').show();
    }
    optionsOpened = !optionsOpened;
}

function toggleSelectedModuleOptions(id) {	
    $("tr[id='display_module_options_"+id+"']").toggle();
}

function toggleModuleDescriptions() {	
    if ( descriptionsOpened ) {
    	$('tr[id^="display_module_info_"]').hide();                	
    }
    else {
    	$('tr[id^="display_module_info_"]').show();                	
    }    
    descriptionsOpened = !descriptionsOpened;
}

