<html>
  <g:set var="isNew" value="${ profile?.id ? false : true }"/>
  <g:set var="isSystem" value="${profile?.writeProtected }" />
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="adding-module-to-sec-profile" />
    <title>
      <g:if test="${isNew}" >
            Create Profile > ${ profile.name ? profile.name : "Unspecified" } > Add/Remove Modules
    </g:if>
    <g:else>
      Edit Profile > ${profile?.name} > Add/Remove Modules
    </g:else>
  </title>
  <r:require modules="application,tcs_sbmodules"/>
  <r:script>

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

    $(document).ready(function() {
      $("#selectionCheckbox").click(function() {
	if ( $('#selectionCheckbox').attr('checked') ) {
          checkAllBoxes("profileBuilder");
        }
        else {
          uncheckAllBoxes("profileBuilder");
        }
      })
    });
  </r:script>
</head>
<body id="profiles">
  <div id="per_page_container">
    <g:form name="profileBuilder" action="profileBuilder">
      <div class="container" id="per_page_header" title="Edit Profile">
        <div class="headerLeft">
          <h1>
            <g:if test="${isNew}" >
              Create Profile > ${ profile.name ? profile.name : "Unspecified" } > Add/Remove Modules
          </g:if>
          <g:else>
              Edit Profile > ${profile?.name} > Add/Remove Modules
          </g:else>
        </h1>
      </div>
      <div class="headerRight">
        <g:submitButton class="btninput btninput_blue" name="back" value="\u00AB Back" title="Click to go Back" />
        <g:submitButton class="btninput btninput_blue" name="save" value="Save Profile" title="Click to save profile" />
        <g:link class="btn btn_blue" controller="profile" action="profileBuilder" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>

    <div class="actionLeft">
      <g:submitButton class="btninput" style="height: 1.7em; #height: 1.6em;" name="advanced" value="Search for Modules" title="Search for Modules"/>
    </div>

    <div id="yui-main">
      <div id="main_content" class="subpage subpageNoMultiAction">
        <div class="profileEditor">
          <div id="currentProfileDisplay">
            <div class="info">
              <div class="info_header" title="Security Modules"><g:if test="${isNew}" >	Select the Security Modules for your new profile</g:if>
                <g:else>Security Modules</g:else>
              </div>
              <table class="security">
                <tr>
                  <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click here to select all" /></th>
                  <th style="text-align: left;"><a href="javascript:toggleModuleDescriptions();" title="Click to view all descriptions.">Security Modules</a></th>
                  <th style="text-align: center; width: 50%;"><a href="javascript:toggleModuleOptions();" title="Click to view all settings.">Settings</a></th>
                </tr>
                <g:each var="module" status="i" in="${masterModuleList}">
                  <g:render template="/profile/profileBuilder/moduleRow" model="['module':module,'i':i,'enabled':profile.securityModules?.contains(module)]" />
                </g:each>
              </table>
            </div>
          </div>
          </g:form>
        </div>
      </div>
    </div>
</div>
</body>
</html>
