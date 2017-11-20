
<html>
  <g:set var="isNew" value="${ profile?.id ? false : true }"/>
  <g:set var="isSystem" value="${profile?.writeProtected }" />
  <head>    
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <meta name="layout" content="main" />
  <g:if test="${isNew}">
    <meta name="contextSensitiveHelp" content="creating-new-security-profile"/>
  </g:if>
  <g:else>
    <meta name="contextSensitiveHelp" content="editing-a-sec-profile"/>
  </g:else>
  <title>
    <g:if test="${isNew}">
        Create Profile
    </g:if>
    <g:else>
      <g:if test="${isSystem}">
        Show Profile > ${profile?.name}
      </g:if>
      <g:else>
        Edit Profile > ${profile?.name}
      </g:else>
    </g:else>
  </title>
  <r:require modules="application,tcs_sbmodules"/>
  <r:script >

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

  <g:if test="${isSystem}">
    $(document).ready(function() {
        disableAll();
    });
  </g:if>

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
		               Create New Profile
          </g:if>
          <g:else>
            <g:if test="${isSystem}">
              Show Profile > ${profile?.name}
            </g:if>
            <g:else>
              Edit Profile > ${profile?.name}
            </g:else>
          </g:else>
        </h1>
      </div>
      <div class="headerRight">
        <g:if test="${!isSystem}">
          <g:submitButton class="btninput btninput_blue" style="padding-bottom: .5em;" name="save" value="Save Profile" title="Click to save profile" />
        </g:if>
        <g:if test="${isSystem}">
          <g:link class="btn btn_blue" controller="profile" action="profileBuilder" event="cancel">&laquo; Back</g:link>
        </g:if>
        <g:else>
          <g:link class="btn btn_blue" controller="profile" action="profileBuilder" event="cancel">Cancel</g:link>
        </g:else>

      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <div class="profileEditor">
          <div id="currentProfileDisplay">
            <div id="table_border">
              <div class="info_header" title="Profile">Profile</div>
              <span class="required" title="* Indicates required field">* Indicates required field</span>
              <table class="logged" style="height: 25px"><!-- class="enterprise"-->
                <tr>
                  <td class="propName" title="Name"><label for="Name">Name*</label>:</td>
                  <td class="profileName" style="text-align: left">
                <g:textField class="input" name="name" onKeyUp="limitText(this.form.name,35);" value="${profile.name}" size="30" title="Enter Profile Name" />
                </td>
                <td style="#padding: 0.25em;"><a class="btn" href="javascript:showHideElement('div_extraInfo');" title="Click for Details">Details</a></td>
                </tr>
              </table>
              <div id="div_extraInfo" style="display:none;" class="logged_">
                <table class="enterprise pad5all">
                  <tr>
                    <td style="vertical-align:top;" class="profileName" title="Summary"><label for="Summary">Summary</label>:</td>
                    <td><g:textField class="input" name="shortDescription" value="${profile.shortDescription}" size="60" onKeyUp="limitText(this.form.shortDescription,80);" title="Enter Short Description" /></td>
                  </tr>
                  <tr>
                    <td style="vertical-align:top;" class="profileName" title="Description will appear in the assessment reports generated with this profile."><label for"Description">Description</label>:</td>
                    <td><g:textArea class="input" name="description" value="${profile.description}" rows="5" cols="62" wrap="soft"/></td>
                  </tr>
                  <tr>
                    <td style="vertical-align:top;" class="profileName" title="Comments"><label for="Comments">Comments</label>:</td>
                    <td><g:textArea class="input" name="comments" value="${profile.comments}" rows="5" cols="62" wrap="soft"/></td>
                  </tr>
                </table>
              </div>

              <table>
                <g:if test="${!isSystem}">
                  <tr>
                    <td colspan="2" class="logged">
                  <g:submitButton class="btninput" name="basicModuleSelector" value="Add/Remove Modules" title="Add/Remove Modules" />
                  </td>
                  </tr>
                </g:if>
                <tr>
                  <th><a href="javascript:toggleModuleDescriptions();" title="Click to view all descriptions.">Security Modules</a></th>
                  <th style="text-align: center; width: 50%"><a href="javascript:toggleModuleOptions();" title="Click to view all settings.">Settings</a></th>
                </tr>
                <g:if test="${profile?.securityModules}">
                  <g:each var="module" status="i" in="${profile?.securityModules}">
                    <g:render template="/profile/profileBuilder/settingsRow" model="['module':module,'i':i,'isProtected':isSystem]" />
                  </g:each>
                </g:if>
                <g:else>
                  <tr class="row_even">
                    <td style="text-align:center;" colspan="2">No modules in current profile</td>
                  </tr>
                </g:else>
              </table>
            </div>
          </div>
        </div>
        </g:form>

      </div>
    </div>
</div>
</body>
</html>
