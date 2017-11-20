
<%@ page import="com.trustedcs.sb.metadata.baseline.BaselineProfile" %>
<html>
  <head>
  <nav:resources override="true"/>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="layout" content="main" />
  
  <meta name="contextSensitiveHelp" content="managing-profiles"/> 
  <sbauth:isBulk>
    <meta name="contextSensitiveHelp" content="managing-profiles-su"/>
  </sbauth:isBulk>

  <g:set var="entityName" value="${message(code: 'baselineProfile.label', default: 'BaselineProfile')}" />
  <title><g:message code="baselineProfile.list.label"/></title>
  <r:require modules="application"/>
  <r:script >

    $(document).ready(function() {

      $("#selectionCheckbox").click(function() {
        if ( $('#selectionCheckbox').attr('checked') ) {
          // Check checkboxes whose name starts with "selected_"
          $('input[type="checkbox"]input[name="baselineProfileList"]').attr('checked', true);
        }
        else {
          // Uncheck checkboxes whose name starts with "selected_"
          $('input[type="checkbox"]input[name="baselineProfileList"]').removeAttr('checked');
        }
      })

       $("#deleteMulti").click(function() {
         if ( checkForNoneSelected('No ${entityName}(s) were selected for deletion.') ) {
           return confirm('Are you sure you want to delete the selected ${entityName}(s)?');
         }
         return false;
       })

       $('.action_title').corners("5px top-left top-right");
       $('.actions').corners("5px");

        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( true );
    });
  </r:script>

  <r:script >
    $(document).ready(function() {
      $('input[type=file]').each(function(){
        $(this).addClass('file').addClass('hidden');
        $(this).parent().append($('<div class="fakefile" />').append($('<input type="text" style="cursor:pointer;"class="input" />').attr('id',$(this).attr('id')+'__fake')).append($('&nbsp;&nbsp;<img src="${resource(dir:'images',file:'browse_over.png')}" alt="Browse" />')));

        $(this).bind('change', function() {
                        $('#'+$(this).attr('id')+'__fake').val($(this).val());;
        });
        $(this).bind('mouseout', function() {
                        $('#'+$(this).attr('id')+'__fake').val($(this).val());;
        });
    });
  });
  </r:script>

  <r:script >
    function toggleVisibility(upload){
      if (upload.style.visibility=="hidden"){
        upload.style.visibility="visible";
      }
      else {
        upload.style.visibility="hidden";
      }
    }
  </r:script>
  
</head>
<body>
  <div id="per_page_container">
    <g:uploadForm id="baselineProfileForm" method="post" action="importBaselineProfile">

      <!-- Gold Header -->
      <div class="container" id="per_page_header" title="Baseline Profiles">
        <div class="headerLeft">
          <h1><g:message code="baselineProfile.list.label"/></h1>
        </div>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <!-- start actionbar -->
      <div id="actionbar_outer" class="yui-b">        
        <div id="actionbar">
          <div class="actions">
            <div class="action_title"><g:message code="baselineProfile.label"/></div>
            <ui>
              <li><g:link class="action_bar_btn" action="create" title="Click to Create a New Baseline Profile">New</g:link></li>
              <li><a class="action_bar_btn" href="javascript:showHideElement('upload');" style="#margin: 0.5em .17em .5em 0.12em;" title="Click to Import Baseline Profiles">Import</a></li>
              <li><g:actionSubmit action="deleteMulti" class="action_bar_btninput" id="deleteMulti" title="Click to Delete selected Baseline Profiles" value="Delete" /></li>
              <li><g:actionSubmit action="copyProfile" class="action_bar_btninput" id="copyProfile" title="Click to Copy Baseline Profiles" name="copyProfile" value="Copy" /></li>
              <li><g:actionSubmit action="exportProfile" class="action_bar_btninput" id="exportProfile" title="Click to Export Baseline Profiles" name="exportProfile" value="Export" /></li>
            </ui>
          </div>
        </div>
      </div>
      <!-- end actionbar -->

      <div id="yui-main">
        <div class="yui-b">
          <div id="main_content" class="subpage">
            <div id="table_border">

              <!--import div-->
              <div id="table_control" style="text-align: right;">

                <div id="upload" style="display: none;" title="Import Baseline Profiles">
                  <div class="fileinputs">Baseline Profile to Import
                    <input type="file" name="profileFile" size="23" class="file" />
                    <div class="fakefile">
                      <!--	<input />
												<img src="${resource(dir:'images',file:'browse.png')}" alt="Browse" onmouseover='this.src="${resource(dir:'images',file:'browse_over.png')}"'  onmouseout='this.src="${resource(dir:'images',file:'browse.png')}"' />-->
                    </div>
                    <g:submitButton action="importBaselineProfile" class="btninput" name="uploadProfile" value="Import" title="Click to Import Baseline Profiles" /> <input type="reset" class="btninput" value="Clear" title="Click to Clear Baseline Profiles Import" />
                  </div>
                </div>
              </div>
              <!--end import-->

              <div class="list">
                <table>
                  <thead>
                    <tr>
                      <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click to select all" /></th>
                      <g:sortableColumn class="profileNameColumn" property="name" title="${message(code: 'baselineProfile.id.label', default: 'Name')}" />
                      <g:sortableColumn class="profileIndustryStandardColumn" property="writeProtected" title="Industry Standard" />
                      <g:sortableColumn property="summary" title="${message(code: 'baselineProfile.id.label', default: 'Summary')}" />
                    </tr>
                  </thead>
                  <tbody>
                  <g:each in="${baselineProfileInstanceList}" status="i" var="baselineProfileInstance">
                    <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                      <td>
                        <g:if test="${baselineProfileInstance.writeProtected}">
<!--
                          <img class="verticalMiddle" title="Industry Profile" src="${resource(dir:'images',file:'SB_fixed_profile.png')}"/>
-->
                        </g:if>
                        <g:else>
                          <g:checkBox name="baselineProfileList" value="${baselineProfileInstance.id}" checked="${selectedList?.contains(baselineProfileInstance.id) ? true : false }" />
                        </g:else>
                      </td>
                      <td class="profileNameColumn"><g:link action="show" id="${baselineProfileInstance.id}">${fieldValue(bean: baselineProfileInstance, field: "name")}</g:link></td>
                      <td class="profileIndustryProfileColumn center"><g:checkBox name="writeProtected" value="${baselineProfileInstance.writeProtected}" checked="${baselineProfileInstance.writeProtected}" disabled="true" /></td>
                      <td title="Summary">${baselineProfileInstance.summary ?: "None Specified"}</td>
                    </tr>
                  </g:each>
                  </tbody>
                </table>
              </div>              
            </div>
            <div class="paginateButtons" style="margin: 1%;">
              <g:paginate prev="&laquo; previous" next="next &raquo;" max="${maxPerPage}" total="${baselineProfileInstanceList.totalCount}" />
            </div>
          </div>
        </div>
      </div>
    </g:uploadForm>
  </div>
</body>
</html>
