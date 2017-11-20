<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="managing-profiles"/>
    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="managing-profiles-su"/>
    </sbauth:isBulk>

    <title>Profiles</title>
    <r:require modules="application"/>
    <r:script>
      $(document).ready(function() {
          $("#selectionCheckbox").click(function() {
            if ( $('#selectionCheckbox').attr('checked') )
            {
                // Check checkboxes whose name starts with "selected_"
                $('input[type="checkbox"]input[name="securityProfileList"]').attr('checked', true);

            }
            else
            {
                // Uncheck checkboxes whose name starts with "selected_"
                $('input[type="checkbox"]input[name="securityProfileList"]').removeAttr('checked');
            }
          })

          $("#deleteMulti").click(function() {
            if ( checkForNoneSelected('No profiles were selected for deletion.') ) {
                return confirm('Are you sure you want to delete the selected profile(s)?');
            }
            return false;
          })

          $('.action_title').corners("5px top-left top-right");
          $('.actions').corners("5px");

          // Mark first column header as sorted, if user did not sort any column
          markFirstColumnAsSortedIfNotUserSorted( true );
      });
    </r:script>

    <r:script>
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
<body id="profiles">
  <div id="per_page_container">

    <g:uploadForm method="post" action="importSecurityProfile">

      <div id="per_page_header" title="Profiles">
        <h1>Profiles</h1>
      </div>

      <!-- LEFT MARGIN ACTION BUTTONS FROM INCLUDED TEMPLATE -->
      <div id="actionbar_outer" class="yui-b">
        <g:render template="/profile/actionbar_multi" />
      </div>

      <div id="yui-main">
        <div class="yui-b">
          <div id="main_content" class="subpage">

            <div id="table_border">
              <div id="table_control" style="text-align: right;">
                <!--import div-->

                <div id="upload" style="display: none;" title="Import Profiles">
                  <div class="fileinputs">Profile to Import
                    <input type="file" name="profileFile" size="23" class="file" />
                    <div class="fakefile">
                      <!--	<input />
												<img src="${resource(dir:'images',file:'browse.png')}" alt="Browse" onmouseover='this.src="${resource(dir:'images',file:'browse_over.png')}"'  onmouseout='this.src="${resource(dir:'images',file:'browse.png')}"' />-->
                    </div>
                    <g:submitButton class="btninput" name="uploadProfile" value="Import" title="Click to Import Profiles" /> <input type="reset" class="btninput" value="Clear" title="Click to Clear Profiles Import" />
                  </div>
                </div>

                <!--end import-->
              </div>
              <table>
                <tr>
                  <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click here to select all" /></th>
                  <g:sortableColumn class="profileNameColumn" property="name" title="Name" />
                  <g:sortableColumn class="profileIndustryStandardColumn" property="writeProtected" title="Industry Standard" />
                  <g:sortableColumn property="shortDescription" title="Summary" />
                </tr>
                <g:each var="profile" status="i" in="${profileList}">
                  <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                    <td title="Click to Select">
                      <g:if test="${profile.writeProtected}">
<!--
                        <img class="verticalMiddle" title="Industry Profile" src="${resource(dir:'images',file:'SB_fixed_profile.png')}"/>
-->
                      </g:if>
                      <g:else>
                        <g:checkBox name="securityProfileList" value="${profile.id}" checked="${selectedList?.contains(profile.id) ? true : false }" />
                      </g:else>
                    </td>
                    <td class="profileNameColumn" title="Profile Name"><g:link controller="profile" action="profileBuilder" event="modify" id="${profile.id}">${profile.name}</g:link></td>
                    <td class="profileIndustryProfileColumn center"><g:checkBox name="writeProtected" value="${profile.writeProtected}" checked="${profile.writeProtected}" disabled="true" /></td>
                    <td title="Summary">${profile.shortDescription ?: "None Specified"}</td>
                  </tr>
                </g:each>
              </table>              
            </div>	 <!-- end table_border -->

            <div class="paginateButtons" style="margin: 1%;">
              <g:paginate prev="&laquo; previous" next="next &raquo;" max="${maxPerPage}" total="${profileList.totalCount}" />
            </div>
            
          </div> <!-- end main_content -->
          
        </div> <!-- end yui-b -->
      </div> <!-- end yui-main -->
    </g:uploadForm>
  </div>
</body>
</html>
